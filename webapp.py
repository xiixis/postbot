# -*- coding: utf-8 -*-
"""Приложение с самого мака. Запаска на случай, если Vercel недоступен.

Логика та же самая: маршруты живут в api и общие для обоих входов. Здесь
только приём запроса и отдача файлов страницы. Раньше тут была своя,
вторая реализация генерации, и она неизбежно разошлась бы с рабочей.
"""

import json
import mimetypes
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

import access
import api
import config
import db
import jobs
import storage
from подпись import проверить

КОРЕНЬ = Path(__file__).resolve().parent / "webapp"


class Ручка(BaseHTTPRequestHandler):
    server_version = "postbot"

    def log_message(self, *_):                       # тишина в консоли бота
        pass

    def _отдать(self, тело: bytes, тип: str, код: int = 200, кэш: str = "no-store"):
        self.send_response(код)
        self.send_header("Content-Type", тип)
        self.send_header("Content-Length", str(len(тело)))
        self.send_header("Cache-Control", кэш)
        # Та же защита, что и в облаке: запаска включается в худший день, и
        # приложение не должно оказаться в этот день голым.
        for имя, значение in config.ЗАЩИТА.items():
            self.send_header(имя, значение)
        self.end_headers()
        self.wfile.write(тело)

    def _json(self, код: int, тело: dict):
        self._отдать(json.dumps(тело, ensure_ascii=False).encode(),
                     "application/json; charset=utf-8", код)

    def _файл(self, путь: Path):
        if not путь.exists():
            return self._отдать(b"not found", "text/plain", 404)
        тип = mimetypes.guess_type(путь.name)[0] or "application/octet-stream"
        кэш = "no-store" if путь.suffix == ".html" else "max-age=86400"
        self._отдать(путь.read_bytes(), тип, кэш=кэш)

    def do_GET(self):
        путь = unquote(urlparse(self.path).path)   # в имени файла бывает кириллица
        if путь in ("/", "/index.html"):
            return self._файл(КОРЕНЬ / "index.html")
        if путь.startswith("/card/"):
            return self._карточка(путь)
        if путь.startswith("/api/"):
            return self._api(путь, {})
        файл = (КОРЕНЬ / путь.lstrip("/")).resolve()
        if КОРЕНЬ in файл.parents:
            return self._файл(файл)
        self._отдать(b"not found", "text/plain", 404)

    def do_POST(self):
        длина = int(self.headers.get("Content-Length", 0) or 0)
        сырое = self.rfile.read(длина) if длина else b"{}"
        try:
            данные = json.loads(сырое or b"{}")
        except ValueError:
            данные = {}
        self._api(urlparse(self.path).path, данные)

    def _карточка(self, путь: str):
        """Картинка поста. Тоже за подписью: по ссылке её не подсмотреть."""
        параметры = dict(parse_qsl(urlparse(self.path).query))
        if not access.можно(проверить(параметры.get("auth", "")) or 0):
            return self._отдать(b"forbidden", "text/plain", 403)
        try:
            ид = int(путь.rsplit("/", 1)[-1].removesuffix(".png"))
        except ValueError:
            return self._отдать(b"not found", "text/plain", 404)
        пост = db.взять(ид)
        данные = storage.байты(пост["image_path"]) if пост else None
        if not данные:
            return self._отдать(b"not found", "text/plain", 404)
        self._отдать(данные, "image/png", кэш="max-age=3600")

    def _api(self, путь: str, данные: dict):
        кто = проверить(self.headers.get("X-Init-Data", "") or данные.get("auth", "")) or 0
        if not кто:
            from urllib.parse import parse_qsl, urlparse
            запрос = dict(parse_qsl(urlparse(self.path).query))
            кто = access.по_ключу(запрос.get("key", "") or данные.get("key", ""))
        if not кто and access.открыто():
            кто = config.АДМИН
        if not access.можно(кто):
            return self._json(403, {"error": "Это личный бот канала."})
        try:
            self._json(*api.обработать(путь.rstrip("/"), данные, кто))
        except ValueError as e:
            self._json(400, {"error": str(e)[:300]})
        except Exception as e:                               # noqa: BLE001
            traceback.print_exc()
            self._json(500, {"error": str(e)[:300]})


class _Сервер(ThreadingHTTPServer):
    # Без этого после остановки бота порт ещё минуту занят системой, и
    # перезапуск падает с «address already in use» на ровном месте.
    allow_reuse_address = True
    daemon_threads = True


def поднять(порт: int) -> ThreadingHTTPServer:
    db.подготовить()
    jobs.подготовить()
    сервер = _Сервер(("0.0.0.0", порт), Ручка)
    threading.Thread(target=сервер.serve_forever, daemon=True).start()
    return сервер
