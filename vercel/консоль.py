# -*- coding: utf-8 -*-
"""Вывод в консоль всегда в utf-8.

На Windows без переменной PYTHONUTF8 Python пишет в консоль и в трубу
кодировкой системы (cp1251 или cp866). Кириллицу она ещё переварит, а «✓»,
«→», «⚠️» и эмодзи — нет: print падает с UnicodeEncodeError посреди работы.
А родитель, читающий вывод дочернего скрипта как utf-8, получает кракозябры.
На маке и в облаке поток уже utf-8, и вызов ничего не меняет.

Модуль лёгкий нарочно: его зовут и config (а значит почти все модули), и
отдельные скрипты, которым config с облачными ключами ни к чему.
"""
import sys


def в_utf8() -> None:
    """Перенастроить stdout и stderr на utf-8, если они ещё не такие."""
    for поток in (sys.stdout, sys.stderr):
        try:
            if (getattr(поток, "encoding", "") or "").lower().replace("-", "") != "utf8":
                поток.reconfigure(encoding="utf-8", errors="replace")
        except Exception:                            # noqa: BLE001
            pass                                     # подменённый поток (тест, pythonw) — оставляем как есть

