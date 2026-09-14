# -*- coding: utf-8 -*-
"""Лист кадров: вся карусель одной картинкой, брак обведён."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import лист  # noqa: E402


def кадры(сколько: int) -> list[Path]:
    from PIL import Image
    папка = Path(tempfile.mkdtemp())
    итог = []
    for н in range(сколько):
        п = папка / f"{н:02d}.png"
        Image.new("RGB", (1620, 2160), (20 + н * 20, 40, 60)).save(п)
        итог.append(п)
    return итог


class Лист(unittest.TestCase):
    def test_десять_кадров_в_два_ряда(self):
        from PIL import Image
        куда = Path(tempfile.mkdtemp()) / "лист.jpg"
        итог = лист.собрать(кадры(10), куда)
        self.assertEqual(итог, куда)
        with Image.open(итог) as к:
            ш, в = к.size
        self.assertEqual(ш, лист.ЗАЗОР + лист.КОЛОНОК * (лист.ШИРИНА + лист.ЗАЗОР))
        self.assertLess(в, ш, "десять кадров 3:4 ложатся в два ряда")

    def test_брак_обведён_цветом(self):
        from PIL import Image
        куда = Path(tempfile.mkdtemp()) / "лист.jpg"
        лист.собрать(кадры(3), куда, брак=[2])
        x = лист.ЗАЗОР + (лист.ШИРИНА + лист.ЗАЗОР) - 3   # левая рамка второго кадра
        with Image.open(куда) as к:
            рамка = к.convert("RGB").getpixel((x, лист.ЗАЗОР + 50))
            у_первого = к.convert("RGB").getpixel((лист.ЗАЗОР - 3, лист.ЗАЗОР + 50))
        self.assertTrue(all(abs(а - б) < 40 for а, б in zip(рамка, лист.БРАК)), рамка)
        self.assertFalse(all(abs(а - б) < 40 for а, б in zip(у_первого, лист.БРАК)),
                         "годный кадр не обводится")

    def test_пусто_без_кадров(self):
        self.assertIsNone(лист.собрать([None, Path("/нет/такого.png")]))
