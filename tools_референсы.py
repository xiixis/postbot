# -*- coding: utf-8 -*-
"""Референсы под рерайт из командной строки.

    python3 tools_референсы.py список [статус|все]
    python3 tools_референсы.py взять [номер]
    python3 tools_референсы.py готово <номер> [пост] [заметка]
    python3 tools_референсы.py отбросить <номер> [причина]
    python3 tools_референсы.py сверить

`сверить` читает тему копией сессии: живой бот держит файл сессии, и два
процесса на одном файле ловят «database is locked».
"""
import shutil
import sys
import tempfile
from pathlib import Path

import db
import референсы


def _строка(р) -> str:
    пост = f" → пост {р['post_id']}" if р["post_id"] else ""
    заметка = f" · {р['заметка']}" if р["заметка"] else ""
    return f"{р['id']:>3}  {р['статус']:<12} {р['добавлена'][:10]}  {р['url']}{пост}{заметка}"


def main(арг: list[str]) -> None:
    команда = арг[0] if арг else "список"
    if команда == "список":
        статус = арг[1] if len(арг) > 1 else "новая"
        ряды = db.референсы(None if статус == "все" else статус)
        print("\n".join(_строка(р) for р in ряды) or "пусто")
    elif команда == "взять":
        р = db.взять_референс(int(арг[1]) if len(арг) > 1 else None)
        print(_строка(р) if р else "новых нет")
    elif команда == "готово":
        db.отметить_референс(int(арг[1]), "использована",
                             post_id=int(арг[2]) if len(арг) > 2 and арг[2].isdigit() else None,
                             заметка=" ".join(арг[3:]) or None)
        print("отмечено")
    elif команда == "отбросить":
        db.отметить_референс(int(арг[1]), "отброшена", заметка=" ".join(арг[2:]) or None)
        print("отброшено")
    elif команда == "сверить":
        import userbot
        with tempfile.TemporaryDirectory() as врем:
            копия = Path(врем) / "аккаунт"
            shutil.copy(f"{userbot.СЕССИЯ}.session", f"{копия}.session")
            userbot.СЕССИЯ = копия
            print("новых:", референсы.сверить())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
