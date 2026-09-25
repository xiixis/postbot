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


def доска(папка: Path, файл: str, тело: str) -> None:
    """Синтетическая доска: шапка и шрифты эталонной, внутри корня — только `тело`."""
    html = (ЭТАЛОНЫ / "A-Main.dc.html").read_text(encoding="utf-8")
    начало = html.index(">", html.index('<div style="width: 1080px')) + 1
    конец = html.index("</div>\n</x-dc>")
    (папка / файл).write_text(html[:начало] + тело + html[конец:], encoding="utf-8")


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


class ПоТексту(unittest.TestCase):
    """Проверка 1, без браузера: оценка строк крупного текста по ширине знака."""

    @classmethod
    def setUpClass(cls):
        import приёмка_досок
        cls.п = приёмка_досок

    def беды(self, имя: str) -> list[str]:
        return self.п.по_тексту((ЭТАЛОНЫ / f"{имя}.dc.html").read_text(encoding="utf-8"))

    def test_годные_без_бед(self):
        for д in снять_доски.доски(ЭТАЛОНЫ):
            if "bityi" not in д["file"]:
                with self.subTest(д["file"]):
                    self.assertEqual(self.беды(д["file"].removesuffix(".dc.html")), [])

    def test_заголовок_финала_в_три_строки(self):
        беды = self.беды("A-bityi-final-3-stroki")
        self.assertEqual(len(беды), 1, беды)
        self.assertIn("≈3 строки", беды[0])
        self.assertIn("Claude", беды[0])          # сосед — список замен

    def test_подпись_на_заголовке(self):
        беды = self.беды("B-bityi-pod-na-zagolovke")
        self.assertTrue(any("Ролик" in б for б in беды), беды)

    def test_разбор_стиля(self):
        с = self.п._свойства("left: 80px; top: 112px; width: 640px; font-family: Onest, 'Arial Black';"
                             " font-size: 80px; line-height: 1.0;")
        self.assertEqual((с["left"], с["top"], с["width"], с["font-size"], с["line-height"]),
                         (80, 112, 640, 80, 1.0))
        self.assertEqual(с["семья"], "Onest")


def беды_с(беды: list[str], слово: str) -> list[str]:
    return [б for б in беды if б.startswith(слово)]


@unittest.skipUnless(config.хром(), "нужен Chrome")
class Разметка(unittest.TestCase):
    """Проверка 2: общий замер запаса на верхних блоках доски и зона кнопок TikTok."""

    @classmethod
    def setUpClass(cls):
        import приёмка_досок
        cls.п = приёмка_досок

    def беды(self, имя: str) -> list[str]:
        return self.п.по_разметке(ЭТАЛОНЫ, f"{имя}.dc.html")

    def test_годные_проходят(self):
        """Кадры и главные обложки обоих постов 24.09 — какими их выпустили, с правкой брака,
        найденного этой же приёмкой (вывод под плашкой, кот на списке)."""
        годные = [д["file"] for д in снять_доски.доски(ЭТАЛОНЫ) if "bityi" not in д["file"]]
        self.assertEqual(len(годные), 14)
        for файл in годные:
            with self.subTest(файл):
                self.assertEqual(self.п.по_разметке(ЭТАЛОНЫ, файл), [])

    def test_кот_у_правого_края_под_кнопками(self):
        """Финал «пар» 3b4e57c: кот стоял `right: 20px` — его закрывала колонка лайков."""
        беды = беды_с(self.беды("A-bityi-kot-u-kraya"), "под кнопками TikTok")
        self.assertEqual(len(беды), 1, беды)
        self.assertIn("кот", беды[0])

    def test_кот_запасной_обложки_тоже(self):
        self.assertTrue(беды_с(self.беды("B-bityi-kot-u-kraya"), "под кнопками TikTok"))

    def test_штамп_за_краем(self):
        """Обложка «списание» a602efa: штамп «Отменено» вылез за правый край."""
        беды = беды_с(self.беды("A-bityi-otmeneno-za-kraem"), "у края")
        self.assertTrue(any("Отменено" in б for б in беды), беды)

    def test_вывод_под_плашкой(self):
        """Кадр 4 до правки: строка вывода в 4 px от плашки «не платим уже»."""
        беды = беды_с(self.беды("A-bityi-vyvod-pod-plashkoy"), "впритык")
        self.assertTrue(any("не платим" in б for б in беды), беды)

    def test_кот_вплотную_к_списку(self):
        беды = беды_с(self.беды("A-bityi-kot-na-spiske"), "впритык")
        self.assertTrue(any("кот" in б for б in беды), беды)

    def test_подпись_на_заголовке(self):
        self.assertTrue(беды_с(self.беды("B-bityi-pod-na-zagolovke"), "впритык"))

    def test_фон_и_сетка_не_блоки(self):
        """Сетка и градиент во весь кадр лежат под всем — с ними «налезает» любой блок."""
        for б in self.беды("A-bityi-kot-u-kraya"):
            self.assertNotIn(" -1080", б)

    def test_повёрнутый_блок_по_контуру(self):
        """Лента, повёрнутая на 7°: описанный прямоугольник на ~150 px выше контура."""
        # Лента 920×120 с центром (540, 360), повёрнута на −7°: правый край поднят, низ
        # идёт от (91, 476) до (1004, 364). Плашка справа (x 700–1000) на 470: по описанному
        # прямоугольнику налезает, по контуру низ ленты там ≈ 400 — зазор ~70. Плашка слева
        # (x 80–300) на 476 — прямо под опущенным краем, зазор ≈ 0: настоящая беда.
        папка = холст_из("A-Main")
        доска(папка, "lenta.dc.html",
              '<div class="лента" style="position: absolute; left: 80px; top: 300px; width: 920px; '
              'height: 120px; background: #333; transform: rotate(-7deg);"></div>'
              '<div class="справа" style="position: absolute; left: 700px; top: 470px; width: 300px; '
              'height: 60px; background: #C7E24B;"></div>'
              '<div class="слева" style="position: absolute; left: 80px; top: 476px; width: 220px; '
              'height: 60px; background: #C7E24B;"></div>')
        беды = беды_с(self.п.по_разметке(папка, "lenta.dc.html"), "впритык")
        self.assertFalse([б for б in беды if "справа" in б], беды)
        self.assertTrue([б for б in беды if "слева" in б], беды)


