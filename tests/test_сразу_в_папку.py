# -*- coding: utf-8 -*-
"""Готовая карусель сразу лежит в папке на рабочем столе.

Раньше папку собирала кнопка «Забрать»: пост дорисован и лежит готовый, а
файлов на столе нет, пока их не попросишь. Владелец выкладывает TikTok руками,
и шаг «нажми, чтобы получить уже готовое» ничего не добавлял — только
забывался. Так пост 88 ушёл в TikTok, а папку с его слайдами пришлось
восстанавливать задним числом.

Теперь папка складывается сама — в момент, когда кадры готовы, — и
обновляется при каждой правке: папка со старыми слайдами хуже, чем никакой,
её легко выложить по ошибке. Только для площадок, которые выкладываются
руками: телеграм публикует бот, и папка для него была бы мусором.
"""

import inspect
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_история import _База                         # noqa: E402


class _Подмена:
    """Подменяет имена в модуле на время проверки."""

    def __init__(self, модуль, **что):
        self.модуль, self.что, self.было = модуль, что, {}

    def __enter__(self):
        for имя, зн in self.что.items():
            self.было[имя] = getattr(self.модуль, имя)
            setattr(self.модуль, имя, зн)
        return self

    def __exit__(self, *_):
        for имя, зн in self.было.items():
            setattr(self.модуль, имя, зн)


# Как у станков по умолчанию: TikTok выкладывает человек, телеграм — бот.
РЕЖИМЫ = {"tiktok": {"режим": "руками"}, "телеграм": {"режим": "сам"}}


class Сразу(unittest.TestCase):
    """Для каких площадок складывать папку и что при этом не делать."""

    def _прогнать(self, куда, собрать=None, ряд=None):
        import db
        import publish
        import выгрузка
        import конвейер
        вызовы, открывали = [], []

        def своё_собрать(ид, к="tiktok"):
            вызовы.append((ид, к))
            return {"папка": Path(f"/tmp/нет-{ид}-{к}"), "файлы": [],
                    "подпись": "", "название": ""}

        есть = ряд if ряд is not None else {"id": 88, "title": "Т", "card": None}
        with _Подмена(db, взять=lambda ид: есть), \
             _Подмена(publish, куда_едет=lambda р: куда), \
             _Подмена(конвейер, настройки=lambda к="tiktok":
                      РЕЖИМЫ.get(к, {"режим": "сам"})), \
             _Подмена(выгрузка, собрать=собрать or своё_собрать,
                      открыть_папку=lambda п: открывали.append(п) or True):
            итог = выгрузка.сразу(88)
        return итог, вызовы, открывали

    def test_ручная_площадка_получает_папку(self):
        итог, вызовы, _ = self._прогнать(["tiktok"])
        self.assertEqual(вызовы, [(88, "tiktok")])
        self.assertEqual(len(итог), 1)

    def test_телеграм_папку_не_получает(self):
        """Телеграм публикует бот сам: папка для него только мусорит стол."""
        итог, вызовы, _ = self._прогнать(["телеграм"])
        self.assertEqual(вызовы, [])
        self.assertEqual(итог, [])

    def test_две_площадки_папка_только_у_ручной(self):
        _, вызовы, _ = self._прогнать(["телеграм", "tiktok"])
        self.assertEqual(вызовы, [(88, "tiktok")])

    def test_finder_не_открывается(self):
        """Автопилот рисует и ночью. Окно Finder среди ночи — не помощь."""
        _, _, открывали = self._прогнать(["tiktok"])
        self.assertEqual(открывали, [])

    def test_сбой_выгрузки_не_роняет(self):
        """Папка — удобство. Из-за неё не должен падать сам пост."""
        def падает(*_, **__):
            raise ValueError("у поста нет картинок")

        итог, _, _ = self._прогнать(["tiktok"], собрать=падает)
        self.assertEqual(итог, [])

    def test_поста_нет_пусто(self):
        import db
        import выгрузка
        with _Подмена(db, взять=lambda ид: None):
            self.assertEqual(выгрузка.сразу(999), [])


