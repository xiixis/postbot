# -*- coding: utf-8 -*-
"""Слайды уходят в облако разом, а не по одному, и порядок не путается."""
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import storage  # noqa: E402


class Разом(unittest.TestCase):
    def test_порядок_запасной_путь_и_скорость(self):
        было = storage.положить

        def положить(ф):
            time.sleep(0.3)
            return None if ф.name == "2.png" else f"https://x/{ф.name}"

        storage.положить = положить
        try:
            t = time.time()
            ссылки = storage.положить_все(
                [Path("1.png"), None, Path("2.png"), Path("3.png"), Path("4.png")])
            прошло = time.time() - t
        finally:
            storage.положить = было
        self.assertEqual(ссылки, ["https://x/1.png", "2.png",
                                  "https://x/3.png", "https://x/4.png"])
        self.assertLess(прошло, 0.6)
