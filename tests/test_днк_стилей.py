# -*- coding: utf-8 -*-
"""Библиотека ДНК в Style/ не разъезжается с источниками.

Папку собирает `tools_днк.py` из чужих кадров и разборов, лежащих в
`исследование-тикток-карусели`. Исследование — не репозиторий: его могут
переместить или почистить, и тогда пересборка тихо отдаст пустые паспорта.
Поэтому проверяется не текст, а то, без чего ДНК перестаёт быть ДНК: у стиля
есть чужие кадры, с них сняты числа, и записано, что перенесено, а что нет.

Упал — пересобрать: `python3 tools_днк.py`.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tools_днк  # noqa: E402

ПАПКА = Path(__file__).resolve().parent.parent / "Style"


class ДНК(unittest.TestCase):
    def test_у_каждого_стиля_своя_папка_с_паспортом(self):
        for имя in list(tools_днк.СТИЛИ) + [tools_днк.ЯКОРЬ]:
            with self.subTest(имя):
                self.assertTrue((ПАПКА / имя / "ДНК.md").exists(), "нет паспорта ДНК")
                self.assertTrue((ПАПКА / имя / "днк.json").exists(), "нет чисел")

    def test_у_чужих_стилей_есть_кадры_референса(self):
        """Стиль без чужих кадров — это описание, а не ДНК: проверить по нему
        нечего, и при следующей правке источника расхождение никто не заметит."""
        for имя in tools_днк.СТИЛИ:
            with self.subTest(имя):
                кадры = list((ПАПКА / имя / "референс").glob("*.jpg"))
                self.assertTrue(кадры, "не скопированы кадры источника")

    def test_числа_сняты_а_не_пустые(self):
        for имя in tools_днк.СТИЛИ:
            with self.subTest(имя):
                д = json.loads((ПАПКА / имя / "днк.json").read_text(encoding="utf-8"))
                ср = д["днк референса"].get("среднее")
                self.assertTrue(ср, "замер не дал чисел")
                self.assertGreater(ср["контраст"], 1.0, "контраст не посчитан")
                self.assertGreater(д["днк референса"]["кадров"], 0)

    def test_среднее_считается_по_кадрам_с_текстом(self):
        """Кадр-заставка без строк даёт контраст 1,0:1 и занижает ДНК стиля."""
        for имя in tools_днк.СТИЛИ:
            with self.subTest(имя):
                д = json.loads((ПАПКА / имя / "днк.json").read_text(encoding="utf-8"))
                числа = д["днк референса"]
                с_текстом = числа.get("кадров с текстом")
                self.assertIsNotNone(с_текстом, "не записано, по скольким кадрам среднее")
                self.assertLessEqual(с_текстом, числа["кадров"])

    def test_у_источника_записан_автор_и_адрес(self):
        for имя, сведения in tools_днк.СТИЛИ.items():
            with self.subTest(имя):
                self.assertTrue(сведения["автор"], "не указан автор источника")
                self.assertTrue(сведения["адрес"], "не указан адрес источника")

    def test_перенос_записан_там_где_есть_разбор(self):
        """«Что НЕ перенесено» — единственная защита от копии чужого почерка.
        Если раздела нет, паспорт должен честно про это сказать."""
        for имя in tools_днк.СТИЛИ:
            with self.subTest(имя):
                д = json.loads((ПАПКА / имя / "днк.json").read_text(encoding="utf-8"))
                текст = (ПАПКА / имя / "ДНК.md").read_text(encoding="utf-8")
                if д["перенос"].get("не перенесено"):
                    self.assertIn("Что НЕ перенесено", текст)
                else:
                    self.assertIn("раздела про перенос", текст)

    def test_якорь_без_чужого_источника(self):
        д = json.loads((ПАПКА / tools_днк.ЯКОРЬ / "днк.json").read_text(encoding="utf-8"))
        self.assertEqual(д["источник"]["автор"], "наш")
        self.assertTrue(д["числа нашего образца"].get("среднее"), "якорь не замерен")


if __name__ == "__main__":
    unittest.main()
