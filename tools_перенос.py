# -*- coding: utf-8 -*-
"""Переносит базу с ноутбука в Supabase. Запускать один раз, перед переездом.

    DATABASE_URL='postgresql://…' python3 tools_перенос.py

Читает файловую базу напрямую, пишет в ту, что указана в DATABASE_URL. Ничего
не удаляет: файл остаётся на месте, и если что-то пойдёт не так, вы просто
уберёте DATABASE_URL и продолжите работать как раньше.
"""

import os
import sqlite3
import sys

import config

ТАБЛИЦЫ = ("posts", "settings")


def main() -> int:
    адрес = os.getenv("DATABASE_URL", "").strip()
    if not адрес.startswith(("postgres://", "postgresql://")):
        print("Задайте DATABASE_URL с адресом Postgres из Supabase.")
        return 1
    if not config.БАЗА.exists():
        print(f"Файловой базы нет: {config.БАЗА}. Переносить нечего.")
        return 1

    файл = sqlite3.connect(config.БАЗА)
    файл.row_factory = sqlite3.Row

    import db                                   # берёт DATABASE_URL из окружения
    if not db.ПОСТГРЕС:
        print("db не увидел DATABASE_URL, перенос отменён.")
        return 1
    db.подготовить()

    with db.соединение() as c:
        for имя in ТАБЛИЦЫ:
            ряды = файл.execute(f"SELECT * FROM {имя}").fetchall()
            if not ряды:
                print(f"{имя}: пусто")
                continue
            поля = list(ряды[0].keys())
            места = ",".join("?" * len(поля))
            конфликт = ("ON CONFLICT (id) DO NOTHING" if имя == "posts"
                        else "ON CONFLICT (key) DO UPDATE SET value=excluded.value")
            for ряд in ряды:
                c.execute(f"INSERT INTO {имя} ({','.join(поля)}) VALUES ({места})"
                          f" {конфликт}", tuple(ряд[п] for п in поля))
            print(f"{имя}: перенесено {len(ряды)}")

        # Postgres сам не подвинет счётчик номеров: следующий пост получил бы id=1
        # и упёрся в уже занятый номер.
        c.execute("SELECT setval(pg_get_serial_sequence('posts','id'),"
                  " COALESCE((SELECT MAX(id) FROM posts), 1))")

    print("Готово. Проверьте: DATABASE_URL='…' python3 -c \"import db; print(db.сводка())\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
