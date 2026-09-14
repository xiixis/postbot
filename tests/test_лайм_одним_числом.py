# -*- coding: utf-8 -*-
"""Лайм задаётся в config один раз.

В card.py полупрозрачный лайм был вписан числом `rgba(199,226,75,…)` в 53
местах, мимо config.ЛАЙМ. Поменяй цвет канала — и сетки, свечения и плашки
остались бы старого цвета. У html-instagram-carousel вся палитра в одном
tokens.css; здесь то же для самого размазанного цвета.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402

КОРЕНЬ = Path(__file__).resolve().parent.parent


class Лайм(unittest.TestCase):
    def test_числа_лайма_нет_в_рисовальщике(self):
        текст = (КОРЕНЬ / "card.py").read_text(encoding="utf-8")
        self.assertEqual(текст.count("199,226,75"), 0)

    def test_rgb_выводится_из_hex(self):
        ч = [int(config.ЛАЙМ[i:i + 2], 16) for i in (1, 3, 5)]
        self.assertEqual(config.ЛАЙМ_RGB, ",".join(map(str, ч)))

    def test_смена_лайма_доходит_до_полупрозрачных(self):
        import card
        было, было_rgb = config.ЛАЙМ, config.ЛАЙМ_RGB
        config.ЛАЙМ, config.ЛАЙМ_RGB = "#FF0000", "255,0,0"
        try:
            стр, _, _ = card.страница_вида("мысль", {"заголовок": "Ш", "текст": "М"},
                                           3, 10, "3к4")
        finally:
            config.ЛАЙМ, config.ЛАЙМ_RGB = было, было_rgb
        self.assertIn("rgba(255,0,0,", стр)
