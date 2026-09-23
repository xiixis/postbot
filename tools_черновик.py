#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Черновик карусели в TikTok через Zernio: python tools_черновик.py <папка на столе> [--отправить]

Последний шаг после «готово» и `Style/выпуск.py` (`.claude/ПУБЛИКАЦИЯ.md`, шаг 9).
Берёт папку `~/Desktop/Посты/<папка>`: кадры `NN.jpg`, `название.txt`, `подпись.txt`.

Без `--отправить` только показывает, что уйдёт. С ним:
1. кадры едут в хранилище Supabase под УНИКАЛЬНЫМИ именами (`<слаг>-NN.jpg`):
   `storage.положить` кладёт по голому имени с upsert, и `01.jpg` двух постов
   затирают друг друга (поймано 23.09.2026);
2. `POST /v1/posts` Zernio с `tiktokSettings.draft: true` — пост падает во входящие
   TikTok владельца, он ставит музыку из сохранённых и публикует с телефона.

Решения владельца, зашитые здесь (23.09.2026):
- `auto_add_music: false` — музыку он выбирает сам; конкретный звук API в черновике
  всё равно игнорирует;
- `video_made_with_ai: false` — «ИИ не нужно ставить».

Лимит TikTok — 5 черновиков в сутки на аккаунт. Отправка — действие во внешнем мире:
только по прямому слову владельца.
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import dotenv_values

import storage

ТУТ = Path(__file__).resolve().parent
СТОЛ = Path.home() / "Desktop" / "Посты"
API = "https://zernio.com/api/v1"
АККАУНТ_TIKTOK = "6ab297a48d284ffb212def20"     # @4x_tube в Zernio (профиль Default)

_ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                 "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                 "yu", "ya"]))


def слаг(имя: str) -> str:
    """Латинское имя папки для хранилища: кириллицу адреса картинок не любят."""
    т = "".join(_ЛАТ.get(б, б) for б in имя.lower())
    return re.sub(r"[^a-z0-9]+", "-", т).strip("-")[:60]


def ключ() -> str:
    к = (dotenv_values(ТУТ / ".env").get("ZERNIO_API_KEY") or "").strip()
    if not к:
        raise SystemExit("нет ZERNIO_API_KEY в postbot/.env")
    return к


def собрать(папка: Path) -> dict:
    кадры = sorted(папка.glob("[0-9][0-9].jpg"))
    if not кадры:
        raise SystemExit(f"в {папка} нет кадров NN.jpg — сперва Style/выпуск.py")
    название = (папка / "название.txt").read_text(encoding="utf-8").strip()
    подпись = (папка / "подпись.txt").read_text(encoding="utf-8").strip()
    if len(название) > 90:
        raise SystemExit(f"название {len(название)} знаков, TikTok берёт до 90")
    return {"кадры": кадры, "название": название, "подпись": подпись}


def залить(кадры: list[Path], имя: str) -> list[str]:
    with tempfile.TemporaryDirectory() as врем:
        копии = []
        for к in кадры:
            н = Path(врем) / f"{имя}-{к.name}"
            shutil.copy(к, н)
            копии.append(н)
        ссылки = storage.положить_все(копии)
    if not all(с.startswith("http") for с in ссылки):
        raise SystemExit("не все кадры легли в хранилище: " + ", ".join(с for с in ссылки if not с.startswith("http")))
    for с in (ссылки[0], ссылки[-1]):
        if requests.get(с, timeout=60).status_code != 200:
            raise SystemExit(f"кадр не открывается по ссылке: {с}")
    return ссылки


def отправить(пост: dict, ссылки: list[str]) -> dict:
    тело = {
        "content": пост["название"],
        "mediaItems": [{"type": "image", "url": у} for у in ссылки],
        "platforms": [{"platform": "tiktok", "accountId": АККАУНТ_TIKTOK}],
        "tiktokSettings": {
            "draft": True, "privacy_level": "PUBLIC_TO_EVERYONE", "allow_comment": True,
            "media_type": "photo", "photo_cover_index": 0, "description": пост["подпись"],
            "auto_add_music": False, "video_made_with_ai": False,
            "content_preview_confirmed": True, "express_consent_given": True,
        },
        "publishNow": True,
    }
    о = requests.post(f"{API}/posts", headers={"Authorization": f"Bearer {ключ()}"}, json=тело, timeout=180)
    д = о.json() if о.content else {}
    if о.status_code >= 300:
        raise SystemExit(f"Zernio {о.status_code}: {д.get('error') or д.get('message') or о.text[:300]}")
    return д.get("post", д)


def main():
    р = argparse.ArgumentParser()
    р.add_argument("папка", help="имя папки в ~/Desktop/Посты или путь к ней")
    р.add_argument("--отправить", action="store_true", help="без флага — только показать")
    а = р.parse_args()
    папка = Path(а.папка) if Path(а.папка).is_dir() else СТОЛ / а.папка
    пост = собрать(папка)
    print(f"{папка.name}: {len(пост['кадры'])} кадров")
    print(f"название ({len(пост['название'])}): {пост['название']}")
    print("подпись:", пост["подпись"].replace("\n", " / "))
    if not а.отправить:
        print("проба: ничего не отправлено (добавь --отправить)")
        return
    ссылки = залить(пост["кадры"], слаг(папка.name))
    итог = отправить(пост, ссылки)
    for пл in итог.get("platforms", []):
        print(f"черновик: Zernio {итог.get('_id')} · {пл.get('status')} · {пл.get('platformPostId')}"
              + (f" · ОШИБКА {пл.get('errorMessage')}" if пл.get("errorMessage") else ""))
    print("дальше: TikTok → Входящие → Системные уведомления → музыка из «Избранного» → опубликовать")


if __name__ == "__main__":
    sys.exit(main())
