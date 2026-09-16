# -*- coding: utf-8 -*-
"""Библиотека стилей в Style/ не отстаёт от кода.

Папку собирает `tools_style.py` из `card.ДИЗАЙНЫ` и `форматы.py`. Здесь
проверяется не текст паспортов — он пересобирается и меняется, — а то, без
чего папка перестаёт быть библиотекой: у каждого дизайна есть своя папка,
живой кадр, числа стиля и посчитанная схожесть с остальными.

Упал — пересобрать: `python3 tools_style.py` (полностью, с отрисовкой) или
`python3 tools_style.py --мерить --собрать`, если кадры на месте.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card  # noqa: E402

ПАПКА = Path(__file__).resolve().parent.parent / "Style"


class Библиотека(unittest.TestCase):
    def test_у_каждого_дизайна_своя_папка(self):
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(имя):
                self.assertTrue((ПАПКА / имя).is_dir(), f"нет папки стиля {имя}")

    def test_у_каждого_стиля_есть_паспорт_токены_и_кадры(self):
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(имя):
                п = ПАПКА / имя
                self.assertTrue((п / "ПАСПОРТ.md").exists(), "нет паспорта")
                self.assertTrue((п / "токены.json").exists(), "нет токенов")
                self.assertTrue((п / "лист.jpg").exists(), "нет листа кадров")
                кадры = sorted((п / "кадры").glob("*.jpg"))
                self.assertEqual(len(кадры), 4, f"кадров должно быть 4, а не {len(кадры)}")

    def test_токены_читаются_и_держат_гарнитуры(self):
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(имя):
                т = json.loads((ПАПКА / имя / "токены.json").read_text(encoding="utf-8"))
                self.assertEqual(т["имя"], имя)
                свои = card.ДИЗАЙНЫ[имя].get("фейсы", [])
                self.assertEqual(len(т["гарнитуры"]), len(свои),
                                 "список гарнитур разошёлся с card.ДИЗАЙНЫ")

    def test_в_токенах_нет_неподставленных_плейсхолдеров(self):
        """`{рамка}` и `{лайм}` заполняет card._дизайн при отрисовке. Если они
        просочились в токены, числа стиля читаются как мусор."""
        for имя in card.ДИЗАЙНЫ:
            with self.subTest(имя):
                текст = (ПАПКА / имя / "токены.json").read_text(encoding="utf-8")
                т = json.loads(текст)
                для_проверки = (т["радиусы"] + т["границы"] + т["тени и свечения"]
                                + т["разрядка"])
                for з in для_проверки:
                    self.assertNotIn("{", з, f"подстановка осталась в значении: {з}")

    def test_схожесть_посчитана_для_всех_пар(self):
        данные = json.loads((ПАПКА / "замеры.json").read_text(encoding="utf-8"))
        всего = len(card.ДИЗАЙНЫ)
        self.assertEqual(len(данные["схожесть"]), всего)
        for имя, соседи in данные["схожесть"].items():
            with self.subTest(имя):
                self.assertEqual(len(соседи), всего - 1, "не со всеми стилями сравнён")
                for сосед, з in соседи.items():
                    self.assertTrue(0 <= з["общая"] <= 100, f"{имя}↔{сосед}: {з}")

    def test_источники_чужих_стилей_на_месте(self):
        """Четыре стиля списаны с чужих каруселей. Кадры источника лежат рядом
        со стилем копией: исследование может переехать, а папка должна
        открываться и через год."""
        import tools_style  # noqa: E402

        for имя in tools_style.ИСТОЧНИКИ:
            with self.subTest(имя):
                реф = ПАПКА / имя / "референс"
                self.assertTrue((реф / "ИСТОЧНИК.md").exists(), "нет описания источника")
                self.assertTrue(list(реф.glob("*.jpg")), "нет кадров источника")


if __name__ == "__main__":
    unittest.main()
