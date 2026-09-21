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


class ПравилоПяти(unittest.TestCase):
    """Граница проверяется с обеих сторон: ошибка на единицу здесь тихая."""

    def test_нетронутая_тема_доступна(self):
        import темы
        self.assertTrue(темы.доступна(9, 3, {}))

    def test_разрыв_меньше_пяти_запрещён(self):
        import темы
        применения = {7: [10]}
        self.assertFalse(темы.доступна(7, 11, применения))   # разрыв 1
        self.assertFalse(темы.доступна(7, 14, применения))   # разрыв 4

    def test_ровно_пять_ещё_рано(self):
        import темы
        self.assertFalse(темы.доступна(7, 15, {7: [10]}))    # разрыв 5

    def test_шесть_уже_можно(self):
        import темы
        self.assertTrue(темы.доступна(7, 16, {7: [10]}))     # разрыв 6

    def test_считается_последнее_применение(self):
        import темы
        # Тема шла давно и совсем недавно: смотреть надо на недавнее.
        self.assertFalse(темы.доступна(7, 17, {7: [2, 16]}))


class Очередь(unittest.TestCase):
    СПРАВОЧНИК = [{"id": 1, "предмет": "выбор нейросети"},
                  {"id": 2, "предмет": "цена ролика"},
                  {"id": 3, "предмет": "озвучка"}]

    def test_занятые_отсеиваются(self):
        import темы
        свободные = темы.свободные(14, self.СПРАВОЧНИК, {1: [12]})
        self.assertEqual([т["id"] for т in свободные], [2, 3])

    def test_порядок_справочника_сохраняется(self):
        import темы
        свободные = темы.свободные(30, self.СПРАВОЧНИК, {})
        self.assertEqual([т["id"] for т in свободные], [1, 2, 3])

    def test_все_заняты_даёт_пусто(self):
        import темы
        занято = {1: [12], 2: [13], 3: [14]}
        self.assertEqual(темы.свободные(15, self.СПРАВОЧНИК, занято), [])


class ЖурналВБазе(unittest.TestCase):
    def test_применения_и_позиция_читаются(self):
        import db
        with _ВременнаяБаза():
            db.подготовить()
            with db.соединение() as c:
                c.execute("INSERT INTO themes (рубрика, предмет) VALUES (?, ?)",
                          ("полезное", "выбор нейросети"))
                c.execute("INSERT INTO theme_usage (theme_id, позиция, дата)"
                          " VALUES (?, ?, ?)", (1, 4, "2026-09-01"))
                c.execute("INSERT INTO theme_usage (theme_id, позиция, дата)"
                          " VALUES (?, ?, ?)", (1, 9, "2026-09-05"))
            self.assertEqual(db.применения_тем(), {1: [4, 9]})
            self.assertEqual(db.позиция_следующего(), 10)

    def test_пустой_журнал_даёт_первую_позицию(self):
        import db
        with _ВременнаяБаза():
            db.подготовить()
            self.assertEqual(db.применения_тем(), {})
            self.assertEqual(db.позиция_следующего(), 1)


if __name__ == "__main__":
    unittest.main()
