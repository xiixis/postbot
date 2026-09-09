# -*- coding: utf-8 -*-
"""Числа для раздела «Вышло»: недели и итоги.

Неделя считается в питоне, а не запросом: у sqlite и постгреса разный
синтаксис усечения даты, и один и тот же отчёт разошёлся бы между машиной
владельца и облаком — причём молча.
"""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_история import _База                         # noqa: E402


def _дней_назад(н: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=н)).isoformat(
        timespec="seconds")


class Недели(unittest.TestCase):
    def test_пустая_база_даёт_нули_а_не_пустоту(self):
        """График из нулей честнее, чем отсутствие графика: провал в выпуске
        это тоже сведения."""
        import db
        with _База():
            ряды = db.по_неделям(недель=4)
            self.assertEqual(len(ряды), 4)
            self.assertEqual([р["штук"] for р in ряды], [0, 0, 0, 0])

    def test_посты_ложатся_в_свои_недели(self):
        import db
        with _База() as б:
            б.добавить(id=1, published_at=_дней_назад(1), views=100)
            б.добавить(id=2, published_at=_дней_назад(2), views=200)
            б.добавить(id=3, published_at=_дней_назад(20))
            ряды = db.по_неделям(недель=6)
            self.assertEqual(sum(р["штук"] for р in ряды), 3)

    def test_средний_охват_недели(self):
        """Среднее считается только по постам, у которых числа есть: пост без
        охвата не должен тянуть среднее к нулю."""
        import db
        with _База() as б:
            б.добавить(id=1, published_at=_дней_назад(0), views=100)
            б.добавить(id=2, published_at=_дней_назад(0), views=200)
            б.добавить(id=3, published_at=_дней_назад(0))
            ряды = db.по_неделям(недель=1)
            self.assertEqual(ряды[-1]["штук"], 3)
            self.assertEqual(ряды[-1]["охват"], 150)

    def test_недели_идут_от_старой_к_свежей(self):
        import db
        with _База():
            метки = [р["неделя"] for р in db.по_неделям(недель=3)]
            self.assertEqual(метки, sorted(метки))

    def test_черновики_в_недели_не_попадают(self):
        import db
        with _База() as б:
            б.добавить(id=1, status="draft", published_at=None)
            self.assertEqual(sum(р["штук"] for р in db.по_неделям(недель=4)), 0)


class Итоги(unittest.TestCase):
    def test_пустая_база(self):
        import db
        with _База():
            и = db.итоги()
            self.assertEqual(и["всего"], 0)
            self.assertEqual(и["охват30"], 0)
            self.assertEqual(и["с_числами"], 0)

    def test_считает_окна_и_охваты(self):
        import db
        with _База() as б:
            б.добавить(id=1, published_at=_дней_назад(1), views=100)
            б.добавить(id=2, published_at=_дней_назад(10), views=200)
            б.добавить(id=3, published_at=_дней_назад(40), views=50)
            и = db.итоги()
            self.assertEqual(и["за7"], 1)
            self.assertEqual(и["за30"], 2)
            self.assertEqual(и["всего"], 3)
            self.assertEqual(и["охват30"], 150)
            self.assertEqual(и["охват_прошлые30"], 50)
            self.assertEqual(и["с_числами"], 3)

    def test_черновики_не_считаются(self):
        import db
        with _База() as б:
            б.добавить(id=1, status="draft", published_at=None)
            self.assertEqual(db.итоги()["всего"], 0)

    def test_без_охватов_нули_а_не_падение(self):
        """У владельца база с первого выпуска: там есть посты без чисел."""
        import db
        with _База() as б:
            б.добавить(id=1, published_at=_дней_назад(3))
            и = db.итоги()
            self.assertEqual(и["за7"], 1)
            self.assertEqual(и["охват30"], 0)
            self.assertEqual(и["с_числами"], 0)


if __name__ == "__main__":
    unittest.main()
