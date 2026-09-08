# -*- coding: utf-8 -*-
"""Очередь заданий между Vercel и маком.

Страница приложения живёт на Vercel и умеет всё быстрое: показать расписание,
одобрить, перенести, опубликовать. Но сочинить пост она не может: там нет ни
браузера для карточки, ни времени на минутную работу.

Поэтому тяжёлое уходит в очередь. Vercel кладёт задание, мак его забирает,
делает и возвращает результат. Приложение всё это время показывает, на каком
шаге работа. Мак нужен включённым только пока вы сочиняете; когда пост
одобрен, он больше ни за что не отвечает.
"""

import json
import time
import uuid

import db

СХЕМА = """CREATE TABLE IF NOT EXISTS jobs (
    id         TEXT PRIMARY KEY,
    kind       TEXT NOT NULL,
    payload    TEXT,
    state      TEXT NOT NULL DEFAULT 'ждёт',
    post_id    INTEGER,
    error      TEXT,
    created_at DOUBLE PRECISION NOT NULL,
    updated_at DOUBLE PRECISION NOT NULL
)"""
СХЕМА_SQLITE = СХЕМА.replace("DOUBLE PRECISION", "REAL")

ЖДЁТ, В_РАБОТЕ, ГОТОВО, ОШИБКА = "ждёт", "в работе", "готово", "ошибка"
ПРОТУХ = 20 * 60          # задание, за которое никто не взялся, считаем брошенным


_ПОДГОТОВЛЕНО = False


def подготовить() -> None:
    """Таблица заданий. Как и у постов, одного раза на запуск достаточно."""
    global _ПОДГОТОВЛЕНО
    if _ПОДГОТОВЛЕНО:
        return
    with db.соединение() as c:
        c.execute(СХЕМА if db.ПОСТГРЕС else СХЕМА_SQLITE)
    _ПОДГОТОВЛЕНО = True


def поставить(вид: str, данные: dict | None = None) -> str:
    """Кладёт задание в очередь и возвращает его ключ."""
    ключ = uuid.uuid4().hex[:12]
    сейчас = time.time()
    with db.соединение() as c:
        c.execute("INSERT INTO jobs (id, kind, payload, state, created_at, updated_at)"
                  " VALUES (?,?,?,?,?,?)",
                  (ключ, вид, json.dumps(данные or {}, ensure_ascii=False),
                   ЖДЁТ, сейчас, сейчас))
    return ключ


def взглянуть(ключ: str) -> dict | None:
    with db.соединение() as c:
        ряд = c.execute("SELECT * FROM jobs WHERE id=?", (ключ,)).fetchone()
    if not ряд:
        return None
    итог = {"id": ряд["id"], "kind": ряд["kind"], "state": ряд["state"],
            "post_id": ряд["post_id"], "error": ряд["error"]}
    # Задание, которое никто не взял в работу, скорее всего осиротело: мак был
    # выключен. Честнее сказать об этом, чем крутить ожидание до бесконечности.
    if итог["state"] == ЖДЁТ and time.time() - ряд["created_at"] > ПРОТУХ:
        итог["state"] = ОШИБКА
        итог["error"] = "мак не отозвался, включите его и повторите"
    return итог


def взять_работу() -> dict | None:
    """Забирает одно задание. Помечает его сразу, чтобы не взяли дважды."""
    with db.соединение() as c:
        ряд = c.execute(
            "SELECT * FROM jobs WHERE state=? ORDER BY created_at LIMIT 1",
            (ЖДЁТ,)).fetchone()
        if not ряд:
            return None
        взято = c.execute(
            "UPDATE jobs SET state=?, updated_at=? WHERE id=? AND state=?"
            " RETURNING id", (В_РАБОТЕ, time.time(), ряд["id"], ЖДЁТ)).fetchone()
        if not взято:
            return None                       # кто-то опередил, ничего страшного
    try:
        данные = json.loads(ряд["payload"] or "{}")
    except ValueError:
        данные = {}
    return {"id": ряд["id"], "kind": ряд["kind"], "payload": данные}


def шаг(ключ: str, состояние: str) -> None:
    """Сообщает, на каком этапе работа: приложение показывает это человеку."""
    with db.соединение() as c:
        c.execute("UPDATE jobs SET state=?, updated_at=? WHERE id=?",
                  (состояние, time.time(), ключ))


def готово(ключ: str, пост: int | None = None) -> None:
    with db.соединение() as c:
        c.execute("UPDATE jobs SET state=?, post_id=?, updated_at=? WHERE id=?",
                  (ГОТОВО, пост, time.time(), ключ))


def сломалось(ключ: str, беда: str) -> None:
    with db.соединение() as c:
        c.execute("UPDATE jobs SET state=?, error=?, updated_at=? WHERE id=?",
                  (ОШИБКА, беда[:300], time.time(), ключ))


ПУЛЬС = "worker"
МОЛЧАНИЕ = 90          # столько ждём удара пульса, прежде чем считать мак спящим


