# -*- coding: utf-8 -*-
"""Конвейер не ставит в план карусель с браком и говорит об этом владельцу."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_сразу_в_папку import _Подмена  # noqa: E402

БРАК = {"годен": False, "кадры": [{"номер": 4, "вид": "мысль",
                                    "брак": ["текст обрезан снизу: Мысль"],
                                    "замечания": [], "ужато": 0.64}]}


class Конвейер(unittest.TestCase):
    def _сделать(self, отчёт, режим="сам"):
        import core
        import db
        import конвейер
        план, доклады = [], []
        ряд = {"id": 7, "card": json.dumps({"приёмка": отчёт}, ensure_ascii=False)}
        with _Подмена(core, карусель=lambda *а, **к: 7,
                      запланировать=lambda ид, час: план.append((ид, час))), \
             _Подмена(db, взять=lambda ид: ряд), \
             _Подмена(конвейер, настройки=lambda к="tiktok": {"режим": режим},
                      следующий_угол=lambda к: ("угол", "пояснение"),
                      свободные_часы=lambda к, с: ["10:00"],
                      _доложить_брак=lambda куда, ид, о: доклады.append((куда, ид))):
            конвейер.сделать_одну("телеграм")
        return план, доклады

    def test_брак_не_ставится_в_план(self):
        план, доклады = self._сделать(БРАК)
        self.assertEqual(план, [])
        self.assertEqual(доклады, [("телеграм", 7)])

    def test_годная_ставится_в_план(self):
        план, доклады = self._сделать({"годен": True, "кадры": []})
        self.assertEqual(план, [(7, "10:00")])
        self.assertEqual(доклады, [])

    def test_брак_в_ручном_режиме_тоже_докладывается(self):
        план, доклады = self._сделать(БРАК, режим="руками")
        self.assertEqual((план, доклады), ([], [("телеграм", 7)]))


class Придирки(unittest.TestCase):
    def test_брак_первой_строкой(self):
        import придирки
        ряд = {"id": 7, "title": "Т", "body": "текст поста", "rubric": "карусель",
               "card": json.dumps({"приёмка": БРАК}, ensure_ascii=False),
               "images": None, "image_path": None}
        беды = придирки.к_посту(ряд)
        self.assertTrue(беды[0].startswith("брак кадров"), беды)
        self.assertIn("№4: текст обрезан снизу: Мысль", беды[0])

    def test_годная_без_замечания_о_браке(self):
        import придирки
        ряд = {"id": 7, "title": "Т", "body": "текст поста", "rubric": "карусель",
               "card": json.dumps({"приёмка": {"годен": True, "кадры": []}}),
               "images": None, "image_path": None}
        self.assertFalse(any(б.startswith("брак") for б in придирки.к_посту(ряд)))
