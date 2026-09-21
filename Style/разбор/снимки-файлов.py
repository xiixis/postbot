# -*- coding: utf-8 -*-
"""Снимки файлов проекта для кадров-доказательств: python3 снимки-файлов.py

Кладёт PNG в `../подборка-сайтов/сайты/` — оттуда их берёт `холст.py` стиля «разбор».
Рисуется окно редактора (кружки, имя файла, строки с номерами), а не настоящий скриншот:
настоящий редактор даёт мелкий шрифт и чужие панели, в ленте это нечитаемо.

Содержимое — правда о постботе: имена файлов и папок настоящие. Пост учит приёму
«RULES / INDEX / MAP», и показывать в нём выдуманный проект нечестно.
"""
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
sys.path.insert(0, str(стиль.ПОСТБОТ))
import браузер  # noqa: E402

ЦЕЛЬ = ТУТ.parent / "подборка-сайтов" / "сайты"
Ш, В = 1400, 520          # пропорция 2,7 — как рамка снимка в кадре «разбора»; без обрезки

ФАЙЛЫ = {
    "rules-md": ("RULES.md", [
        ("#", " Правила работы в проекте"),
        ("", ""),
        ("##", " Как отвечать"),
        ("-", " Коротко и по делу, по-русски."),
        ("", ""),
        ("##", " В каком порядке работать"),
        ("1.", " Прочитать INDEX.md"),
        ("2.", " Открыть только нужные файлы"),
        ("3.", " Написать тест, потом код"),
    ]),
    "index-md": ("INDEX.md", [
        ("#", " Что где лежит"),
        ("", ""),
        ("card.py", " — рисовальщик кадров."),
        ("", "  Читать, когда правим вёрстку слайда."),
        ("", ""),
        ("конвейер.py", " — план постов на неделю."),
        ("", "  Читать, когда план просел."),
        ("", ""),
        ("приёмка.py", " — проверка кадров на брак."),
        ("", "  Читать, когда кадр вышел кривым."),
    ]),
    "map-md": ("MAP.md", [
        ("#", " Карта проекта"),
        ("", ""),
        ("postbot/", "            бот, рисовальщик, база"),
        ("├── webapp/", "        мини-приложение"),
        ("├── assets/", "        шрифты, кот, логотип"),
        ("├── Style/", "         ДНК стилей из референсов"),
        ("└── tests/", "         525 тестов"),
        ("", ""),
        ("Style/", "            стили каруселей"),
        ("└── сервисы/", "       подборка сервисов"),
    ]),
}

СТРАНИЦА = """<!doctype html><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{Ш}px;height:{В}px;background:#0D0F0C;font-family:-apple-system,"Helvetica Neue",Arial}}
.окно{{position:absolute;inset:24px;border-radius:34px;overflow:hidden;background:#151713;
  box-shadow:0 30px 80px rgba(0,0,0,.55),inset 0 0 0 2px rgba(238,240,232,.10)}}
.верх{{display:flex;align-items:center;gap:14px;height:70px;padding:0 30px;background:#1D201A}}
.точка{{width:20px;height:20px;border-radius:50%;background:#3C3F36}}
.точка:first-child{{background:#E6584A}}.точка:nth-child(2){{background:#E3B341}}.точка:nth-child(3){{background:{ЛАЙМ}}}
.имя{{margin-left:18px;font-size:30px;color:#9DA291}}
.код{{padding:18px 0;font-family:"JetBrains Mono","SF Mono",Menlo,monospace;font-size:34px;line-height:1.42;color:#E7EAE0}}
.строка{{display:flex;gap:26px;padding:0 34px}}
.н{{width:42px;text-align:right;color:#4E5348;flex:none}}
.ключ{{color:{ЛАЙМ};font-weight:700}}
</style><body><div class=окно>
<div class=верх><span class=точка></span><span class=точка></span><span class=точка></span><span class=имя>{имя}</span></div>
<div class=код>{строки}</div></div></body>"""


def страница(имя: str, строки: list[tuple[str, str]]) -> str:
    тело = "".join(
        f"<div class=строка><span class=н>{н}</span><span>"
        f"<span class=ключ>{ключ}</span>{хвост}</span></div>"
        for н, (ключ, хвост) in enumerate(строки, 1))
    return СТРАНИЦА.format(Ш=Ш, В=В, ЛАЙМ=стиль.ЛАЙМ, имя=имя, строки=тело)


def main():
    ЦЕЛЬ.mkdir(parents=True, exist_ok=True)
    for файл, (имя, строки) in ФАЙЛЫ.items():
        путь = ЦЕЛЬ / f"{файл}.png"
        if not браузер.снять(страница(имя, строки), Ш, В, путь):
            raise SystemExit(f"снимок не вышел: {файл}")
        print(путь, f"{путь.stat().st_size // 1024} КБ", flush=True)


if __name__ == "__main__":
    main()
