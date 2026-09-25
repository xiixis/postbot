# -*- coding: utf-8 -*-
"""Время публикаций. Хранится в UTC, показывается в вашей зоне.

Почему так, а не «просто локальное время везде»: пост может быть запланирован
на ночь перед переводом часов или бот может переехать на сервер в другой зоне.
Тогда локальная строка в базе начинает означать другой момент, и посты уезжают
на час. UTC такого не умеет.
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def _зона():
    """Зона по имени, а не по смещению.

    datetime.now().astimezone() отдаёт застывшее «+03:00». Бот живёт неделями,
    и после перевода часов все запланированные посты уехали бы на час. Имя
    зоны переводит время само, поэтому сначала ищем его: в POSTBOT_TZ (облако может
    резервировать TZ), в TZ, потом в ссылке /etc/localtime, которой macOS и Linux
    хранят выбор системы, а на Windows — через tzlocal: ссылки там нет, и раньше
    бот на ПК жил на застывшем смещении (аудит 25.09.2026).
    """
    имя = (os.getenv("POSTBOT_TZ", "") or os.getenv("TZ", "")).strip()
    if not имя:
        ссылка = Path("/etc/localtime")
        if ссылка.is_symlink() and "zoneinfo" in str(ссылка.resolve()):
            имя = str(ссылка.resolve()).split("zoneinfo/")[-1]
    if not имя:
        try:
            import tzlocal
            имя = tzlocal.get_localzone_name() or ""
        except Exception:                                    # noqa: BLE001
            имя = ""
    try:
        return ZoneInfo(имя) if имя else None
    except Exception:                                        # noqa: BLE001
        return None


ЗОНА = _зона()
if ЗОНА is None:
    # Имя зоны не нашлось: живём на застывшем смещении и честно об этом говорим —
    # после перевода часов запланированные посты уедут на час.
    import sys
    print("⚠ часовой пояс не определён: задайте POSTBOT_TZ (например Europe/Kyiv) в .env", file=sys.stderr)
    ЗОНА = datetime.now().astimezone().tzinfo

МЕСЯЦЫ = ["янв", "фев", "мар", "апр", "мая", "июн",
          "июл", "авг", "сен", "окт", "ноя", "дек"]


def сейчас() -> datetime:
    return datetime.now(tz=ЗОНА)


def в_базу(когда: datetime) -> str:
    return когда.astimezone(timezone.utc).isoformat(timespec="seconds")


def из_базы(строка: str) -> datetime:
    return datetime.fromisoformat(строка).astimezone(ЗОНА)


def подпись(когда: datetime) -> str:
    """«сегодня в 20:00», «завтра в 10:00», «6 сен в 18:30»."""
    сегодня = сейчас().date()
    д = когда.date()
    часы = когда.strftime("%H:%M")
    if д == сегодня:
        return f"сегодня в {часы}"
    if д == сегодня + timedelta(days=1):
        return f"завтра в {часы}"
    return f"{д.day} {МЕСЯЦЫ[д.month - 1]} в {часы}"


def _ближайшее(час: int, минута: int = 0) -> datetime:
    """Сегодня в это время, а если уже прошло, то завтра."""
    т = сейчас().replace(hour=час, minute=минута, second=0, microsecond=0)
    return т if т > сейчас() + timedelta(minutes=2) else т + timedelta(days=1)


def варианты() -> list[tuple[str, datetime]]:
    """Готовые кнопки времени. Утро и вечер, потому что канал живёт ими."""
    ч = сейчас().replace(second=0, microsecond=0)
    список = [("Через 15 минут", ч + timedelta(minutes=15)),
              ("Через час", ч + timedelta(hours=1)),
              ("Утро, 10:00", _ближайшее(10)),
              ("День, 14:00", _ближайшее(14)),
              ("Вечер, 20:00", _ближайшее(20)),
              ("Завтра, 10:00", (ч + timedelta(days=1)).replace(hour=10, minute=0)),
              ("Через неделю", (ч + timedelta(days=7)).replace(hour=10, minute=0))]
    видели, итог = set(), []
    for подпись_, момент in список:
        ключ = момент.strftime("%d %H:%M")
        if ключ not in видели:
            видели.add(ключ)
            итог.append((подпись_, момент))
    return итог


def разобрать(текст: str) -> datetime | None:
    """Своё время руками: «20:00», «завтра 9:30», «06.09 18:00»."""
    т = текст.strip().lower().replace("в ", " ").strip()
    завтра = т.startswith("завтра")
    т = т.removeprefix("завтра").removeprefix("сегодня").strip()

    м = re.fullmatch(r"(\d{1,2})[.\-/](\d{1,2})(?:[.\-/](\d{2,4}))?\s+"
                     r"(\d{1,2})[:.](\d{2})", т)
    if м:
        день, месяц, год, час, минута = м.groups()
        год = int(год or сейчас().year)
        год += 2000 if год < 100 else 0
        try:
            return datetime(год, int(месяц), int(день), int(час), int(минута),
                            tzinfo=ЗОНА)
        except ValueError:
            return None

    м = re.fullmatch(r"(\d{1,2})[:.](\d{2})", т)
    if м:
        час, минута = int(м.group(1)), int(м.group(2))
        if not (0 <= час < 24 and 0 <= минута < 60):
            return None
        момент = сейчас().replace(hour=час, minute=минута, second=0, microsecond=0)
        if завтра:
            момент += timedelta(days=1)
        elif момент <= сейчас():
            момент += timedelta(days=1)
        return момент
    return None
