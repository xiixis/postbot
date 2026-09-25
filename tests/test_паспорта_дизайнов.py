# -*- coding: utf-8 -*-
"""Паспорта дизайнов в docs/дизайны не отстают от кода.

Паспорт собирается из `card.ДИЗАЙНЫ` и `форматы.py` скриптом `tools_дизайны.py`. Описание,
которое правят руками, устаревает с первой правки кода — поэтому тест сверяет файл
с тем, что скрипт собрал бы сейчас. Упал — пересобрать: `python3 tools_дизайны.py --без-картинок`.
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card            # noqa: E402
import tools_дизайны   # noqa: E402


def без_даты(текст: str) -> str:
    return re.sub(r"из кода \d\d\.\d\d\.\d{4}", "из кода", текст)


class Паспорта(unittest.TestCase):
    def test_у_каждого_дизайна_есть_папка_с_паспортом(self):
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(дизайн=имя):
                self.assertTrue((tools_дизайны.ПАПКА / имя / "ПАСПОРТ.md").exists())

    def test_паспорт_совпадает_с_кодом(self):
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(дизайн=имя):
                папка = tools_дизайны.ПАПКА / имя
                файл = (папка / "ПАСПОРТ.md").read_text(encoding="utf-8")
                сейчас = tools_дизайны.паспорт(имя, (папка / "лист.jpg").exists())
                self.assertEqual(без_даты(файл), без_даты(сейчас))


if __name__ == "__main__":
    unittest.main()
