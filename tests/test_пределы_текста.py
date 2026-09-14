# -*- coding: utf-8 -*-
"""Схема и задание называют модели одни и те же пределы.

Они разошлись: поле схемы говорило «заголовок до 24, мысль 35-50», а текст
задания — «до 38, мысль 45-84». Модель получала два ответа на один вопрос.
Верны меньшие: они мерены на готовых кадрах.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import carousel  # noqa: E402


class Пределы(unittest.TestCase):
    def test_схема_и_задание_согласны(self):
        заголовок = carousel.Слайд.model_fields["заголовок"].description
        мысль = carousel.Слайд.model_fields["текст"].description
        от, до = carousel.МЫСЛЬ
        self.assertIn(f"до {carousel.ЗАГОЛОВОК_ДО} символов", заголовок)
        self.assertIn(f"{от}-{до} символов", мысль)
        self.assertIn(f"Заголовок до {carousel.ЗАГОЛОВОК_ДО} символов", carousel.ЗАДАЧА)
        self.assertIn(f"мысль на {от}-{до} символов", carousel.ЗАДАЧА)

    def test_старых_чисел_нет(self):
        self.assertNotIn("45-84", carousel.ЗАДАЧА)
        self.assertNotIn("до 38 символов", carousel.ЗАДАЧА)
