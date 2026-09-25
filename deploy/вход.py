# -*- coding: utf-8 -*-
"""Разовый вход в Telegram аккаунтом. Два шага, чтобы код можно было передать.

    python3 deploy/вход.py запрос +79000000000
    python3 deploy/вход.py код 12345
    python3 deploy/вход.py пароль СЕКРЕТ     # если стоит облачный пароль
"""
import asyncio, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config, userbot                                       # noqa: E402
from telethon import TelegramClient                          # noqa: E402
from telethon.errors import SessionPasswordNeededError       # noqa: E402

ПАМЯТКА = config.КОРЕНЬ / "deploy" / "ключи" / "вход.json"


async def запрос(телефон: str):
    клиент = TelegramClient(str(userbot.СЕССИЯ), userbot.API_ID, userbot.API_HASH)
    await клиент.connect()
    ответ = await клиент.send_code_request(телефон)
    ПАМЯТКА.write_text(json.dumps({"телефон": телефон,
                                   "хеш": ответ.phone_code_hash}), encoding="utf-8")
    ПАМЯТКА.chmod(0o600)
    print("код отправлен, тип:", type(ответ.type).__name__)
    await клиент.disconnect()


async def смс(_=None):
    """Просит прислать код по SMS: в приложении его иногда не замечают."""
    import json as _json
    д = _json.loads(ПАМЯТКА.read_text(encoding="utf-8"))
    клиент = TelegramClient(str(userbot.СЕССИЯ), userbot.API_ID, userbot.API_HASH)
    await клиент.connect()
    ответ = await клиент.send_code_request(д["телефон"], force_sms=True)
    ПАМЯТКА.write_text(_json.dumps({"телефон": д["телефон"],
                                    "хеш": ответ.phone_code_hash}), encoding="utf-8")
    print("повтор отправлен, тип:", type(ответ.type).__name__)
    await клиент.disconnect()


async def код(значение: str):
    д = json.loads(ПАМЯТКА.read_text(encoding="utf-8"))
    клиент = TelegramClient(str(userbot.СЕССИЯ), userbot.API_ID, userbot.API_HASH)
    await клиент.connect()
    try:
        я = await клиент.sign_in(д["телефон"], значение, phone_code_hash=д["хеш"])
        print("вошли:", я.first_name, "id", я.id)
    except SessionPasswordNeededError:
        print("НУЖЕН ПАРОЛЬ: запустите шаг «пароль»")
    await клиент.disconnect()


async def пароль(значение: str):
    клиент = TelegramClient(str(userbot.СЕССИЯ), userbot.API_ID, userbot.API_HASH)
    await клиент.connect()
    я = await клиент.sign_in(password=значение)
    print("вошли:", я.first_name, "id", я.id)
    await клиент.disconnect()


if __name__ == "__main__":
    шаг = sys.argv[1]
    значение = sys.argv[2] if len(sys.argv) > 2 else ""
    asyncio.run({"запрос": запрос, "смс": смс, "код": код,
                 "пароль": пароль}[шаг](значение))
