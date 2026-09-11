# -*- coding: utf-8 -*-
"""Второй проход по голосу идёт с усердием medium, а не с high из общих настроек."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import humanizer  # noqa: E402
import агент      # noqa: E402


class Усердие(unittest.TestCase):
    def test_проход_идёт_на_medium(self):
        пойманное = {}
        было = агент.текстом

        def текстом(задача, **к):
            пойманное.update(к)
            return задача

        агент.текстом = текстом
        try:
            humanizer.очеловечить("Первая строка поста, дальше мысль. " * 5)
        finally:
            агент.текстом = было
        self.assertEqual(пойманное.get("усердие"), "medium")
