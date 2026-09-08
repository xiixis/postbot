# -*- coding: utf-8 -*-
"""Тонкий клиент Bot API: только то, что нужно этому боту.

Длинный опрос, а не вебхук — боту не нужен публичный адрес с сертификатом,
он одинаково работает и на сервере, и с ноутбука.
"""

import json
from pathlib import Path

import requests

import config
import markup

БАЗА = f"https://api.telegram.org/bot{config.ТОКЕН}"


class ОшибкаTG(RuntimeError):
    pass


def _вызвать(метод: str, данные: dict | None = None,
             файлы: dict | None = None, таймаут: int = 60) -> dict:
    r = requests.post(f"{БАЗА}/{метод}", data=данные or {}, files=файлы, timeout=таймаут)
    тело = r.json()
    if not тело.get("ok"):
        raise ОшибкаTG(f"{метод}: {тело.get('description', r.text[:200])}")
    return тело["result"]


def обновления(смещение: int, ожидание: int = 25) -> list[dict]:
    """Длинный опрос. Ждём на стороне Telegram, а не крутим цикл вхолостую."""
    try:
        return _вызвать("getUpdates",
                        {"offset": смещение, "timeout": ожидание,
                         "allowed_updates": '["message","callback_query"]'},
                        таймаут=ожидание + 15)
    except (requests.RequestException, ОшибкаTG):
        # Сеть моргнула или у телеграма пятисотая: и то, и другое случается
        # регулярно и лечится следующим кругом. Ронять из-за этого бота,
        # который держит расписание, нельзя.
        return []


def кнопки(ряды: list) -> str:
    """Инлайн-клавиатура. Пара (подпись, данные) или готовый словарь кнопки."""
    import json
    сетка = [[к if isinstance(к, dict) else {"text": к[0], "callback_data": к[1]}
              for к in ряд] for ряд in ряды]
    return json.dumps({"inline_keyboard": сетка})


def _разметить(текст: str) -> str:
    """Звёздочки автора → HTML, обычные эмодзи → иконки канала.

    icons ввозится внутри функции, а не сверху: он сам обращается к этому
    модулю за составом набора, и на верхнем уровне вышел бы круг импортов.
    """
    import icons
    return icons.подставить(markup.в_html(icons.к_своим(текст)))


def написать(чат: int, текст: str, клавиатура: str | None = None,
             разметка: str = "HTML", тихо: bool = False) -> dict:
    """Разметка пустая, если текст служебный и звёздочки в нём не разметка."""
    тело = {"chat_id": чат, "disable_web_page_preview": "true",
            "text": _разметить(текст) if разметка else текст}
    if разметка:
        тело["parse_mode"] = "HTML"
    if тихо:
        тело["disable_notification"] = "true"
    if клавиатура:
        тело["reply_markup"] = клавиатура
    return _вызвать("sendMessage", тело)


def фото(чат: str | int, картинка: "Path | str", подпись: str,
         клавиатура: str | None = None, тихо: bool = False) -> dict:
    """Пост с картинкой. Подпись телеграм ограничивает 1024 символами.

    Считаем длину без разметки: теги в лимит не входят, телеграм меряет уже
    разобранный текст. Если всё же переросло, режем по границе абзаца, а не
    посреди слова, и остаток уходит тихо, без второго уведомления.
    """
    хвост = ""
    if markup.длина(подпись) > 1024:
        обрез = подпись
        while обрез and markup.длина(обрез) > 1024:
            граница = обрез.rfind("\n\n")
            обрез = обрез[:граница] if граница > 200 else обрез[:-40]
        хвост = подпись[len(обрез):].strip()
        подпись = обрез.rstrip()

    тело = {"chat_id": чат, "caption": _разметить(подпись), "parse_mode": "HTML"}
    if тихо:
        тело["disable_notification"] = "true"
    if клавиатура:
        тело["reply_markup"] = клавиатура
    # Картинку можно отдать файлом, а можно ссылкой: телеграм заберёт сам.
    # Второе нужно там, где диска нет вовсе, например в облачной функции.
    if isinstance(картинка, str) and картинка.startswith("http"):
        тело["photo"] = картинка
        ответ = _вызвать("sendPhoto", тело, таймаут=120)
    else:
        with open(картинка, "rb") as f:
            ответ = _вызвать("sendPhoto", тело, файлы={"photo": f}, таймаут=120)

    if хвост:
        _вызвать("sendMessage", {"chat_id": чат, "text": _разметить(хвост),
                                 "parse_mode": "HTML",
                                 "disable_notification": "true"})
    return ответ


