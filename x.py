# -*- coding: utf-8 -*-
"""Публикация в X (бывший твиттер).

Здесь нет ни одной библиотеки поверх сети: X подписывает запросы по OAuth 1.0a,
а это тридцать строк на HMAC, и ради них тащить зависимость в облачную функцию
незачем.

Ключи берутся в кабинете разработчика X: приложению нужен доступ на запись, а
токен должен быть выпущен от имени того аккаунта, куда мы постим.
"""

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import time
from urllib.parse import quote, urlencode

import requests

КЛЮЧ = os.getenv("X_API_KEY", "").strip()
СЕКРЕТ = os.getenv("X_API_SECRET", "").strip()
ТОКЕН = os.getenv("X_ACCESS_TOKEN", "").strip()
ТОКЕН_СЕКРЕТ = os.getenv("X_ACCESS_SECRET", "").strip()

ТВИТЫ = "https://api.x.com/2/tweets"
ЗАГРУЗКА = "https://api.x.com/2/media/upload"
ЗАГРУЗКА_СТАРАЯ = "https://upload.twitter.com/1.1/media/upload.json"

ПРЕДЕЛ = 280          # столько символов помещается в один твит
СНИМКОВ = 4           # больше четырёх картинок в один твит X не берёт
ЦЕПОЧКА = 8           # столько слайдов имеет смысл тащить в цепочку ответов


class ОшибкаX(RuntimeError):
    pass


def настроен() -> bool:
    return all((КЛЮЧ, СЕКРЕТ, ТОКЕН, ТОКЕН_СЕКРЕТ))


# ── подпись ─────────────────────────────────────────────────────────────────

def _экр(значение) -> str:
    """Процентное кодирование по RFC 3986: у OAuth свой набор безопасных букв."""
    return quote(str(значение), safe="~-._")


def _подпись(метод: str, адрес: str, параметры: dict) -> str:
    """Заголовок Authorization для одного запроса.

    В подпись входят только параметры строки адреса и служебные поля OAuth.
    Тело запроса, будь то JSON или файл, не подписывается вовсе.
    """
    служебные = {
        "oauth_consumer_key": КЛЮЧ,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ТОКЕН,
        "oauth_version": "1.0",
    }
    всё = {**параметры, **служебные}
    строка = "&".join(f"{_экр(к)}={_экр(всё[к])}" for к in sorted(всё))
    основа = f"{метод.upper()}&{_экр(адрес)}&{_экр(строка)}"
    ключ = f"{_экр(СЕКРЕТ)}&{_экр(ТОКЕН_СЕКРЕТ)}".encode()
    служебные["oauth_signature"] = base64.b64encode(
        hmac.new(ключ, основа.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{_экр(к)}="{_экр(з)}"'
                                for к, з in sorted(служебные.items()))


def _ответ(r) -> dict:
    try:
        тело = r.json()
    except ValueError:
        тело = {"error": r.text[:300]}
    if r.status_code >= 300:
        подробности = (тело.get("detail") or тело.get("title")
                       or (тело.get("errors") or [{}])[0].get("message")
                       or тело.get("error") or r.text[:200])
        raise ОшибкаX(f"{r.status_code}: {подробности}")
    return тело


# ── картинки ────────────────────────────────────────────────────────────────

def _скачать(источник) -> tuple[bytes, str]:
    if isinstance(источник, str) and источник.startswith("http"):
        о = requests.get(источник, timeout=120)
        о.raise_for_status()
        return о.content, (о.headers.get("content-type") or "image/png")
    with open(источник, "rb") as f:
        тип = mimetypes.guess_type(str(источник))[0] or "image/png"
        return f.read(), тип


def залить(картинка) -> str:
    """Кладёт снимок в X и возвращает его номер для твита."""
    данные, тип = _скачать(картинка)
    for адрес in (ЗАГРУЗКА, ЗАГРУЗКА_СТАРАЯ):
        заголовки = {"Authorization": _подпись("POST", адрес, {})}
        try:
            r = requests.post(адрес, headers=заголовки,
                              files={"media": ("slide.png", данные, тип)},
                              timeout=180)
            тело = _ответ(r)
        except ОшибкаX:
            if адрес == ЗАГРУЗКА_СТАРАЯ:
                raise
            continue          # новый путь закрыт тарифом, пробуем старый
        номер = (тело.get("data") or {}).get("id") or тело.get("media_id_string")
        if номер:
            return str(номер)
    raise ОшибкаX("X не вернул номер картинки")


# ── публикация ──────────────────────────────────────────────────────────────

def _твит(текст: str, снимки: list[str], ответ_на: str | None = None) -> str:
    тело: dict = {"text": текст}
    if снимки:
        тело["media"] = {"media_ids": снимки}
    if ответ_на:
        тело["reply"] = {"in_reply_to_tweet_id": ответ_на}
    заголовки = {"Authorization": _подпись("POST", ТВИТЫ, {}),
                 "Content-Type": "application/json"}
    о = _ответ(requests.post(ТВИТЫ, headers=заголовки,
                             data=json.dumps(тело), timeout=120))
    return str((о.get("data") or {}).get("id", ""))


def опубликовать(текст: str, картинки: list | None = None) -> str:
    """Отправляет пост в X. Возвращает адрес первого твита.

    Карусель из шести слайдов в один твит не влезает: X берёт четыре снимка.
    Поэтому длинная карусель выходит цепочкой, где ответ на первый твит несёт
    остальные слайды. Читателю это привычно, а слайды остаются вместе.
    """
    if not настроен():
        raise ОшибкаX("не заданы ключи X: X_API_KEY, X_API_SECRET, "
                      "X_ACCESS_TOKEN, X_ACCESS_SECRET")
    текст = (текст or "").strip()
    if not текст:
        raise ОшибкаX("пустой текст")
    if len(текст) > ПРЕДЕЛ:
        текст = текст[:ПРЕДЕЛ - 1].rstrip() + "…"

    картинки = list(картинки or [])
    номера = [залить(к) for к in картинки[:ЦЕПОЧКА]] if картинки else []

    первый = _твит(текст, номера[:СНИМКОВ])
    остальные = номера[СНИМКОВ:]
    предыдущий = первый
    пока = 0
    while остальные:
        кусок, остальные = остальные[:СНИМКОВ], остальные[СНИМКОВ:]
        пока += 1
        предыдущий = _твит(f"({пока + 1})", кусок, предыдущий)
    return f"https://x.com/i/status/{первый}" if первый else ""


def кто_мы() -> dict:
    """Проверка ключей: чей аккаунт за ними стоит."""
    адрес = "https://api.x.com/2/users/me"
    заголовки = {"Authorization": _подпись("GET", адрес, {})}
    return _ответ(requests.get(адрес, headers=заголовки, timeout=60))
