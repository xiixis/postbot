# -*- coding: utf-8 -*-
"""Заголовки безопасности у выложенного приложения.

Второй эшелон обороны. Первый — экранирование, но оно держится на том, что
никто не забыл позвать «экр»; забыть легко, а CSP не забывает. Смысл строгой
политики ровно один: внедрённый обработчик события вроде onmouseover не
выполнится, даже если разметка всё-таки протекла.
"""

import json
import sys
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))


def _настройки() -> dict:
    """Настройки Vercel такими, какими их пишет сборщик."""
    import tools_vercel
    return json.loads(tools_vercel.НАСТРОЙКИ)


def _заголовки() -> dict:
    """Заголовки для всех путей, именем к значению."""
    for правило in _настройки().get("headers", []):
        if правило.get("source") in ("/(.*)", "/:path*"):
            return {з["key"]: з["value"] for з in правило["headers"]}
    raise AssertionError("в настройках нет правила заголовков на все пути")


class Политика(unittest.TestCase):
    def test_политика_есть(self):
        self.assertIn("Content-Security-Policy", _заголовки())

    def test_чужой_скрипт_не_запустится(self):
        """Ради этого всё и затевалось: без «unsafe-inline» браузер не
        исполнит ни внедрённый <script>, ни атрибут-обработчик."""
        правила = _заголовки()["Content-Security-Policy"]
        скрипты = [ч for ч in правила.split(";") if ч.strip().startswith("script-src")]
        self.assertEqual(len(скрипты), 1, правила)
        self.assertNotIn("unsafe-inline", скрипты[0])
        self.assertNotIn("unsafe-eval", скрипты[0])

    def test_свой_скрипт_и_телеграм_разрешены(self):
        скрипты = [ч for ч in _заголовки()["Content-Security-Policy"].split(";")
                   if ч.strip().startswith("script-src")][0]
        self.assertIn("'self'", скрипты)
        self.assertIn("https://telegram.org", скрипты)

    def test_чужая_рамка_и_подмена_основы_закрыты(self):
        правила = _заголовки()["Content-Security-Policy"]
        self.assertIn("frame-ancestors", правила)
        self.assertIn("base-uri 'none'", правила)
        self.assertIn("object-src 'none'", правила)

    def test_остальные_заголовки(self):
        з = _заголовки()
        self.assertEqual(з.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("Referrer-Policy", з)


class Настройки(unittest.TestCase):
    def test_переписывание_адресов_на_месте(self):
        """Заголовки не должны вытеснить то, ради чего файл существует."""
        н = _настройки()
        self.assertEqual(н["regions"], ["dub1"])
        self.assertTrue(н["rewrites"])


if __name__ == "__main__":
    unittest.main()