def документы(чат: str | int, пути: list, подпись: str = "") -> dict:
    """Файлы как файлы, а не как снимки.

    Снимки телеграм пережимает по-своему, а слайды рисовались ровно под
    площадку: 1080 и JPEG, как просит TikTok. Отданные документом, они
    доезжают байт в байт, и выложить их можно без потери.

    Группами по десять: больше телеграм в одно сообщение не берёт.
    """
    ответ = {}
    for начало in range(0, len(пути), 10):
        кусок = пути[начало:начало + 10]
        состав, файлы = [], {}
        for н, п in enumerate(кусок):
            имя = f"файл{начало}_{н}"
            часть = {"type": "document", "media": f"attach://{имя}"}
            if начало == 0 and н == 0 and подпись:
                часть["caption"] = _разметить(подпись)
                часть["parse_mode"] = "HTML"
            состав.append(часть)
            файлы[имя] = open(п, "rb")
        тело = {"chat_id": чат,
                "media": json.dumps(состав, ensure_ascii=False)}
        try:
            ответ = _вызвать("sendMediaGroup", тело, файлы=файлы, таймаут=180)
        finally:
            for ф_ in файлы.values():
                ф_.close()
    return ответ


def альбом(чат: str | int, картинки: list, подпись: str,
           тихо: bool = False) -> dict:
    """Карусель: несколько снимков одним сообщением, подпись у первого.

    Телеграм показывает такую группу как листалку и считает её одним постом:
    один охват, один набор реакций. Подпись живёт только у первого снимка,
    и её лимит тут жёстче обычного, 1024 символа вместе с разметкой уже
    разобранной. Что не влезло, уходит следом отдельным тихим сообщением.
    """
    хвост = ""
    if markup.длина(подпись) > 1024:
        обрез = подпись
        while обрез and markup.длина(обрез) > 1024:
            граница = обрез.rfind("\n\n")
            обрез = обрез[:граница] if граница > 200 else обрез[:-40]
        хвост = подпись[len(обрез):].strip()
        подпись = обрез.rstrip()

    состав, файлы = [], {}
    for н, к in enumerate(картинки):
        кусок = {"type": "photo"}
        if isinstance(к, str) and к.startswith("http"):
            кусок["media"] = к
        else:
            имя = f"фото{н}"
            кусок["media"] = f"attach://{имя}"
            файлы[имя] = open(к, "rb")
        if н == 0:
            кусок["caption"] = _разметить(подпись)
            кусок["parse_mode"] = "HTML"
        состав.append(кусок)

    тело = {"chat_id": чат, "media": json.dumps(состав, ensure_ascii=False)}
    if тихо:
        тело["disable_notification"] = "true"
    try:
        ответ = _вызвать("sendMediaGroup", тело, файлы=файлы or None, таймаут=180)
    finally:
        for ф in файлы.values():
            ф.close()

    if хвост:
        _вызвать("sendMessage", {"chat_id": чат, "text": _разметить(хвост),
                                 "parse_mode": "HTML",
                                 "disable_notification": "true"})
    # Ответ это список сообщений. Наружу отдаём первое: по нему группа и
    # опознаётся, и правится.
    первое = ответ[0] if isinstance(ответ, list) and ответ else ответ
    return первое if isinstance(первое, dict) else {}


def ответить_на_кнопку(ид: str, текст: str = "") -> None:
    """Гасит «часики» на кнопке. Без этого клиент висит и кажется, что сломалось."""
    try:
        _вызвать("answerCallbackQuery", {"callback_query_id": ид, "text": текст[:200]})
    except Exception:                                        # noqa: BLE001
        pass


def правка_кнопок(чат: int, сообщение: int, клавиатура: str) -> None:
    """Меняет кнопки под уже отправленным сообщением.

    Нужно для переключателей: человек нажимает «TikTok», галочка появляется
    на той же карточке, а не новым сообщением следом.
    """
    try:
        _вызвать("editMessageReplyMarkup",
                 {"chat_id": чат, "message_id": сообщение,
                  "reply_markup": клавиатура})
    except Exception:                                        # noqa: BLE001
        pass          # кнопки не изменились или сообщение старое, это не беда


def убрать_кнопки(чат: int, сообщение: int) -> None:
    try:
        _вызвать("editMessageReplyMarkup",
                 {"chat_id": чат, "message_id": сообщение, "reply_markup": "{}"})
    except Exception:                                        # noqa: BLE001
        pass


def меню_приложения(адрес: str, чат: int, подпись: str = "Редактор") -> None:
    """Кнопка слева от поля ввода, открывающая мини-приложение."""
    import json
    _вызвать("setChatMenuButton", {
        "chat_id": чат,
        "menu_button": json.dumps({"type": "web_app", "text": подпись,
                                   "web_app": {"url": адрес}})})


def кнопка_приложения(подпись: str, адрес: str) -> dict:
    """Кнопка внутри сообщения. Работает только в личке, не в канале."""
    return {"text": подпись, "web_app": {"url": адрес}}


def скачать(file_id: str) -> bytes | None:
    """Забирает файл по его id. Нужно для голосовых заметок."""
    try:
        ф = _вызвать("getFile", {"file_id": file_id})
        о = requests.get(f"https://api.telegram.org/file/bot{config.ТОКЕН}"
                         f"/{ф['file_path']}", timeout=120)
        о.raise_for_status()
        return о.content
    except Exception:                                        # noqa: BLE001
        return None


def кто_я() -> dict:
    return _вызвать("getMe")
