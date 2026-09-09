# -*- coding: utf-8 -*-
"""«Сочинить» и копилка: с чего начинается пост.

Копилка из бота была недоступна вовсе: заметки в неё падали, а посмотреть,
что там лежит, и выкинуть ненужное можно было только в приложении. Здесь она
становится экраном, и сторожатся две вещи.

Первая: клавиатура не резиновая. Больше десяти кнопок телеграм показывает
со своей полосой прокрутки внутри чата, и нижние строки человек не видит
вовсе — поэтому идей на экране ровно столько, сколько влезает, а удаление
живёт отдельным экраном, а не второй кнопкой у каждой строки.

Вторая: вопрос словами обязан быть отменяемым и не путаться с копилкой.
Обычное сообщение в чат бот кладёт в копилку; если после «Своя тема» он о
вопросе забудет, тема молча станет заметкой, и человек будет ждать пост,
которого никто не сочиняет.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import навигация                                             # noqa: E402
import экраны                                                # noqa: E402


def _собрать(код: str, арг: str = "", владелец: bool = True) -> экраны.Экран:
    запись, _ = экраны.найти(код)
    return запись.собрать(экраны.Пар(чат=1, арг=арг, владелец=владелец))


def _кнопки(э: экраны.Экран) -> list[tuple[str, str]]:
    return [к for ряд in э.ряды for к in ряд if not isinstance(к, dict)]


def _коды(э: экраны.Экран) -> list[str]:
    return [к[1] for к in _кнопки(э)]


class Сочинить(unittest.TestCase):
    """Всё, с чего начинается пост, собрано на одном экране."""

    def setUp(self):
        import ideas
        self.настоящий = ideas.список
        self.ideas = ideas
        ideas.список = lambda *_, **__: []

    def tearDown(self):
        self.ideas.список = self.настоящий

    def test_все_способы_начать_на_месте(self):
        коды = _коды(_собрать("make"))
        for код in ("gen:auto", "carousel", "r", "ideas", "stream", "topic"):
            with self.subTest(код=код):
                self.assertIn(код, коды)

    def test_рубрики_и_копилка_теперь_под_сочинить(self):
        """Раньше рубрики висели в главном меню вровень с «сделать пост»."""
        self.assertEqual(экраны.родитель("r"), "make")
        self.assertEqual(экраны.родитель("ideas"), "make")
        self.assertEqual(экраны.родитель("make"), "home")

    def test_пустая_копилка_без_числа(self):
        """Ноль на кнопке читается как поломка, а не как «там пусто»."""
        подписи = dict((к[1], к[0]) for к in _кнопки(_собрать("make")))
        self.assertNotIn("·", подписи["ideas"])

    def test_непустая_копилка_с_числом(self):
        self.ideas.список = lambda *_, **__: [{"id": 1, "text": "раз"},
                                              {"id": 2, "text": "два"}]
        подписи = dict((к[1], к[0]) for к in _кнопки(_собрать("make")))
        self.assertIn("2", подписи["ideas"])


class Копилка(unittest.TestCase):

    def setUp(self):
        import ideas
        self.настоящий = ideas.список
        self.ideas = ideas

    def tearDown(self):
        self.ideas.список = self.настоящий

    def _идеи(self, сколько: int):
        self.ideas.список = lambda *_, **__: [
            {"id": и, "text": f"идея номер {и}"} for и in range(1, сколько + 1)]

    def test_тычок_берёт_идею_в_работу(self):
        self._идеи(2)
        коды = _коды(_собрать("ideas"))
        self.assertIn("idea:1", коды)
        self.assertIn("idea:2", коды)

    def test_клавиатура_не_переполняется(self):
        """Больше десяти кнопок телеграм прячет за своей прокруткой."""
        self._идеи(30)
        for код in ("ideas", "ideas:rm"):
            with self.subTest(экран=код):
                self.assertLessEqual(len(_кнопки(_собрать(код))), 10)

    def test_остальные_посчитаны_словами(self):
        self._идеи(30)
        self.assertIn("ещё", _собрать("ideas").текст)

    def test_пустая_копилка_объясняет_себя(self):
        self._идеи(0)
        э = _собрать("ideas")
        self.assertEqual([к for к in _коды(э) if к.startswith("idea:")], [])
        self.assertTrue(э.текст.strip())
        self.assertNotIn("ideas:rm", _коды(э),
                         "убирать нечего — кнопке удаления неоткуда взяться")

    def test_удаление_живёт_своим_экраном(self):
        self._идеи(3)
        self.assertIn("ideas:rm", _коды(_собрать("ideas")))
        self.assertEqual(экраны.родитель("ideas:rm"), "ideas")
        self.assertIn("idrm:1", _коды(_собрать("ideas:rm")))

    def test_добавить_спрашивает_словами(self):
        self._идеи(1)
        self.assertIn("idnew", _коды(_собрать("ideas")))


class ВопросСловами(unittest.TestCase):
    """Ответ на вопрос уходит по назначению, а не в копилку."""

    def setUp(self):
        self.было = dict(навигация.ЖДЁМ)
        навигация.ЖДЁМ.clear()

    def tearDown(self):
        навигация.ЖДЁМ.clear()
        навигация.ЖДЁМ.update(self.было)

    def test_тема_уходит_в_пост_а_не_в_копилку(self):
        import bot
        сочинили, отложили = [], []
        настоящие = (bot.сделать_пост, bot.отложить_идею)
        bot.сделать_пост = lambda чат, рубрика, тема=None, *а, **к: (
            сочинили.append(тема))
        bot.отложить_идею = lambda *а, **к: отложили.append(а)
        навигация.ЖДЁМ[1] = ("тема", {})
        try:
            bot.ответить_словами(1, "про кота и озвучку")
        finally:
            bot.сделать_пост, bot.отложить_идею = настоящие
        self.assertEqual(сочинили, ["про кота и озвучку"])
        self.assertEqual(отложили, [])
        self.assertIsNone(навигация.чего_ждём(1), "ожидание снимается сразу")

    def test_идея_ложится_в_копилку_без_вопросов(self):
        """Из копилки её и просили: спрашивать «сделать пост?» тут незачем."""
        import bot
        import ideas
        добавили = []
        настоящие = (ideas.добавить, ideas.подготовить)
        ideas.добавить = lambda текст: (добавили.append(текст) or 1)
        ideas.подготовить = lambda: None
        навигация.ЖДЁМ[1] = ("идея", {})
        try:
            bot.ответить_словами(1, "посмотреть, как считают охват")
        finally:
            ideas.добавить, ideas.подготовить = настоящие
        self.assertEqual(добавили, ["посмотреть, как считают охват"])

    def test_чужого_текста_без_вопроса_не_трогаем(self):
        import bot
        self.assertFalse(bot.ответить_словами(1, "просто мысль"))


if __name__ == "__main__":
    unittest.main()
