# -*- coding: utf-8 -*-
"""Снимает разделы приложения безголовым Chrome.

Зачем. Разбор скрипта говорит, что файл не сломан, но ничего не говорит про
то, как экран выглядит: налезли ли подписи, влезла ли полоса дня, не ушла ли
лента под нижнюю панель. Это видно только глазами, и снимок — единственный
способ посмотреть, не открывая телефон.

Данные берём из `webapp/_стенд.json`, а не из настоящей базы: у неё за
океаном свои сроки, а нам нужны предсказуемые числа и все состояния сразу,
включая пустые и тревожные. Файл начинается с подчёркивания, поэтому в
облачную сборку он не уезжает.

    python3 tools_снимок.py            # все разделы в data/снимки
    python3 tools_снимок.py out        # только «Вышло»
"""

import http.server
import json
import socket
import subprocess
import sys
import threading
from pathlib import Path

import config

КОРЕНЬ = Path(__file__).resolve().parent
ПАПКА = КОРЕНЬ / "webapp"
СТЕНД = ПАПКА / "_стенд.json"
КУДА = КОРЕНЬ / "data" / "снимки"

# Телефон, на котором это открывают. 390×844 — iPhone 14; всё, что не влезает
# в эту ширину, на деле не влезает никуда.
#
# Само окно браузера при этом шире: безголовый Chrome не открывает окно уже
# 500 пикселей и «--window-size=390» молча пропускает мимо ушей. Поэтому
# приложение живёт внутри рамки ровно на 390, а окно берём с запасом.
ШИРИНА, ВЫСОТА = 390, 844
ОКНО_Ш, ОКНО_В = 520, 880

РАЗДЕЛЫ = ["today", "plan", "out", "out-числа", "stock"]


class Ручка(http.server.SimpleHTTPRequestHandler):
    """Отдаёт файлы страницы, а на запросы к API — заготовленный ответ."""

    def __init__(self, *а, **кв):
        super().__init__(*а, directory=str(ПАПКА), **кв)

    def log_message(self, *_):
        pass

    def _json(self, тело):
        сырое = json.dumps(тело, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(сырое)))
        self.end_headers()
        self.wfile.write(сырое)

    def _ответить(self):
        стенд = json.loads(СТЕНД.read_text(encoding="utf-8"))
        путь = self.path.split("?")[0]
        for имя, ключ in (("/api/state", "state"), ("/api/history", "history"),
                          ("/api/stats", "stats")):
            if путь.endswith(имя):
                return self._json(стенд[ключ])
        return None

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._ответить()
        if self.path.startswith("/logo.png"):
            self.path = "/logo.png"
        return super().do_GET()

    def do_POST(self):
        длина = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(длина)
        if self._ответить() is None:
            self._json({})


def _порт() -> int:
    с = socket.socket()
    с.bind(("127.0.0.1", 0))
    порт = с.getsockname()[1]
    с.close()
    return порт


def снять(разделы=None) -> list[Path]:
    разделы = разделы or РАЗДЕЛЫ
    хром = config.хром()
    if not хром:
        raise SystemExit("Chrome не найден: поставьте CHROME_PATH")
    КУДА.mkdir(parents=True, exist_ok=True)
    порт = _порт()
    сервер = http.server.ThreadingHTTPServer(("127.0.0.1", порт), Ручка)
    threading.Thread(target=сервер.serve_forever, daemon=True).start()
    сделано = []
    try:
        for раздел in разделы:
            итог = КУДА / f"{раздел}.png"
            # Через рамку, а не напрямую: почему — рассказано в _рамка.html.
            адрес = f"http://127.0.0.1:{порт}/_рамка.html#{раздел}"
            subprocess.run(
                [хром, "--headless", "--disable-gpu", "--hide-scrollbars",
                 "--no-sandbox", "--disable-dev-shm-usage",
                 "--disable-background-networking", "--no-first-run",
                 "--disable-extensions", "--disable-sync",
                 "--disable-default-apps", "--mute-audio",
                 # Странице надо успеть сходить за состоянием и перерисоваться.
                 "--virtual-time-budget=4000",
                 f"--screenshot={итог}",
                 f"--window-size={ОКНО_Ш},{ОКНО_В}",
                 "--default-background-color=0f0f0fff",
                 "--force-device-scale-factor=2", адрес],
                capture_output=True, timeout=90)
            if итог.exists():
                сделано.append(итог)
                print(f"снято: {итог}")
            else:
                print(f"не вышло: {раздел}")
    finally:
        сервер.shutdown()
    return сделано


if __name__ == "__main__":
    снять(sys.argv[1:] or None)
