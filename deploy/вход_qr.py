# -*- coding: utf-8 -*-
"""Вход по QR-коду: тот же способ, которым Telegram подключает компьютер.

Кода из сообщения не требует вовсе. Открывается картинка, вы наводите на неё
телефон, Telegram спрашивает подтверждение, и сессия готова.

    python3 deploy/вход_qr.py

Картинка обновляется сама: Telegram делает ссылку недолговечной, и её надо
пересоздавать, пока вы ищете телефон.
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import userbot                                               # noqa: E402
import qrcode                                                # noqa: E402
from telethon import TelegramClient                          # noqa: E402
from telethon.errors import SessionPasswordNeededError       # noqa: E402

КАРТИНКА = Path(__file__).resolve().parent / "ключи" / "qr.png"


def нарисовать(ссылка: str) -> None:
    код = qrcode.QRCode(box_size=10, border=3)
    код.add_data(ссылка)
    код.make(fit=True)
    код.make_image(fill_color="black", back_color="white").save(КАРТИНКА)


async def main():
    клиент = TelegramClient(str(userbot.СЕССИЯ), userbot.API_ID, userbot.API_HASH)
    await клиент.connect()
    if await клиент.is_user_authorized():
        я = await клиент.get_me()
        print("уже вошли:", я.first_name, "id", я.id)
        return await клиент.disconnect()

    вход = await клиент.qr_login()
    нарисовать(вход.url)
    # Команды open нет ни на Windows, ни на линуксе: каждая система своим способом.
    if sys.platform == "darwin":
        subprocess.run(["open", str(КАРТИНКА)], check=False)
    elif sys.platform == "win32":
        os.startfile(str(КАРТИНКА))                          # noqa: S606
    else:
        subprocess.run(["xdg-open", str(КАРТИНКА)], check=False)
    print("Картинка открылась. В телефоне: Настройки → Устройства →")
    print("Подключить устройство, и наведите камеру на неё.")
    print("Жду до двух минут, картинка обновляется сама…")

    for попытка in range(12):
        try:
            await вход.wait(10)
            break
        except asyncio.TimeoutError:
            await вход.recreate()
            нарисовать(вход.url)
            print(f"  обновил картинку ({попытка + 1})")
        except SessionPasswordNeededError:
            print("НУЖЕН ОБЛАЧНЫЙ ПАРОЛЬ: запустите")
            print("  python3 deploy/вход.py пароль ВАШПАРОЛЬ")
            return await клиент.disconnect()
    else:
        print("не дождался, запустите заново")
        return await клиент.disconnect()

    я = await клиент.get_me()
    print("вошли:", я.first_name, "@" + (я.username or "без имени"), "id", я.id)
    await клиент.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
