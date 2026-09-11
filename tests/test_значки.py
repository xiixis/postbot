# -*- coding: utf-8 -*-
"""Значки инструментов: распознавание имени, вшивание данными, цвет."""
import unittest

import card
import config


class ЗнакПоИмени(unittest.TestCase):
    def test_имя_в_начале_даёт_знак(self):
        маска, имя, остаток = card._знак_инструмента("Claude держит голос")
        self.assertTrue(маска)
        self.assertEqual(имя, "Claude")
        self.assertEqual(остаток, "держит голос")

    def test_имя_из_двух_слов(self):
        _, имя, остаток = card._знак_инструмента("Hugging Face для моделей")
        self.assertEqual(имя, "Hugging Face")
        self.assertEqual(остаток, "для моделей")

    def test_имя_в_середине_знака_не_даёт(self):
        """«похоже на claude» — предложение, а не пункт про Claude."""
        маска, _, остаток = card._знак_инструмента("похоже на claude")
        self.assertFalse(маска)
        self.assertEqual(остаток, "похоже на claude")

    def test_незнакомое_имя_молчит(self):
        маска, _, _ = card._знак_инструмента("Midjourney рисует картинки")
        self.assertFalse(маска, "логотипа Midjourney у нас нет — знака быть не должно")

    def test_нет_файла_нет_знака(self):
        self.assertEqual(card.значок("такого-нет"), "")


class ЗнакВСтранице(unittest.TestCase):
    def test_вшит_данными_а_не_ссылкой(self):
        """Маску с file:// Chrome не грузит и молча рисует пустоту."""
        правило = card.значок("claude")
        self.assertIn("data:image/svg+xml;base64,", правило)
        self.assertNotIn("file://", правило)

    def test_все_имена_из_карты_на_месте(self):
        нет = sorted({ф for ф in card.ЗНАЧКИ.values()
                      if not (config.АССЕТЫ / "значки" / (ф + ".svg")).exists()})
        self.assertEqual(нет, [], "в карте есть имена без файлов")


class ЦветЗнака(unittest.TestCase):
    def test_на_светлом_кадре_знак_не_лаймовый(self):
        """Лайм на кремовом даёт контраст 1,3 к 1 — знак пропадает."""
        светлый = card._общее(3, 10)      # нечётный, значит светлый
        тёмный = card._общее(2, 10)
        self.assertTrue(card.светлый_ли(3))
        self.assertNotEqual(светлый["знак_цвет"], config.ЛАЙМ)
        self.assertEqual(тёмный["знак_цвет"], config.ЛАЙМ)

    def test_в_инверсии_знак_тёмный(self):
        д = card._общее(2, 10, оформление="инверсия")
        self.assertEqual(д["знак_цвет"], config.ФОН)


class ПоверхностьНаСветломКадре(unittest.TestCase):
    """Плитки и чипы на светлом кадре выходили тёмными с тёмным текстом."""

    def test_поверхность_выворачивается_вместе_с_палитрой(self):
        светлый = card._общее(3, 10)
        self.assertNotEqual(светлый["поверхность"], config.ПОВЕРХНОСТЬ)
        # Поверхность светлого кадра должна быть светлой: сравниваем яркость
        # с цветом текста, который на таком кадре тёмный.
        def яркость(цвет):
            ц = цвет.lstrip("#")
            return sum(int(ц[i:i + 2], 16) for i in (0, 2, 4)) / 3
        self.assertGreater(яркость(светлый["поверхность"]),
                           яркость(светлый["текст"]) + 80)


if __name__ == "__main__":
    unittest.main()
