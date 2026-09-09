# -*- coding: utf-8 -*-
"""Мини-приложение: экранирование и синтаксис скрипта страницы.

Страница собирает разметку строками и вставляет её через innerHTML, так что
единственная защита от чужого текста — функция «экр». Проверяем её настоящую,
вырезанную из index.html и выполненную в node: копия в тесте разошлась бы с
оригиналом ровно в тот день, когда оригинал сломают.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent
ПАПКА = КОРЕНЬ / "webapp"
СТРАНИЦА = ПАПКА / "index.html"
NODE = shutil.which("node")


ФАЙЛЫ = ["core.js", "sheets.js", "screens.js", "app.js"]


def _скрипт() -> str:
    """Все скрипты страницы одной строкой, в порядке подключения.

    Один файл вырос до без малого двух тысяч строк, и его разложили по
    четырём. Проверка обязана смотреть на все: иначе «экр» переедет в
    соседний файл, а тест будет искать его в старом и не найдёт.
    """
    return "\n".join((ПАПКА / имя).read_text(encoding="utf-8")
                     for имя in ФАЙЛЫ)


def _прогнать(выражение: str) -> str:
    """Выполняет выражение рядом с «экр» и отдаёт напечатанное."""
    # До следующей строки верхнего уровня: обрывать по «;» нельзя, точка с
    # запятой стоит внутри самих сущностей вроде «&amp;».
    объявление = re.search(r"^const экр = .*?(?=^\S)", _скрипт(), re.M | re.S)
    if not объявление:
        raise AssertionError("на странице не нашлось объявления «экр»")
    итог = subprocess.run(
        [NODE, "-e", объявление.group(0) + f"\nconsole.log({выражение});"],
        capture_output=True, text=True, timeout=20)
    if итог.returncode:
        raise AssertionError(итог.stderr.strip())
    return итог.stdout.strip()


@unittest.skipIf(NODE is None, "node не установлен")
class Экранирование(unittest.TestCase):
    def test_угловые_скобки(self):
        self.assertEqual(_прогнать('экр("<img src=x>")'),
                         "&lt;img src=x&gt;")

    def test_двойная_кавычка(self):
        self.assertEqual(_прогнать('экр(\'бе"да\')'), "бе&quot;да")

    def test_одинарная_кавычка(self):
        """Атрибуты сегодня в двойных кавычках, но защита не должна от этого
        зависеть: одна правка разметки — и дыра открыта молча."""
        self.assertEqual(_прогнать('экр("бе\'да")'), "бе&#x27;да")

    def test_амперсанд_первым(self):
        """Иначе «&lt;» получилось бы из уже экранированного «&»."""
        self.assertEqual(_прогнать('экр("&lt;")'), "&amp;lt;")

    def test_пустота_не_роняет(self):
        self.assertEqual(_прогнать("экр(null)"), "")


class БезИнлайна(unittest.TestCase):
    """Строгая CSP держится на том, что своего кода в странице нет.

    Стоит вернуть один <script> внутрь разметки — и он молча перестанет
    исполняться: браузер откажет по политике, а на глаз страница будет
    выглядеть просто пустой.
    """

    def test_своих_скриптов_в_разметке_нет(self):
        разметка = СТРАНИЦА.read_text(encoding="utf-8")
        свои = [т for т in re.findall(r"<script[^>]*>", разметка)
                if "src=" not in т]
        self.assertEqual(свои, [])

    def test_блоков_стиля_в_разметке_нет(self):
        разметка = СТРАНИЦА.read_text(encoding="utf-8")
        self.assertNotIn("<style", разметка)

    def test_страница_ссылается_на_свои_файлы(self):
        разметка = СТРАНИЦА.read_text(encoding="utf-8")
        self.assertIn('href="app.css"', разметка)
        self.assertTrue((ПАПКА / "app.css").exists())
        for имя in ФАЙЛЫ:
            self.assertIn(f'src="{имя}"', разметка)
            self.assertTrue((ПАПКА / имя).exists())

    def test_порядок_подключения_соблюдён(self):
        """core объявляет то, чем пользуются остальные, а app запускает всё.
        Перепутанный порядок ломает страницу молча: она просто пустая."""
        разметка = СТРАНИЦА.read_text(encoding="utf-8")
        места = [разметка.index(f'src="{имя}"') for имя in ФАЙЛЫ]
        self.assertEqual(места, sorted(места))

    def test_файлы_страницы_уезжают_в_сборку(self):
        """Сборщик берёт из webapp всё, кроме черновиков с «_» в начале."""
        import sys
        sys.path.insert(0, str(КОРЕНЬ))
        import tools_vercel
        едут = {ф.name for ф in sorted(ПАПКА.iterdir())
                if ф.is_file() and not ф.name.startswith("_")}
        self.assertLessEqual({"index.html", "app.css", *ФАЙЛЫ}, едут)
        self.assertTrue(tools_vercel.ЦЕЛЬ.name)


@unittest.skipIf(NODE is None, "node не установлен")
class СинтаксисСтраницы(unittest.TestCase):
    def test_каждый_скрипт_разбирается(self):
        """Ошибка в скрипте не видна на глаз: страница просто перестаёт
        исполняться, и приложение показывает пустоту."""
        for имя in ФАЙЛЫ:
            with self.subTest(файл=имя):
                итог = subprocess.run(
                    [NODE, "--check", "-"],
                    input=(ПАПКА / имя).read_text(encoding="utf-8"),
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(итог.returncode, 0, итог.stderr.strip())

    def test_модулей_нет(self):
        """`node --check` читает поток как обычный скрипт: «import» наверху
        файла уронил бы проверку, а вместе с ней и всю защиту от опечаток.

        Обычные скрипты делят между собой глобальные объявления верхнего
        уровня — именно на этом и держится разбиение на четыре файла."""
        for имя in ФАЙЛЫ:
            текст = (ПАПКА / имя).read_text(encoding="utf-8")
            self.assertNotRegex(текст, r"(?m)^\s*(import|export)\s")

    def test_объявления_не_повторяются(self):
        """Одно и то же имя верхнего уровня в двух файлах — это SyntaxError
        на весь набор, и страница не исполнится вовсе."""
        видели = {}
        for имя in ФАЙЛЫ:
            текст = (ПАПКА / имя).read_text(encoding="utf-8")
            for объявление in re.findall(
                    r"(?m)^(?:const|let|function)\s+([^\s(=,]+)", текст):
                self.assertNotIn(
                    объявление, видели,
                    f"«{объявление}» объявлено и в {видели.get(объявление)},"
                    f" и в {имя}")
                видели[объявление] = имя


if __name__ == "__main__":
    unittest.main()
