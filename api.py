# -*- coding: utf-8 -*-
"""Что умеет приложение. Одна реализация на оба входа.

Приложение открывается двумя путями: с Vercel, где живёт облачная функция, и
с самого мака, если Vercel недоступен. Логика у них обязана быть одна, иначе
однажды окажется, что кнопка в одном месте делает не то же самое, что в
другом. Поэтому маршруты живут здесь, а по краям только приём запроса.

Тяжёлого тут нет намеренно: ни браузера, ни моделей. Всё, что дольше
секунды, уходит заданием на мак.
"""

from datetime import datetime

import access
import channels
import config
import db
import jobs
import markup
import publish
import stream
import times
from content import РУБРИКИ


# ── данные для экрана ───────────────────────────────────────────────────────

def _ссылка(ряд) -> str | None:
    канал = (ряд["channel"] if "channel" in ряд.keys() else "") or config.КАНАЛ
    if not ряд["tg_message_id"] or not канал.startswith("@"):
        return None
    return f"https://t.me/{канал[1:]}/{ряд['tg_message_id']}"


def _конвейер() -> list:
    """Состояние конвейера по площадкам для вкладки «Ещё»."""
    try:
        import конвейер
        import площадки as пл
    except Exception:                                        # noqa: BLE001
        # Пустой список раньше выглядел в приложении как «конвейер не
        # настроен», хотя настройки у него есть всегда. На деле модуль просто
        # не уехал на сервер, и понять это было неоткуда: жалобы никто не
        # видел. Теперь причина уходит в журнал функции.
        import traceback
        traceback.print_exc()
        return []
    итог = []
    for к in конвейер.ПО_УМОЛЧАНИЮ:
        с = конвейер.настройки(к)
        итог.append({"код": к, "имя": пл.имя(к), "вкл": bool(с["вкл"]),
                     # Угол следующей карусели: по нему видно, не ходит ли
                     # станок по кругу из двух тем.
                     "угол": с.get("угол") or "",
                     "режим": с.get("режим", "сам"), "часов": len(с["часы"]),
                     "часы": с["часы"], "дней": с["дней"],
                     "готово": len(конвейер.в_плане(к)),
                     "запас": конвейер.запас(к),
                     "формат": пл.формат(к), "файл": пл.файл(к),
                     "ширина": пл.ширина(к)})
    return итог


def _тикток_кратко() -> dict:
    """Кто подключён в TikTok. Без обращения к самому TikTok: только из базы."""
    try:
        import tiktok
    except Exception:                                        # noqa: BLE001
        return {}
    кто = tiktok.профиль()
    return {"ready": bool(tiktok.КЛЮЧ), "connected": tiktok.подключён(),
            "name": кто.get("имя"), "nick": кто.get("ник"),
            "link": tiktok.ссылка_входа() if tiktok.КЛЮЧ else ""}


def _куда(ряд) -> list:
    """Площадки поста с отметкой, выбрана ли каждая и есть ли к ней ключи."""
    import publish
    import площадки as пл
    выбраны = set(publish.куда_едет(ряд))
    return [{"код": к, "имя": пл.имя(к), "готова": пл.готова(к),
             "выбрана": к in выбраны} for к in пл.ПОРЯДОК]


def _пост(ряд) -> dict:
    когда = ряд["scheduled_at"] if "scheduled_at" in ряд.keys() else None
    return {
        "id": ряд["id"],
        "link": _ссылка(ряд),
        "rubric": ряд["rubric"],
        "shape": ряд["shape"] if "shape" in ряд.keys() else None,
        "title": ряд["title"],
        "body": ряд["body"],
        "html": markup.в_html(ряд["body"]),
        "status": ряд["status"],
        "card": db.карточка(ряд),
        "image": ряд["image_path"] if (ряд["image_path"] or "").startswith("http") else None,
        # Карусель. Пусто у обычного поста, и приложение по этому полю решает,
        # показать одну картинку или листалку.
        "images": [с for с in db.картинки(ряд) if с.startswith("http")],
        "when": times.подпись(times.из_базы(когда)) if когда else None,
        "when_iso": когда,
        "published": (times.подпись(times.из_базы(ряд["published_at"]))
                      if ряд["published_at"] else None),
        "views": ряд["views"] if "views" in ряд.keys() else None,
        # Куда этот пост уже ушёл наружу. Ключ это площадка, значение адрес
        # или текст ошибки: повторять удачную отправку незачем.
        "outside": db.карточка(ряд).get("outside_done") or {},
        "where": _куда(ряд),
        "reactions": ряд["reactions"] if "reactions" in ряд.keys() else None,
        # Пост, отданный телеграму, выйдет даже если у нас всё выключено.
        # Это другое поведение, и в списке оно должно быть видно.
        "at_telegram": bool(ряд["tg_sched_id"] if "tg_sched_id" in ряд.keys() else None),
    }


