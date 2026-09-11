# -*- coding: utf-8 -*-
"""Кэш замера: та же страница того же размера меряется один раз."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card  # noqa: E402


class Кэш(unittest.TestCase):
    def setUp(self):
        card._ЗАМЕРЫ.clear()
        self.вызовы = []
        self.было = card._замерить_заново
        card._замерить_заново = (
            lambda с, ш=1080, в=1440: self.вызовы.append((ш, в)) or {"холст": [ш, в]})

    def tearDown(self):
        card._замерить_заново = self.было
        card._ЗАМЕРЫ.clear()

    def test_та_же_страница_меряется_один_раз(self):
        card._замерить("<p>а</p>", 1080, 1440)
        card._замерить("<p>а</p>", 1080, 1440)
        self.assertEqual(len(self.вызовы), 1)

    def test_другой_размер_меряется_заново(self):
        card._замерить("<p>а</p>", 1080, 1440)
        card._замерить("<p>а</p>", 1080, 1920)
        self.assertEqual(len(self.вызовы), 2)

    def test_неудачный_замер_не_запоминается(self):
        card._замерить_заново = lambda *а, **к: self.вызовы.append(1) or {}
        card._замерить("<p>б</p>")
        card._замерить("<p>б</p>")
        self.assertEqual(len(self.вызовы), 2)

    def test_правка_ответа_не_портит_кэш(self):
        з = card._замерить("<p>в</p>")
        з["холст"][0] = 1
        self.assertEqual(card._замерить("<p>в</p>")["холст"][0], 1080)
