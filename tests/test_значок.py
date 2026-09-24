# -*- coding: utf-8 -*-
"""Значок сервиса для кадра: лестница favicon 256 → сайт → App Store, без чужого приложения.

24.09.2026 первым в App Store по запросу «Lumen5» стоял «Lumen AI» — другое приложение, и
значок чуть не уехал в пост. Поэтому App Store берётся только с совпадением имени, а
несовпадение печатается как «проверить», а не молча.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Style"))

import значок  # noqa: E402


class ИконкиСайта(unittest.TestCase):
    def test_крупные_первыми_и_адрес_полный(self):
        html = ('<link rel="icon" href="/favicon-32.png" sizes="32x32">'
                '<link rel="apple-touch-icon" href="/apple-180.png" sizes="180x180">'
                '<link href="https://cdn.x.io/logo.svg" rel="icon" type="image/svg+xml">'
                '<meta property="og:image" content="/og.png">')
        адреса = значок.иконки_сайта(html, "https://x.io/")
        self.assertEqual(адреса[:2], ["https://cdn.x.io/logo.svg", "https://x.io/apple-180.png"])
        self.assertIn("https://x.io/favicon-32.png", адреса)
        self.assertEqual(адреса[-1], "https://x.io/og.png")     # обложка страницы — последней

    def test_пусто(self):
        self.assertEqual(значок.иконки_сайта("<html></html>", "https://x.io/"), [])


class ПриложениеПоИмени(unittest.TestCase):
    РЕЗУЛЬТАТЫ = [{"trackName": "Lumen AI: Chat & Ask", "sellerName": "Lumen Labs"},
                  {"trackName": "Lumen5 Video Maker", "sellerName": "Lumen5"}]

    def test_берёт_то_самое_а_не_первое(self):
        выбор, _ = значок.приложение(self.РЕЗУЛЬТАТЫ, "lumen5")
        self.assertEqual(выбор["trackName"], "Lumen5 Video Maker")

    def test_нет_совпадения_нет_выбора(self):
        выбор, строки = значок.приложение(self.РЕЗУЛЬТАТЫ, "vyond")
        self.assertIsNone(выбор)
        self.assertEqual(len(строки), 2)          # кандидаты печатаются для проверки


if __name__ == "__main__":
    unittest.main()
