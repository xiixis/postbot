# -*- coding: utf-8 -*-
"""Вызов модели без обвеса Claude Code.

Замер 14 сентября 2026: вопрос «Столица Франции?» с прежними флагами стоил
17 130 токенов входа. Туда уходили описания инструментов, которые список
запретов не закрывал, и все CLAUDE.md с памятью — бот запускается из папки
проекта. `--tools ""` и `--setting-sources ""` оставили 471 токен. Писатель с
гуманизатором на Opus: 43,3 тыс. токенов входа против 10,5 тыс., голос и счёт
следов нейросети те же.

Модель здесь не зовётся: тест сторожит состав команды.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import агент  # noqa: E402


def _после(команда: list, флаг: str):
    return команда[команда.index(флаг) + 1]


class БезОбвеса(unittest.TestCase):
    def test_инструментов_нет_вовсе(self):
        команда, _ = агент._команда("claude", "задача", "система", "opus",
                                    None, "", None)
        self.assertEqual(_после(команда, "--tools"), "")
        self.assertNotIn("--disallowedTools", команда,
                         "список запретов не закрывает всех инструментов")

    def test_настройки_и_память_не_грузятся(self):
        команда, _ = агент._команда("claude", "задача", "система", "opus",
                                    None, "", None)
        self.assertEqual(_после(команда, "--setting-sources"), "")
        self.assertIn("--no-session-persistence", команда)

    def test_картинкам_достаётся_только_чтение(self):
        команда, задача = агент._команда("claude", "разбери", "", "", None, "",
                                         ["/tmp/слайд.png"])
        self.assertEqual(_после(команда, "--tools"), "Read")
        self.assertEqual(_после(команда, "--allowedTools"), "Read")
        self.assertIn("/tmp/слайд.png", задача)

    def test_модель_усердие_система_и_схема_на_месте(self):
        команда, _ = агент._команда("claude", "задача", "голос", "sonnet",
                                    {"type": "object"}, "low", None)
        self.assertEqual(_после(команда, "--model"), "sonnet")
        self.assertEqual(_после(команда, "--effort"), "low")
        self.assertEqual(_после(команда, "--system-prompt"), "голос")
        self.assertIn('"object"', _после(команда, "--json-schema"))


if __name__ == "__main__":
    unittest.main()
