# -*- coding: utf-8 -*-
"""Дизайн «пособие»: курсивный акцент вместо плашки и призрачный номер."""
import unittest

import card
import форматы


class Дизайн(unittest.TestCase):
    def размеры(self, номер=3, всего=8):
        return card._виды_размеры(card._общее(номер, всего, формат="тикток"))

    def test_есть_и_в_ротации(self):
        self.assertIn("пособие", card.ДИЗАЙНЫ)
        self.assertIn("пособие", форматы.ДИЗАЙНЫ_ОК)

    def test_подсветка_идёт_курсивом_без_плашки(self):
        css = card._дизайн("пособие", self.размеры())
        self.assertIn("PlayfairIt", css)
        self.assertIn("background:none", css)

    def test_призрачный_номер_показывает_номер_кадра(self):
        css = card._дизайн("пособие", self.размеры(номер=4))
        self.assertIn('content:"04"', css)

    def test_у_других_дизайнов_призрака_нет(self):
        self.assertNotIn("content:\"03\"", card._дизайн("фирменный", self.размеры()))

    def test_курсивные_начертания_на_месте(self):
        """Латиница нужна отдельно: названия вроде Claude кириллицей не набрать."""
        папка = card.config.АССЕТЫ / "fonts"
        for подмн in ("cyrillic", "latin"):
            self.assertTrue((папка / f"playfair-700-italic-{подмн}.woff2").exists(),
                            f"нет начертания {подмн}")

    def test_дизайн_собирается_и_для_обложки(self):
        """У обложки нет размеров вида — дизайн не должен падать на ключе."""
        д = card._общее(1, 8, формат="тикток")
        self.assertIn("content:", card._дизайн("пособие", д))


class ПодсветкаНаОбложке(unittest.TestCase):
    """Звёздочки в заголовке обложки раньше уезжали в кадр как есть."""

    def test_звёздочки_разбираются(self):
        д = card._общее(1, 8, формат="тикток")
        разметка = card._подсветить(card._текст("Ночью канал *работает сам*", 60),
                                    блоком=True)
        self.assertNotIn("*", разметка)
        self.assertIn('<span class="свет">работает сам</span>', разметка)

    def test_у_обложки_есть_стиль_подсветки(self):
        """Без правила разобранное слово выходило обычным текстом."""
        self.assertIn(".свет", card.ОБЛОЖКА_ЕЩЁ)


if __name__ == "__main__":
    unittest.main()
