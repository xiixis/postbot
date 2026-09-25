# -*- coding: utf-8 -*-
"""Claude CLI из npm на Windows зовётся через node напрямую, а не через `cmd /c`.

`cmd /c` разбирает командную строку заново: кавычки, `%`, `&` в системной подсказке и
JSON-схеме ломаются, а длина упирается в 8191 знак (аудит 25.09.2026).
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import агент                                                 # noqa: E402

# Так выглядит обёртка, которую npm кладёт в %APPDATA%\npm\claude.cmd.
ОБЁРТКА = r'''@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

IF EXIST "%dp0%\node.exe" (
  SET "_prog=%dp0%\node.exe"
) ELSE (
  SET "_prog=node"
  SET PATHEXT=%PATHEXT:;.JS;=;%
)

endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & "%_prog%"  "%dp0%\node_modules\@anthropic-ai\claude-code\cli.js" %*
'''


class ОбёрткаNpm(unittest.TestCase):
    def test_разбирается_в_node_и_cli(self):
        with tempfile.TemporaryDirectory() as папка:
            п = Path(папка)
            (п / "claude.cmd").write_text(ОБЁРТКА, encoding="utf-8")
            скрипт = п / "node_modules" / "@anthropic-ai" / "claude-code" / "cli.js"
            скрипт.parent.mkdir(parents=True)
            скрипт.write_text("// cli", encoding="utf-8")
            (п / "node.exe").write_bytes(b"")
            итог = агент.без_обёртки_npm(str(п / "claude.cmd"))
            self.assertEqual(итог, [str(п / "node.exe"), str(скрипт)])

    def test_непонятная_обёртка_не_разбирается(self):
        with tempfile.TemporaryDirectory() as папка:
            п = Path(папка) / "claude.cmd"
            п.write_text("@echo off\nsomething-else %*\n", encoding="utf-8")
            self.assertIsNone(агент.без_обёртки_npm(str(п)), "без cli.js остаётся запасной путь через cmd")


if __name__ == "__main__":
    unittest.main()
