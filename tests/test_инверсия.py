# -*- coding: utf-8 -*-
"""Инверсия — перевёрнутая палитра: лаймовый фон, тёмный акцент, ничего не сливается."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card    # noqa: E402
import config  # noqa: E402


class Палитра(unittest.TestCase):
    def test_фон_лайм_акцент_тёмный_и_на_светлом_кадре(self):
        д = card._общее(3, 10, "3к4", "инверсия")      # третий кадр обычно светлый
        self.assertEqual(д["фон"], config.ЛАЙМ)
        self.assertEqual(д["лайм"], config.ФОН)
        self.assertEqual(д["по_лайму"], config.ЛАЙМ)

    def test_без_инверсии_палитра_прежняя(self):
        д = card._общее(2, 10, "3к4")
        self.assertEqual((д["фон"], д["лайм"], д["по_лайму"]),
                         (config.ФОН, config.ЛАЙМ, config.ФОН))


@unittest.skipUnless(config.хром(), "нужен Chrome")
class ВБраузере(unittest.TestCase):
    def test_на_инверсии_ничего_не_сливается(self):
        образцы = {
            "список": {"заголовок": "Кому поручить", "пункты": ["ChatGPT: таблицы",
                                                              "Claude: по шагам"]},
            "правка": {"неверно": "Продажи упали из-за рекламы",
                       "верно": "Продажи *упали из-за цены*"},
            "цифра": {"заголовок": "Экономия", "текст": "в неделю", "цифра": "5 ч"},
        }
        for вид, поля in образцы.items():
            with self.subTest(вид=вид):
                стр, ш, в = card.страница_вида(вид, поля, 3, 10, "3к4",
                                               оформление="инверсия")
                self.assertEqual(card._замерить(стр, ш, в)["невидимо"], [])
