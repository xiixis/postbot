# -*- coding: utf-8 -*-
"""Публичный адрес для мини-приложения.

Telegram открывает мини-приложение только по https и только с адреса, который
виден из интернета. Бот живёт на ноутбуке, поэтому наружу его выводит
cloudflared: он поднимает временный туннель и выдаёт адрес вида
https://что-то.trycloudflare.com, не требуя ни аккаунта, ни домена.

Адрес меняется при каждом запуске, поэтому бот сам прописывает его в кнопку
меню. Руками ничего обновлять не нужно.

Если бот переедет на сервер со своим доменом, туннель не нужен: пропишите
WEBAPP_URL в .env, и всё это не запустится.
"""

import re
import shutil
import subprocess
import threading
import time

АДРЕС = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def доступен() -> bool:
    return bool(shutil.which("cloudflared"))


def поднять(порт: int, ждать: int = 40) -> tuple[str, subprocess.Popen] | tuple[None, None]:
    """Возвращает публичный адрес и процесс туннеля."""
    if not доступен():
        return None, None

    процесс = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{порт}",
         "--no-autoupdate"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    найденный: list[str] = []

    def читать():
        for строка in процесс.stderr:                        # type: ignore[union-attr]
            м = АДРЕС.search(строка)
            if м and not найденный:
                найденный.append(м.group(0))

    threading.Thread(target=читать, daemon=True).start()

    предел = time.time() + ждать
    while time.time() < предел and not найденный:
        if процесс.poll() is not None:
            return None, None
        time.sleep(0.3)

    if not найденный:
        процесс.terminate()
        return None, None
    return найденный[0], процесс
