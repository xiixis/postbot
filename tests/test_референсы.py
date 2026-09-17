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


if __name__ == "__main__":
    unittest.main()
