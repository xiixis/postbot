# -*- coding: utf-8 -*-
"""Разовый вход в TikTok.

    python3 deploy/тикток_вход.py            покажет ссылку, по которой надо разрешить
    python3 deploy/тикток_вход.py КОД        обменяет код на токены
    python3 deploy/тикток_вход.py проверка   скажет, кто мы там и что нам можно

Секрет приложения живёт только здесь, на маке. Обновляющий токен сохраняется в
общую базу: он меняется сам при каждом обновлении, и держать его в .env
означало бы каждый день править файл руками.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db          # noqa: E402
import tiktok      # noqa: E402


def главное() -> None:
    db.подготовить()
    довод = (sys.argv[1] if len(sys.argv) > 1 else "").strip()

    if not tiktok.КЛЮЧ or not tiktok.СЕКРЕТ:
        print("Нет ключей. Впишите в .env:")
        print("  TIKTOK_CLIENT_KEY=…")
        print("  TIKTOK_CLIENT_SECRET=…")
        print("  TIKTOK_REDIRECT_URI=https://ваш-адрес/api/tiktok")
        return

    if not довод:
        print("Откройте эту ссылку и разрешите доступ:\n")
        print(tiktok.ссылка_входа())
        print("\nПотом вернитесь сюда с кодом, который покажет страница.")
        return

    if довод == "проверка":
        кто = tiktok.сведения()
        print("автор:", кто.get("creator_nickname") or кто.get("creator_username"))
        print("разрешённая видимость:", ", ".join(кто.get("privacy_level_options") or []))
        print("комментарии отключены:", кто.get("comment_disabled"))
        return

    tiktok.войти(довод)
    print("вошли, токены сохранены")
    кто = tiktok.сведения()
    print("автор:", кто.get("creator_nickname") or кто.get("creator_username"))
    print("разрешённая видимость:", ", ".join(кто.get("privacy_level_options") or []))


if __name__ == "__main__":
    главное()
