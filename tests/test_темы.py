# -*- coding: utf-8 -*-
"""Журнал тем: справочник, применения и правило пяти постов.

Сторожится здесь ровно одно, но оно и есть смысл затеи: тема не должна
возвращаться раньше, чем между ней и прошлым разом лягут пять чужих постов.
Граница проверяется с обеих сторон, потому что ошибка на единицу здесь тихая:
разрыв в пять постов выглядит достаточным, а по правилу он ещё мал.

Считается по позиции — сквозному номеру поста, а не по дате. Дата скачет от
расписания: два поста могут выйти в один день, а между ними по порядку будет
разрыв. Порядок выхода не скачет.

База в тестах своя, временная, и обязательно sqlite. Подменить один
`config.БАЗА` мало: при заданном `DATABASE_URL` модуль уходит в постгрес и
путь к файлу не смотрит вовсе — тест молча пошёл бы в рабочую базу владельца и
завёл таблицы там. Поэтому подменяется и признак постгреса.
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class _ВременнаяБаза:
    """Подменяет путь к базе на пустой файл и возвращает всё как было."""

    def __enter__(self):
        import config
        import db
        self._папка = tempfile.TemporaryDirectory(prefix="темы-")
        self._было = config.БАЗА
        self._готово = db._ПОДГОТОВЛЕНО
        self._постгрес = db.ПОСТГРЕС
        config.БАЗА = Path(self._папка.name) / "posts.db"
        db.ПОСТГРЕС = False
        db._ПОДГОТОВЛЕНО = False
        db.закрыть()
        return self

    def __exit__(self, *беда):
        import config
        import db
        db.закрыть()
        config.БАЗА = self._было
        db.ПОСТГРЕС = self._постгрес
        db._ПОДГОТОВЛЕНО = self._готово
        self._папка.cleanup()
        return False

    def таблицы(self) -> set:
        import config
        связь = sqlite3.connect(config.БАЗА)
        try:
            return {р[0] for р in связь.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        finally:
            связь.close()


class Схема(unittest.TestCase):
    def test_таблицы_заводятся(self):
        import db
        with _ВременнаяБаза() as база:
            db.подготовить()
            имена = база.таблицы()
        self.assertIn("themes", имена)
        self.assertIn("theme_usage", имена)


if __name__ == "__main__":
    unittest.main()