def _копилка() -> list:
    """Идеи, ждущие своей очереди. Пустой список, если таблицы ещё нет."""
    try:
        import ideas
        ideas.подготовить()
        return ideas.список(12)
    except Exception:                                        # noqa: BLE001
        return []


def _главный() -> str:
    """Канал, по которому считается всё показываемое человеку."""
    return channels.основной()


def _показатели() -> list:
    """Живые значения проекта. Пусто, если таблицы ещё нет."""
    try:
        import facts
        facts.подготовить()
        return facts.все()
    except Exception:                                        # noqa: BLE001
        return []


def _состояние() -> dict:
    # История, охват и «вышло» считаются по основному каналу: тестовый
    # существует, чтобы пробовать, и его числа в общей картине только мешают.
    план, черновики, история = db.для_экрана(_главный())
    return {
        "schedule": [_пост(р) for р in план],
        "drafts": [_пост(р) for р in черновики],
        "history": [_пост(р) for р in история],
        "stats": db.сводка(_главный()),
        "main_channel": _главный(),
        "rubrics": list(РУБРИКИ),
        "slots": [{"label": п, "iso": м.isoformat(), "human": times.подпись(м)}
                  for п, м in times.варианты()],
        "now": times.сейчас().strftime("%H:%M"),
        # Дата сервера: приложение строит по ней время ячейки, а часовой
        # пояс телефона может не совпадать с нашим.
        "today": times.сейчас().strftime("%Y-%m-%d"),
        "channel": channels.текущий(),
        "channels": channels.настройки(),
        "silent": publish.звук_выключен(),
        # По этому приложение решает, какие кнопки показывать: всё, что
        # трогает канал, умеет только мак, там лежит сессия аккаунта.
        "mac": {"alive": jobs.мак_жив(), "seen": jobs.когда_видели()},
        # Что делается прямо сейчас: приложение показывает это полоской на
        # любом экране, а не только в листе, из которого запустили.
        "работы": jobs.в_работе(),
        # Свежие сбои: станок, который встал, виден прямо в цехе, а не
        # только в чате бота.
        "беды": jobs.последние_беды(),
        "ideas": _копилка(),
        "pipeline": _конвейер(),
        "tiktok": _тикток_кратко(),
        "facts": _показатели(),
        # Углы, по которым станок ходит по кругу. Приложение показывает
        # пройденные бледными: так видно, что темы не повторяются.
        "углы": list(__import__("content").УГЛЫ_TIKTOK),
        "reach": [{"rubric": р["rubric"], "shape": р["shape"],
                   "count": int(р["штук"]), "avg": round(float(р["среднее"] or 0))}
                  for р in db.охват_по_рубрикам(_главный())],
    }


# ── маршруты ────────────────────────────────────────────────────────────────

