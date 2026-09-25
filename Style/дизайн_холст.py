# -*- coding: utf-8 -*-
"""Правимый холст типа Design на claude.ai — общий для стилей, у которых нет своего.

Порядок записан в `.claude/ПУБЛИКАЦИЯ.md`, шаг 5: холст собирается своими руками, без
помощника и без /design. Здесь только файлы: папка `холсты/<пост>/project/` с досками
`*.dc.html`, картинками, шрифтами и `canvas.json` (`"v": 3`). Выкладывает её Claude одним
вызовом Artifact (`root` = `холсты/<пост>`, `file_path` = `project/canvas.json`).

Доска — обычная статичная вёрстка 1080×1440 без `{{…}}`: владелец правит её прямо на
холсте, а `выпуск.py` открывает сохранённую доску как есть и снимает в полуторном
масштабе. Картинки и шрифты лежат рядом с досками и зовутся по относительному имени
латиницей: так холст лёгкий, а выпуск вшивает их данными перед снимком.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import стиль

Ш, В = 1080, 1440                     # доска холста; на стол уходит 1080×1440, снимок ×1,5
ШАГ_Х, ШАГ_У = 80, 200                # зазоры между досками: в ряду и между рядами

# ── Проверенное на постах 23.09.2026 (правки владельца) ─────────────────────
# Всё важное — выше 1105 px доски, знак — в полосе 1191..1235 (`замер.py`), ниже —
# подпись и кнопки TikTok. Заголовок обложки — от 110 px, он должен остановить ленту.
НИЗ_СОДЕРЖИМОГО = 1105
ЗНАК_ВЕРХ = 1191
CLAUDE = "#D97757"                    # фирменный цвет Claude: слово «Claude» на обложках


def маркер(текст: str, тёмный_фон: bool = False, чернила: str = "#12130E", цвет: str = "") -> str:
    """Акцент слова: лаймовая капсула под тёмным текстом; на тёмном фоне — лайм текстом.

    Олива #3F4D08 по крему держала контраст 8:1, но в ленте «тусклая, незаметная»;
    лайм текстом по светлому не читается (1,7:1). Тёмный текст на лайме — ~13:1 и
    самое заметное пятно кадра. Капсула — inline-block со своим отступом сверху:
    строчная подсветка при плотном интерлиньяже залезала на строку выше.
    """
    цвет = цвет or стиль.ЛАЙМ          # акцент стиля; у всех, кроме «навыков», — лайм
    if тёмный_фон:
        return f'<span style="color: {цвет};">{текст}</span>'
    return (f'<span style="background: {цвет}; color: {чернила}; display: inline-block; line-height: 1; '
            f'padding: .03em .16em .08em; margin-top: .1em; border-radius: .16em;">{текст}</span>')


def шрифты(*гарнитуры: tuple) -> tuple[str, list[Path]]:
    """@font-face по относительным именам и список файлов, которые надо положить рядом.

    Гарнитура — («семья», «файл без набора», вес), как у `стиль.фейсы`.
    """
    css, файлы = [], []
    for семья, файл, вес in гарнитуры:
        for набор, диапазон in (("latin", стиль.ЛАТИНИЦА), ("cyrillic", стиль.КИРИЛЛИЦА)):
            имя = f"{файл}-{набор}.woff2"
            файлы.append(стиль.ШРИФТЫ / имя)
            css.append(f"@font-face{{font-family:{семья};font-weight:{вес};font-display:block;"
                       f"src:url({имя}) format('woff2');unicode-range:{диапазон}}}")
    return "\n".join(css), файлы


def шрифты_холста(css: str, корень: Path) -> str:
    """Шрифты с адресами самого холста первыми, локальный файл — запасным.

    Редактор холста не грузит шрифт по относительному имени из CSS: подставляет запасную
    гарнитуру, строки ширятся и «плывут» (поймал владелец 23.09.2026). Поэтому файлы шрифтов
    загружаются на холст (`Artifact publish asset:true`), их адреса `/_blob/…` пишутся в
    `холсты/<пост>/шрифты-холста.json`, и здесь встают первыми в `src`. Выпуск открывает
    доску с диска: `/_blob/` там не грузится, и браузер берёт следующий, локальный файл.
    """
    карта = корень / "шрифты-холста.json"
    if not карта.exists():
        raise SystemExit(f"нет {карта}: сперва загрузить шрифты на холст (asset) и записать их адреса")
    адреса = json.loads(карта.read_text(encoding="utf-8"))
    for имя, адрес in адреса.items():
        css = css.replace(f"src:url({имя}) format('woff2')",
                          f"src:url({адрес}) format('woff2'),url({имя}) format('woff2')")
    return css


def доска(название: str, тело: str, фон: str, css: str) -> str:
    """Полная доска .dc.html: корень фиксированного размера, стили в <helmet>."""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{название}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
{css}
</style>
</helmet>
<div style="width: {Ш}px; height: {В}px; position: relative; overflow: hidden; background: {фон};">
{тело}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{Ш},"height":{В}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""


def собрать(корень: Path, название: str, доски: list[tuple[str, str, str]],
            файлы: list[Path], заметка: str = "", в_ряд: int = 5, источник: str = "") -> Path:
    """Раскладывает `корень/project/`: доски, файлы рядом, canvas.json. Возвращает project/.

    `доски` — (имя файла, подпись на холсте, html). Главная обложка — `Main.dc.html`,
    запасные — `Oblozhka2.dc.html`, `Oblozhka3.dc.html`: выпуск их не снимает.

    `источник` — ссылка на референс; на холсте она стоит всегда (слово владельца
    23.09.2026: «теперь всегда прикрепляй ссылку в самом холсте»). Без неё холст не собирается.
    """
    if not источник.strip():
        raise SystemExit("нет ссылки на референс: заполни поле «источник» в файле поста")
    проект = корень / "project"
    if проект.exists():
        shutil.rmtree(проект)
    проект.mkdir(parents=True)
    for ф in файлы:
        shutil.copy(ф, проект / ф.name)
    доски_json, порядок = {}, []
    for i, (имя, подпись, html) in enumerate(доски):
        (проект / имя).write_text(html, encoding="utf-8")
        доски_json[имя] = {"x": i % в_ряд * (Ш + ШАГ_Х), "y": i // в_ряд * (В + ШАГ_У),
                           "w": Ш, "h": В, "title": подпись}
        порядок.append(имя)
    заметки = {}
    if заметка:
        заметки["pravka"] = {"x": 0, "y": -560, "text": заметка, "w": 900, "fill": "green", "size": "l"}
    # Только сама ссылка, крупно (слово владельца 23.09.2026: «пиши там только ссылку и сделай
    # заметку больше в 3 раза»): первая ссылка из поля «источник», без ника и пояснений.
    import re
    ссылка = (re.findall(r"https?://\S+", источник) or [источник.strip()])[0]
    заметки["referens"] = {"x": Ш + ШАГ_Х, "y": -800, "text": ссылка, "w": 2700, "fill": "blue", "size": 120}
    индекс = {"v": 3, "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
              "title": название, "launch": {"view": "canvas"}, "pages": [], "boards": доски_json,
              "order": порядок, "notes": заметки, "designSystems": []}
    (проект / "canvas.json").write_text(json.dumps(индекс, ensure_ascii=False, indent=1), encoding="utf-8")
    return проект


def логотип(папка: Path) -> Path:
    """Логотип канала рядом с досками (на каждом кадре, слово владельца 17.09.2026)."""
    from PIL import Image
    путь = папка / "logo.png"
    папка.mkdir(parents=True, exist_ok=True)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и.thumbnail((160, 160))
        и.save(путь, optimize=True)
    return путь


def кот(поза: str, папка: Path) -> Path:
    """Поза кота, обрезанная по видимому, webp латиницей рядом с досками."""
    from PIL import Image
    путь = папка / f"kot-{стиль.латиницей(поза)}.webp"
    папка.mkdir(parents=True, exist_ok=True)
    with Image.open(стиль.ПОЗЫ / f"{поза}.png") as и:
        и = и.convert("RGBA")
        и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
        и.thumbnail((900, 1200))
        и.save(путь, "WEBP", quality=90)
    return путь


def снимок_сайта(исходник: Path, папка: Path, ширина: int = 1400) -> Path:
    """Снимок сайта в jpg нужной ширины: 1-мегабайтный PNG доске ни к чему."""
    from PIL import Image
    путь = папка / (исходник.stem + ".jpg")
    папка.mkdir(parents=True, exist_ok=True)
    with Image.open(исходник) as и:
        и = и.convert("RGB")
        if и.width > ширина:
            и = и.resize((ширина, round(и.height * ширина / и.width)), Image.LANCZOS)
        и.save(путь, quality=88)
    return путь
