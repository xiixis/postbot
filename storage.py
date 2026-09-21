# -*- coding: utf-8 -*-
"""Где лежат карточки постов.

Пока всё крутилось на маке, карточки были файлами рядом с кодом, и этого
хватало. С переездом приложения на Vercel так больше нельзя: страница живёт в
чужом дата-центре и до файлов на маке не дотянется.

Поэтому карточки уезжают в хранилище Supabase, а в базе остаётся ссылка.
Ссылка постоянная и открывается напрямую, минуя наш код: браузер забирает
картинку у Supabase, а не гоняет её через приложение.

Файловый путь тоже понимается: старые посты не ломаются, и на маке без
настроенного хранилища всё работает как раньше.
"""

import os
from pathlib import Path

import requests

import config

АДРЕС = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
КЛЮЧ = os.getenv("SUPABASE_KEY", "").strip()
ВЕДРО = os.getenv("SUPABASE_BUCKET", "cards").strip()
ПРЕДЕЛ = 4 * 1024 * 1024      # карточка весит около полумегабайта; всё, что
                              # сильно больше, это сбой отрисовки, а не картинка


def включено() -> bool:
    return bool(АДРЕС and КЛЮЧ)


def _заголовки(тип: str | None = None) -> dict:
    ш = {"Authorization": f"Bearer {КЛЮЧ}", "apikey": КЛЮЧ}
    if тип:
        ш["Content-Type"] = тип
    return ш


def положить(файл: Path) -> str | None:
    """Заливает карточку и возвращает постоянную ссылку на неё."""
    if not включено() or not Path(файл).exists():
        return None
    вес = Path(файл).stat().st_size
    if вес > ПРЕДЕЛ:
        return None
    имя = Path(файл).name
    тип = ("image/jpeg" if имя.lower().endswith((".jpg", ".jpeg"))
           else "image/webp" if имя.lower().endswith(".webp") else "image/png")
    о = requests.post(f"{АДРЕС}/storage/v1/object/{ВЕДРО}/{имя}",
                      headers={**_заголовки(тип), "x-upsert": "true"},
                      data=Path(файл).read_bytes(), timeout=120)
    if о.status_code not in (200, 201):
        return None
    return f"{АДРЕС}/storage/v1/object/public/{ВЕДРО}/{имя}"


def положить_все(файлы) -> list[str]:
    """Ссылки на все файлы в прежнем порядке; не залитый остаётся путём.

    По одному десять слайдов шли ~7 с: каждый — отдельный поход в хранилище
    в Ирландии. Четыре разом — около двух.
    """
    from concurrent.futures import ThreadPoolExecutor
    файлы = [ф for ф in файлы if ф]
    with ThreadPoolExecutor(max_workers=4) as пул:
        ссылки = list(пул.map(lambda ф: положить(ф), файлы))
    return [с or str(ф) for с, ф in zip(ссылки, файлы)]


def байты(ссылка: str) -> bytes | None:
    """Содержимое карточки, откуда бы она ни лежала."""
    if not ссылка:
        return None
    if ссылка.startswith("http"):
        о = requests.get(ссылка, timeout=60)
        return о.content if о.ok else None
    п = Path(ссылка)
    return п.read_bytes() if п.exists() else None


def во_временный(ссылка: str) -> Path | None:
    """Локальный файл: телеграму нужно отдать картинку, а не адрес.

    Отправлять по ссылке телеграм умеет, но тогда он тянет её сам и молча
    отваливается на любой заминке. Скачать самим надёжнее.
    """
    if not ссылка:
        return None
    if not ссылка.startswith("http"):
        п = Path(ссылка)
        return п if п.exists() else None
    # Сначала смотрим на диск. Карточки рисуются здесь же, на маке, и только
    # потом уезжают в облако — качать их обратно значит гонять по сети то, что
    # лежит в соседней папке. На карусели из двенадцати кадров это лишние
    # четыре с половиной секунды при каждой выгрузке, замерено.
    #
    # Имя файла годится в опознание: оно собрано из времени и случайных
    # шести знаков, и совпасть у двух разных карточек не может.
    свой = config.ВЫВОД / ссылка.rsplit("/", 1)[-1]
    if свой.exists() and свой.stat().st_size > 0:
        return свой
    данные = байты(ссылка)
    if not данные:
        return None
    config.ВЫВОД.mkdir(parents=True, exist_ok=True)
    п = config.ВЫВОД / ссылка.rsplit("/", 1)[-1]
    п.write_bytes(данные)
    return п
