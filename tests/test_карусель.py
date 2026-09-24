# -*- coding: utf-8 -*-
"""Одна команда сборки карусели: снабжение, обложки, сборка, приёмка, параметры выкладки.

Ловит до сборки то, что раньше всплывало на холсте: нет значка или позы кота, запасная
обложка без поля, неизвестный макет, та же пара запасных, что у прошлого поста стиля.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(КОРЕНЬ))
sys.path.insert(0, str(КОРЕНЬ / "Style"))

import карусель  # noqa: E402

ПАРЫ = КОРЕНЬ / "Style" / "пары"
ПОСТ_А = ПАРЫ / "посты" / "платно-бесплатно.json"


def стиль_во_временной(пост: dict, соседи: dict | None = None) -> Path:
    """Папка стиля во временном каталоге: рисовальщик-пустышка, значки, посты."""
    папка = Path(tempfile.mkdtemp()) / "стиль"
    (папка / "посты").mkdir(parents=True)
    (папка / "значки").mkdir()
    (папка / "значки" / "est.png").write_bytes(b"png")
    (папка / "категории.py").write_text("print('годен')\n")
    for имя, п in (соседи or {}).items():
        (папка / "посты" / f"{имя}.json").write_text(json.dumps(п, ensure_ascii=False))
    путь = папка / "посты" / "проба.json"
    путь.write_text(json.dumps(пост, ensure_ascii=False))
    return путь


ЗАПАСНЫЕ = {"замена": {"строки": ["а", "б"], "под": "в", "было": "$1"},
            "число": {"число": "5", "строки": ["а", "б"], "под": "в", "плашка": "г", "поза": "ukazyvaet"}}


class Снабжение(unittest.TestCase):
    def test_находит_нехватку(self):
        путь = стиль_во_временной({"вид": "категории", "кадры": [{"платно": {"файл": "est.png"},
                                                                  "бесплатно": {"файл": "nety.png"}}],
                                   "финал": {"поза": "nety-pozy"}, "обложка": {"сцена": "nety-sceny"}})
        беды = карусель.снабжение(json.loads(путь.read_text()), путь.parent.parent)
        self.assertEqual(len(беды), 3, беды)
        self.assertTrue(any("nety.png" in б and "значок" in б for б in беды))
        self.assertTrue(any("nety-pozy" in б and "поза" in б for б in беды))
        self.assertTrue(any("nety-sceny" in б and "сцена" in б for б in беды))

    def test_старый_путь_сцены_от_стиля(self):
        путь = стиль_во_временной({"обложка": {"сцена": "картинки/нет.png"}})
        беды = карусель.снабжение(json.loads(путь.read_text()), путь.parent.parent)
        self.assertEqual(len(беды), 1)
        self.assertIn("картинки/нет.png", беды[0])


class Обложки(unittest.TestCase):
    def test_годные(self):
        путь = стиль_во_временной({"запасные": ЗАПАСНЫЕ})
        беды, предупреждения = карусель.обложки_поста(json.loads(путь.read_text()), путь)
        self.assertEqual((беды, предупреждения), ([], []))

    def test_одна_запасная_и_чужой_макет(self):
        беды, _ = карусель.обложки_поста({"запасные": {"веер": {}}}, ПОСТ_А)
        self.assertTrue(any("ровно две" in б for б in беды), беды)
        self.assertTrue(any("нет макета «веер»" in б for б in беды), беды)

    def test_нет_поля(self):
        беды, _ = карусель.обложки_поста({"запасные": {**ЗАПАСНЫЕ, "число": {"число": "5"}}}, ПОСТ_А)
        self.assertTrue(any("«число»: нет поля «строки»" in б for б in беды), беды)

    def test_та_же_пара_что_у_соседа(self):
        путь = стиль_во_временной({"запасные": ЗАПАСНЫЕ}, соседи={"прошлый": {"запасные": ЗАПАСНЫЕ}})
        _, предупреждения = карусель.обложки_поста(json.loads(путь.read_text()), путь)
        self.assertEqual(len(предупреждения), 1)
        self.assertIn("прошлый", предупреждения[0])


class Рисовальщик(unittest.TestCase):
    def test_по_полю_вид(self):
        путь = стиль_во_временной({"вид": "категории"})
        self.assertEqual(карусель.рисовальщик({"вид": "категории"}, путь.parent.parent).name, "категории.py")

    def test_нет_рисовальщика(self):
        путь = стиль_во_временной({})
        with self.assertRaises(SystemExit) as с:
            карусель.рисовальщик({"вид": "нету"}, путь.parent.parent)
        self.assertIn("категории", str(с.exception))


@unittest.skipUnless((ПАРЫ / "значки" / "claude.png").exists() and (ПАРЫ / "картинки" / "kot-chek.png").exists(),
                     "нет значков и сцены поста 24.09 (они вне git)")
class Команда(unittest.TestCase):
    def test_пост_24_09_без_снимка(self):
        р = subprocess.run([sys.executable, str(КОРЕНЬ / "Style" / "карусель.py"), str(ПОСТ_А), "--без-снимка"],
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(р.returncode, 0, р.stdout[-800:] + р.stderr[-800:])
        self.assertIn("годен", р.stdout)
        self.assertIn("KVY4guCxa7niTvSCgh7xsv", р.stdout)          # ссылка на холст из поста
        self.assertIn("project/canvas.json", р.stdout)


if __name__ == "__main__":
    unittest.main()
