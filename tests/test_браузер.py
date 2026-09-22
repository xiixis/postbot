# -*- coding: utf-8 -*-
"""Прогретый браузер: те же замеры и снимки, что у командной строки, и без утечек."""
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card     # noqa: E402
import config   # noqa: E402
import браузер  # noqa: E402

ПАПКА = Path(__file__).resolve().parent / "эталоны" / "пост96"
ОПИСЬ = json.loads((ПАПКА / "замеры.json").read_text(encoding="utf-8"))


def эталон(имя: str) -> str:
    return (ПАПКА / имя).read_text(encoding="utf-8").replace("file://{{АССЕТЫ}}", config.АССЕТЫ.as_uri())


@contextmanager
def без_тёплого():
    было = os.environ.get("ТЁПЛЫЙ_ХРОМ")
    os.environ["ТЁПЛЫЙ_ХРОМ"] = "0"
    try:
        yield
    finally:
        if было is None:
            os.environ.pop("ТЁПЛЫЙ_ХРОМ", None)
        else:
            os.environ["ТЁПЛЫЙ_ХРОМ"] = было


@unittest.skipUnless(config.хром(), "нужен Chrome")
class Тёплый(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        with браузер._замок:
            браузер._погасить()

    def test_замер_как_у_командной_строки(self):
        for к in ОПИСЬ["кадры"][:3]:
            with self.subTest(кадр=к["файл"]):
                стр = эталон(к["файл"])
                тёплый = браузер.замерить(стр + card.ЗАМЕР, к["ширина"], к["высота"])
                with без_тёплого():
                    холодный = card._замерить_заново(стр, к["ширина"], к["высота"])
                self.assertEqual(тёплый, холодный)

    def test_снимок_как_у_командной_строки(self):
        import numpy as np
        from PIL import Image
        к = ОПИСЬ["кадры"][1]
        стр = эталон(к["файл"])
        with tempfile.TemporaryDirectory() as т:
            тёплый = Path(т) / "тёплый.png"
            self.assertTrue(браузер.снять(стр, к["ширина"], к["высота"], тёплый))
            with без_тёплого():
                холодный = card._снять(стр, к["ширина"], к["высота"])
            А = np.asarray(Image.open(тёплый).convert("RGB")).astype(int)
            Б = np.asarray(Image.open(холодный).convert("RGB")).astype(int)
            Path(холодный).unlink()
        self.assertEqual(А.shape, (round(к["высота"] * 1.5), round(к["ширина"] * 1.5), 3))
        self.assertEqual(А.shape, Б.shape)
        self.assertLess((np.abs(А - Б).max(axis=2) > 8).mean(), 0.01)

    def test_гаснет_после_простоя_и_поднимается_снова(self):
        к = ОПИСЬ["кадры"][0]
        стр = эталон(к["файл"]) + card.ЗАМЕР
        self.assertTrue(браузер.замерить(стр, к["ширина"], к["высота"]))
        было = браузер.ПРОСТОЙ
        браузер.ПРОСТОЙ = 0
        try:
            time.sleep(0.05)
            self.assertTrue(браузер._погасить_если_простаивает())
            self.assertIsNone(браузер._браузер["процесс"])
        finally:
            браузер.ПРОСТОЙ = было
        self.assertTrue(браузер.замерить(стр, к["ширина"], к["высота"]))

    def test_две_нити_разом(self):
        кадры, итоги = ОПИСЬ["кадры"][:2], {}

        def мерить(к):
            итоги[к["файл"]] = браузер.замерить(
                эталон(к["файл"]) + card.ЗАМЕР, к["ширина"], к["высота"])

        нити = [threading.Thread(target=мерить, args=(к,)) for к in кадры]
        for н in нити:
            н.start()
        for н in нити:
            н.join(60)
        for к in кадры:
            self.assertEqual(итоги[к["файл"]]["текст"], к["замер"]["текст"])

    def test_после_падения_браузер_поднимается(self):
        к = ОПИСЬ["кадры"][0]
        стр = эталон(к["файл"]) + card.ЗАМЕР
        self.assertTrue(браузер.замерить(стр, к["ширина"], к["высота"]))
        браузер._браузер["процесс"].kill()
        браузер._браузер["процесс"].wait(10)
        self.assertEqual(браузер.замерить(стр, к["ширина"], к["высота"])["холст"],
                         к["замер"]["холст"])


@unittest.skipUnless(браузер.включён(), "нужен Chrome")
class ОшибкиСтраницы(unittest.TestCase):
    """Ошибки страницы доходят до снимка, а не теряются в протоколе."""

    def test_снимок_сообщает_об_ошибке_страницы(self):
        ошибки = []
        with tempfile.TemporaryDirectory() as папка:
            куда = Path(папка) / "к.png"
            self.assertTrue(браузер.снять(
                '<meta charset="utf-8"><script>нет_такого()</script><p>x</p>',
                400, 300, куда, ошибки))
        self.assertTrue(any("нет_такого" in е for е in ошибки), ошибки)

    def test_чистая_страница_без_ошибок(self):
        ошибки = []
        with tempfile.TemporaryDirectory() as папка:
            куда = Path(папка) / "к.png"
            self.assertTrue(браузер.снять('<meta charset="utf-8"><p>чисто</p>',
                                          400, 300, куда, ошибки))
        self.assertEqual(ошибки, [])

    def test_эталонный_кадр_без_ошибок(self):
        к = ОПИСЬ["кадры"][0]
        ошибки = []
        with tempfile.TemporaryDirectory() as папка:
            self.assertTrue(браузер.снять(эталон(к["файл"]), к["ширина"], к["высота"],
                                          Path(папка) / "к.png", ошибки))
        self.assertEqual(ошибки, [])
