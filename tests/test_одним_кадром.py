# -*- coding: utf-8 -*-
"""Пост из одной картинки: паспорт, запрос к модели, отрисовка, выкладка."""
import random
import unittest
from unittest import mock

import carousel
import форматы


class ПаспортТипа(unittest.TestCase):
    def test_тип_есть_и_просит_один_кадр(self):
        о = форматы.ТИПЫ["одним кадром"]
        self.assertEqual(о["кадров"], [1, 1])
        self.assertFalse(о["кот"], "коту на плотном кадре места нет")
        self.assertEqual(о["каркасы"], [], "пути мысли здесь нет")

    def test_паспорт_несёт_вёрстку(self):
        """Один кадр собирается плотной вёрсткой, а не «мыслью»."""
        случай = random.Random(3)
        паспорта = [форматы.подобрать([], случай) for _ in range(200)]
        одним = [п for п in паспорта if п["тип"] == "одним кадром"]
        self.assertTrue(одним, "тип ни разу не выпал")
        for п in одним:
            self.assertIn(п["вид"], форматы.ТИПЫ["одним кадром"]["виды"])

    def test_выпадает_реже_обычной(self):
        случай = random.Random(11)
        типы = [форматы.подобрать([], случай)["тип"] for _ in range(2000)]
        доля = типы.count("одним кадром") / len(типы)
        self.assertLess(доля, 0.2, "один кадр не должен идти каждым третьим")
        self.assertGreater(доля, 0.05, "иначе он не выйдет вовсе")

    def test_у_обычной_вида_нет(self):
        случай = random.Random(5)
        обычные = [п for п in (форматы.подобрать([], случай) for _ in range(60))
                   if п["тип"] == "обычная"]
        self.assertTrue(обычные)
        self.assertNotIn("вид", обычные[0], "вёрстку слайдов выбирает модель")


class ЗапросКМодели(unittest.TestCase):
    ПАСПОРТ = {"тип": "одним кадром", "каркас": "", "кадров": [1, 1],
               "дизайн": "фирменный", "оформление": "чистый", "кот": False,
               "вид": "шпаргалка"}

    def test_узнаётся_по_числу_кадров(self):
        self.assertTrue(carousel.одним_кадром(self.ПАСПОРТ))
        self.assertFalse(carousel.одним_кадром({"кадров": [8, 12]}))
        self.assertFalse(carousel.одним_кадром(None))

    def test_модели_сказано_про_один_кадр_и_вёрстку(self):
        текст = carousel._формат(self.ПАСПОРТ)
        self.assertIn("ОДИН КАДР", текст)
        self.assertIn("шпаргалка", текст)
        self.assertIn("обложки и отдельного итога нет", текст)
        self.assertNotIn("каркас:", текст)


class Отрисовка(unittest.TestCase):
    ДАННЫЕ = {
        "паспорт": {"тип": "одним кадром", "кадров": [1, 1], "кот": False,
                    "дизайн": "фирменный", "оформление": "чистый",
                    "вид": "шпаргалка"},
        "cover_title": "", "cover_kicker": "", "closing": "",
        "slides": [{"вид": "шпаргалка", "заголовок": "Чем работать",
                    "строки": ["Тексты: Claude длинный; ChatGPT правки"]}],
    }

    def test_рисуется_ровно_один_кадр_без_обложки_и_итога(self):
        with mock.patch("card.слайд_вида", return_value="/тмп/кадр.png") as вид, \
             mock.patch("card.слайд_обложка") as обложка, \
             mock.patch("card.слайд_финал") as финал:
            файлы = carousel.нарисовать(self.ДАННЫЕ, формат="тикток")
        self.assertEqual(файлы, ["/тмп/кадр.png"])
        обложка.assert_not_called()
        финал.assert_not_called()
        self.assertEqual(вид.call_args.args[2:4], (1, 1),
                         "кадр номер один из одного")

    def test_кота_на_таком_кадре_нет(self):
        with mock.patch("card.слайд_вида", return_value="/тмп/кадр.png") as вид:
            carousel.нарисовать(self.ДАННЫЕ, формат="тикток")
        self.assertEqual(вид.call_args.args[6], "нет")

    def test_обычная_карусель_рисуется_по_прежнему(self):
        данные = {**self.ДАННЫЕ,
                  "паспорт": {"тип": "обычная", "кадров": [8, 12], "кот": True},
                  "cover_title": "Заголовок", "closing": "Итог"}
        with mock.patch("card.слайд_вида", return_value="/тмп/с.png"), \
             mock.patch("card.слайд_обложка", return_value="/тмп/о.png") as обложка, \
             mock.patch("card.слайд_финал", return_value="/тмп/ф.png") as финал:
            файлы = carousel.нарисовать(данные, формат="тикток")
        обложка.assert_called_once()
        финал.assert_called_once()
        self.assertEqual(len(файлы), 3)


class ВыкладкаВТелеграм(unittest.TestCase):
    """Группа из одной картинки телеграму не годится: он требует от двух."""

    def test_одна_картинка_уходит_снимком(self):
        import telegram
        with mock.patch.object(telegram, "фото", return_value={"ok": 1}) as фото:
            telegram.альбом(1, ["/тмп/один.png"], "подпись")
        фото.assert_called_once()

    def test_несколько_картинок_уходят_группой(self):
        import telegram
        with mock.patch.object(telegram, "_вызвать", return_value=[{}]) as зов, \
             mock.patch("builtins.open", mock.mock_open(read_data=b"x")):
            telegram.альбом(1, ["/тмп/а.png", "/тмп/б.png"], "подпись")
        self.assertEqual(зов.call_args.args[0], "sendMediaGroup")


if __name__ == "__main__":
    unittest.main()
