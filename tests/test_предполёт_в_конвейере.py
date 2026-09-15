# -*- coding: utf-8 -*-
"""Предполёт стоит в конвейере: эскиз и дорисовка не пускают сломанную вёрстку.

Эскиз — новый текст, его ещё никто не видел, и модели можно один раз
переложить сломанный слайд. Дорисовка рисует текст, который владелец видел и
мог поправить: там модель не зовётся, вёрстка чинится без неё.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import carousel   # noqa: E402
import придирки   # noqa: E402
import форматы    # noqa: E402
import предполёт  # noqa: E402
from test_эскиз import _Дублёры, _Карусель  # noqa: E402

ПАСПОРТ = {"тип": "обычная", "каркас": "разбор", "кадров": [8, 12],
           "дизайн": "каталог", "оформление": "чистый", "кот": False}
БЫЛО = {"вид": "было", "заголовок": "Было и стало", "текст": "", "значение": "",
        "реплика": "", "строки": ["Руками два часа", "С ИИ пять минут"]}


class _СБедой(_Карусель):
    def model_dump(self):
        return {"cover_title": self.cover_title, "closing": "", "поза": self.поза,
                "slides": [dict(БЫЛО)]}


class Довести(unittest.TestCase):
    def setUp(self):
        self.было = carousel.переверстать
        self.звали = []
        carousel.переверстать = lambda к, отчёт, формат: self.звали.append(1) or к

    def tearDown(self):
        carousel.переверстать = self.было

    def test_годная_не_зовёт_модель(self):
        к = {"slides": [], "паспорт": dict(ПАСПОРТ)}
        _, отчёт = предполёт.довести(к, "3к4", модель=True)
        self.assertTrue(отчёт["годен"])
        self.assertEqual(self.звали, [])

    def test_без_модели_чинит_сама(self):
        к = {"slides": [dict(БЫЛО)], "паспорт": dict(ПАСПОРТ)}
        новая, отчёт = предполёт.довести(к, "3к4")
        self.assertEqual(self.звали, [])
        self.assertEqual(новая["slides"][0]["вид"], "мысль")
        self.assertTrue(отчёт["годен"])
        self.assertEqual(отчёт["исправлено"], ["№2: «было» → «мысль»"])

    def test_с_моделью_сперва_модель_потом_починка(self):
        к = {"slides": [dict(БЫЛО)], "паспорт": dict(ПАСПОРТ)}
        новая, отчёт = предполёт.довести(к, "3к4", модель=True)
        self.assertEqual(self.звали, [1])
        self.assertTrue(отчёт["годен"])


class ВКонвейере(unittest.TestCase):
    def setUp(self):
        self.было = (форматы.следующий, carousel.переверстать)
        форматы.следующий = lambda куда: dict(ПАСПОРТ)
        self.модель = []
        carousel.переверстать = lambda к, отчёт, формат: self.модель.append(1) or к

    def tearDown(self):
        форматы.следующий, carousel.переверстать = self.было

    def test_эскиз_кладёт_починенную_карусель_и_отчёт(self):
        with _Дублёры() as д:
            carousel.сочинить = lambda *а, **к: _СБедой()
            д.core.эскиз(None, площадка="tiktok")
        карточка = д.положено["карточка"]
        self.assertEqual(карточка["carousel"]["slides"][0]["вид"], "мысль")
        self.assertTrue(карточка["предполёт"]["годен"])
        self.assertEqual(self.модель, [1], "в эскизе модели дают один проход")

    def test_дорисовка_чинит_без_модели_и_рисует_починенное(self):
        карточка = {"carousel": {"поза": "privet", "slides": [dict(БЫЛО)],
                                 "паспорт": dict(ПАСПОРТ)},
                    "формат": "3к4", "стадия": "эскиз"}
        нарисовано = []
        with _Дублёры() as д:
            import db
            db.взять = lambda ид: {"id": ид,
                                   "card": json.dumps(карточка, ensure_ascii=False)}
            carousel.нарисовать = lambda к, *а, **кв: нарисовано.append(
                к["slides"][0]["вид"]) or ["/tmp/слайд.png"]
            д.core.дорисовать(42)
        сохранено = json.loads(д.положено["card"])
        self.assertEqual(нарисовано, ["мысль"])
        self.assertEqual(сохранено["carousel"]["slides"][0]["вид"], "мысль")
        self.assertIn("исправлено", сохранено["предполёт"])
        self.assertEqual(self.модель, [], "дорисовка не зовёт модель")


class Придирки(unittest.TestCase):
    def test_показывает_исправленное_и_замечания(self):
        поля = {"предполёт": {"годен": True, "исправлено": ["№2: «было» → «мысль»"],
                              "кадры": [{"номер": 4, "вид": "мысль", "беды": [],
                                         "замечания": ["заголовок длинный"]}]}}
        self.assertEqual(придирки._предполёт(поля),
                         ["до отрисовки поправлено: №2: «было» → «мысль»",
                          "предполёт: №4: заголовок длинный"])

    def test_без_отчёта_молчит(self):
        self.assertEqual(придирки._предполёт({}), [])


if __name__ == "__main__":
    unittest.main()
