# -*- coding: utf-8 -*-
"""Сверка с отложенными Telegram: вышедший пост получает настоящий номер сообщения.

Пост, который Telegram выпустил сам в назначенный час, раньше отмечался номером 0.
Под этим нулём слипались все такие посты, и сбор охвата (`worker.собрать_охват`)
спрашивал у канала сообщение №0 — просмотров у них не было никогда (аудит 25.09.2026).
"""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db                                                    # noqa: E402
import publish                                               # noqa: E402
import userbot                                               # noqa: E402

КАНАЛ = "@канал"


class Сверка(unittest.TestCase):
    def setUp(self):
        self.было = {
            (publish, "через_аккаунт"): publish.через_аккаунт,
            (db, "настройка"): db.настройка,
            (db, "запомнить"): db.запомнить,
            (db, "расписание"): db.расписание,
            (db, "отметить_опубликованным"): db.отметить_опубликованным,
            (db, "снять_с_плана"): db.снять_с_плана,
            (userbot, "отложенные"): userbot.отложенные,
        }
        if hasattr(userbot, "найти_вышедший"):
            self.было[(userbot, "найти_вышедший")] = userbot.найти_вышедший
        час_назад = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
        self.пост = {"id": 7, "tg_sched_id": 37, "scheduled_at": час_назад, "channel": КАНАЛ,
                     "body": "*Заголовок*\n\nТекст поста", "status": "planned"}
        self.отмечено = []
        publish.через_аккаунт = lambda: True
        # Второй промах подряд; остальные настройки (ссылка подписки в футере) — по умолчанию.
        db.настройка = lambda ключ, по_умолчанию=None: [7] if ключ == "sync_misses" else по_умолчанию
        db.запомнить = lambda ключ, значение: None
        db.расписание = lambda: [self.пост]
        db.отметить_опубликованным = lambda ид, номер, канал="": self.отмечено.append((ид, номер, канал))
        db.снять_с_плана = lambda ид: self.fail("вышедший пост не снимается с плана")
        userbot.отложенные = lambda канал: []                        # в очереди Telegram его больше нет

    def tearDown(self):
        for (модуль, имя), функция in self.было.items():
            setattr(модуль, имя, функция)
        if (userbot, "найти_вышедший") not in self.было and hasattr(userbot, "найти_вышедший"):
            delattr(userbot, "найти_вышедший")

    def test_вышедший_получает_настоящий_номер(self):
        спрошено = []

        def найти(канал, когда, текст):
            спрошено.append((канал, когда, текст))
            return 1290
        userbot.найти_вышедший = найти
        self.assertEqual(publish.сверить_с_телеграмом(), 1)
        self.assertEqual(self.отмечено, [(7, 1290, КАНАЛ)])
        канал, когда, текст = спрошено[0]
        self.assertEqual(канал, КАНАЛ)
        self.assertEqual(когда, datetime.fromisoformat(self.пост["scheduled_at"]))   # тот же момент
        self.assertIn("Текст поста", текст)

    def test_не_нашли_номер_не_ноль(self):
        userbot.найти_вышедший = lambda канал, когда, текст: None
        publish.сверить_с_телеграмом()
        self.assertEqual(self.отмечено, [(7, None, КАНАЛ)],
                         "без номера пишется пусто: ноль слипается с другими постами")

    def test_сбой_поиска_не_роняет_сверку(self):
        def сломан(канал, когда, текст):
            raise ConnectionError("Telegram моргнул")
        userbot.найти_вышедший = сломан
        self.assertEqual(publish.сверить_с_телеграмом(), 1)
        self.assertEqual(self.отмечено, [(7, None, КАНАЛ)])


class ПоискВышедшего(unittest.TestCase):
    """Выбор сообщения канала, в которое превратился отложенный пост."""

    def test_по_тексту_и_времени(self):
        когда = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
        сообщения = [
            (1301, когда + timedelta(minutes=40), "Другой пост"),
            (1300, когда + timedelta(seconds=20), "Заголовок\n\nТекст поста"),
            (1299, когда - timedelta(hours=3), "Заголовок\n\nТекст поста"),   # старый повтор
        ]
        self.assertEqual(userbot.выбрать_вышедший(сообщения, когда, "Заголовок\n\nТекст поста"), 1300)

    def test_нет_подходящего(self):
        когда = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
        сообщения = [(1301, когда + timedelta(hours=2), "Заголовок\n\nТекст поста")]
        self.assertIsNone(userbot.выбрать_вышедший(сообщения, когда, "Заголовок\n\nТекст поста"))


if __name__ == "__main__":
    unittest.main()