class Отчёт(unittest.TestCase):
    """Итог в форме `приёмка.py`: одинаково показывается у бота и у стилей."""

    def test_без_снимка_только_текст(self):
        import приёмка
        import приёмка_досок
        отчёт = приёмка_досок.проверить(холст_из("A-Main", "A-bityi-final-3-stroki"), снимки=False)
        self.assertFalse(приёмка.годен(отчёт))
        self.assertEqual(приёмка.бракованные(отчёт), [2])
        self.assertTrue(приёмка.строкой(отчёт).startswith("№2: «Вся замена"))
        self.assertEqual(отчёт["кадры"][1]["доска"], "A-bityi-final-3-stroki.dc.html")
        self.assertNotIn("лист", отчёт)

    def test_команда_без_снимка(self):
        import subprocess
        папка = холст_из("A-Main", "A-bityi-final-3-stroki")
        р = subprocess.run([sys.executable, str(КОРЕНЬ / "Style" / "приёмка_досок.py"), str(папка.parent),
                            "--без-снимка"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(р.returncode, 1, р.stderr)
        self.assertIn("брак: №2:", р.stdout)


@unittest.skipUnless(config.хром(), "нужен Chrome")
class ОтчётПолный(unittest.TestCase):
    def test_разметка_снимок_и_лист(self):
        import приёмка
        import приёмка_досок
        отчёт = приёмка_досок.проверить(холст_из("B-Kadr02", "B-bityi-kot-u-kraya"))
        self.assertEqual(приёмка.бракованные(отчёт), [2])
        self.assertIn("под кнопками TikTok: кот", приёмка.строкой(отчёт))
        self.assertTrue(Path(отчёт["лист"]).exists())
        # Нормы вкуса из замера снимка — замечания, а не брак.
        self.assertTrue(all(isinstance(з, str) for к in отчёт["кадры"] for з in к["замечания"]))

    def test_годные_проходят_все_три_проверки(self):
        """Снимок ловит то, чего не видит разметка: при выводе шириной 560 кадр 4 «пар» лёг
        в четыре строки и сел на знак, а по разметке был чист."""
        import приёмка
        import приёмка_досок
        годные = [д["file"].removesuffix(".dc.html") for д in снять_доски.доски(ЭТАЛОНЫ)
                  if "bityi" not in д["file"]]
        отчёт = приёмка_досок.проверить(холст_из(*годные))
        self.assertTrue(приёмка.годен(отчёт), приёмка.строкой(отчёт))


if __name__ == "__main__":
    unittest.main()
