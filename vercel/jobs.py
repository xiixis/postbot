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
