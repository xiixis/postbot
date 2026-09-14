# -*- coding: utf-8 -*-
"""Брак ставит снимок: одна точка на обложку, середину и финал."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card      # noqa: E402
import приёмка   # noqa: E402


def png(ширина: int, высота: int) -> Path:
    from PIL import Image
    путь = Path(tempfile.mkdtemp()) / "кадр.png"
    Image.new("RGB", (ширина, высота)).save(путь)
    return путь


class Принять(unittest.TestCase):
    def setUp(self):
        self.было = card._замерить

    def tearDown(self):
        card._замерить = self.было
        приёмка.итог()

    def test_без_журнала_не_меряет(self):
        card._замерить = lambda *а, **к: self.fail("без журнала мерить незачем")
        путь = png(1620, 2160)
        self.assertEqual(card._принять(путь, "<p>", 1080, 1440), путь)

    def test_итог_проверок_это_брак(self):
        приёмка.начать()
        приёмка.кадр(3, "мысль")
        card._замерить = lambda *а, **к: {"холст": [1080, 1440],
                                          "перелив": [["h1", 900, 800]],
                                          "битые_картинки": ["кота.png"]}
        card._принять(png(1620, 2160), "<p>", 1080, 1440, ["ReferenceError: нет"])
        брак = приёмка.итог()["кадры"][0]["брак"]
        self.assertIn("слово шире колонки", брак)
        self.assertIn("страница: картинка не загрузилась: кота.png", брак)
        self.assertIn("страница: ошибка в браузере: ReferenceError: нет", брак)

    def test_чистый_кадр_годен(self):
        приёмка.начать()
        приёмка.кадр(2, "мысль")
        card._замерить = lambda *а, **к: {"холст": [1080, 1440]}
        card._принять(png(1620, 2160), "<p>", 1080, 1440)
        self.assertTrue(приёмка.итог()["годен"])

    def test_размер_снимка_не_тот_это_брак(self):
        приёмка.начать()
        приёмка.кадр(2, "мысль")
        card._замерить = lambda *а, **к: {"холст": [1080, 1440]}
        card._принять(png(1080, 1440), "<p>", 1080, 1440)
        self.assertIn("страница: кадр 1080×1440 вместо 1620×2160",
                      приёмка.итог()["кадры"][0]["брак"])

    def test_формат_по_размеру(self):
        self.assertEqual(card._формат_по_размеру(1080, 1440), "3к4")
        self.assertEqual(card._формат_по_размеру(1080, 1080), "квадрат")
        self.assertEqual(card._формат_по_размеру(1080, 1920), "вертикаль")
        self.assertEqual(card._формат_по_размеру(1280, 720), "широкий")


class Плотность(unittest.TestCase):
    def tearDown(self):
        приёмка.итог()

    def test_плотность_идёт_замечанием(self):
        import замер
        было = замер.проверить_снимок
        замер.проверить_снимок = lambda путь, дизайн="": ["чернил 1%"]
        try:
            приёмка.начать()
            приёмка.кадр(2, "мысль")
            card._плотность(Path("/tmp/кадр.png"), "мысль", "фирменный")
            запись = приёмка.итог()["кадры"][0]
        finally:
            замер.проверить_снимок = было
        self.assertEqual(запись["брак"], [])
        self.assertEqual(запись["замечания"], ["плотность: чернил 1%"])
