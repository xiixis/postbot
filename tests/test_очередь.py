# -*- coding: utf-8 -*-
"""Очередь: план и черновики одним списком, пост — отдельной карточкой.

Сторожатся три вещи, которые в кнопочном интерфейсе ломаются молча.

Первая: список не должен расти без предела. Клавиатура из сорока строк
скроллится отдельно от чата, и человек её просто не пролистывает — поэтому
показываются первые двенадцать, а остальные честно посчитаны словами.

Вторая: набор кнопок под постом зависит от того, что это за пост. Кнопка
«снять с расписания» под вышедшим постом — обещание, которого бот не может
сдержать: опубликованное не снимается ничем.

Третья: нажатие с карточки не должно плодить меню. Карточка — отдельное
сообщение с картинкой, меню живёт своим; снял пост с плана — обновиться
обязан тот экран, что уже висит, а не новый внизу.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import навигация                                             # noqa: E402
import экраны                                                # noqa: E402


def _пост(ид: int, статус: str, заголовок: str = "Заголовок",
          когда: str | None = None, **ещё) -> dict:
    """Ряд базы настолько, насколько он нужен экрану.

    Словаря хватает: и sqlite3.Row, и он отвечают на «пост[поле]» и keys().
    """
    ряд = {"id": ид, "status": статус, "title": заголовок,
           "scheduled_at": когда, "rubric": "полезное", "body": "текст",
           "image_path": None, "images": None, "card": None,
           "tg_message_id": None, "channel": "@канал", "views": None,
           "tg_sched_id": None}
    ряд.update(ещё)
    return ряд


def _собрать(код: str, арг: str = "", владелец: bool = True) -> экраны.Экран:
    запись, _ = экраны.найти(код)
    return запись.собрать(экраны.Пар(чат=1, арг=арг, владелец=владелец))


def _коды(э: экраны.Экран) -> list[str]:
    return [к[1] for ряд in э.ряды for к in ряд if not isinstance(к, dict)]


class Очередь(unittest.TestCase):
    """Экран «Очередь» читает базу одним походом и складывает список сам."""

    def setUp(self):
        import db
        self.настоящая = db.для_экрана
        self.db = db

    def tearDown(self):
        self.db.для_экрана = self.настоящая

    def _подсунуть(self, план, черновики):
        self.db.для_экрана = lambda *_, **__: (план, черновики, [])

    def test_план_сверху_черновики_следом(self):
        """Ближайшее по времени — первым: очередь читается сверху вниз."""
        self._подсунуть([_пост(1, "scheduled", когда="2026-09-09T15:00:00+00:00")],
                        [_пост(2, "draft")])
        self.assertEqual(_коды(_собрать("q"))[:2], ["p:1", "p:2"])

    def test_у_плана_время_у_черновика_пометка(self):
        self._подсунуть([_пост(1, "scheduled", "Про кота",
                               когда="2026-09-09T15:00:00+00:00")],
                        [_пост(2, "draft", "Про мышь")])
        подписи = [к[0] for ряд in _собрать("q").ряды for к in ряд
                   if not isinstance(к, dict)]
        self.assertIn("Про кота", подписи[0])
        self.assertIn("черновик", подписи[1])
        self.assertIn("Про мышь", подписи[1])

    def test_длинный_заголовок_обрезается(self):
        """Кнопка с длинной подписью рвётся на узком экране на две строки."""
        self._подсунуть([], [_пост(1, "draft", "Очень длинный заголовок, "
                                               "который никуда не влезет никогда")])
        подпись = _собрать("q").ряды[0][0][0]
        self.assertLessEqual(len(подпись), 40)
        self.assertTrue(подпись.endswith("…"), подпись)

    def test_больше_двенадцати_показываются_первые_двенадцать(self):
        """Листалка в клавиатуре читается хуже, чем список: остальные словами."""
        self._подсунуть([], [_пост(и, "draft") for и in range(1, 21)])
        э = _собрать("q")
        self.assertEqual(len([к for к in _коды(э) if к.startswith("p:")]), 12)
        self.assertIn("ещё 8", э.текст)

    def test_пустая_очередь_говорит_что_делать(self):
        self._подсунуть([], [])
        э = _собрать("q")
        self.assertEqual([к for к in _коды(э) if к.startswith("p:")], [])
        self.assertTrue(э.текст.strip())

    def test_сводка_рядом_и_ведёт_к_себе(self):
        self._подсунуть([], [])
        self.assertIn("q:sum", _коды(_собрать("q")))
        self.assertEqual(экраны.родитель("q:sum"), "q")
        self.assertEqual(экраны.родитель("q"), "home")


class КнопкиПоста(unittest.TestCase):
    """Под постом ровно то, что с ним можно сделать в его состоянии."""

    def _набор(self, пост) -> list[str]:
        import json

        import bot
        сетка = json.loads(bot.кнопки_поста(пост))["inline_keyboard"]
        return [к.get("callback_data", "") for ряд in сетка for к in ряд]

    def test_у_запланированного_есть_снятие_и_перенос(self):
        коды = self._набор(_пост(7, "scheduled",
                                 когда="2026-09-09T15:00:00+00:00"))
        self.assertIn("unpl:7", коды)
        self.assertIn("mv:7", коды)

    def test_у_вышедшего_снятия_нет(self):
        """Опубликованное не снимается ничем — кнопка была бы обманом."""
        коды = self._набор(_пост(7, "published", tg_message_id=42))
        self.assertNotIn("unpl:7", коды)
        self.assertIn("redo:7", коды)

    def test_у_черновика_прежний_набор(self):
        """Черновик уже умел всё нужное: набор переносится как есть."""
        import bot
        коды = self._набор(_пост(7, "draft"))
        self.assertIn("pub:7", коды)
        self.assertIn("edit:7", коды)
        self.assertTrue(any(к.startswith("when:7:") for к in коды), коды)
        self.assertEqual(bot.кнопки_поста(_пост(7, "draft")),
                         bot.превью_кнопки(7))

    def test_ссылка_в_канал_только_когда_есть_куда(self):
        import json

        import bot
        вышел = json.loads(bot.кнопки_поста(
            _пост(7, "published", tg_message_id=42, channel="@канал")))
        ссылки = [к for ряд in вышел["inline_keyboard"] for к in ряд if "url" in к]
        self.assertEqual(len(ссылки), 1)
        self.assertTrue(ссылки[0]["url"].endswith("/42"), ссылки)

        без_номера = json.loads(bot.кнопки_поста(_пост(7, "published")))
        self.assertFalse([к for ряд in без_номера["inline_keyboard"]
                          for к in ряд if "url" in к])


class ДлинаКодов(unittest.TestCase):
    """Предел callback_data — 64 байта, и кириллица занимает по два."""

    def test_все_коды_очереди_влезают(self):
        import db
        настоящая = db.для_экрана
        db.для_экрана = lambda *_, **__: (
            [_пост(999999, "scheduled", когда="2026-09-09T15:00:00+00:00")],
            [_пост(888888, "draft")], [])
        try:
            коды = _коды(_собрать("q")) + _коды(_собрать("q:sum"))
        finally:
            db.для_экрана = настоящая
        for к in коды:
            with self.subTest(код=к):
                self.assertLessEqual(len(к.encode("utf-8")), 64)


class МенюНеПлодится(unittest.TestCase):
    """Действие с карточки правит висящее меню, а не шлёт новое."""

    def setUp(self):
        self.было = dict(навигация.ЭКРАН)
        навигация.ЭКРАН.clear()

    def tearDown(self):
        навигация.ЭКРАН.clear()
        навигация.ЭКРАН.update(self.было)

    def test_перерисовать_правит_сообщение_меню(self):
        import telegram as tg
        правки, письма = [], []
        настоящие = (tg.правка_текста, tg.написать)
        tg.правка_текста = lambda чат, сообщение, *а, **к: (
            правки.append(сообщение) or True)
        tg.написать = lambda *а, **к: (письма.append(а) or {"message_id": 5})
        навигация.ЭКРАН[1] = (77, "q")
        try:
            import db
            настоящая = db.для_экрана
            db.для_экрана = lambda *_, **__: ([], [], [])
            try:
                навигация.перерисовать(1, владелец=True)
            finally:
                db.для_экрана = настоящая
        finally:
            tg.правка_текста, tg.написать = настоящие
        self.assertEqual(правки, [77])
        self.assertEqual(письма, [])

    def test_без_живого_меню_перерисовка_молчит(self):
        """Меню ещё не показывали — слать его вдогонку действию незачем."""
        import telegram as tg
        письма = []
        настоящая = tg.написать
        tg.написать = lambda *а, **к: (письма.append(а) or {"message_id": 5})
        try:
            навигация.перерисовать(1, владелец=True)
        finally:
            tg.написать = настоящая
        self.assertEqual(письма, [])


if __name__ == "__main__":
    unittest.main()
