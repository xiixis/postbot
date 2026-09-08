# -*- coding: utf-8 -*-
"""Возврат из TikTok: страницу видит браузер на нашем домене.

Адрес /api/tiktok открыт всем и отдаёт HTML, а текст отказа приезжает
параметром запроса. Значит его пишет не TikTok, а тот, кто прислал ссылку.
Домен тот же, где живёт мини-приложение, и в его localStorage лежит ключ
доступа: чужой скрипт, выполнившийся здесь, забирает бота целиком.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tiktok                                                # noqa: E402


def _не_ставить(*_а, **_к):
    raise AssertionError("задание ставиться не должно")


class СтраницаВозврата(unittest.TestCase):
    def test_текст_отказа_не_вносит_разметку(self):
        нутро = tiktok.нутро_возврата("", "<script>beda()</script>", _не_ставить)
        self.assertNotIn("<script>", нутро)
        self.assertIn("&lt;script&gt;", нутро)

    def test_кавычка_в_отказе_не_рвёт_атрибут(self):
        нутро = tiktok.нутро_возврата("", 'бе"да', _не_ставить)
        self.assertNotIn('"да', нутро)

    def test_сбой_постановки_не_вносит_разметку(self):
        def падает(*_а, **_к):
            raise RuntimeError("<img src=x onerror=beda>")

        нутро = tiktok.нутро_возврата("код-от-тиктока", "", падает)
        self.assertNotIn("<img", нутро)

    def test_код_уходит_заданием(self):
        поставлено = []
        нутро = tiktok.нутро_возврата(
            "код-от-тиктока", "", lambda код: поставлено.append(код))
        self.assertEqual(поставлено, ["код-от-тиктока"])
        self.assertIn("Готово", нутро)

    def test_ни_кода_ни_ошибки(self):
        нутро = tiktok.нутро_возврата("", "", _не_ставить)
        self.assertIn("Ни кода, ни ошибки", нутро)


class ЦелаяСтраница(unittest.TestCase):
    def test_страница_возврата_обёрнута_и_в_байтах(self):
        готово = tiktok.страница_возврата("", "", _не_ставить)
        self.assertIsInstance(готово, bytes)
        self.assertIn("charset".encode(), готово)


if __name__ == "__main__":
    unittest.main()
