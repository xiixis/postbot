# -*- coding: utf-8 -*-
"""Папка «Посты» задаётся в одном месте и на любой ОС.

Раньше путь `~/Desktop/Посты` был зашит в четырёх файлах, переопределить его можно было
только в одном, а на Windows рабочий стол бывает перенесён в OneDrive — тогда выпуск
складывал посты в одну папку, а черновик TikTok искал их в другой (аудит 25.09.2026).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config                                                # noqa: E402


class ПапкаПостов(unittest.TestCase):
    def setUp(self):
        self.было_env = os.environ.pop("ВЫГРУЗКА_ПАПКА", None)
        self.был_стол = config.рабочий_стол

    def tearDown(self):
        os.environ.pop("ВЫГРУЗКА_ПАПКА", None)
        if self.было_env is not None:
            os.environ["ВЫГРУЗКА_ПАПКА"] = self.было_env
        config.рабочий_стол = self.был_стол

    def test_переменная_главнее(self):
        os.environ["ВЫГРУЗКА_ПАПКА"] = "~/где-то/посты"
        self.assertEqual(config.папка_постов(), Path("~/где-то/посты").expanduser())

    def test_посты_на_рабочем_столе(self):
        with tempfile.TemporaryDirectory() as стол:
            config.рабочий_стол = lambda: Path(стол)
            self.assertEqual(config.папка_постов(), Path(стол) / "Посты")

    def test_без_стола_в_данные(self):
        config.рабочий_стол = lambda: Path("/нет/такого/стола")
        self.assertEqual(config.папка_постов(), config.ДАННЫЕ / "выгрузка")

    def test_все_пользуются_одной_папкой(self):
        """Выпуск, выгрузка бота и черновик TikTok смотрят в одну и ту же папку."""
        sys.path.insert(0, str(Path(config.КОРЕНЬ) / "Style"))
        import выгрузка
        import стиль
        import tools_черновик
        self.assertEqual(стиль.СТОЛ, config.папка_постов())
        self.assertEqual(выгрузка.ПАПКА, config.папка_постов())
        self.assertEqual(tools_черновик.СТОЛ, config.папка_постов())

    @unittest.skipUnless(sys.platform == "win32", "реестр рабочего стола есть только в Windows")
    def test_windows_берёт_стол_из_реестра(self):
        стол = config.рабочий_стол()
        self.assertTrue(стол.is_dir(), f"рабочий стол из реестра не найден: {стол}")


if __name__ == "__main__":
    unittest.main()
