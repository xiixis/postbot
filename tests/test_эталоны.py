# -*- coding: utf-8 -*-
"""Эталон поста 96: замер обязан совпасть, годные кадры — без тревог.

Страховка перед сменой движка и новыми проверками: десять настоящих кадров,
которые ушли в TikTok и были приняты владельцем.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card    # noqa: E402
import config  # noqa: E402

ПАПКА = Path(__file__).resolve().parent / "эталоны" / "пост96"
СТАРЫЕ = ("холст", "текст", "кот", "реплика", "призыв", "знак", "полоса",
          "перелив", "строки")


def страница(имя: str) -> str:
    return (ПАПКА / имя).read_text(encoding="utf-8").replace(
        "file://{{АССЕТЫ}}", config.АССЕТЫ.as_uri())


def близко(а, б) -> bool:
    """Совпадение с точностью до пикселя.

    Chrome на Windows растеризует шрифт иначе, чем на маке: край строки уезжает
    на 1 px (замер 22.09.2026: 701 против 700). Это не поломка вёрстки. Число
    блоков и строк при этом обязано совпасть точно — там и живут настоящие сбои.
    """
    if isinstance(а, (int, float)) and isinstance(б, (int, float)):
        return abs(а - б) <= 1
    if isinstance(а, list) and isinstance(б, list):
        return len(а) == len(б) and all(близко(x, y) for x, y in zip(а, б))
    return а == б


def опись() -> dict:
    return json.loads((ПАПКА / "замеры.json").read_text(encoding="utf-8"))


@unittest.skipUnless(config.хром(), "нужен Chrome")
class Эталон(unittest.TestCase):
    def test_замеры_совпадают(self):
        for к in опись()["кадры"]:
            with self.subTest(кадр=к["файл"]):
                з = card._замерить(страница(к["файл"]), к["ширина"], к["высота"])
                было = {и: к["замер"].get(и) for и in СТАРЫЕ}
                стало = {и: з.get(и) for и in СТАРЫЕ}
                self.assertTrue(all(близко(стало[и], было[и]) for и in СТАРЫЕ),
                                f"замер разошёлся больше чем на 1 px:\n{стало}\n{было}")

    def test_на_годных_кадрах_тревог_нет(self):
        формат = опись()["формат"]
        for к in опись()["кадры"]:
            with self.subTest(кадр=к["файл"]):
                з = card._замерить(страница(к["файл"]), к["ширина"], к["высота"])
                self.assertEqual(з.get("порвано", []), [])
                self.assertEqual(з.get("невидимо", []), [])
                self.assertEqual(з.get("обрезано", []), [])
                self.assertEqual(card.проверить_страницу(з), [])
                self.assertEqual(card.проверить_композицию(з, формат),
                                 card.проверить_композицию(к["замер"], формат))
