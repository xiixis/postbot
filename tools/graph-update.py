#!/usr/bin/env python3
"""Обновление графа Graphify по коду — быстро, локально и без путей этой машины.

Зачем обёртка, а не `graphify update .`
--------------------------------------
1. ИИ. Штатное обновление на каждое сообщество графа (у нас их сотни) идёт за
   названием к стороннему бесплатному ИИ pollinations.ai. Отключить это
   переменной окружения нельзя: любой другой провайдер без ключа отвечает
   ошибкой HTTP, а она наследует URLError — и graphify возвращается к тому же
   pollinations. На практике вызовы упираются в ограничение по частоте, и
   обновление не заканчивается за десять минут, то есть автоматическим быть
   не может. Заодно наружу уходят имена наших функций и файлов. Обёртка
   говорит graphify, что ИИ недоступен: названия сообществ считаются
   эвристикой по самым связанным узлам, на этой же машине. Было больше
   десяти минут — стало около пятнадцати секунд.

2. Пути. graphify раскрывает корень в абсолютный, и в графе оседает
   `/Users/…/yt-searcher/run.py` либо `C:\\Users\\…\\run.py`. Такой граф
   нельзя держать в репозитории на двоих: у напарника он показывает чужую
   машину, а каждая пересборка переписывает файл целиком. Поэтому после
   сборки пути укорачиваются до `run.py`, `app/server.py` — как и было в
   первой, «настоящей» сборке через скил.

Ни одной правки в самом graphify тут нет: обновление пакета ничего не сломает.

Запуск (питон именно из окружения graphify):
    ~/.graphify-venv/bin/python tools/graph-update.py .
"""

import json
import sys
from pathlib import Path

# Заглушка ИИ нужна была старым выпускам graphify: сборка ходила за
# названиями сообществ к стороннему бесплатному ИИ. В нынешних выпусках
# модуля graphify.ai нет вовсе, а пересбор по коду идёт без ИИ — поэтому
# заглушку ставим, только если есть что глушить.
try:
    from graphify.ai import Summarizer                # noqa: F401

    Summarizer.is_available = lambda self: False      # noqa: E731
except ImportError:
    pass

from graphify.watch import _rebuild_code            # noqa: E402


def укоротить(корень: Path) -> int:
    """Абсолютные пути в графе → относительные. Возвращает, сколько поправил."""
    выход = корень / "graphify-out"
    префиксы = [str(корень) + "/", str(корень) + "\\", str(корень)]
    правок = 0

    граф = выход / "graph.json"
    if граф.exists():
        d = json.loads(граф.read_text(encoding="utf-8"))
        for узел in d.get("nodes", []):
            п = узел.get("source_file")
            if not п:
                continue
            for пре in префиксы:
                if п.startswith(пре):
                    узел["source_file"] = п[len(пре):].replace("\\", "/")
                    правок += 1
                    break
        граф.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    # Остальные выходные файлы — простой заменой строки: в html данные графа
    # зашиты текстом, в отчётах путь стоит в заголовке. Заменяем именно
    # префикс корня, поэтому задеть чужое нечем.
    прочее = ("graph.json", "graph.html", "GRAPH_REPORT.md", "COMPASS.md",
              "DOMAINS.md", "graph.compact.txt", "manifest.json",
              "metadata.json", "intelligence.json", "suggestions.json")
    for имя in прочее:
        f = выход / имя
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        было = t
        for пре in префиксы:
            t = t.replace(пре, "")
        if t != было:
            f.write_text(t, encoding="utf-8")
    return правок


# Windows без PYTHONUTF8: консоль cp1251, print кириллицы падает — поток в utf-8.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import консоль  # noqa: E402

консоль.в_utf8()
цель = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
если_ок = _rebuild_code(цель)
if если_ок:
    n = укоротить(цель)
    print(f"[graph-update] пути укорочены до относительных: {n} узлов")
sys.exit(0 if если_ок else 1)
