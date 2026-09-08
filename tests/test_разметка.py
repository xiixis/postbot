# -*- coding: utf-8 -*-
"""Разметка: текст поста доверять нельзя.

Тело поста сочиняет модель, а правит человек — в том числе человек с ролью
«готовит», не владелец. Оттуда оно уезжает в мини-приложение и рисуется
сырым HTML. Значит ни один кусок этого текста не должен уметь дописать
атрибут к нашему тегу.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import markup                                                # noqa: E402


class Ссылки(unittest.TestCase):
    def test_кавычка_в_адресе_не_дописывает_атрибут(self):
        """Кавычка закрывала href, и дальше писался любой атрибут."""
        итог = markup.в_html('[тык](https://x.ru"style="position:fixed;inset:0)')
        self.assertNotIn('"style="', итог)
        self.assertIn("&quot;", итог)

    def test_кавычка_в_адресе_не_вешает_обработчик(self):
        итог = markup.в_html('[тык](https://x.ru"onmouseover="location=name)')
        self.assertNotIn('"onmouseover="', итог)

    def test_одинарная_кавычка_в_адресе_тоже_экранируется(self):
        """Сегодня атрибут в двойных кавычках, но менять разметку опасно."""
        итог = markup.в_html("[тык](https://x.ru'onmouseover='beda)")
        self.assertNotIn("'onmouseover='", итог)

    def test_обычная_ссылка_цела(self):
        итог = markup.в_html("[тык](https://x.ru/путь)")
        self.assertIn('<a href="https://x.ru/путь">тык</a>', итог)

    def test_амперсанд_в_адресе_не_экранируется_дважды(self):
        """Ссылка с параметрами обязана остаться рабочей."""
        итог = markup.в_html("[тык](https://x.ru/a?один=1&два=2)")
        self.assertIn("один=1&amp;два=2", итог)
        self.assertNotIn("amp;amp;", итог)

    def test_теги_в_тексте_ссылки_экранированы(self):
        итог = markup.в_html("[<img src=x onerror=beda>](https://ok.ru)")
        self.assertNotIn("<img", итог)


if __name__ == "__main__":
    unittest.main()