def обработать(путь: str, данные: dict, кто: int) -> tuple[int, dict]:
    if путь.endswith("/state"):
        return 200, _состояние()

    if путь.endswith("/generate"):
        вид = ("анонс" if данные.get("stream") else
               "карусель" if данные.get("carousel") else "новый")
        ключ = jobs.поставить(вид, {"rubric": данные.get("rubric") or None,
                                    "topic": (данные.get("topic") or "").strip()[:300]})
        return 200, {"job": ключ}

    # Заказ станку: сразу партия и сразу по ячейкам. Отдельный маршрут, а
    # не «generate» несколько раз: партию собирает мак одним заданием, и
    # закрытое приложение ей не мешает.
    if путь.endswith("/order"):
        if not jobs.мак_жив():
            return 409, {"error": "мак выключен, собирать некому"}
        return 200, {"job": jobs.поставить("заказ", {
            "сколько": int(данные.get("сколько") or 1),
            "куда": (данные.get("куда") or "tiktok").strip(),
            "часы": данные.get("часы") or None,
            "тема": (данные.get("тема") or "").strip()[:300] or None})}

    if путь.endswith("/rewrite"):
        если = (данные.get("instruction") or "").strip()
        if не_годится := not если:
            return 400, {"error": "напишите, что поправить"}
        return 200, {"job": jobs.поставить("переписать",
                                           {"id": int(данные["id"]), "instruction": если[:500]})}

    if путь.endswith("/repose"):
        return 200, {"job": jobs.поставить("перерисовать", {
            "id": int(данные["id"]), "слайд": данные.get("слайд"),
            "брак": bool(данные.get("брак")),
            "новая": bool(данные.get("новая"))})}

    if путь.endswith("/update"):
        return 200, {"job": jobs.поставить("обновить", {
            "id": int(данные["id"]), "body": данные.get("body"),
            "card": данные.get("card")})}

    if путь.endswith("/plan"):
        return 200, {"job": jobs.поставить("неделя", {
            "days": int(данные.get("days", 7)),
            "times": данные.get("times") or ["10:00"]})}

    if путь.endswith("/job"):
        итог = jobs.взглянуть(данные.get("job", ""))
        if not итог:
            return 404, {"error": "задача потерялась"}
        ответ = {"state": итог["state"], "error": итог["error"]}
        if итог["post_id"]:
            ряд = db.взять(int(итог["post_id"]))
            if ряд:
                ответ["post"] = _пост(ряд)
        return 200, ответ

    # Публикация и расписание трогают канал, а он необратим. Роль «готовит»
    # сочиняет и правит, но в канал не отправляет.
    if (путь.endswith(("/schedule", "/publish", "/unschedule"))
            and not access.может_публиковать(кто)):
        return 403, {"error": "у вас роль «готовит»: сочиняйте и правьте, "
                              "а публикацию оставьте владельцу"}

    # Одобрение: пост занимает ячейку смены, но времени в расписании не
    # получает. Разница существенная: время означает «опубликуй сам», а в
    # ручном режиме публикует человек, и автопубликация через API у того же
    # TikTok просто не проходит. Ячейка — это план для человека, не для бота.
    if путь.endswith("/approve"):
        import json as _json
        ид = int(данные["id"])
        ряд = db.взять(ид)
        if not ряд:
            return 404, {"error": "поста уже нет"}
        поля = db.карточка(ряд)
        час = (данные.get("час") or "").strip()
        if час:
            поля["ячейка"] = час
        else:
            поля.pop("ячейка", None)
        db.правка(ид, card=_json.dumps(поля, ensure_ascii=False))
        return 200, {"ok": True, "state": _состояние(данные)}

    if путь.endswith("/schedule"):
        когда = datetime.fromisoformat(данные["when"])
        if когда.tzinfo is None:
            когда = когда.replace(tzinfo=times.ЗОНА)
        if когда <= times.сейчас():
            return 400, {"error": "это время уже прошло"}
        # Отдать пост телеграму умеет только мак. Записать время себе в базу
        # мы бы могли, но публиковать его потом было бы некому, и пост тихо
        # не вышел бы. Лучше честно сказать, что мак нужен.
        if not jobs.мак_жив():
            return 409, {"error": "мак выключен, а поставить время может только он"}
        return 200, {"job": jobs.поставить("запланировать",
                                           {"id": int(данные["id"]),
                                            "when": когда.isoformat()})}

    # Забрать файлами: TikTok у нас в ручном режиме, и это самый частый
    # способ публикации. Работа уходит на мак — папка открывается там, а
    # файлы приезжают в чат, откуда их достаёт телефон.
    if путь.endswith("/take"):
        if not jobs.мак_жив():
            return 409, {"error": "мак выключен, файлы собрать некому"}
        return 200, {"job": jobs.поставить("забрать", {
            "id": int(данные["id"]), "куда": данные.get("куда") or "tiktok"})}

    if путь.endswith("/publish"):
        # Через мак, потому что только он публикует от аккаунта, а значит с
        # фирменными иконками. Через бота они молча пропадают.
        if not jobs.мак_жив():
            return 409, {"error": "мак выключен, а без него пост уйдёт без "
                                  "фирменных иконок"}
        имя = None if access.владелец(кто) else access.свои().get(кто, {}).get("имя")
        return 200, {"job": jobs.поставить("опубликовать",
                                           {"id": int(данные["id"]), "by": имя})}

    if путь.endswith("/unschedule"):
        ид = int(данные["id"])
        ряд = db.взять(ид)
        # Пост, отданный телеграму, снять может только мак: там лежит сессия.
        if ряд and (ряд["tg_sched_id"] if "tg_sched_id" in ряд.keys() else None):
            if not jobs.мак_жив():
                return 409, {"error": "пост лежит в отложенных телеграма, "
                                      "снять его может только мак"}
            return 200, {"job": jobs.поставить("снять", {"id": ид})}
        db.снять_с_плана(ид)
        return 200, {"ok": True, "state": _состояние()}

    if путь.endswith("/facts/drop"):
        import facts
        facts.забыть(данные.get("name", ""))
        return 200, {"ok": True, "facts": facts.все()}

    if путь.endswith("/ideas/drop"):
        import ideas
        ideas.убрать(int(данные["id"]))
        return 200, {"ok": True, "ideas": ideas.список()}

    # Эти три обязаны идти именно в таком порядке. Адреса сверяются по концу
    # строки, а «/facts/drop» и «/ideas/drop» кончаются на «/drop». Стой общий
    # маршрут выше, удаление идеи номер семь помечало бы пропущенным пост
    # номер семь: идентификаторы у них разные, а числа одинаковые.
    if путь.endswith("/drop"):
        db.отметить_пропущенным(int(данные["id"]))
        return 200, {"ok": True, "state": _состояние()}

    # ── TikTok ──────────────────────────────────────────────────────────────
    # Адреса сверяются по концу строки, поэтому хвост каждого должен быть
    # уникален во всём наборе. «/tiktok» занят возвратом из OAuth, «/publish»
    # обычной публикацией, «/state» главным экраном. Отсюда «/tt/info».
    # Куда поедет пост. То же, что кнопками под черновиком в чате: раньше это
    # было только там, и из приложения было не выбрать площадку.
    # Переключатели конвейера из приложения: те же, что кнопками в чате.
    if путь.endswith("/pipeline"):
        import конвейер
        куда = (данные.get("net") or "").strip()
        что = (данные.get("what") or "").strip()
        if куда in конвейер.ПО_УМОЛЧАНИЮ:
            if что == "auto":
                конвейер.переключить(куда)
            elif что == "mode":
                с = конвейер.настройки(куда).get("режим", "сам")
                конвейер.сохранить(куда, режим="руками" if с == "сам" else "сам")
        return 200, {"pipeline": _конвейер()}

    if путь.endswith("/where"):
        import publish
        import площадки as пл
        ид = int(данные["id"])
        ряд = db.взять(ид)
        if not ряд:
            return 404, {"error": "черновика уже нет"}
        доступны = пл.ПОРЯДОК
        выбраны = set(publish.куда_едет(ряд))
        что = (данные.get("net") or "").strip()
        if что == "all":
            готовые = {к for к in доступны if пл.готова(к)}
            выбраны = set() if выбраны >= готовые else готовые
        elif что in доступны:
            выбраны.symmetric_difference_update({что})
        if что:
            publish.назначить(ид, [к for к in доступны if к in выбраны] or ["телеграм"])
            выбраны = set(publish.куда_едет(db.взять(ид)))
        return 200, {"where": [
            {"код": к, "имя": пл.имя(к), "готова": пл.готова(к),
             "выбрана": к in выбраны} for к in доступны]}

    if путь.endswith("/tt/info"):
        import tiktok
        # Спрашивать сам TikTok отсюда нельзя: для этого нужен секрет
        # приложения, а он живёт только на маке. Имя профиля берём из базы,
        # туда его кладёт мак после входа.
        кто = tiktok.профиль()
        свод = {"ready": bool(tiktok.КЛЮЧ),
                "connected": tiktok.подключён(),
                "name": кто.get("имя"), "nick": кто.get("ник"),
                "privacy": кто.get("видимость") or [],
                "link": tiktok.ссылка_входа() if tiktok.КЛЮЧ else ""}
        # Карусели, готовые уехать в TikTok: черновики и то, что в плане.
        готовые = []
        for ряд in list(db.черновики()) + list(db.расписание()):
            if not db.картинки(ряд):
                continue
            готовые.append({"id": ряд["id"], "title": ряд["title"],
                            "images": [с for с in db.картинки(ряд)
                                       if с.startswith("http")][:3],
                            "done": (db.карточка(ряд).get("выложено") or {}).get("tiktok")})
        свод["posts"] = готовые[:10]
        return 200, свод

    if путь.endswith("/tt/send"):
        if not access.может_публиковать(кто):
            return 403, {"error": "у вас роль «готовит»: публикацию оставьте владельцу"}
        return 200, {"job": jobs.поставить("вовне", {
            "id": int(данные["id"]), "where": ["tiktok"]})}

    if путь.endswith("/cleanup"):
        return 200, {"job": jobs.поставить("уборка", {})}

    if путь.endswith("/sound"):
        return 200, {"silent": publish.переключить_звук(), "state": _состояние()}

    if путь.endswith("/channel/pick"):
        if not access.владелец(кто):
            return 403, {"error": "канал переключает только владелец"}
        channels.выбрать(данные.get("kind", ""))
        return 200, {"ok": True, "state": _состояние()}

    if путь.endswith("/channel/set"):
        if not access.владелец(кто):
            return 403, {"error": "канал задаёт только владелец"}
        channels.задать(данные.get("kind", ""), данные.get("address", ""))
        return 200, {"ok": True, "state": _состояние()}

    if путь.endswith("/channel/check"):
        return 200, channels.проверить(данные.get("address", ""))

    if путь.endswith("/access"):
        return 200, {"owner": access.владелец(кто),
                     "can_publish": access.может_публиковать(кто),
                     "people": [{"id": и, "имя": з.get("имя", ""),
                                 "роль": з.get("роль", access.ПОЛНЫЙ)}
                                for и, з in access.свои().items()]}

    if путь.endswith("/access/code"):
        if not access.владелец(кто):
            return 403, {"error": "коды создаёт только владелец"}
        return 200, {"code": access.создать_код()}

    if путь.endswith("/access/role"):
        if not access.владелец(кто):
            return 403, {"error": "роли назначает только владелец"}
        ид = int(данные["id"])
        имя = (access.свои().get(ид) or {}).get("имя", "")
        access.добавить(ид, имя, данные.get("role", access.ПОЛНЫЙ))
        return 200, {"ok": True}

    if путь.endswith("/access/remove"):
        if not access.владелец(кто):
            return 403, {"error": "доступом управляет только владелец"}
        access.убрать(int(данные["id"]))
        return 200, {"ok": True}

    if путь.endswith("/ideas"):
        import ideas
        ideas.подготовить()
        return 200, {"ideas": ideas.список()}

    if путь.endswith("/ideas/add"):
        import ideas
        ideas.подготовить()
        текст = данные.get("text", "")
        ideas.добавить(текст)
        # Заметка может нести живое значение: каналов стало шесть. Разбирать
        # её умеет только мак, там модель. Ставим задание и не ждём: заметка
        # уже сохранена, показатели подтянутся через секунды.
        if jobs.мак_жив():
            jobs.поставить("показатели", {"text": текст})
        return 200, {"ok": True, "ideas": ideas.список(), "state": _состояние()}

    if путь.endswith("/facts"):
        import facts
        facts.подготовить()
        return 200, {"facts": facts.все()}

    if путь.endswith("/facts/save"):
        import facts
        facts.подготовить()
        facts.запомнить(данные.get("name", ""), данные.get("value", ""))
        return 200, {"ok": True, "facts": facts.все()}

    if путь.endswith("/repeats"):
        import repeats
        return 200, {"rules": [{**п, "human": repeats.описание(п)}
                               for п in repeats.правила()],
                     "days": repeats.ДНИ}

    if путь.endswith("/repeats/save"):
        if not access.владелец(кто):
            return 403, {"error": "повторы настраивает только владелец"}
        import repeats
        repeats.сохранить(данные.get("rules") or [])
        if jobs.мак_жив():
            jobs.поставить("повторы", {})
        return 200, {"ok": True}

    if путь.endswith("/repeat"):
        # Повторить удачный пост: копия в черновики, дальше правится словами.
        ряд = db.взять(int(данные["id"]))
        if not ряд:
            return 404, {"error": "поста уже нет"}
        новый = db.добавить(ряд["rubric"], ряд["title"], ряд["body"],
                            ряд["image_path"], ряд["shape"], db.карточка(ряд))
        return 200, {"ok": True, "post": _пост(db.взять(новый)),
                     "state": _состояние()}

    if путь.endswith("/stream"):
        return 200, stream.настройки()

    if путь.endswith("/stream/save"):
        stream.сохранить(данные)
        return 200, {"ok": True, "stream": stream.настройки()}

    if путь.endswith("/tick"):
        # Будильник со стороны: раз в минуту смотрим, не пора ли публиковать.
        return 200, {"сделано": publish.догнать_расписание()}

    return 404, {"error": "нет такого метода"}
