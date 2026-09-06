# -*- coding: utf-8 -*-
"""Проверка подписи Telegram у мини-приложения.

Адрес приложения публичный, поэтому каждый запрос несёт подпись (initData) и
проверяется секретом, выведенным из токена бота. Подделать её, не зная токена,
нельзя. Отдельный модуль, потому что этим пользуются и бот на маке, и функция
на Vercel, а тащить ради двадцати строк весь сервер приложения незачем.
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

import config


def проверить(initdata: str) -> int | None:
    """Возвращает id пользователя, если подпись настоящая и свежая."""
    if not initdata:
        return None
    поля = dict(parse_qsl(initdata, keep_blank_values=True))
    подпись = поля.pop("hash", "")
    if not подпись:
        return None

    строка = "\n".join(f"{к}={поля[к]}" for к in sorted(поля))
    секрет = hmac.new(b"WebAppData", config.ТОКЕН.encode(), hashlib.sha256).digest()
    свой = hmac.new(секрет, строка.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(свой, подпись):
        return None
    if time.time() - int(поля.get("auth_date", 0)) > 24 * 3600:
        return None                                   # старую ссылку не пускаем
    try:
        return int(json.loads(поля.get("user", "{}")).get("id", 0))
    except (ValueError, TypeError):
        return None
