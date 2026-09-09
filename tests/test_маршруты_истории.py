# -*- coding: utf-8 -*-
"""Маршруты ленты и чисел.

Разбор пути идёт лестницей `endswith` сверху вниз. Новый маршрут, чей суффикс
совпадает с чужим, молча перехватил бы чужие запросы — и это единственная
ошибка здесь, которую не видно ни в одном журнале.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api                                                   # noqa: E402


class _Ряд(dict):
    """Ряд базы отвечает и на `keys()`, и на доступ по имени."""


class _Подмена:
    """Подменяет имена в модуле на время проверки."""

    def __init__(self, модуль=None, **что):
        self.что = что
        self.было = {}
        self.модуль = модуль

    def __enter__(self):
        import db
        цель = self.модуль or db
        self.цель = цель
        for имя, значение in self.что.items():
            self.было[имя] = getattr(цель, имя)
            setattr(цель, имя, значение)
        return self

    def __exit__(self, *_):
        for имя, значение in self.было.items():
            setattr(self.цель, имя, значение)


def _ряд(ид: int, заголовок: str) -> _Ряд:
    return _Ряд({
        "id": ид, "rubric": "разбор", "title": заголовок, "body": "текст",
        "image_path": None, "status": "published", "shape": None,
        "created_at": "2026-09-01T10:00:00",
        "published_at": "2026-09-01T10:00:00", "tg_message_id": 5,
        "scheduled_at": None, "card": None, "channel": "@канал",
        "views": 10, "reactions": 1, "images": None, "link": None,
        "tg_sched_id": None})


class Лента(unittest.TestCase):
    def test_маршрут_отдаёт_посты_и_признак_продолжения(self):
        with _Подмена(история=lambda **_: ([_ряд(1, "Раз")], 5)):
            код, тело = api.обработать("/api/history",
                                       {"offset": 0, "limit": 1}, 1)
        self.assertEqual(код, 200)
        self.assertEqual(тело["total"], 5)
        self.assertTrue(тело["has_more"])
        self.assertEqual(тело["posts"][0]["title"], "Раз")

    def test_последняя_страница_без_продолжения(self):
        with _Подмена(история=lambda **_: ([_ряд(1, "Раз")], 1)):
            _, тело = api.обработать("/api/history", {"offset": 0, "limit": 20}, 1)
        self.assertFalse(тело["has_more"])

    def test_отбор_доезжает_до_базы(self):
        поймано = {}

        def ловушка(**поля):
            поймано.update(поля)
            return [], 0

        with _Подмена(история=ловушка):
            api.обработать("/api/history",
                           {"q": " пенсия ", "rubric": "разбор",
                            "platform": "телеграм", "days": 30}, 1)
        self.assertEqual(поймано["запрос"], "пенсия")
        self.assertEqual(поймано["рубрика"], "разбор")
        self.assertEqual(поймано["площадка"], "телеграм")
        self.assertEqual(поймано["дней"], 30)

    def test_чужая_площадка_не_проходит(self):
        """С клиента приезжает что угодно; в базу должно уйти только своё."""
        поймано = {}

        def ловушка(**поля):
            поймано.update(поля)
            return [], 0

        with _Подмена(история=ловушка):
            api.обработать("/api/history", {"platform": "instagram"}, 1)
        self.assertIsNone(поймано["площадка"])

    def test_пустой_поиск_это_не_поиск(self):
        поймано = {}

        def ловушка(**поля):
            поймано.update(поля)
            return [], 0

        with _Подмена(история=ловушка):
            api.обработать("/api/history", {"q": "   "}, 1)
        self.assertIsNone(поймано["запрос"])


class Числа(unittest.TestCase):
    def test_маршрут_собирает_все_части(self):
        with _Подмена(
                итоги=lambda канал=None: {"всего": 3, "за7": 1, "за30": 2,
                                          "охват30": 100,
                                          "охват_прошлые30": 50,
                                          "с_числами": 3},
                по_неделям=lambda недель=8, канал=None: [
                    {"неделя": "2026-09-07", "штук": 2, "охват": 100}],
                охват_по_рубрикам=lambda канал=None: [
                    _Ряд({"rubric": "разбор", "shape": None,
                          "штук": 2, "среднее": 100.0})],
                что_зашло=lambda сколько=6, канал=None: {
                    "лучшие": [{"заголовок": "Раз", "рубрика": "разбор",
                                "форма": None, "просмотры": 200, "отклики": 4}],
                    "худшие": [{"заголовок": "Два", "рубрика": "разбор",
                                "форма": None, "просмотры": 10, "отклики": 0}],
                    "средний": 105}):
            код, тело = api.обработать("/api/stats", {}, 1)
        self.assertEqual(код, 200)
        self.assertEqual(тело["summary"]["всего"], 3)
        self.assertEqual(тело["weekly"][0]["штук"], 2)
        self.assertEqual(тело["by_rubric"][0]["avg"], 100)
        self.assertEqual(тело["best"][0]["заголовок"], "Раз")
        self.assertEqual(тело["collected"], 3)

    def test_числа_не_роняют_экран_когда_база_старая(self):
        """У владельца база живёт с первого выпуска. Отсутствующей колонки
        хватит, чтобы уронить весь раздел, а он должен просто быть пустым."""
        def падает(*_, **__):
            raise RuntimeError("нет колонки")

        with _Подмена(итоги=падает, по_неделям=падает,
                      охват_по_рубрикам=падает, что_зашло=падает):
            код, тело = api.обработать("/api/stats", {}, 1)
        self.assertEqual(код, 200)
        self.assertEqual(тело["weekly"], [])
        self.assertEqual(тело["summary"]["всего"], 0)


class ПорядокМаршрутов(unittest.TestCase):
    def test_history_не_перехватывается_состоянием(self):
        with _Подмена(история=lambda **_: ([], 0)):
            код, тело = api.обработать("/api/history", {}, 1)
        self.assertEqual(код, 200)
        self.assertIn("posts", тело)
        self.assertNotIn("drafts", тело)

    def test_stats_не_перехватывается_состоянием(self):
        код, тело = api.обработать("/api/stats", {}, 1)
        self.assertEqual(код, 200)
        self.assertIn("summary", тело)
        self.assertNotIn("drafts", тело)


if __name__ == "__main__":
    unittest.main()
