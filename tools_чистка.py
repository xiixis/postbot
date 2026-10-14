"""Чистка канала @FourXtube от неактивных подписчиков. Работает юзерботом.

    pb py tools_чистка.py найти [N]   отобрать N человек (по умолчанию 100), только чтение
    pb py tools_чистка.py удалить     исключить отобранных, по одному раз в 2 секунды

Отбираются удалённые аккаунты и те, чья точная дата последнего входа старше
двух месяцев. Скрывших время входа («был давно») не трогаем: среди них есть
живые люди. Исключение, а не бан: человек может подписаться снова.

Обычный список участников канала Telegram отдаёт только на 200 человек,
поэтому подписчиков добираем поиском по буквам и сочетаниям букв.
"""
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from telethon.errors import FloodWaitError
from telethon.tl import functions, types

import userbot

КАНАЛ = "@FourXtube"
СПИСОК = Path(__file__).parent / "data" / "чистка_канала.json"
ПАУЗА = 2
БУКВЫ = list("abcdefghijklmnopqrstuvwxyz") + list("абвгдежзиклмнопрстуфхцчшэюя")


async def _найти(нужно: int) -> None:
    порог = datetime.now(timezone.utc) - timedelta(days=61)
    async with userbot._клиент() as к:
        канал = await к.get_entity(КАНАЛ)
        видели, цели = set(), {}
        очередь = [""] + БУКВЫ
        while очередь and len(цели) < нужно:
            запрос = очередь.pop(0)
            while True:
                try:
                    ответ = await к(functions.channels.GetParticipantsRequest(
                        канал, types.ChannelParticipantsSearch(запрос),
                        offset=0, limit=200, hash=0))
                    break
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
            for u in ответ.users:
                if u.id in видели:
                    continue
                видели.add(u.id)
                имя = " ".join(filter(None, [u.first_name, u.last_name]))
                if u.deleted:
                    цели[u.id] = {"id": u.id, "имя": имя, "почему": "удалённый аккаунт"}
                elif (not u.bot and isinstance(u.status, types.UserStatusOffline)
                      and u.status.was_online < порог):
                    цели[u.id] = {"id": u.id, "имя": имя, "ник": u.username,
                                  "почему": "был " + u.status.was_online.date().isoformat()}
            # Упёрлись в потолок выдачи: уточняем запрос ещё одной буквой.
            if len(ответ.users) >= 200 and запрос and len(запрос) < 2:
                очередь += [запрос + б for б in БУКВЫ]
            await asyncio.sleep(0.6)
    список = list(цели.values())[:нужно]
    СПИСОК.write_text(json.dumps(список, ensure_ascii=False, indent=1), encoding="utf-8")
    удалённых = sum(1 for x in список if x["почему"] == "удалённый аккаунт")
    print(f"просмотрено {len(видели)}, отобрано {len(список)}, из них удалённых аккаунтов {удалённых}")
    print(f"список: {СПИСОК}")


async def _удалить() -> None:
    цели = json.loads(СПИСОК.read_text(encoding="utf-8"))
    async with userbot._клиент() as к:
        канал = await к.get_entity(КАНАЛ)
        до = (await к.get_participants(канал, limit=0)).total
        ок, ошибки = 0, []
        for н, ц in enumerate(цели, 1):
            while True:
                try:
                    await к.kick_participant(канал, ц["id"])
                    ок += 1
                    break
                except FloodWaitError as e:
                    print("Telegram просит паузу", e.seconds, "с", flush=True)
                    await asyncio.sleep(e.seconds + 1)
                except Exception as e:
                    ошибки.append((ц["id"], type(e).__name__))
                    break
            print(f"{н}/{len(цели)} {ц['почему']}", flush=True)
            await asyncio.sleep(ПАУЗА)
        после = (await к.get_participants(канал, limit=0)).total
    print(f"удалено {ок}, ошибок {len(ошибки)} | подписчиков было {до}, стало {после}")
    for о in ошибки:
        print(о)
    СПИСОК.unlink()   # список отработан, второй раз по нему не пойдём


if __name__ == "__main__":
    команда = sys.argv[1] if len(sys.argv) > 1 else ""
    if команда == "найти":
        asyncio.run(_найти(int(sys.argv[2]) if len(sys.argv) > 2 else 100))
    elif команда == "удалить":
        asyncio.run(_удалить())
    else:
        print(__doc__)
