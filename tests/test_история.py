# -*- coding: utf-8 -*-
"""Лента вышедшего: страницы, поиск и отбор.

База у владельца живёт в Ирландии, и лента не может приезжать целиком. Значит
страницы и отбор считает сама база, а не клиент.

Стенд нарочно переключает `ПОСТГРЕС` в ложь. Настройки на машине владельца
указывают на облачную базу, обёртка по этому признаку заменяет «?» на «%s», и
тест против sqlite падал бы на первом же запросе — причём с ошибкой синтаксиса,
по которой ни за что не догадаешься, что дело в чужих настройках.
"""

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class _База:
    """Свежая база в памяти на каждый тест."""

    def __enter__(self):
        import db
        self.db = db
        self.было_постгрес = db.ПОСТГРЕС
        db.ПОСТГРЕС = False
        self.связь = sqlite3.connect(":memory:")
        self.связь.row_factory = sqlite3.Row
        # Тот же самый «lower», что и у настоящей базы: копия прививки
        # разошлась бы с оригиналом в первый же день.
        db.привить(self.связь)
        self.было = db.соединение
        db.соединение = self._дать
        for запрос in db.СХЕМА:
            # Схема собрана под облако: там номера раздаёт SERIAL, здесь его нет.
            self.связь.execute(запрос.replace("SERIAL PRIMARY KEY",
                                              "INTEGER PRIMARY KEY AUTOINCREMENT"))
        for имя, тип in db.ДОБАВКИ:
            try:
                self.связь.execute(f"ALTER TABLE posts ADD COLUMN {имя} {тип}")
            except sqlite3.OperationalError:
                pass                                  # колонка уже в схеме
        return self

    def _дать(self):
        внешний = self

        class Держатель:
            def __enter__(self_):
                return внешний.db._Связь(внешний.связь)

            def __exit__(self_, *_):
                внешний.связь.commit()
        return Держатель()

    def добавить(self, **поля):
        поля.setdefault("rubric", "разбор")
        поля.setdefault("title", "Заголовок")
        поля.setdefault("body", "Текст")
        поля.setdefault("status", "published")
        поля.setdefault("created_at", "2026-09-01T10:00:00")
        поля.setdefault("published_at", "2026-09-01T10:00:00")
        ключи = ", ".join(поля)
        места = ", ".join("?" for _ in поля)
        self.связь.execute(
            f"INSERT INTO posts ({ключи}) VALUES ({места})", tuple(поля.values()))
        self.связь.commit()

    def __exit__(self, *_):
        self.db.соединение = self.было
        self.db.ПОСТГРЕС = self.было_постгрес
        self.связь.close()


class Лента(unittest.TestCase):
    def test_страница_и_общее_число(self):
        import db
        with _База() as б:
            for н in range(5):
                б.добавить(title=f"Пост {н}", id=н + 1)
            ряды, всего = db.история(смещение=0, сколько=2)
            self.assertEqual(всего, 5)
            self.assertEqual([р["title"] for р in ряды], ["Пост 4", "Пост 3"])
            вторые, _ = db.история(смещение=2, сколько=2)
            self.assertEqual([р["title"] for р in вторые], ["Пост 2", "Пост 1"])

    def test_черновики_в_ленту_не_попадают(self):
        import db
        with _База() as б:
            б.добавить(title="Вышел", id=1)
            б.добавить(title="Черновик", id=2, status="draft", published_at=None)
            ряды, всего = db.история()
            self.assertEqual(всего, 1)
            self.assertEqual(ряды[0]["title"], "Вышел")

    def test_поиск_по_заголовку_без_регистра(self):
        import db
        with _База() as б:
            б.добавить(title="Пенсия и налоги", id=1)
            б.добавить(title="Совсем другое", id=2)
            ряды, всего = db.история(запрос="ПЕНСИЯ")
            self.assertEqual(всего, 1)
            self.assertEqual(ряды[0]["title"], "Пенсия и налоги")

    def test_процент_в_запросе_ничего_не_ломает(self):
        """Процент в поиске — обычный знак, а не подстановка."""
        import db
        with _База() as б:
            б.добавить(title="Скидка 50%", id=1)
            б.добавить(title="Без скидки", id=2)
            _, всего = db.история(запрос="50%")
            self.assertEqual(всего, 1)

    def test_отбор_по_рубрике(self):
        import db
        with _База() as б:
            б.добавить(title="Раз", id=1, rubric="разбор")
            б.добавить(title="Два", id=2, rubric="новость")
            _, всего = db.история(рубрика="новость")
            self.assertEqual(всего, 1)

    def test_площадка_телеграм_и_руками(self):
        """Ручную публикацию от нашей отличает пустой tg_message_id."""
        import db
        with _База() as б:
            б.добавить(title="Через бота", id=1, tg_message_id=17)
            б.добавить(title="Руками", id=2, link="https://tiktok.com/x")
            тг, сколько_тг = db.история(площадка="телеграм")
            рук, сколько_рук = db.история(площадка="руками")
            self.assertEqual(сколько_тг, 1)
            self.assertEqual(тг[0]["title"], "Через бота")
            self.assertEqual(сколько_рук, 1)
            self.assertEqual(рук[0]["title"], "Руками")

    def test_отбор_по_сроку(self):
        import db
        from datetime import datetime, timedelta, timezone
        свежо = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(
            timespec="seconds")
        давно = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(
            timespec="seconds")
        with _База() as б:
            б.добавить(title="Свежий", id=1, published_at=свежо)
            б.добавить(title="Старый", id=2, published_at=давно)
            _, всего = db.история(дней=30)
            self.assertEqual(всего, 1)

    def test_ручной_пост_виден_при_отборе_по_каналу(self):
        """У выложенного руками канала нет вовсе: строгое равенство выкинуло
        бы его из ленты совсем, как это уже было в «для_экрана»."""
        import db
        with _База() as б:
            б.добавить(title="В канале", id=1, channel="@главный")
            б.добавить(title="Руками", id=2, channel=None)
            _, всего = db.история(канал="@главный")
            self.assertEqual(всего, 2)

    def test_сколько_ограничено_сверху(self):
        """Клиент не должен уметь попросить всю базу одним запросом."""
        import db
        with _База() as б:
            for н in range(3):
                б.добавить(title=f"П{н}", id=н + 1)
            ряды, _ = db.история(сколько=10_000)
            self.assertLessEqual(len(ряды), db.ПРЕДЕЛ_ЛЕНТЫ)


if __name__ == "__main__":
    unittest.main()
