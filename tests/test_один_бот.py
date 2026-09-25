# -*- coding: utf-8 -*-
"""Один бот на все машины: пост по расписанию не выходит дважды.

Проект живёт на маке и на ПК, база у них общая (Supabase). Запущенные разом два бота
раньше оба видели созревший пост и оба его публиковали, а ответ Telegram 409 («опрос
уже идёт») бот молча глотал (аудит кроссплатформенности 25.09.2026). Теперь пост перед
публикацией захватывается замком в базе, а второй бот не стартует, пока жив первый.
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class _ВременнаяБаза:
    """Тот же приём, что в test_референсы: SQLite во временной папке вместо Supabase."""

    def __enter__(self):
        import config
        import db
        self._папка = tempfile.TemporaryDirectory(prefix="один-бот-")
        self._было, self._готово, self._постгрес = config.БАЗА, db._ПОДГОТОВЛЕНО, db.ПОСТГРЕС
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


class ЗамокПубликации(unittest.TestCase):
    def test_второй_захват_не_проходит(self):
        import db
        with _ВременнаяБаза():
            self.assertTrue(db.захватить_публикацию(5))
            self.assertFalse(db.захватить_публикацию(5), "пост уже публикует другой бот")
            db.отпустить_публикацию(5)
            self.assertTrue(db.захватить_публикацию(5), "после отпуска пост снова свободен")

    def test_протухший_замок_перехватывается(self):
        import db
        with _ВременнаяБаза():
            self.assertTrue(db.захватить_публикацию(5, сейчас=time.time() - 3600))
            self.assertTrue(db.захватить_публикацию(5), "замок упавшего процесса не держит пост вечно")
            self.assertFalse(db.захватить_публикацию(5))


class Хозяин(unittest.TestCase):
    def setUp(self):
        import хозяин
        self.хозяин = хозяин
        self.было = хозяин.я

    def tearDown(self):
        self.хозяин.я = self.было

    def test_чужой_живой_бот_мешает_старту(self):
        with _ВременнаяБаза():
            self.хозяин.я = lambda: "мак:101"
            self.хозяин.отметиться()
            self.хозяин.я = lambda: "пк:202"
            занят = self.хозяин.занят_другим()
            self.assertIsNotNone(занят)
            self.assertEqual(занят["кто"], "мак:101")

    def test_свой_и_старый_не_мешают(self):
        with _ВременнаяБаза():
            self.хозяин.я = lambda: "мак:101"
            self.хозяин.отметиться()
            self.assertIsNone(self.хозяин.занят_другим(), "свою отметку за чужую не считаем")
            self.хозяин.отметиться(когда=time.time() - 3600)
            self.хозяин.я = lambda: "пк:202"
            self.assertIsNone(self.хозяин.занят_другим(), "бот, молчащий час, уже не живой")

    def test_уход_снимает_отметку(self):
        with _ВременнаяБаза():
            self.хозяин.я = lambda: "мак:101"
            self.хозяин.отметиться()
            self.хозяин.уйти()
            self.хозяин.я = lambda: "пк:202"
            self.assertIsNone(self.хозяин.занят_другим())


class Расписание(unittest.TestCase):
    """Догонялка расписания не публикует пост, который держит другой бот."""

    def test_занятый_пост_пропускается(self):
        import core
        import db
        import times
        with _ВременнаяБаза():
            было = (core.опубликовать, db.созревшие, core.publish.площадка, core.publish.площадка_готова)
            вызовы = []
            пост = {"id": 9, "scheduled_at": times.в_базу(times.сейчас()), "channel": "@к",
                    "status": "scheduled", "tg_sched_id": None}
            try:
                core.опубликовать = lambda ид, *а, **к: вызовы.append(ид)
                db.созревшие = lambda сейчас: [пост]
                core.publish.площадка = lambda п: "телеграм"
                core.publish.площадка_готова = lambda куда: True
                self.assertTrue(db.захватить_публикацию(9))     # держит другой бот
                core.догнать_расписание()
                self.assertEqual(вызовы, [], "занятый пост второй раз не публикуется")
                db.отпустить_публикацию(9)
                core.догнать_расписание()
                self.assertEqual(вызовы, [9])
                self.assertTrue(db.захватить_публикацию(9), "после публикации замок отпущен")
            finally:
                core.опубликовать, db.созревшие, core.publish.площадка, core.publish.площадка_готова = было


if __name__ == "__main__":
    unittest.main()
