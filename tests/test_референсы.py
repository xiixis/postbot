# tests/test_референсы.py
# -*- coding: utf-8 -*-
"""База референсов под рерайт: запись без повторов, очередь, курсор.

Ловится то, что ломается тихо: одна ссылка, скинутая дважды, даёт две строки;
курсор уезжает при ошибке сети и ссылки пропадают навсегда.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class _ВременнаяБаза:
    def __enter__(self):
        import config
        import db
        self._папка = tempfile.TemporaryDirectory(prefix="референсы-")
        self._было, self._готово, self._постгрес = config.БАЗА, db._ПОДГОТОВЛЕНО, db.ПОСТГРЕС
        # Схема собрана при импорте: с DATABASE_URL в .env номера раздаёт SERIAL,
        # которого SQLite не знает, и id остаётся пустым (тот же приём в test_история).
        self._схема = db.СХЕМА
        db.СХЕМА = [з.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT") for з in db.СХЕМА]
        config.БАЗА = Path(self._папка.name) / "posts.db"
        db.ПОСТГРЕС = False
        db._ПОДГОТОВЛЕНО = False
        db.закрыть()
        db.забыть_кэш()
        db.подготовить()
        return self

    def __exit__(self, *беда):
        import config
        import db
        db.закрыть()
        db.забыть_кэш()
        config.БАЗА, db._ПОДГОТОВЛЕНО, db.ПОСТГРЕС = self._было, self._готово, self._постгрес
        db.СХЕМА = self._схема
        self._папка.cleanup()
        return False


class База(unittest.TestCase):
    def test_повтор_не_создаёт_строку(self):
        import db
        with _ВременнаяБаза():
            self.assertTrue(db.добавить_референс("https://www.instagram.com/p/A/", "instagram", 5, "2026-09-17"))
            self.assertFalse(db.добавить_референс("https://www.instagram.com/p/A/", "instagram", 6, "2026-09-17"))
            self.assertEqual(len(db.референсы(None)), 1)

    def test_взять_без_номера_старую_новую(self):
        import db
        with _ВременнаяБаза():
            db.добавить_референс("https://a/1", "другое", 1, "2026-09-16")
            db.добавить_референс("https://a/2", "другое", 2, "2026-09-17")
            ряд = db.взять_референс()
            self.assertEqual(ряд["url"], "https://a/1")
            self.assertEqual(ряд["статус"], "в работе")
            self.assertEqual([р["url"] for р in db.референсы()], ["https://a/2"])

    def test_отметить_использованной(self):
        import db
        with _ВременнаяБаза():
            db.добавить_референс("https://a/1", "другое", 1, "2026-09-16")
            ид = db.референсы()[0]["id"]
            db.отметить_референс(ид, "использована", post_id=42, заметка="на столе")
            ряд = db.референсы("использована")[0]
            self.assertEqual((ряд["post_id"], ряд["заметка"]), (42, "на столе"))

    def test_чужой_статус_отклоняется(self):
        import db
        with _ВременнаяБаза():
            db.добавить_референс("https://a/1", "другое", 1, "2026-09-16")
            with self.assertRaises(ValueError):
                db.отметить_референс(db.референсы()[0]["id"], "готово")


class Ссылки(unittest.TestCase):
    def test_instagram_без_параметров(self):
        import референсы as р
        self.assertEqual(р.привести("https://www.instagram.com/p/Dc8GZlYgB6b/?img_index=4&stkn=Nnps"),
                         "https://www.instagram.com/p/Dc8GZlYgB6b/")
        self.assertEqual(р.привести("https://www.instagram.com/p/Dc8GZlYgB6b/"),
                         "https://www.instagram.com/p/Dc8GZlYgB6b/")

    def test_короткая_tiktok_как_есть(self):
        import референсы as р
        self.assertEqual(р.привести("https://vt.tiktok.com/ZSqbckB6R/"), "https://vt.tiktok.com/ZSqbckB6R/")
        self.assertEqual(р.площадка("https://vt.tiktok.com/ZSqbckB6R/"), "tiktok")
        self.assertEqual(р.площадка("https://www.instagram.com/p/A/"), "instagram")
        self.assertEqual(р.площадка("https://example.com/"), "другое")

    def test_несколько_ссылок_в_сообщении(self):
        import референсы as р
        текст = "глянь https://www.instagram.com/p/A/?x=1 и https://vt.tiktok.com/B/"
        self.assertEqual(р.ссылки(текст, ["https://www.instagram.com/p/A/?x=1"]),
                         ["https://www.instagram.com/p/A/?x=1", "https://vt.tiktok.com/B/"])


class Сбор(unittest.TestCase):
    def test_курсор_двигается_и_без_ссылок(self):
        import db
        import референсы as р
        with _ВременнаяБаза():
            новых = р.записать([
                {"id": 15, "дата": "2026-09-16", "текст": "https://www.instagram.com/p/A/?img_index=1", "адреса": []},
                {"id": 16, "дата": "2026-09-16", "текст": "просто текст", "адреса": []}])
            self.assertEqual(новых, 1)
            self.assertEqual(db.настройка(р.КУРСОР), 16)

    def test_курсор_стоит_при_ошибке_чтения(self):
        import db
        import референсы as р
        with _ВременнаяБаза():
            db.запомнить(р.КУРСОР, 10)

            def сломано(после):
                raise ConnectionError("сеть")
            with self.assertRaises(ConnectionError):
                р.сверить(сломано)
            self.assertEqual(db.настройка(р.КУРСОР), 10)

    def test_сверить_читает_после_курсора_и_повтор_ноль(self):
        import db
        import референсы as р
        with _ВременнаяБаза():
            db.запомнить(р.КУРСОР, 14)
            спросили = []

            def читать(после):
                спросили.append(после)
                return [{"id": 20, "дата": "2026-09-17", "текст": "", "адреса": ["https://www.instagram.com/p/A/"]}]
            self.assertEqual(р.сверить(читать), 1)
            self.assertEqual(р.сверить(читать), 0)
            self.assertEqual(спросили, [14, 20])

if __name__ == "__main__":
    unittest.main()
