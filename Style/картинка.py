# -*- coding: utf-8 -*-
"""Нарисовать картинку для кадра карусели: python3 картинка.py <файл.png> "<описание>" [--форма 4:5]

Тот же канал, которым `postbot/mascot.py` рисует кота (Gemini, ключ из `postbot/.env`), но
без эталона персонажа и без хромакея: здесь нужна не поза кота, а предметная сцена под текст
кадра. Опорные картинки — `--опора <файл>` (можно несколько): модель держится их по стилю.

Текст на картинке запрещён прямо в задании: кадр несёт свой набранный текст, а буквы от
модели приходят кривыми и спорят с вёрсткой.
"""
import argparse
import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, "/Users/xiix/4xSoft/postbot")
import config  # noqa: E402
import requests  # noqa: E402

API = "https://generativelanguage.googleapis.com/v1beta/models/{модель}:generateContent"
# Vertex тратит кредиты Google Cloud, AI Studio — предоплату, которая кончилась.
# Поэтому сначала пробуем Vertex, и только если он недоступен — прежний путь по ключу.
ЧЕРЕЗ_VERTEX = os.getenv("КАРТИНКИ_БЕЗ_VERTEX", "") == ""
БЕЗ_БУКВ = ("\n\nSTRICTLY NO WRITING ANYWHERE IN THE IMAGE: no text, no letters, no numbers, "
            "no watermarks, no labels, no UI with readable words. The frame carries its own "
            "typeset text, and letters from the model collide with it.")


def нарисовать(описание: str, форма: str = "4:5", опоры: list[Path] = (), размер: str = "2K",
               буквы: bool = False) -> bytes:
    """`буквы` снимает запрет на надписи: этикетка бренда на товаре без них не выходит."""
    части = [{"text": описание + ("" if буквы else БЕЗ_БУКВ)}]
    for о in опоры:
        части.append({"inlineData": {"mimeType": "image/png" if о.suffix == ".png" else "image/jpeg",
                                     "data": base64.b64encode(о.read_bytes()).decode()}})
    тело = {"contents": [{"role": "user", "parts": части}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": форма, "imageSize": размер}}}
    if ЧЕРЕЗ_VERTEX:
        import вертекс
        адрес, заголовки = вертекс.адрес(config.МОДЕЛЬ_КАРТИНОК), вертекс.заголовки()
    else:
        if not config.КЛЮЧ_GEMINI:
            raise SystemExit("GEMINI_API_KEY не задан и Vertex выключен")
        адрес = API.format(модель=config.МОДЕЛЬ_КАРТИНОК)
        заголовки = {"x-goog-api-key": config.КЛЮЧ_GEMINI, "Content-Type": "application/json"}
    о = requests.post(адрес, headers=заголовки, json=тело, timeout=300)
    if о.status_code >= 400:
        raise SystemExit(f"{о.status_code}: {о.json().get('error', {}).get('message', о.text)[:300]}")
    for ч in о.json()["candidates"][0]["content"]["parts"]:
        д = ч.get("inlineData") or ч.get("inline_data")
        if д and д.get("data"):
            return base64.b64decode(д["data"])
    raise RuntimeError("модель не вернула картинку")


def main():
    р = argparse.ArgumentParser()
    р.add_argument("файл")
    р.add_argument("описание")
    р.add_argument("--форма", default="4:5", help="соотношение сторон: 4:5, 1:1, 3:4…")
    р.add_argument("--опора", action="append", default=[], help="картинка-образец стиля")
    р.add_argument("--размер", default="2K", help="1K, 2K или 4K; кадру 1620×2160 мало 1K")
    р.add_argument("--буквы", action="store_true", help="разрешить надписи: этикетки брендов на товаре")
    а = р.parse_args()
    путь = Path(а.файл)
    путь.parent.mkdir(parents=True, exist_ok=True)
    путь.write_bytes(нарисовать(а.описание, а.форма, [Path(о) for о in а.опора], а.размер, а.буквы))
    print(f"{путь} — {путь.stat().st_size // 1024} КБ, модель {config.МОДЕЛЬ_КАРТИНОК}")


if __name__ == "__main__":
    main()
