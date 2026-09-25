# -*- coding: utf-8 -*-
"""Сторож кодировки: каждый текстовый файл и каждый текстовый вывод процесса —
с явным encoding.

Без него Python берёт кодировку системы: на маке и в облаке это utf-8, а на
Windows без PYTHONUTF8 — cp1251. Тогда кириллица в подписи, JSON или выводе
Chrome либо превращается в кракозябры, либо роняет UnicodeDecodeError. Ловим
это разбором исходников через ast, без запуска кода.

Что считается нарушением:
  • x.read_text(...) / x.write_text(...) без encoding=;
  • open(...), io.open, os.fdopen, Path(...).open(...), tempfile.*TemporaryFile
    в текстовом режиме без encoding= (режим переменной не угадать — пропускаем);
  • subprocess.run/Popen/check_output/call/check_call с text=True или
    universal_newlines=True без encoding=.
"""

import ast
import unittest
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent.parent

# Копии для облака пересобирает tools_vercel.py, чужие окружения и архив не наши.
МИМО = {"vercel", ".venv", "venv", "graphify-out", "__pycache__", "node_modules", ".git"}
МИМО_ПУТИ = {("docs", "архив")}

# Места, которые сейчас правит другой человек: не трогаем, но и не забываем.
# Как только место исправлено, второй тест требует убрать его отсюда.
ПОКА_ЧУЖОЕ: set[str] = set()

ВЫЗОВЫ_ПРОЦЕССА = {"run", "Popen", "check_output", "call", "check_call"}
# .open() у этих объектов — не текстовый файл (картинка, браузер, архив).
НЕ_ФАЙЛ = {"Image", "webbrowser", "tarfile", "zipfile", "wave", "shelve", "dbm", "sqlite3"}
ВРЕМЕННЫЕ = {"NamedTemporaryFile", "TemporaryFile", "SpooledTemporaryFile"}


def _файлы():
    for путь in sorted(КОРЕНЬ.rglob("*.py")):
        части = путь.relative_to(КОРЕНЬ).parts
        if any(ч in МИМО for ч in части[:-1]):
            continue
        if any(части[: len(п)] == п for п in МИМО_ПУТИ):
            continue
        yield путь


def _есть(вызов: ast.Call, имя: str) -> bool:
    # **kw не разобрать — верим, что кодировка там
    return any(k.arg in (имя, None) for k in вызов.keywords)


def _правда(вызов: ast.Call, имя: str) -> bool:
    for k in вызов.keywords:
        if k.arg == имя:
            return not (isinstance(k.value, ast.Constant) and not k.value.value)
    return False


def _режим(вызов: ast.Call, позиция: int):
    """Режим открытия: строка, None (не задан) или ... (не угадать)."""
    for k in вызов.keywords:
        if k.arg == "mode":
            return k.value.value if isinstance(k.value, ast.Constant) else ...
    if len(вызов.args) > позиция:
        узел = вызов.args[позиция]
        if isinstance(узел, ast.Constant) and isinstance(узел.value, str):
            return узел.value
        return ...
    if any(isinstance(а, ast.Starred) for а in вызов.args):
        return ...
    return None


def _имя(узел) -> str:
    if isinstance(узел, ast.Name):
        return узел.id
    if isinstance(узел, ast.Attribute):
        return узел.attr
    return ""


def узлы(дерево):
    """Вызовы без явной кодировки: пары (узел вызова, что это)."""
    for вызов in ast.walk(дерево):
        if not isinstance(вызов, ast.Call):
            continue
        ф = вызов.func
        if isinstance(ф, ast.Attribute) and ф.attr in ("read_text", "write_text"):
            if not _есть(вызов, "encoding"):
                yield вызов, ф.attr
            continue
        # open(путь, режим), io.open, os.fdopen — режим вторым аргументом;
        # Path(...).open(режим) и tempfile.*TemporaryFile(режим) — первым.
        позиция, по_умолчанию = None, "r"
        if (isinstance(ф, ast.Name) and ф.id == "open") or (
            isinstance(ф, ast.Attribute) and ф.attr in ("open", "fdopen")
            and _имя(ф.value) in ("io", "codecs", "os")
        ):
            позиция = 1
        elif isinstance(ф, ast.Attribute) and ф.attr in ВРЕМЕННЫЕ:
            позиция, по_умолчанию = 0, "w+b"
        elif isinstance(ф, ast.Attribute) and ф.attr == "open" and _имя(ф.value) not in НЕ_ФАЙЛ:
            if not вызов.args and not вызов.keywords and not isinstance(ф.value, ast.Call):
                # x.open() без аргументов у переменной может быть и не файлом —
                # считаем, только когда объект явно путь: Path(...).open().
                continue
            позиция = 0
        if позиция is not None:
            режим = _режим(вызов, позиция)
            if режим is None:
                режим = по_умолчанию
            if режим is not ... and "b" not in режим and not _есть(вызов, "encoding"):
                yield вызов, "open"
            continue
        if isinstance(ф, ast.Attribute) and ф.attr in ВЫЗОВЫ_ПРОЦЕССА \
                and _имя(ф.value) in ("subprocess", "sp"):
            if (_правда(вызов, "text") or _правда(вызов, "universal_newlines")) \
                    and not _есть(вызов, "encoding"):
                yield вызов, "subprocess." + ф.attr


def нарушения(исходник: str) -> list[tuple[int, str]]:
    return sorted((в.lineno, что) for в, что in узлы(ast.parse(исходник)))


def _все_места() -> list[tuple[str, int, str]]:
    места = []
    for путь in _файлы():
        имя = путь.relative_to(КОРЕНЬ).as_posix()
        for строка, что in нарушения(путь.read_text(encoding="utf-8")):
            места.append((имя, строка, что))
    return места


class ТестКодировки(unittest.TestCase):
    def test_везде_явная_кодировка(self):
        плохо = [f"{ф}:{с} {что}" for ф, с, что in _все_места()
                 if f"{ф}:{что}" not in ПОКА_ЧУЖОЕ]
        if плохо:
            self.fail(
                "Без encoding= на Windows без PYTHONUTF8 кириллица ломается (cp1251). "
                f"Места ({len(плохо)}):\n" + "\n".join(плохо))

    def test_чужое_ещё_не_исправлено(self):
        есть = {f"{ф}:{что}" for ф, _, что in _все_места()}
        лишнее = sorted(ПОКА_ЧУЖОЕ - есть)
        self.assertFalse(лишнее, f"уже исправлено — убрать из ПОКА_ЧУЖОЕ: {лишнее}")

    def test_сторож_видит_нарушения(self):
        образец = (
            "import subprocess\n"
            "p.read_text()\n"
            "p.write_text('x')\n"
            "open('a')\n"
            "open('a', 'w')\n"
            "subprocess.run(['x'], text=True)\n"
            "p.read_text(encoding='utf-8')\n"
            "open('a', 'rb')\n"
            "subprocess.run(['x'], text=True, encoding='utf-8')\n"
            "subprocess.run(['x'], capture_output=True)\n"
            "tempfile.NamedTemporaryFile('w')\n"
            "tempfile.NamedTemporaryFile()\n"
            "Image.open('a.png')\n"
            "open(путь, режим)\n"
        )
        self.assertEqual([с for с, _ in нарушения(образец)], [2, 3, 4, 5, 6, 11])


if __name__ == "__main__":
    unittest.main()
