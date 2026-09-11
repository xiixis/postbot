# -*- coding: utf-8 -*-
"""Снимает эталон: вёрстку каждого кадра поста 96 и её замер.

Запускается руками один раз, результат лежит в истории. Картинки не рисуем:
_снять подменён записью, Chrome зовётся только для замеров.
"""
import json
import sys
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(КОРЕНЬ))

import card      # noqa: E402
import carousel  # noqa: E402
import config    # noqa: E402
import db        # noqa: E402
import mascot    # noqa: E402

ЦЕЛЬ = Path(__file__).resolve().parent / "пост96"
ЦЕЛЬ.mkdir(parents=True, exist_ok=True)
ЗНАК = "{{АССЕТЫ}}"
кадры = []


def записать(страница, ширина=1280, высота=720):
    кадры.append((страница, ширина, высота))
    return None


card._снять = записать
поля = db.карточка(db.взять(96))
к = поля["carousel"]
формат = поля.get("формат") or "квадрат"
carousel.нарисовать(к, формат, mascot.взять(к.get("поза") or ""))

опись = {"пост": 96, "формат": формат, "кадры": []}
for н, (страница, ш, в) in enumerate(кадры, start=1):
    текст = страница.replace(str(config.АССЕТЫ), ЗНАК)
    assert "/Users/" not in текст, f"кадр {н}: в вёрстке остался абсолютный путь"
    имя = f"{н:02d}.html"
    (ЦЕЛЬ / имя).write_text(текст, encoding="utf-8")
    опись["кадры"].append({"файл": имя, "ширина": ш, "высота": в,
                           "замер": card._замерить(страница, ш, в)})
(ЦЕЛЬ / "замеры.json").write_text(json.dumps(опись, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
print(f"эталон: {len(кадры)} кадров в {ЦЕЛЬ}")
