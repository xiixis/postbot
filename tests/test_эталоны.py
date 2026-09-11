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
        "{{АССЕТЫ}}", str(config.АССЕТЫ))


def опись() -> dict:
    return json.loads((ПАПКА / "замеры.json").read_text(encoding="utf-8"))


@unittest.skipUnless(config.хром(), "нужен Chrome")
class Эталон(unittest.TestCase):
    def test_замеры_совпадают(self):
        for к in опись()["кадры"]:
            with self.subTest(кадр=к["файл"]):
                з = card._замерить(страница(к["файл"]), к["ширина"], к["высота"])
                self.assertEqual({и: з.get(и) for и in СТАРЫЕ},
                                 {и: к["замер"].get(и) for и in СТАРЫЕ})

    def test_на_годных_кадрах_тревог_нет(self):
        формат = опись()["формат"]
        for к in опись()["кадры"]:
            with self.subTest(кадр=к["файл"]):
                з = card._замерить(страница(к["файл"]), к["ширина"], к["высота"])
                self.assertEqual(з.get("порвано", []), [])
                self.assertEqual(з.get("невидимо", []), [])
                self.assertEqual(card.проверить_композицию(з, формат),
                                 card.проверить_композицию(к["замер"], формат))
