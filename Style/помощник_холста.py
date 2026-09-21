# -*- coding: utf-8 -*-
"""Где лежит `seed-canvas.mjs` — помощник холста из скила design.

Claude Code распаковывает скилы во временную папку, и её адрес зависит и от
системы, и от пользователя: на маке это `/tmp/claude-<номер>/bundled-skills`,
на Windows — подпапка внутри `%TEMP%`. Раньше путь был записан целиком, вместе
с номером пользователя (`claude-501`), и повторён в одиннадцати файлах. Он
ломался дважды: при переезде на другую машину и при смене номера на этой же.

Поиск можно обойти: переменная окружения `SEED_CANVAS` задаёт файл напрямую.
Это запасной ход на случай, если Claude Code снова сменит место распаковки, —
чтобы чинилось настройкой, а не правкой кода.
"""
import os
import tempfile
from pathlib import Path

ПЕРЕМЕННАЯ = "SEED_CANVAS"
ХВОСТ = "*/*/design/seed-canvas.mjs"
БЕДА = "нет помощника холста: в сессии Claude Code вызвать /design, он распакуется"


def _корни() -> list[Path]:
    """Папки, где могут лежать распакованные скилы, без повторов.

    На маке `tempfile.gettempdir()` отдаёт `/var/folders/...` из TMPDIR, а
    скилы лежат в `/tmp`, поэтому оба места проверяются, а не одно.
    """
    места = [Path(tempfile.gettempdir()), Path("/tmp"), Path("/private/tmp")]
    видели: set[str] = set()
    итог: list[Path] = []
    for м in места:
        try:
            ключ = str(м.resolve())
        except OSError:
            continue
        if ключ in видели or not м.is_dir():
            continue
        видели.add(ключ)
        итог.append(м)
    return итог


def найти() -> Path | None:
    """Самый свежий `seed-canvas.mjs`, либо None, если его нет нигде."""
    явный = os.getenv(ПЕРЕМЕННАЯ, "").strip()
    if явный:
        п = Path(явный).expanduser()
        return п if п.is_file() else None

    найденные: list[Path] = []
    for корень in _корни():
        # Обычный случай: своя папка на пользователя, внутри неё скилы.
        найденные += корень.glob(f"claude-*/bundled-skills/{ХВОСТ}")
        # И тот же поиск без обёртки: место распаковки у Claude Code менялось.
        найденные += корень.glob(f"bundled-skills/{ХВОСТ}")
    if not найденные:
        return None
    return sorted(найденные, key=lambda п: п.stat().st_mtime)[-1]


def помощник() -> Path:
    """То же, но без права вернуть пустоту: нет помощника — нет и холста."""
    п = найти()
    if п is None:
        raise SystemExit(БЕДА)
    return п
