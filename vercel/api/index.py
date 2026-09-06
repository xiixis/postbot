# -*- coding: utf-8 -*-
"""Приём запросов на Vercel. Вся логика в общем модуле api."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import access                                                # noqa: E402
import api                                                   # noqa: E402
import config                                                # noqa: E402
import db                                                    # noqa: E402
import jobs                                                  # noqa: E402
from подпись import проверить                                # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _ответ(self, код: int, тело: dict):
        данные = json.dumps(тело, ensure_ascii=False).encode()
        self.send_response(код)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(данные)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(данные)

    def _слайд(self, имя: str, только_шапка: bool = False) -> bool:
        """Отдаёт слайд с нашего адреса. Без подписи и без разбора, кто пришёл.

        Нужно ровно для TikTok: он забирает картинки сам и берёт их только с
        домена, который ему подтвердили. Хранилище Supabase чужое, а этот
        адрес наш.

        Пересылаем строго из своего ведра и строго по имени файла: иначе из
        этого вышел бы открытый прокси, через который можно тянуть что угодно
        с нашего домена.
        """
        имя = (имя or "").strip().rsplit("/", 1)[-1]
        if not имя or not имя.lower().endswith((".png", ".jpg", ".jpeg")):
            self._ответ(400, {"error": "не картинка"})
            return True
        import storage
        if not storage.включено():
            self._ответ(404, {"error": "хранилище не настроено"})
            return True
        данные = storage.байты(
            f"{storage.АДРЕС}/storage/v1/object/public/{storage.ВЕДРО}/{имя}")
        if not данные:
            self._ответ(404, {"error": "нет такого слайда"})
            return True
        тип = "image/jpeg" if имя.lower().endswith((".jpg", ".jpeg")) else "image/png"
        self.send_response(200)
        self.send_header("Content-Type", тип)
        self.send_header("Content-Length", str(len(данные)))
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        # На HEAD тело слать нельзя, только заголовки. Это не мелочь: TikTok
        # перед тем, как забрать картинку, спрашивает про неё HEAD-запросом, и
        # без ответа считает, что файла нет.
        if not только_шапка:
            self.wfile.write(данные)
        return True

    def _тикток(self, запрос: dict) -> bool:
        """Возврат из TikTok после разрешения доступа.

        Код на токены меняет мак: там лежит секрет приложения, и в облаке ему
        делать нечего. Поэтому здесь код просто кладётся в очередь заданием, а
        человеку показывается, что можно возвращаться в приложение.
        """
        код = (запрос.get("code") or "").strip()
        беда = (запрос.get("error_description") or запрос.get("error") or "").strip()
        if код:
            try:
                jobs.подготовить()
                jobs.поставить("тикток_вход", {"code": код})
                нутро = ("<h2>Готово</h2><p>Аккаунт подключается. Вернитесь в "
                         "приложение, через несколько секунд там появится имя "
                         "профиля.</p>")
            except Exception as e:                           # noqa: BLE001
                нутро = f"<h2>Код получен, но не сохранился</h2><pre>{e}</pre>"
        elif беда:
            нутро = f"<h2>TikTok отказал</h2><p>{беда}</p>"
        else:
            нутро = "<h2>Ни кода, ни ошибки</h2>"
        страница = ("<meta charset='utf-8'><meta name='viewport' "
                    "content='width=device-width,initial-scale=1'><style>"
                    "body{font:16px/1.6 system-ui;max-width:34rem;margin:3rem auto;"
                    "padding:0 1rem;background:#12130F;color:#F1F3EA}"
                    "h2{color:#C7E24B}pre{background:#1B1E17;padding:1rem;"
                    "border-radius:.5rem;overflow-x:auto}</style>"
                    + нутро).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(страница)))
        self.end_headers()
        self.wfile.write(страница)
        return True

    def _работа(self, данные: dict):
        запрос = dict(parse_qsl(urlparse(self.path).query))
        # Настоящий адрес приезжает параметром: Vercel переписывает все
        # /api/* на одну функцию и сам путь при этом теряет.
        путь = "/" + запрос.get("route", "").strip("/")
        if путь == "/":
            путь = urlparse(self.path).path.rstrip("/")

        # Слайд отдаётся раньше всего: за ним приходит TikTok, а не человек,
        # и подписи телеграма у него нет и быть не может.
        if путь.endswith("/slide"):
            return self._слайд(запрос.get("f", ""))

        # Сюда TikTok возвращает браузер после разрешения. Мы только
        # показываем код: менять его на токены будет мак, там лежит секрет
        # приложения, и на сервере ему делать нечего.
        if путь.endswith("/tiktok"):
            return self._тикток(запрос)

        db.подготовить()
        jobs.подготовить()

        # Будильник приходит без подписи телеграма: у него её и быть не может.
        if путь.endswith("/tick"):
            слово = os.getenv("TICK_SECRET", "")
            if not слово or запрос.get("key") != слово:
                return self._ответ(403, {"error": "не тот ключ"})
            return self._ответ(*api.обработать(путь, данные, 0))

        кто = проверить(self.headers.get("X-Init-Data", "") or данные.get("auth", "")) or 0
        # Подписи телеграма нет, значит человек мог прийти по личной ссылке.
        if not кто:
            кто = access.по_ключу(запрос.get("key", "") or данные.get("key", ""))
        if not кто and access.открыто():
            кто = config.АДМИН          # дверь открыта, гость работает как владелец
        if not access.можно(кто):
            return self._ответ(403, {"error": "Это личный бот канала."})
        try:
            self._ответ(*api.обработать(путь, данные, кто))
        except ValueError as e:
            self._ответ(400, {"error": str(e)[:300]})
        except Exception as e:                               # noqa: BLE001
            self._ответ(500, {"error": str(e)[:300]})

    def do_GET(self):
        self._работа({})

    def do_HEAD(self):
        """Только заголовки. Так проверяют картинку перед скачиванием."""
        запрос = dict(parse_qsl(urlparse(self.path).query))
        путь = "/" + запрос.get("route", "").strip("/")
        if путь.endswith("/slide"):
            return self._слайд(запрос.get("f", ""), только_шапка=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        длина = int(self.headers.get("Content-Length", 0) or 0)
        сырое = self.rfile.read(длина) if длина else b"{}"
        try:
            данные = json.loads(сырое or b"{}")
        except ValueError:
            данные = {}
        self._работа(данные)