class СтараяПапка(unittest.TestCase):
    """Имя папки содержит заголовок. Сменился заголовок — сменилось и имя,
    и прежняя папка того же поста осталась бы сиротой со старыми слайдами."""

    def test_после_смены_заголовка_прежняя_папка_уходит(self):
        import db
        import storage
        import варианты
        import выгрузка
        корень = Path(tempfile.mkdtemp())
        try:
            старая = корень / "88-tiktok-Старый-заголовок"
            чужой_пост = корень / "8-tiktok-Другой-пост"
            другая_площадка = корень / "88-x-Тот-же-пост"
            for п in (старая, чужой_пост, другая_площадка):
                п.mkdir()
                (п / "01.jpg").write_bytes(b"x")
            исходник = корень / "исходник.jpg"
            исходник.write_bytes(b"img")

            with _Подмена(выгрузка, ПАПКА=корень), \
                 _Подмена(db, взять=lambda ид: {"id": 88,
                                                "title": "Новый заголовок"}), \
                 _Подмена(варианты, получить=lambda ид, куда: {
                     "images": ["https://x/1.jpg"], "body": "подпись",
                     "title": ""}), \
                 _Подмена(storage, во_временный=lambda с: str(исходник)):
                итог = выгрузка.собрать(88, "tiktok")

            self.assertFalse(старая.exists())
            self.assertTrue(чужой_пост.exists(), "пост 8 — не пост 88")
            self.assertTrue(другая_площадка.exists())
            self.assertEqual(итог["папка"].name, "88-tiktok-Новый-заголовок")
            self.assertTrue((итог["папка"] / "01.jpg").exists())
            self.assertTrue((итог["папка"] / "подпись.txt").exists())
        finally:
            shutil.rmtree(корень, ignore_errors=True)


class Дорисовка(unittest.TestCase):
    """Точка, где карусель становится готовой: кадры записаны в базу."""

    def _карусель(self, б, ид=5):
        б.добавить(id=ид, status="draft", published_at=None,
                   card=json.dumps({"carousel": {"поза": ""}, "формат": "3к4",
                                    "стадия": "эскиз", "куда": ["tiktok"]}))

    def _заглушки(self):
        import carousel
        import core
        import mascot
        import storage
        return (_Подмена(carousel, нарисовать=lambda *а, **к:
                         [Path("/tmp/a.png"), Path("/tmp/b.png")]),
                _Подмена(mascot, взять=lambda *а, **к: None),
                _Подмена(storage, положить=lambda ф: f"https://x/{Path(ф).name}"),
                _Подмена(core, _сохранить_позу=lambda п: None))

    def test_папка_складывается_когда_кадры_уже_в_базе(self):
        """Выгрузка читает слайды из базы. Позови её до записи — и в папку
        уедут прежние кадры или никаких."""
        import core
        import db
        import выгрузка
        видели = []

        def сразу(ид):
            ряд = db.взять(ид)
            видели.append((ид, json.loads(ряд["images"] or "[]")))
            return []

        with _База() as б:
            self._карусель(б)
            а, в, г, д = self._заглушки()
            with а, в, г, д, _Подмена(выгрузка, сразу=сразу):
                core.дорисовать(5)
        self.assertEqual(видели, [(5, ["https://x/a.png", "https://x/b.png"])])

    def test_сбой_папки_не_ломает_дорисовку(self):
        import core
        import db
        import выгрузка

        def падает(ид):
            raise RuntimeError("стол недоступен")

        with _База() as б:
            self._карусель(б)
            а, в, г, д = self._заглушки()
            with а, в, г, д, _Подмена(выгрузка, сразу=падает):
                self.assertEqual(core.дорисовать(5), 5)
            self.assertEqual(json.loads(db.взять(5)["images"]),
                             ["https://x/a.png", "https://x/b.png"])


class ПравкаОбновляетПапку(unittest.TestCase):
    def test_правка_текста_обновляет_папку(self):
        import core
        import выгрузка
        звали = []
        with _База() as б:
            б.добавить(id=6, status="draft", published_at=None, body="старый",
                       card=json.dumps({"куда": ["tiktok"]}))
            with _Подмена(выгрузка, сразу=lambda ид: звали.append(ид) or []):
                core.обновить(6, текст="новый текст")
        self.assertEqual(звали, [6])

    def test_пустая_правка_папку_не_трогает(self):
        """Ничего не поменялось — пересобирать нечего."""
        import core
        import выгрузка
        звали = []
        with _База() as б:
            б.добавить(id=7, status="draft", published_at=None,
                       card=json.dumps({"куда": ["tiktok"]}))
            with _Подмена(выгрузка, сразу=lambda ид: звали.append(ид) or []):
                core.обновить(7)
        self.assertEqual(звали, [])

    def test_перерисовки_и_переписывание_обновляют_папку(self):
        """Каждая дорога, по которой у поста меняются кадры или текст,
        обязана обновить папку — иначе на столе останется старая версия."""
        import core
        for ф in (core.перерисовать, core._перерисовать_карусель,
                  core.перерисовать_слайд, core.переписать):
            with self.subTest(функция=ф.__name__):
                self.assertIn("_в_папку(", inspect.getsource(ф))


if __name__ == "__main__":
    unittest.main()
