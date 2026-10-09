# -*- coding: utf-8 -*-
"""Стиль «разбор», вид «шаги»: состав карусели и лапа вместо «Ж» на обложке.

Ловит то, что приёмка досок не видит: потерянный кадр (их шесть после обложки, по числу
слайдов референса), кадр без знака канала и обложку, где лапа не встала на место буквы.
Вёрстку по пикселям проверяет `приёмка_досок.py` после сборки.
"""
import json
import sys
import unittest
from pathlib import Path

ТУТ = Path(__file__).resolve().parent
sys.path.insert(0, str(ТУТ.parent))
sys.path.insert(0, str(ТУТ.parent / "разбор"))

ПОСТ = json.loads((ТУТ.parent / "разбор" / "посты" / "проекты-claude.json").read_text(encoding="utf-8"))


class Шаги(unittest.TestCase):
    def test_шесть_кадров_со_знаком(self):
        import шаги
        доски = шаги.доски_кадров(ПОСТ)
        self.assertEqual([и for и, _, _ in доски], [f"Kadr{н:02d}.dc.html" for н in range(2, 8)])
        for имя, _, html in доски:
            self.assertIn('src="logo.png"', html, f"{имя}: нет знака канала")

    def test_лапа_вместо_ж(self):
        import шаги
        html = шаги.заголовок_с_лапой("ХИТРО🐾ОПАЯ")
        self.assertIn("data-лапа", html)
        self.assertNotIn("🐾", html)
        self.assertTrue(html.startswith("ХИТРО") and html.endswith("ОПАЯ"))


НОЧЬ = json.loads((ТУТ.parent / "разбор" / "посты" / "проекты-claude-ночь.json").read_text(encoding="utf-8"))


class ШагиНочь(unittest.TestCase):
    def test_шесть_кадров_со_знаком_и_без_тире(self):
        import re
        import шаги_ночь
        доски = шаги_ночь.доски_кадров(НОЧЬ)
        self.assertEqual([и for и, _, _ in доски], [f"Kadr{н:02d}.dc.html" for н in range(2, 8)])
        for имя, _, html in доски:
            self.assertIn('src="logo.png"', html, f"{имя}: нет знака канала")
            текст = re.sub(r"<[^>]+>", " ", html.split("<x-dc>")[1])
            self.assertNotIn("—", текст, f"{имя}: длинное тире в тексте кадра (запрет genjutsu)")


if __name__ == "__main__":
    unittest.main()
