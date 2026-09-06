# -*- coding: utf-8 -*-
"""Публикация в Threads.

Threads работает не так, как X: пост сначала собирают контейнером, а потом
отдельным запросом публикуют. Ради карусели это даже удобно, каждый снимок
кладётся своим контейнером, и в конце они собираются в один пост.

Картинки Threads забирает сам по ссылке, файлы он не принимает. Нам это ничего
не стоит: слайды и так лежат в хранилище публичной ссылкой.
"""

import os
import time

import requests

БАЗА = "https://graph.threads.net/v1.0"
ТОКЕН = os.getenv("THREADS_TOKEN", "").strip()
ПОЛЬЗОВАТЕЛЬ = os.getenv("THREADS_USER_ID", "").strip()

ПРЕДЕЛ = 500          # столько символов помещается в пост Threads
СНИМКОВ = 20          # столько снимков берёт карусель


class ОшибкаThreads(RuntimeError):
    pass


def настроен() -> bool:
    return bool(ТОКЕН and ПОЛЬЗОВАТЕЛЬ)


def _запрос(путь: str, поля: dict) -> dict:
    поля = {**поля, "access_token": ТОКЕН}
    r = requests.post(f"{БАЗА}/{путь}", data=поля, timeout=120)
    try:
        тело = r.json()
    except ValueError:
        тело = {"error": {"message": r.text[:300]}}
    if r.status_code >= 300 or "error" in тело:
        беда = (тело.get("error") or {}).get("message") or r.text[:200]
        raise ОшибкаThreads(f"{r.status_code}: {беда}")
    return тело


def _контейнер(поля: dict) -> str:
    номер = _запрос(f"{ПОЛЬЗОВАТЕЛЬ}/threads", поля).get("id")
    if not номер:
        raise ОшибкаThreads("Threads не вернул номер заготовки")
    return str(номер)


def опубликовать(текст: str, картинки: list | None = None) -> str:
    """Отправляет пост в Threads. Возвращает его номер.

    Ссылки на снимки должны быть публичными: Threads скачивает их со своей
    стороны, и путь к файлу на маке ему не годится.
    """
    if not настроен():
        raise ОшибкаThreads("не заданы THREADS_TOKEN и THREADS_USER_ID")
    текст = (текст or "").strip()
    if len(текст) > ПРЕДЕЛ:
        текст = текст[:ПРЕДЕЛ - 1].rstrip() + "…"

    ссылки = [к for к in (картинки or [])
              if isinstance(к, str) and к.startswith("http")][:СНИМКОВ]

    if len(ссылки) > 1:
        # Карусель: сначала каждый снимок отдельной заготовкой, потом они
        # собираются в один пост. Текст живёт у сборки, а не у снимков.
        дети = [_контейнер({"media_type": "IMAGE", "image_url": с,
                            "is_carousel_item": "true"}) for с in ссылки]
        заготовка = _контейнер({"media_type": "CAROUSEL",
                                "children": ",".join(дети), "text": текст})
    elif ссылки:
        заготовка = _контейнер({"media_type": "IMAGE", "image_url": ссылки[0],
                                "text": текст})
    else:
        if not текст:
            raise ОшибкаThreads("пустой пост")
        заготовка = _контейнер({"media_type": "TEXT", "text": текст})

    # Threads просит подождать, пока он заберёт картинки. Без паузы публикация
    # иногда отвечает, что заготовка ещё не готова.
    time.sleep(8 if ссылки else 1)
    ответ = _запрос(f"{ПОЛЬЗОВАТЕЛЬ}/threads_publish", {"creation_id": заготовка})
    return str(ответ.get("id", ""))


def кто_мы() -> dict:
    """Проверка ключей: чей профиль за ними стоит."""
    r = requests.get(f"{БАЗА}/me",
                     params={"fields": "id,username", "access_token": ТОКЕН},
                     timeout=60)
    тело = r.json() if r.content else {}
    if r.status_code >= 300 or "error" in тело:
        raise ОшибкаThreads((тело.get("error") or {}).get("message", r.text[:200]))
    return тело
