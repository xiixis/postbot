# -*- coding: utf-8 -*-
"""Карусель пишется сразу голосом хуманайзера, второго прохода по подписи нет."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import carousel   # noqa: E402
import humanizer  # noqa: E402
import writer     # noqa: E402
import агент      # noqa: E402


class ОдинПроход(unittest.TestCase):
    def setUp(self):
        self.было = []

    def подменить(self, модуль, имя, значение):
        self.было.append((модуль, имя, getattr(модуль, имя)))
        setattr(модуль, имя, значение)

    def tearDown(self):
        for модуль, имя, значение in reversed(self.было):
            setattr(модуль, имя, значение)

    def сочинить(self, площадка="tiktok"):
        пойманное = {}

        def по_форме(задача, форма, система="", **к):
            пойманное["система"] = система
            return carousel.Карусель.model_construct(
                topic="т", каркас="", cover_kicker="н", cover_title="з", slides=[],
                closing="в", caption="Живая подпись под каруселью. #ии",
                запасные_заголовки=[], название="н", hashtags=["#ии"], поза="privet")

        def нельзя(*а, **к):
            raise AssertionError("второй проход хуманайзера не нужен")

        self.подменить(агент, "по_форме", по_форме)
        self.подменить(humanizer, "очеловечить", нельзя)
        for имя in ("_факты", "_значки"):
            self.подменить(writer, имя, lambda *а, **к: "")
        for имя in ("_чужой_опыт", "_подсмотренное", "_позы"):
            self.подменить(carousel, имя, lambda *а, **к: "")
        return carousel.сочинить("тема", [], "", площадка, False), пойманное

    def test_голос_хуманайзера_в_подсказке(self):
        _, пойманное = self.сочинить()
        self.assertIn(humanizer.ГОЛОС, пойманное["система"])

    def test_подпись_tiktok_без_второго_прохода(self):
        к, _ = self.сочинить()
        self.assertIn("Живая подпись", к.caption)

    def test_подпись_телеграма_без_второго_прохода(self):
        к, _ = self.сочинить("телеграм")
        self.assertIn("Живая подпись", к.caption)
