# -*- coding: utf-8 -*-
"""Лист кадров: вся карусель одной картинкой.

Приём из html-instagram-carousel: после отрисовки там собирается contact sheet,
и ритм серии, повторы вёрсток и кривой кадр видны одним взглядом. Десять
отдельных картинок так не смотрятся: каждая по отдельности выглядит сносно.

Собирается Pillow, без браузера: на маке 16 ГБ, и поднимать Chrome ради
склейки готовых PNG незачем. Подписи — только номера: встроенный шрифт Pillow
кириллицы не знает, а брак и так виден по рамке.
"""

import secrets
from pathlib import Path

КОЛОНОК = 5
ШИРИНА = 216          # превью кадра; десять кадров 3:4 — лист около 1200×690
ЗАЗОР = 16
ПОДПИСЬ = 32
ФОН = (18, 19, 15)
ТЕКСТ = (241, 243, 234)
БРАК = (226, 112, 58)  # config.РЖАВЫЙ


def собрать(файлы: list, куда: Path | None = None, брак=()) -> Path | None:
    """Склеивает кадры сеткой. Номера кадров из «брак» обводятся ржавым."""
    from PIL import Image, ImageDraw, ImageFont

    кадры = [Path(ф) for ф in файлы if ф and Path(ф).exists()]
    if not кадры:
        return None
    превью = []
    for ф in кадры:
        with Image.open(ф) as к:
            к = к.convert("RGB")
            превью.append(к.resize((ШИРИНА, round(к.height * ШИРИНА / к.width)),
                                   Image.LANCZOS))
    колонок = min(КОЛОНОК, len(превью))
    рядов = -(-len(превью) // колонок)
    клетка = max(п.height for п in превью) + ПОДПИСЬ
    холст = Image.new("RGB", (ЗАЗОР + колонок * (ШИРИНА + ЗАЗОР),
                              ЗАЗОР + рядов * (клетка + ЗАЗОР)), ФОН)
    рисунок = ImageDraw.Draw(холст)
    шрифт = ImageFont.load_default(size=22)
    плохие = set(брак)
    for н, п in enumerate(превью, start=1):
        ряд, колонка = divmod(н - 1, колонок)
        x = ЗАЗОР + колонка * (ШИРИНА + ЗАЗОР)
        y = ЗАЗОР + ряд * (клетка + ЗАЗОР)
        холст.paste(п, (x, y))
        if н in плохие:
            рисунок.rectangle([x - 5, y - 5, x + ШИРИНА + 4, y + п.height + 4],
                              outline=БРАК, width=6)
        рисунок.text((x, y + п.height + 6), f"{н:02d}",
                     fill=БРАК if н in плохие else ТЕКСТ, font=шрифт)
    if куда is None:
        import config
        config.ВЫВОД.mkdir(parents=True, exist_ok=True)
        куда = config.ВЫВОД / f"лист_{secrets.token_hex(4)}.jpg"
    холст.save(куда, quality=90)
    return Path(куда)
