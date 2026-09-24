# -*- coding: utf-8 -*-
"""Приёмка досок холста: брак, который 24.09.2026 ловился глазами, ловит код.

Сессия двух рерайтов 24.09 прошла пять кругов правок владельца, и половина кругов была
машинной: заголовок налез на список, подпись на заголовок, кот сел под кнопки TikTok.
Эталоны в `эталоны/доски/`: доски тех постов (годные — какими их выпустили, после правки
найденного здесь брака) и битые — прежние версии из истории и воспроизведённые сдвигом.
Сцены и значки в эталонах — серые заглушки: настоящие потерялись вместе с копией сессии,
а раскладке пиксели сцены не нужны.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))
sys.path.insert(0, str(КОРЕНЬ / "Style"))

import config          # noqa: E402
import снять_доски     # noqa: E402

ЭТАЛОНЫ = Path(__file__).resolve().parent / "эталоны" / "доски"


def холст_из(*доски: str) -> Path:
    """Временный холст из нескольких эталонных досок: доски, их файлы и canvas.json."""
    import json
    import re
    папка = Path(tempfile.mkdtemp()) / "холст" / "project"
    папка.mkdir(parents=True)
    индекс = {"v": 3, "boards": {}, "order": []}
    for н, имя in enumerate(доски):
        html = (ЭТАЛОНЫ / f"{имя}.dc.html").read_text(encoding="utf-8")
        for ссылка in set(re.findall(r"""(?:src=["']|url\(["']?)([^"'/:()]+\.(?:webp|png|jpe?g|svg|woff2))""", html)):
            shutil.copy(ЭТАЛОНЫ / ссылка, папка / ссылка)
        (папка / f"{имя}.dc.html").write_text(html, encoding="utf-8")
        индекс["boards"][f"{имя}.dc.html"] = {"x": н * 1160, "y": 0, "w": 1080, "h": 1440, "title": имя}
        индекс["order"].append(f"{имя}.dc.html")
    (папка / "canvas.json").write_text(json.dumps(индекс, ensure_ascii=False), encoding="utf-8")
    return папка


class СписокДосок(unittest.TestCase):
    def test_по_раскладке_и_с_запасными_обложками(self):
        доски = снять_доски.доски(ЭТАЛОНЫ)
        self.assertEqual([д["номер"] for д in доски], list(range(1, len(доски) + 1)))
        self.assertEqual([д["file"] for д in доски[:2]], ["A-Main.dc.html", "A-Kadr02.dc.html"])
        self.assertIn("B-bityi-kot-u-kraya.dc.html", [д["file"] for д in доски])
        ключи = [(д["y"], д["x"]) for д in доски]
        self.assertEqual(ключи, sorted(ключи))

    def test_папка_холста_или_project(self):
        project = холст_из("A-Main")
        self.assertEqual(снять_доски.проект(project.parent), project)
        self.assertEqual(снять_доски.проект(project), project)


class Страница(unittest.TestCase):
    def setUp(self):
        self.html = снять_доски.страница(ЭТАЛОНЫ, "A-Main.dc.html", скрипт="window.метка = 1;")

    def test_без_support_js_и_с_вшитыми_файлами(self):
        self.assertNotIn("support.js", self.html)
        self.assertNotIn('src="logo.png"', self.html)
        self.assertIn("data:image/png;base64,", self.html)
        self.assertIn("url(data:font/woff2;base64,", self.html)

    def test_кот_помечен_а_сцена_нет(self):
        self.assertIn("<img data-кот", self.html)
        сцена = снять_доски.страница(ЭТАЛОНЫ, "B-Main.dc.html")
        self.assertNotIn("data-кот", сцена)          # kot-rezhisser.jpg — сцена во весь кадр

    def test_скрипт_перед_концом_тела(self):
        self.assertIn("<script>window.метка = 1;</script></body>", self.html)


@unittest.skipUnless(config.хром(), "нужен Chrome")
class Снимки(unittest.TestCase):
    def test_все_доски_и_без_пересъёмки(self):
        from PIL import Image
        project = холст_из("A-Main", "B-bityi-kot-u-kraya")
        снимки = снять_доски.снять(project)
        self.assertEqual([с.name for с in снимки], ["01-A-Main.png", "02-B-bityi-kot-u-kraya.png"])
        with Image.open(снимки[1]) as и:
            self.assertEqual(и.size, (1620, 2160))
        было = [с.stat().st_mtime_ns for с in снимки]
        снять_доски.снять(project)
        self.assertEqual([с.stat().st_mtime_ns for с in снимки], было)


if __name__ == "__main__":
    unittest.main()
