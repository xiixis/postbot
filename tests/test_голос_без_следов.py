# -*- coding: utf-8 -*-
"""Запреты «Антидетектора» и приёмы «Сторителлинг-корректора» доходят до модели.

Детектор ловит следы после, но дешевле, чтобы их не было с первого раза.
Поэтому оба блока стоят в тех подсказках, которыми пишется текст: запреты в
голосе текста и во втором проходе, история в голосе канала.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import humanizer  # noqa: E402
import writer     # noqa: E402


class Подсказки(unittest.TestCase):
    def test_запреты_в_голосе_и_во_втором_проходе(self):
        self.assertIn(humanizer.ЗАПРЕТЫ_ИИ, humanizer.ГОЛОС)
        self.assertIn(humanizer.ЗАПРЕТЫ_ИИ, humanizer.ЗАДАЧА)

    def test_запреты_называют_главные_формулы(self):
        for формула in ("не просто", "не только", "это не про", "данный",
                        "является", "по-настоящему", "сам ответил", "просто. честно"):
            with self.subTest(формула=формула):
                self.assertIn(формула, humanizer.ЗАПРЕТЫ_ИИ.lower())

    def test_история_в_голосе_канала(self):
        self.assertIn(writer.ИСТОРИЯ, writer.ГОЛОС)
        for приём in ("НО", "ПОЭТОМУ", "СТАВКИ", "ПОВОРОТ", "СЦЕНА"):
            with self.subTest(приём=приём):
                self.assertIn(приём, writer.ИСТОРИЯ)

    def test_история_не_разрешает_выдумывать(self):
        """Сцена и мысли — зрителя, реплики — только из материала."""
        self.assertIn("не выдумывай", writer.ИСТОРИЯ.lower())