# Задания, у которых состояние — это этап работы, а не «ждёт/готово».
КОНЕЧНЫЕ = {ЖДЁТ, ГОТОВО, ОШИБКА}


def в_работе(предел: int = 6) -> list[dict]:
    """Что делается прямо сейчас. Для полоски хода в приложении.

    Генерация идёт минутами, и человек за это время сворачивает приложение.
    Без такого списка вернувшийся видит прежнюю очередь и не понимает,
    делается ли что-нибудь вообще.
    """
    порог = time.time() - 30 * 60
    with db.соединение() as c:
        ряды = c.execute(
            "SELECT id, kind, state, payload, updated_at FROM jobs"
            " WHERE state NOT IN (?,?,?) AND updated_at > ?"
            " ORDER BY created_at LIMIT ?",
            (ЖДЁТ, ГОТОВО, ОШИБКА, порог, предел)).fetchall()
    итог = []
    for р in ряды:
        try:
            данные = json.loads(р["payload"] or "{}")
        except ValueError:
            данные = {}
        # Площадка и объём партии: без них приложение не знает, чей это труд,
        # и показывало «собираю» сразу на всех станках.
        итог.append({"id": р["id"], "вид": р["kind"], "этап": р["state"],
                     "куда": данные.get("куда"),
                     "сколько": данные.get("сколько"),
                     "давно": round(time.time() - р["updated_at"])})
    return итог


def последние_беды(часов: int = 6, предел: int = 3) -> list[dict]:
    """Свежие сбои. Станок, который встал, должен быть виден в цехе.

    Раньше ошибка жила только в чате бота и в журнале: приложение показывало
    прежнюю картинку, и человек узнавал о непринятом посте через день.
    """
    порог = time.time() - часов * 3600
    with db.соединение() as c:
        ряды = c.execute(
            "SELECT id, kind, error, payload, updated_at FROM jobs"
            " WHERE state=? AND updated_at > ? ORDER BY updated_at DESC LIMIT ?",
            (ОШИБКА, порог, предел)).fetchall()
    итог = []
    for р in ряды:
        try:
            данные = json.loads(р["payload"] or "{}")
        except ValueError:
            данные = {}
        итог.append({"вид": р["kind"], "беда": (р["error"] or "")[:200],
                     "пост": данные.get("id"), "куда": данные.get("куда"),
                     "давно": round(time.time() - р["updated_at"])})
    return итог


def отметиться() -> None:
    """Мак говорит, что он на месте. Раз в полминуты, из рабочего цикла."""
    db.запомнить(ПУЛЬС, {"когда": time.time()})


def мак_жив() -> bool:
    """Доступен ли мак прямо сейчас.

    Приложение спрашивает это перед тем, как показать кнопки. Всё, что
    трогает канал, умеет только мак: сессия аккаунта лежит там, и без неё
    пост уйдёт без фирменных иконок или не уйдёт вовсе.
    """
    отметка = db.настройка(ПУЛЬС, {}) or {}
    return time.time() - отметка.get("когда", 0) < МОЛЧАНИЕ


def когда_видели() -> float | None:
    отметка = db.настройка(ПУЛЬС, {}) or {}
    return отметка.get("когда") or None


def вернуть_брошенные() -> int:
    """Всё, что числится в работе, возвращается в очередь при запуске.

    Свежий процесс не ведёт ни одного задания: если что-то помечено «в
    работе», значит прежнего рабочего убили посреди дела — перезапуском,
    закрытой крышкой, чем угодно. Ждать десять минут, пока сработает общий
    предел, значит десять минут тишины ровно тогда, когда человек смотрит
    на приложение и не понимает, делается ли хоть что-нибудь.
    """
    with db.соединение() as c:
        ряды = c.execute(
            "UPDATE jobs SET state=?, updated_at=? WHERE state NOT IN (?,?,?)"
            " RETURNING id", (ЖДЁТ, time.time(), ЖДЁТ, ГОТОВО, ОШИБКА)).fetchall()
    return len(ряды)


def вернуть_зависшие(предел: int = 600) -> int:
    """Задания, застрявшие «в работе», возвращаем в очередь.

    Рабочего могли убить посреди дела: закрыли крышку, перезапустили бота.
    Без этого задание висит вечно, а человек в приложении ждёт молча.
    """
    порог = time.time() - предел
    with db.соединение() as c:
        ряды = c.execute("UPDATE jobs SET state=?, updated_at=? WHERE state=?"
                         " AND updated_at < ? RETURNING id",
                         (ЖДЁТ, time.time(), В_РАБОТЕ, порог)).fetchall()
    return len(ряды)


def прибрать(старше: int = 24 * 3600) -> int:
    """Выкидывает старые задания: очередь не архив."""
    with db.соединение() as c:
        c.execute("DELETE FROM jobs WHERE updated_at < ?", (time.time() - старше,))
    return 0
