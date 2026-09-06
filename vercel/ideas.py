# -*- coding: utf-8 -*-
"""Копилка идей.

Ссылки и мысли приходят в течение дня, а садишься писать вечером. Раньше
единственным способом было тут же сочинить пост: увидел материал, нажал,
ждёшь минуту. Теперь идея кладётся в копилку за секунду, а пост из неё
делается тогда, когда есть время.

Копилка же чинит и вторую вещь. Когда жмёшь «Сам выберу», бот придумывает
тему с нуля, хотя ваши собственные заготовки обычно лучше выдуманных.
"""

import time

import db

СХЕМА = """CREATE TABLE IF NOT EXISTS ideas (
    id         {ключ},
    text       TEXT NOT NULL,
    used       INTEGER NOT NULL DEFAULT 0,
    created_at DOUBLE PRECISION NOT NULL
)"""


_ПОДГОТОВЛЕНО = False


def подготовить() -> None:
    global _ПОДГОТОВЛЕНО
    if _ПОДГОТОВЛЕНО:
        return
    ключ = "SERIAL PRIMARY KEY" if db.ПОСТГРЕС else "INTEGER PRIMARY KEY AUTOINCREMENT"
    запрос = СХЕМА.format(ключ=ключ)
    if not db.ПОСТГРЕС:
        запрос = запрос.replace("DOUBLE PRECISION", "REAL")
    with db.соединение() as c:
        c.execute(запрос)
    _ПОДГОТОВЛЕНО = True


def добавить(текст: str) -> int:
    текст = (текст or "").strip()[:500]
    if not текст:
        raise ValueError("пустая идея")
    with db.соединение() as c:
        ряд = c.execute("INSERT INTO ideas (text, created_at) VALUES (?,?)"
                        " RETURNING id", (текст, time.time())).fetchone()
    return int(ряд["id"] if db.ПОСТГРЕС else ряд[0])


def список(сколько: int = 30) -> list[dict]:
    with db.соединение() as c:
        ряды = c.execute("SELECT * FROM ideas WHERE used=0"
                         " ORDER BY id DESC LIMIT ?", (сколько,)).fetchall()
    return [{"id": р["id"], "text": р["text"]} for р in ряды]


def взять(ид: int) -> str | None:
    with db.соединение() as c:
        ряд = c.execute("SELECT text FROM ideas WHERE id=?", (ид,)).fetchone()
    return ряд["text"] if ряд else None


def израсходовать(ид: int) -> None:
    with db.соединение() as c:
        c.execute("UPDATE ideas SET used=1 WHERE id=?", (ид,))


def убрать(ид: int) -> None:
    with db.соединение() as c:
        c.execute("DELETE FROM ideas WHERE id=?", (ид,))


def самая_старая() -> dict | None:
    """Идея, которая ждёт дольше всех. Ею и займёмся, если тему не задали."""
    with db.соединение() as c:
        ряд = c.execute("SELECT * FROM ideas WHERE used=0"
                        " ORDER BY id LIMIT 1").fetchone()
    return {"id": ряд["id"], "text": ряд["text"]} if ряд else None
