# -*- coding: utf-8 -*-
"""Облачная копия не должна отставать от исходников.

Зачем. Vercel собирает ровно то, что лежит в `vercel/` в git, а кладёт туда
модули только `tools_vercel.py`. Правило «правишь модуль — пересобери» было
записано в скиле `postbot-ревизия`, но держалось на памяти и не сработало:
21.09.2026 аудит нашёл, что `vercel/db.py` отстал на неделю — в облаке не было
таблицы референсов, — а `vercel/config.py` не подтягивал ключи команды. Бот и
облако работали разным кодом, и ничто об этом не говорило.

Теперь говорит этот тест.
"""
import sys
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))

import tools_vercel  # noqa: E402


class ОблачнаяКопия(unittest.TestCase):
    def test_каждый_модуль_совпадает_с_исходником(self):
        отстали = []
        for имя in tools_vercel.МОДУЛИ:
            исходник, копия = КОРЕНЬ / имя, КОРЕНЬ / "vercel" / имя
            self.assertTrue(исходник.exists(), f"нет исходника {имя}")
            if not копия.exists():
                отстали.append(f"{имя}: копии нет вовсе")
            elif исходник.read_bytes() != копия.read_bytes():
                отстали.append(имя)
        self.assertEqual(отстали, [],
                         "облачная копия отстала — запустить `python3 tools_vercel.py` "
                         "и закоммитить vercel/ вместе с правкой")

    def test_страница_приложения_тоже_уехала(self):
        """webapp уезжает в public целиком, кроме файлов с подчёркиванием (стенд)."""
        ждём = {ф.name for ф in (КОРЕНЬ / "webapp").iterdir()
                if ф.is_file() and not ф.name.startswith("_")}
        есть = {ф.name for ф in (КОРЕНЬ / "vercel" / "public").iterdir() if ф.is_file()}
        self.assertEqual(ждём - есть, set(), "в облачной странице не хватает файлов webapp")


if __name__ == "__main__":
    unittest.main()
