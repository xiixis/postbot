# -*- coding: utf-8 -*-
"""Измеритель кадров: контраст считается по буквам, а ритм — по всей карусели.

Мерка контраста — доля текста, не дотянувшего до 8:1. Одно число «худший пиксель»
сюда не годится: им оказывается контур кота или край логотипа, то есть картинка, и
годный кадр объявляется браком. Целая бледная строка даёт заметную долю, точечная
примесь картинки — нет.

Кадры для проверок рисуются настоящим шрифтом, а не прямоугольниками: прямоугольник
для измерителя — плашка, и правильно, что он её отбрасывает.
"""
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import замер  # noqa: E402

# Ожидания тестов сняты с метрик Arial Bold, поэтому ищем его на любой ОС: раньше путь
# был только маковский, и на Windows и Linux 7 тестов падали на ровном месте (аудит
# 25.09.2026). Шрифт проекта — запасной: у Onest хвосты «р», «у» мелкой строки замер
# считает отдельной полосой, и тест «два уровня кегля» с ним не сходится.
ШРИФТЫ_ARIAL = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",       # мак
                "C:/Windows/Fonts/arialbd.ttf",                              # Windows
                "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",    # Linux с msttcorefonts
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
ШРИФТ = next((ш for ш in ШРИФТЫ_ARIAL if Path(ш).exists()),
             str(Path(__file__).resolve().parents[2] / "assets/fonts/onest-800-cyrillic.woff2"))


def кадр_с_текстом(папка: Path, имя: str, цвет: str, фон: str,
                   крупно: int = 150, мелко: int = 46) -> Path:
    и = Image.new("RGB", (1080, 1440), фон)
    д = ImageDraw.Draw(и)
    д.text((80, 200), "ТРИ СЕРВИСА", font=ImageFont.truetype(ШРИФТ, крупно), fill=цвет)
    д.text((80, 430), "которые правда работают", font=ImageFont.truetype(ШРИФТ, мелко), fill=цвет)
    путь = папка / имя
    и.save(путь)
    return путь


class Контраст(unittest.TestCase):
    def test_индиго_по_крему_проходит(self):
        """#1B3487 по #F2EFE8 — 9,7:1 по формуле WCAG: слабого текста быть не должно."""
        с = tempfile.TemporaryDirectory()
        путь = кадр_с_текстом(Path(с.name), "01.png", "#1B3487", "#F2EFE8")
        д = замер.кадр(путь)
        self.assertGreater(д["контраст_середина"], 8.0)
        self.assertLess(д["слабых_доля"], 0.15)

    def test_бледно_серый_по_крему_это_брак(self):
        """Приглушённый серый по светлому — ровно то, ради чего порог 8:1."""
        с = tempfile.TemporaryDirectory()
        путь = кадр_с_текстом(Path(с.name), "01.png", "#A6A29C", "#F2EFE8")
        self.assertGreater(замер.кадр(путь)["слабых_доля"], 0.15)

    def test_точечная_примесь_картинки_не_делает_брака(self):
        """Тёмный значок рядом с текстом даёт слабые пиксели, но кадр остаётся годным."""
        с = tempfile.TemporaryDirectory()
        путь = кадр_с_текстом(Path(с.name), "01.png", "#12130E", "#F1F2EA")
        и = Image.open(путь)
        ImageDraw.Draw(и).ellipse([700, 900, 860, 1060], fill="#6E6A64")   # значок, не буква
        и.save(путь)
        self.assertLess(замер.кадр(путь)["слабых_доля"], 0.15)


class Строки(unittest.TestCase):
    def test_кегли_и_перепад(self):
        """Заголовок 150 px и подпись 46 px дают два уровня кегля и заметный перепад."""
        с = tempfile.TemporaryDirectory()
        путь = кадр_с_текстом(Path(с.name), "01.png", "#12130E", "#F1F2EA")
        д = замер.кадр(путь)
        self.assertEqual(len(д["кегли"]), 2)
        self.assertGreater(д["перепад"], 2.0)

    def test_снимок_экрана_не_считается_строкой(self):
        """Широкий снимок интерфейса на пол-кадра — картинка. Попав в строки, он выдаёт
        «крупную строку» в 40% высоты и перепад кеглей в сотню раз."""
        с = tempfile.TemporaryDirectory()
        путь = кадр_с_текстом(Path(с.name), "01.png", "#1B3487", "#F2EFE8")
        и = Image.open(путь)
        и.paste(Image.effect_noise((900, 560), 60).convert("RGB"), (90, 760))
        и.save(путь)
        кегли = замер.кадр(путь)["кегли"]
        self.assertTrue(all(к < 0.2 for к in кегли), f"в строки попал снимок: {кегли}")


class Карусель(unittest.TestCase):
    def test_ровный_ритм_это_брак(self):
        """Семь одинаково светлых кадров сливаются в превью-сетке профиля."""
        с = tempfile.TemporaryDirectory()
        for н in range(1, 8):
            кадр_с_текстом(Path(с.name), f"{н:02d}.png", "#12130E", "#F2EFE8")
        отчёт = замер.карусель(Path(с.name))
        self.assertIn("брак", отчёт)
        self.assertIn("ритм", отчёт)

    def test_тёмные_по_краям_ритм_в_порядке(self):
        """Т-С-С-С-Т: чередование есть, про ритм отчёт молчит."""
        с = tempfile.TemporaryDirectory()
        for н in range(1, 6):
            тёмный = н in (1, 5)
            кадр_с_текстом(Path(с.name), f"{н:02d}.png",
                           "#F2EFE8" if тёмный else "#12130E",
                           "#12130E" if тёмный else "#F2EFE8")
        self.assertNotIn("ритм", замер.карусель(Path(с.name)))


if __name__ == "__main__":
    unittest.main()
