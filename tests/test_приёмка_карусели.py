# -*- coding: utf-8 -*-
"""Каждый кадр карусели попадает в журнал под своим номером."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card      # noqa: E402
import carousel  # noqa: E402
import mascot    # noqa: E402
import приёмка   # noqa: E402

КАРУСЕЛЬ = {"cover_kicker": "Над", "cover_title": "Обложка",
            "slides": [{"вид": "мысль", "заголовок": "Раз", "текст": "Мысль раз"},
                       {"вид": "мысль", "заголовок": "Два", "текст": "Мысль два"}],
            "closing": "Итог", "паспорт": {"кот": False}}


class ЖурналКарусели(unittest.TestCase):
    def setUp(self):
        self.было = (card.слайд_обложка, card.слайд_вида, card.слайд_финал,
                     mascot.библиотека)
        self.номера = []

        def отметить(*а, **к):
            self.номера.append(приёмка.текущий().get("номер"))
            return Path("/tmp/кадр.png")

        card.слайд_обложка = card.слайд_вида = card.слайд_финал = отметить
        mascot.библиотека = lambda: {}

    def tearDown(self):
        (card.слайд_обложка, card.слайд_вида, card.слайд_финал,
         mascot.библиотека) = self.было
        приёмка.итог()

    def test_номера_кадров_по_порядку(self):
        приёмка.начать()
        carousel.нарисовать(КАРУСЕЛЬ, "3к4", Path("/tmp/поза.png"))
        отчёт = приёмка.итог()
        self.assertEqual(self.номера, [1, 2, 3, 4])
        self.assertEqual([к["вид"] for к in отчёт["кадры"]],
                         ["обложка", "мысль", "мысль", "финал"])

    def test_один_кадр_по_номеру(self):
        приёмка.начать()
        carousel.нарисовать(КАРУСЕЛЬ, "3к4", Path("/tmp/поза.png"), только=3)
        self.assertEqual([к["номер"] for к in приёмка.итог()["кадры"]], [3])

    def test_пост_одним_кадром(self):
        приёмка.начать()
        carousel.нарисовать({"slides": [{"вид": "мысль", "текст": "Одна"}],
                             "паспорт": {"кадров": [1, 1], "вид": "мысль"}},
                            "3к4", Path("/tmp/поза.png"))
        отчёт = приёмка.итог()
        self.assertEqual(self.номера, [1])
        self.assertEqual([к["номер"] for к in отчёт["кадры"]], [1])
