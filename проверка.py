# -*- coding: utf-8 -*-
"""Проверка перед запуском: ловит поломки, которые видно без единого вызова модели.

Зачем она есть. За один вечер бот встал четыре раза подряд, и все четыре
поломки были одного сорта: имя инструмента, которого больше нет в Claude Code;
кириллица в ключах схемы, которую перестал принимать API; функции, вызванные,
но не написанные; поле, переименованное в одном месте и не переименованное в
другом. Ни одну из них нельзя увидеть, читая код глазами, и каждая ждала до
первого живого запуска — то есть до момента, когда пост нужен.

Все они проверяются за секунды и без обращения к модели. Поэтому проверка
ничего не сочиняет и никуда не ходит: она только смотрит, сойдётся ли то, из
чего бот собран.

Запуск:
    python3 проверка.py
"""

import ast
import builtins
import importlib
import io
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent

# Ключи схемы, которые принимает API. Кириллицу он отвергает целиком, а узнать
# об этом можно только по ответу 400 посреди работы.
КЛЮЧ_СХЕМЫ = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

# Модули, которые незачем поднимать: у одних работа начинается прямо при
# запуске, другие тянут за собой сеть.
НЕ_ПОДНИМАТЬ = {"bot", "проверка"}


def _файлы() -> list[Path]:
    return sorted(п for п in КОРЕНЬ.glob("*.py") if п.name != "проверка.py")


def имена() -> list[str]:
    """Имена, которые где-то вызваны, но нигде не заданы.

    Так нашлись `_живой` и `_подогнать_вид`: код их звал, а самих функций в
    файле не было. Питон об этом молчит до самого вызова.
    """
    беды = []
    for ф in _файлы():
        try:
            дерево = ast.parse(ф.read_text(encoding="utf-8"))
        except SyntaxError as e:
            беды.append(f"{ф.name}: не разбирается, {e}")
            continue
        свои = {"__file__", "__name__", "__doc__"}
        for у in ast.walk(дерево):
            if isinstance(у, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                свои.add(у.name)
            elif isinstance(у, ast.Name) and isinstance(у.ctx, ast.Store):
                свои.add(у.id)
            elif isinstance(у, ast.arg):
                свои.add(у.arg)
            elif isinstance(у, (ast.Import, ast.ImportFrom)):
                for и in у.names:
                    свои.add((и.asname or и.name).split(".")[0])
            elif isinstance(у, ast.ExceptHandler) and у.name:
                свои.add(у.name)
        нет = sorted({у.id for у in ast.walk(дерево)
                      if isinstance(у, ast.Name) and isinstance(у.ctx, ast.Load)
                      and у.id not in свои and not hasattr(builtins, у.id)})
        if нет:
            беды.append(f"{ф.name}: вызвано, но не задано — {', '.join(нет)}")
    return беды


def модули() -> list[str]:
    """Каждый модуль должен подниматься сам по себе."""
    беды = []
    sys.path.insert(0, str(КОРЕНЬ))
    for ф in _файлы():
        имя = ф.stem
        if имя in НЕ_ПОДНИМАТЬ:
            continue
        try:
            with redirect_stdout(io.StringIO()):
                importlib.import_module(имя)
        except Exception as e:                               # noqa: BLE001
            беды.append(f"{имя}: не поднимается, {type(e).__name__}: {e}")
    return беды


def формы() -> list[str]:
    """Все формы, по которым мы спрашиваем модель, должны лечь в схему API.

    Имена полей у нас русские, и это нарочно: по русскому имени модель
    попадает в поле точнее. Наружу они уходят переведёнными (`агент.по_форме`),
    и проверяем мы именно перевод.
    """
    import агент
    import carousel
    import crosspost
    import facts
    import writer
    import отклики

    беды = []
    for форма in (carousel.Карусель, carousel.Слайд, writer.Пост,
                  отклики.Кандидат, отклики.Отбор, отклики.Тройка,
                  отклики.Ответы, crosspost._модель(), facts._модели()):
        карта: dict = {}
        схема = агент._переименовать(форма.model_json_schema(), карта)
        плохие: list[str] = []

        def обойти(узел):
            if isinstance(узел, dict):
                for ключ, значение in узел.items():
                    if ключ in ("properties", "$defs", "definitions") and isinstance(значение, dict):
                        плохие.extend(и for и in значение if not КЛЮЧ_СХЕМЫ.match(и))
                    обойти(значение)
            elif isinstance(узел, list):
                for э in узел:
                    обойти(э)

        обойти(схема)
        if плохие:
            беды.append(f"{форма.__name__}: API не примет ключи {плохие}")
    return беды


def агент_готов() -> list[str]:
    """Claude Code на месте и понимает то, чем мы его зовём.

    Неизвестное имя инструмента CLI не пропускает мимо: он падает на старте,
    ещё не начав работу, и падает одинаково на каждой попытке. Так бот молчал
    целый вечер из-за одного лишнего слова в списке запретов.
    """
    import агент
    путь = агент.бинарь()
    if not путь:
        return ["claude не найден: бот не сможет сочинять"]

    беды = []
    среда = {**os.environ}
    for ключ in агент.КЛЮЧИ_API:
        среда.pop(ключ, None)
    for имя in агент.БЕЗ_ИНСТРУМЕНТОВ.split(","):
        готово = subprocess.run(
            [путь, "-p", "--disallowedTools", имя, "--max-turns", "0"],
            input="", capture_output=True, text=True, timeout=60, env=среда)
        вывод = (готово.stdout or "") + (готово.stderr or "")
        if "matches no known tool" in вывод:
            беды.append(f"агент.БЕЗ_ИНСТРУМЕНТОВ: «{имя}» этот Claude Code уже "
                        f"не знает и ругается на каждый вызов")
    return беды


def окружение() -> list[str]:
    """Ключи, браузер и прочее, без чего часть работы не сделается."""
    import config
    return config.проверить()


ЧТО_СМОТРИМ = [
    ("имена", имена, True),
    ("модули", модули, True),
    ("формы для модели", формы, True),
    ("Claude Code", агент_готов, True),
    ("окружение", окружение, False),
]


def всё() -> int:
    """Гоняет все проверки. Возвращает число настоящих бед."""
    sys.path.insert(0, str(КОРЕНЬ))
    бед = 0
    for имя, что, строгая in ЧТО_СМОТРИМ:
        try:
            найдено = что()
        except Exception as e:                               # noqa: BLE001
            найдено = [f"проверка сорвалась: {type(e).__name__}: {e}"]
        if not найдено:
            print(f"  ✓ {имя}")
            continue
        знак = "✗" if строгая else "!"
        print(f"  {знак} {имя}")
        for беда in найдено:
            print(f"      {беда}")
        if строгая:
            бед += len(найдено)
    return бед


if __name__ == "__main__":
    print("Проверка бота\n")
    сколько = всё()
    print()
    if сколько:
        print(f"Бед: {сколько}. Запускать бота нельзя, сначала это.")
    else:
        print("Всё сходится, можно запускать.")
    sys.exit(1 if сколько else 0)
