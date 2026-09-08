# -*- coding: utf-8 -*-
"""Мак отдаёт то же приложение, что и облако, — значит и защищать обязан так же.

Запаска включается ровно тогда, когда Vercel недоступен, то есть в худший
день. Заголовки, живущие только в vercel.json, в этот день не работают, и
приложение открывается голым.
"""

import sys
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))

import config                                                # noqa: E402
import webapp                                                # noqa: E402


class _Тихая:
    """Ручка без сокета: нас интересуют только заголовки, а не сеть."""

    def __init__(self):
        self.заголовки = {}
        self.код = None
        self.wfile = self

    def write(self, _данные):
        pass

    def send_response(self, код):
        self.код = код

    def send_header(self, имя, значение):
        self.заголовки[имя] = значение

    def end_headers(self):
        pass


def _отдать(тип="text/html", код=200):
    ручка = _Тихая()
    webapp.Ручка._отдать(ручка, "тело".encode(), тип, код)
    return ручка


class ЗаголовкиОтдачи(unittest.TestCase):
    def test_политика_та_же_что_в_облаке(self):
        self.assertEqual(_отдать().заголовки.get("Content-Security-Policy"),
                         config.ПОЛИТИКА)

    def test_остальные_заголовки(self):
        з = _отдать().заголовки
        self.assertEqual(з.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("Referrer-Policy", з)

    def test_отдача_не_сломалась(self):
        ручка = _отдать(код=404)
        self.assertEqual(ручка.код, 404)
        self.assertEqual(ручка.заголовки["Content-Length"], "8")
        self.assertEqual(ручка.заголовки["Cache-Control"], "no-store")


class ОднаПолитикаНаОбаКрая(unittest.TestCase):
    def test_сборщик_берёт_политику_оттуда_же(self):
        import tools_vercel
        self.assertIn(config.ПОЛИТИКА, tools_vercel.НАСТРОЙКИ)


if __name__ == "__main__":
    unittest.main()
