# -*- coding: utf-8 -*-
"""Рабочая папка поста: открыть, а если её удалили — собрать заново.

Главное ограничение здесь не в коде, а в том, где что лежит. Приложение
работает в облаке, а папка — на маке владельца. Облако не может ни увидеть
её, ни открыть: у него нет ни этого диска, ни Finder. Значит проверяет и
открывает мак, по заданию, а приложение только просит.

Поэтому кнопка показывается всегда, когда у поста есть слайды, и никогда не
обещает, что папка на месте: узнать это заранее неоткуда.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api                                                   # noqa: E402


class _Подмена:
    def __init__(self, модуль, **что):
        self.модуль, self.что, self.было = модуль, что, {}

    def __enter__(self):
        for имя, зн in self.что.items():
            self.было[имя] = getattr(self.модуль, имя, None)
            setattr(self.модуль, имя, зн)
        return self

    def __exit__(self, *_):
        for имя, зн in self.было.items():
            setattr(self.модуль, имя, зн)


class ИмяПапки(unittest.TestCase):
    """Имя должно получаться одинаковым и на маке, и в облаке: по нему мак
    находит папку, собранную когда-то раньше."""

    def test_из_номера_площадки_и_заголовка(self):
        import выгрузка
        self.assertEqual(
            выгрузка._имя_папки(88, "Хватит платить за устаревший ИИ", "tiktok"),
            "88-tiktok-Хватит-платить-за-устаревший-ИИ")

    def test_знаки_препинания_выкидываются(self):
        import выгрузка
        имя = выгрузка._имя_папки(7, "Что делать, если стаж «потерян»?", "tiktok")
        self.assertNotIn(",", имя)
        self.assertNotIn("«", имя)
        self.assertTrue(имя.startswith("7-tiktok-"))

    def test_без_заголовка_остаётся_узнаваемым(self):
        import выгрузка
        self.assertEqual(выгрузка._имя_папки(5, "", "tiktok"), "5-tiktok")


class ОткрытьПапку(unittest.TestCase):
    def setUp(self):
        import выгрузка
        self.в = выгрузка
        self.ряд = {"id": 88, "title": "Хватит платить за устаревший ИИ"}

    def test_папка_на_месте_заново_не_собирается(self):
        """Пересобирать существующую папку — значит стереть её и скачать всё
        заново из Supabase. Человек ждёт открытия, а не загрузки."""
        import db
        собирали = []
        with _Подмена(self.в, ПАПКА=Path("/tmp/нет-такой"),
                      собрать=lambda *а, **к: собирали.append(а) or {},
                      открыть_папку=lambda п: True), \
             _Подмена(db, взять=lambda ид: self.ряд):
            папка = self.в.ПАПКА / self.в._имя_папки(88, self.ряд["title"], "tiktok")
            папка.mkdir(parents=True, exist_ok=True)
            (папка / "01.jpg").write_bytes(b"x")
            try:
                итог = self.в.открыть(88, "tiktok")
            finally:
                import shutil
                shutil.rmtree(self.в.ПАПКА, ignore_errors=True)
        self.assertTrue(итог["была"])
        self.assertEqual(собирали, [])

    def test_папки_нет_собираем_заново(self):
        import db
        собирали = []

        def собрать(ид, куда="tiktok"):
            собирали.append(ид)
            папка = self.в.ПАПКА / self.в._имя_папки(ид, self.ряд["title"], куда)
            папка.mkdir(parents=True, exist_ok=True)
            return {"папка": папка, "файлы": [], "подпись": "", "название": ""}

        with _Подмена(self.в, ПАПКА=Path("/tmp/нет-такой-2"), собрать=собрать,
                      открыть_папку=lambda п: True), \
             _Подмена(db, взять=lambda ид: self.ряд):
            try:
                итог = self.в.открыть(88, "tiktok")
            finally:
                import shutil
                shutil.rmtree(self.в.ПАПКА, ignore_errors=True)
        self.assertFalse(итог["была"])
        self.assertEqual(собирали, [88])

    def test_пустая_папка_считается_отсутствующей(self):
        """Папка есть, а файлов в ней нет — открывать нечего, это то же
        самое, что её удалили."""
        import db
        собирали = []

        def собрать(ид, куда="tiktok"):
            собирали.append(ид)
            return {"папка": self.в.ПАПКА / "x", "файлы": [], "подпись": "",
                    "название": ""}

        with _Подмена(self.в, ПАПКА=Path("/tmp/нет-такой-3"), собрать=собрать,
                      открыть_папку=lambda п: True), \
             _Подмена(db, взять=lambda ид: self.ряд):
            папка = self.в.ПАПКА / self.в._имя_папки(88, self.ряд["title"], "tiktok")
            папка.mkdir(parents=True, exist_ok=True)
            try:
                итог = self.в.открыть(88, "tiktok")
            finally:
                import shutil
                shutil.rmtree(self.в.ПАПКА, ignore_errors=True)
        self.assertFalse(итог["была"])
        self.assertEqual(собирали, [88])

    def test_поста_нет_говорим_прямо(self):
        import db
        with _Подмена(db, взять=lambda ид: None):
            with self.assertRaises(ValueError):
                self.в.открыть(999, "tiktok")


class Маршрут(unittest.TestCase):
    def test_мак_спит_папку_открыть_некому(self):
        import jobs
        with _Подмена(jobs, мак_жив=lambda: False):
            код, тело = api.обработать("/api/folder", {"id": 88}, 1)
        self.assertEqual(код, 409)
        self.assertIn("мак", тело["error"])

    def test_мак_жив_задание_уходит(self):
        import jobs
        поймано = {}
        with _Подмена(jobs, мак_жив=lambda: True,
                      поставить=lambda вид, д: поймано.update(вид=вид, **д) or "к1"):
            код, тело = api.обработать("/api/folder",
                                       {"id": 88, "куда": "tiktok"}, 1)
        self.assertEqual(код, 200)
        self.assertEqual(тело["job"], "к1")
        self.assertEqual(поймано["вид"], "папка")
        self.assertEqual(поймано["id"], 88)

    def test_чужая_площадка_не_проходит(self):
        import jobs
        поймано = {}
        with _Подмена(jobs, мак_жив=lambda: True,
                      поставить=lambda вид, д: поймано.update(**д) or "к1"):
            api.обработать("/api/folder", {"id": 88, "куда": "instagram"}, 1)
        self.assertEqual(поймано["куда"], "tiktok")


if __name__ == "__main__":
    unittest.main()
