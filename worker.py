# -*- coding: utf-8 -*-
"""Рабочий: берёт задания из очереди и делает тяжёлое.

Живёт на маке, потому что здесь есть всё, чего нет на Vercel: браузер для
карточек, модели, быстрый процессор. Крутится рядом с ботом в отдельной нити и
ничего не знает про то, кто задание положил, приложение или чат.

Опрос раз в две секунды. Это не нагрузка: один короткий запрос к базе, зато
человек в приложении видит отклик почти сразу.
"""

import threading
import time
import traceback

import core
import jobs

ПАУЗА = 2
ЖИВЁМ = True


def сделать(работа: dict) -> int | None:
    """Выполняет одно задание. Возвращает номер поста, если он появился."""
    ключ, вид, данные = работа["id"], работа["kind"], работа["payload"]
    ход = lambda что: jobs.шаг(ключ, что)                    # noqa: E731

    if вид == "новый":
        return core.новый(данные.get("rubric") or None, ход, данные.get("topic") or None)
    if вид == "анонс":
        return core.анонс()
    if вид == "карусель":
        return core.карусель(данные.get("topic") or None, ход)
    if вид == "переписать":
        return core.переписать(int(данные["id"]), данные.get("instruction", ""), ход)
    if вид == "перерисовать":
        return core.перерисовать(int(данные["id"]))
    if вид == "обновить":
        core.обновить(int(данные["id"]), данные.get("body"), данные.get("card"))
        return int(данные["id"])
    if вид == "снять":
        core.снять_с_плана(int(данные["id"]))
        return int(данные["id"])
    if вид == "запланировать":
        import times
        from datetime import datetime
        когда = datetime.fromisoformat(данные["when"])
        if когда.tzinfo is None:
            когда = когда.replace(tzinfo=times.ЗОНА)
        core.запланировать(int(данные["id"]), когда)
        return int(данные["id"])
    if вид == "опубликовать":
        import publish
        publish.опубликовать(int(данные["id"]), данные.get("by") or None)
        return int(данные["id"])
    if вид == "вовне":
        import publish
        ход("пишу")
        publish.опубликовать(int(данные["id"]), None, данные.get("where") or None)
        return int(данные["id"])
    if вид == "тикток_вход":
        import tiktok
        ход("пишу")
        tiktok.войти(данные["code"])
        tiktok.кто_мы(заново=True)      # чтобы имя профиля увидело и приложение
        return None
    if вид == "уборка":
        import уборка
        ход("рисую")
        уборка.прибраться()
        return None
    if вид == "показатели":
        import facts
        facts.обновить_из(данные.get("text", ""))
        return None
    if вид == "повторы":
        import repeats
        repeats.разложить()
        return None
    if вид == "неделя":
        return _неделя(данные, ход)
    raise ValueError(f"неизвестное задание: {вид}")


def _неделя(данные: dict, ход) -> int | None:
    """Набивает расписание вперёд: по посту на день в заданное время."""
    from datetime import timedelta
    import times
    дней = max(1, min(14, int(данные.get("days", 7))))
    часы = [ч for ч in (данные.get("times") or ["10:00"]) if ч] or ["10:00"]
    последний = None
    for н in range(дней):
        ход(f"пост {н + 1} из {дней}")
        ид = core.новый(None)
        час, минута = (часы[н % len(часы)].split(":") + ["0"])[:2]
        когда = (times.сейчас() + timedelta(days=н + 1)).replace(
            hour=int(час), minute=int(минута), second=0, microsecond=0)
        core.запланировать(ид, когда)
        последний = ид
    return последний


def собрать_охват() -> int:
    """Спрашивает у телеграма, сколько людей увидело недавние посты.

    Раз в полчаса и только по свежим: у поста месячной давности числа уже не
    меняются, а лишние запросы к аккаунту ни к чему.
    """
    import channels
    import db
    import publish
    if not publish.через_аккаунт():
        return 0
    import userbot
    # Охват собираем только по основному каналу: тестовый смотрит один человек,
    # и его двойка просмотров в средних числах только врёт.
    главный = channels.основной()
    свежие = db.свежие_публикации(канал=главный)
    по_каналам: dict[str, dict[int, int]] = {}
    for п in свежие:
        по_каналам.setdefault(главный, {})[int(п["tg_message_id"])] = int(п["id"])
    обновлено = 0
    for канал, соответствие in по_каналам.items():
        try:
            данные = userbot.охват(канал, list(соответствие))
        except Exception:                                    # noqa: BLE001
            continue
        for номер, д in данные.items():
            db.записать_охват(соответствие[номер], д["просмотры"],
                              д["реакции"] + д["пересылки"])
            обновлено += 1
    return обновлено


def круг() -> bool:
    """Одно задание за раз. Вернёт False, если работы не было."""
    работа = jobs.взять_работу()
    if not работа:
        return False
    print(f"рабочий: взял «{работа['kind']}»")
    try:
        пост = сделать(работа)
        jobs.готово(работа["id"], пост)
        print(f"рабочий: готово, пост {пост}")
    except Exception as e:                                   # noqa: BLE001
        traceback.print_exc()
        jobs.сломалось(работа["id"], str(e))
    return True


def запустить() -> threading.Thread:
    """Поднимает рабочего рядом с ботом."""
    jobs.подготовить()

    def цикл():
        приборка, пульс, охват, повторы, сверка = 0, 0, 0, 0, 0
        while ЖИВЁМ:
            try:
                # Пульс важнее работы: по нему приложение решает, что показывать
                if time.time() - пульс > 30:
                    jobs.отметиться()
                    jobs.вернуть_зависшие()
                    пульс = time.time()
                if not круг():
                    time.sleep(ПАУЗА)
                if time.time() - приборка > 3600:
                    jobs.прибрать()
                    приборка = time.time()
                if time.time() - сверка > 300:
                    import publish
                    сколько = publish.сверить_с_телеграмом()
                    if сколько:
                        print(f"рабочий: поправил {сколько} расхождений с телеграмом")
                    сверка = time.time()
                if time.time() - повторы > 3600:
                    import repeats
                    for что in repeats.разложить():
                        print("рабочий: поставил повтор,", что)
                    повторы = time.time()
                if time.time() - охват > 1800:
                    сколько = собрать_охват()
                    if сколько:
                        print(f"рабочий: обновил охват у {сколько} постов")
                    охват = time.time()
            except Exception:                                # noqa: BLE001
                traceback.print_exc()
                time.sleep(5)

    нить = threading.Thread(target=цикл, daemon=True)
    нить.start()
    return нить
