# -*- coding: utf-8 -*-
"""Часовой пояс — по имени на любой ОС, иначе после перевода часов посты уезжают на час."""

import importlib
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import times                                                 # noqa: E402


class Пояс(unittest.TestCase):
    def setUp(self):
        self.было = {к: os.environ.get(к) for к in ("POSTBOT_TZ", "TZ")}

    def tearDown(self):
        for к, в in self.было.items():
            os.environ.pop(к, None)
            if в is not None:
                os.environ[к] = в
        importlib.reload(times)

    def test_postbot_tz_главнее_tz(self):
        os.environ["POSTBOT_TZ"], os.environ["TZ"] = "Europe/Kyiv", "Asia/Tokyo"
        self.assertEqual(str(times._зона()), "Europe/Kyiv")

    def test_зона_по_имени_на_этой_машине(self):
        """Без переменных зона всё равно находится по имени (мак — ссылка, Windows — tzlocal)."""
        os.environ.pop("POSTBOT_TZ", None)
        os.environ.pop("TZ", None)
        self.assertIsNotNone(times._зона(), "имя зоны не нашлось — бот жил бы на застывшем смещении")

    def test_перевод_часов_учитывается(self):
        os.environ["POSTBOT_TZ"] = "Europe/Kyiv"
        зона = times._зона()
        лето = datetime(2026, 9, 25, 12, tzinfo=timezone.utc).astimezone(зона).utcoffset()
        зима = datetime(2026, 11, 25, 12, tzinfo=timezone.utc).astimezone(зона).utcoffset()
        self.assertNotEqual(лето, зима)


if __name__ == "__main__":
    unittest.main()
