# -*- coding: utf-8 -*-
"""Публикация от вашего аккаунта, а не от бота.

Зачем это вообще нужно. Боту Telegram не даёт двух вещей: ставить пост в
отложенные и вставлять свои эмодзи. Обе нужны, и обе доступны обычному
аккаунту. Поэтому текст сочиняет и рисует бот, а в канал пост уходит от вас.

Что это меняет по существу. Одобренный пост отправляется в Telegram сразу и
ложится в отложенные. Дальше Telegram публикует его сам, и ни мак, ни сервер
в этот момент не нужны. Расписание перестаёт зависеть от того, включено ли у
нас что-нибудь.

Файл сессии равен входу в аккаунт. Он лежит рядом с проектом, доступен только
владельцу и в git не попадает. Отозвать доступ можно в Telegram:
Настройки → Устройства → завершить сеанс.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import MessageEntityCustomEmoji

import config
import icons
import markup

СЕССИЯ = config.КОРЕНЬ / "deploy" / "ключи" / "аккаунт"
API_ID = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()


def настроен() -> bool:
    return bool(API_ID and API_HASH)


def вошли() -> bool:
    return настроен() and Path(f"{СЕССИЯ}.session").exists()


def _клиент() -> TelegramClient:
    return TelegramClient(str(СЕССИЯ), API_ID, API_HASH)


# ── разметка ────────────────────────────────────────────────────────────────

def _в_utf16(строка: str) -> int:
    """Длина в кодовых единицах utf-16: Telegram считает смещения именно так.

    Для латиницы и кириллицы это то же самое, что длина строки, а вот эмодзи
    занимает две единицы вместо одной. Если считать по-питоновски, вся разметка
    после первого же смайлика уедет.
    """
    return len(строка.encode("utf-16-le")) // 2


def _иконки(текст: str) -> list:
    """Метки своих эмодзи поверх готового текста.

    Бот подставляет их HTML-тегами, но Telethon такие теги не понимает,
    поэтому здесь мы находим эмодзи в уже разобранном тексте и вешаем метки
    сами, считая смещения в utf-16.
    """
    таблица = icons.таблица()
    if not таблица:
        return []
    метки, сдвиг, i = [], 0, 0
    ключи = sorted(таблица, key=len, reverse=True)
    while i < len(текст):
        for значок in ключи:
            if текст.startswith(значок, i):
                длина = _в_utf16(значок)
                метки.append(MessageEntityCustomEmoji(
                    offset=сдвиг, length=длина,
                    document_id=int(таблица[значок])))
                сдвиг += длина
                i += len(значок)
                break
        else:
            сдвиг += _в_utf16(текст[i])
            i += 1
    return метки


def разметить(текст: str) -> tuple[str, list]:
    """Текст автора → (чистый текст, метки разметки и своих эмодзи)."""
    from telethon.extensions import html as разбор
    # Чужие эмодзи меняем на фирменные до разбора: смещения считаются по
    # готовому тексту, и после подменять было бы поздно.
    чистый, метки = разбор.parse(markup.в_html(icons.к_своим(текст)))
    return чистый, list(метки) + _иконки(чистый)


# ── отправка ────────────────────────────────────────────────────────────────

async def _отложить(канал: str, текст: str, картинка: "Path | str | None",
                    когда: datetime) -> int:
    чистый, метки = разметить(текст)
    # Карточка обычно лежит в хранилище, а не на диске: скачиваем её сюда,
    # иначе Telethon примет ссылку за подпись к файлу и картинки не будет.
    if картинка:
        import storage
        картинка = storage.во_временный(str(картинка))
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        общее = {"formatting_entities": метки}
        if когда:
            общее["schedule"] = когда
        if картинка and Path(картинка).exists():
            письмо = await клиент.send_file(куда, str(картинка), caption=чистый, **общее)
        else:
            письмо = await клиент.send_message(куда, чистый, **общее)
        return int(getattr(письмо, "id", 0))


def отложить(канал: str, текст: str, картинка: "Path | str | None",
             когда: datetime | None = None) -> int:
    """Кладёт пост в отложенные канала. Дальше Telegram публикует сам.

    Без времени отправляет сразу: это тот же путь, и им же сохраняются
    фирменные иконки, которых боту Telegram не даёт.
    """
    return asyncio.run(_отложить(канал, текст, картинка, когда))


async def _альбом(канал: str, картинки: list, текст: str,
                  когда: datetime | None) -> int:
    """Карусель от аккаунта: группа снимков с фирменными иконками в подписи."""
    чистый, метки = разметить(текст)
    import storage
    files = [storage.во_временный(str(к)) for к in картинки]
    files = [str(п) for п in files if п and Path(п).exists()]
    if not files:
        raise ValueError("нечего отправлять: слайды не скачались")
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        общее = {"formatting_entities": метки}
        if когда:
            общее["schedule"] = когда
        # Список файлов Telethon отправляет альбомом, подпись достаётся первому.
        письма = await клиент.send_file(куда, files, caption=чистый, **общее)
        первое = письма[0] if isinstance(письма, list) else письма
        return int(getattr(первое, "id", 0))


def альбом(канал: str, картинки: list, текст: str,
           когда: "datetime | None" = None) -> int:
    """Отправляет или откладывает карусель. Возвращает номер первого снимка."""
    return asyncio.run(_альбом(канал, картинки, текст, когда))


async def _добавить_иконки(канал: str, номер: int, текст: str) -> int:
    чистый, метки = разметить(текст)
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        м = await клиент.edit_message(куда, номер, чистый, formatting_entities=метки)
        return sum(1 for э in (м.entities or [])
                   if isinstance(э, MessageEntityCustomEmoji))


def дописать_иконки(канал: str, номер: int, текст: str) -> int:
    """Добавляет фирменные иконки в уже опубликованный пост.

    Нужно там, где под постом кнопки: кнопки умеет прикреплять только бот, а
    иконки только аккаунт, и совместить их в одной отправке нельзя. Зато
    администратор канала может править чужие посты, и правка кнопок не
    трогает. Поэтому бот публикует, аккаунт дописывает.
    """
    return asyncio.run(_добавить_иконки(канал, номер, текст))


async def _охват(канал: str, номера: list[int]) -> dict:
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        итог = {}
        async for м in клиент.iter_messages(куда, ids=номера):
            if м is None:
                continue
            реакций = (sum(р.count for р in м.reactions.results)
                       if getattr(м, "reactions", None) and м.reactions.results else 0)
            итог[м.id] = {"просмотры": м.views or 0, "реакции": реакций,
                          "пересылки": м.forwards or 0}
        return итог


def охват(канал: str, номера: list[int]) -> dict:
    """Просмотры, реакции и пересылки постов канала.

    Боту эти числа Telegram не отдаёт вовсе, поэтому раньше честной обратной
    связи не было. Аккаунт видит их так же, как видит человек.
    """
    return asyncio.run(_охват(канал, номера))


async def _список(канал: str) -> list:
    from telethon.tl.functions.messages import GetScheduledHistoryRequest
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        ответ = await клиент(GetScheduledHistoryRequest(peer=куда, hash=0))
        return [(п.id, п.date) for п in ответ.messages]


def отложенные(канал: str) -> list:
    """Что уже лежит в отложенных у самого Telegram."""
    return asyncio.run(_список(канал))


async def _отменить(канал: str, номера: list[int]) -> None:
    from telethon.tl.functions.messages import DeleteScheduledMessagesRequest
    async with _клиент() as клиент:
        куда = await клиент.get_entity(канал)
        await клиент(DeleteScheduledMessagesRequest(peer=куда, id=номера))


def отменить(канал: str, номера: list[int]) -> None:
    asyncio.run(_отменить(канал, номера))
