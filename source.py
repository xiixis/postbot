# -*- coding: utf-8 -*-
"""Материал для поста: ссылка на статью или своя идея текстом.

Ссылку бот открывает сам и вытаскивает читаемый текст. Пересказ чужой статьи
своими словами для своей аудитории, это нормальная работа редактора; копировать
чужие абзацы нельзя, и об этом отдельно сказано в задании модели.

Адреса берём только внешние. Владелец бота не станет специально просить
открыть локальный адрес, но бот ходит по ссылке с той же машины, где живёт
конвейер, и служебные адреса ему видны. Проще закрыть, чем однажды объяснять.
"""

import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

ССЫЛКА = re.compile(r"https?://[^\s<>\"']+")
ПРЕДЕЛ = 2 * 1024 * 1024          # больше двух мегабайт страницы не читаем
ВЫДЕРЖКА = 6000                   # столько символов уходит в модель


class _Текст(HTMLParser):
    """Выдирает читаемый текст. Полноценный парсер тут был бы лишней зависимостью."""

    ПРОПУСК = {"script", "style", "noscript", "svg", "head", "nav", "footer"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.куски: list[str] = []
        self.заголовок = ""
        self._в_заголовке = False
        self._глубина = 0

    def handle_starttag(self, тег, атрибуты):
        if тег in self.ПРОПУСК:
            self._глубина += 1
        if тег == "title":
            self._в_заголовке = True

    def handle_endtag(self, тег):
        if тег in self.ПРОПУСК and self._глубина:
            self._глубина -= 1
        if тег == "title":
            self._в_заголовке = False

    def handle_data(self, данные):
        if self._в_заголовке:
            self.заголовок += данные
        elif not self._глубина and данные.strip():
            self.куски.append(данные.strip())


def _внешний(адрес: str) -> bool:
    узел = urlparse(адрес).hostname or ""
    try:
        сведения = socket.getaddrinfo(узел, None)
    except OSError:
        return False
    for сведение in сведения:
        ип = ipaddress.ip_address(сведение[4][0])
        if ип.is_private or ип.is_loopback or ип.is_link_local or ип.is_reserved:
            return False
    return True


def забрать(адрес: str) -> dict | None:
    """Заголовок и текст страницы. None, если не открылась."""
    if not _внешний(адрес):
        return None
    try:
        о = requests.get(адрес, timeout=20, stream=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; 4xTubeBot/1.0)"})
        о.raise_for_status()
        if "html" not in о.headers.get("Content-Type", "text/html"):
            return None
        сырое = о.raw.read(ПРЕДЕЛ, decode_content=True).decode(
            о.encoding or "utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        return None

    разбор = _Текст()
    try:
        разбор.feed(сырое)
    except Exception:                                        # noqa: BLE001
        pass
    # Сначала берём только длинные куски: меню, списки языков и подвалы состоят
    # из коротких, и без этого фильтра первые полторы тысячи символов страницы
    # уходят в модель навигацией.
    крупные = [к for к in разбор.куски if len(к) >= 60]
    текст = re.sub(r"\s{2,}", " ", " ".join(крупные or разбор.куски))
    заголовок = " ".join(разбор.заголовок.split())[:200]
    if not заголовок and len(текст) < 200:
        return None
    return {"адрес": адрес, "заголовок": заголовок, "текст": текст[:ВЫДЕРЖКА]}


def разобрать(ввод: str) -> tuple[str | None, dict | None]:
    """Из строки владельца делает тему и, если была ссылка, содержимое страницы."""
    ввод = (ввод or "").strip()
    if not ввод:
        return None, None
    найдена = ССЫЛКА.search(ввод)
    if not найдена:
        return ввод[:300], None
    материал = забрать(найдена.group(0))
    остальное = ССЫЛКА.sub("", ввод).strip(" .,:;\n")
    тема = остальное[:300] or None
    if not материал:
        # Страница не открылась: не молчим, а пишем по адресу как по теме. Сам
        # адрес обязан остаться в теме, даже если владелец прислал ссылку со
        # словами: по нему потом ставится последняя строка поста, и без него
        # получится рассказ про вещь, до которой читателю не добраться.
        хвост = f"по ссылке {найдена.group(0)}"
        return (f"{тема}, {хвост}" if тема else хвост), None
    return тема, материал
