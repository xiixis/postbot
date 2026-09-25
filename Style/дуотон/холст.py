# -*- coding: utf-8 -*-
"""Холст стиля «дуотон»: python3 холст.py посты/<пост>.json

Разбор референса — в `ДИЗАЙН.md` рядом. Коротко: рукописная строка-зачин, под ней заголовок
гигантом прописными, слово в рамке как выделение, фотография в двух цветах внизу, мелкие
метки сверху и капсула с адресом.

Главный приём набора — **дуотон**: фото переводится в чёрно-белое, автоконтрастится и
красится в два цвета. У автора это фиолетовый, у нас тени уходят в наш тёмный, света в
лайм. Именно тонировка собирает разнородные снимки в один набор — без неё стиль
рассыпается на случайные картинки.

Кадры бывают двух грунтов, тёмный и светлый, и чередуются: ритм ленты получается сам.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageOps

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

КРЕМ, ТЁМНЫЙ, ЛАЙМ = "#F1F2EA", стиль.ТЁМНЫЙ, стиль.ЛАЙМ
СВЕТЛЫЙ, ЧЕРНИЛА = стиль.СВЕТЛЫЙ, "#12130E"
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"
Р = "font-family:Caveat,'Bradley Hand',cursive;font-weight:700"

ПОЛЕ = 70
НИЗ_КОНТЕНТА = 1164


def дуотон(исходник: Path, цель: Path, тень=(18, 19, 15), свет=(199, 226, 75)) -> Path:
    """Фото в два цвета: тени — грунт, света — лайм."""
    with Image.open(исходник) as и:
        серое = ImageOps.grayscale(и.convert("RGB"))
        серое = ImageOps.autocontrast(серое, cutoff=2)
        окрашенное = ImageOps.colorize(серое, black=тень, white=свет)
        окрашенное.thumbnail((1000, 1000), Image.LANCZOS)
        окрашенное.save(цель, quality=80, optimize=True)
    return цель


def голова(тёмный: bool) -> str:
    грунт = ТЁМНЫЙ if тёмный else КРЕМ
    цвет = СВЕТЛЫЙ if тёмный else ЧЕРНИЛА
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700), ("Caveat", "caveat-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;
        background:{грунт};color:{цвет} }}
    .метки {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:66px;display:flex;
        justify-content:space-between;{Т};font-weight:700;font-size:26px;letter-spacing:.22em;
        color:{ЛАЙМ if тёмный else "#4C5A1C"} }}
    .рука {{ position:absolute;left:{ПОЛЕ}px;{Р};font-size:86px;line-height:1;
        color:{ЛАЙМ if тёмный else ЧЕРНИЛА} }}
    .крупно {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;{К};font-size:168px;
        line-height:.92;letter-spacing:-.045em }}
    /* Единственная граница в макете — рамка вокруг выделенного слова. */
    .врамке {{ display:inline-block;border:6px solid currentColor;padding:0 22px 10px 22px;
        margin-top:10px }}
    .под {{ position:absolute;left:{ПОЛЕ}px;{Т};font-size:42px;line-height:1.3 }}
    .фото {{ position:absolute;left:0;right:0;bottom:335px;width:100%;object-fit:cover }}
    .капсула {{ position:absolute;left:{ПОЛЕ}px;bottom:360px;background:{ЛАЙМ};color:{ЧЕРНИЛА};
        border-radius:44px;padding:12px 30px;{Т};font-weight:700;font-size:32px;z-index:5 }}
    .кот {{ position:absolute;z-index:4 }}
    .знак {{ position:absolute;left:{ПОЛЕ}px;bottom:205px;height:44px;z-index:6 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;z-index:6;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool) -> str:
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{ЛАЙМ}"></div>')


def кегль_заголовка(текст: str) -> int:
    """По самой длинной строке: у Onest 800 прописной знак занимает около 0,62 кегля."""
    длинная = max((len(с) for с in текст.split("<br>")), default=1)
    return min(168, int((1080 - 2 * ПОЛЕ) / (0.70 * max(длинная, 1))))


def метки(к: dict) -> str:
    return "<div class=метки>" + "".join(f"<span>{м}</span>" for м in к.get("метки", [])) + "</div>"


def кот(к: dict) -> str:
    """Кот файлом: вшитый данными PNG раздувал доску до 3,9 МБ, и помощник холста её не брал
    (предел 2 МБ на доску)."""
    где = ";".join(f"{ключ}:{к[ключ]}px" for ключ in ("left", "top", "right", "bottom") if ключ in к)
    return f'<img class=кот src="kot-{латиницей(к["поза"])}.webp" style="height:{к["высота"]}px;{где}">' 


def кадр(к: dict, доля: float, тёмный: bool, обложка: bool = False) -> str:
    """Один кадр. Текст с рамкой занимает на строку больше — пояснение опускается ниже,
    иначе оно наезжает на рамку."""
    рамка = (f' <span class=врамке style="color:{ЛАЙМ if тёмный else ЧЕРНИЛА}">'
             f'{к["врамке"]}</span>' if к.get("врамке") else "")
    # Заголовок со словом в рамке занимает лишнюю строку — текст опускается, иначе наезжает.
    # Кегль считается по всей фразе вместе с рамкой: раньше рамка в счёт не шла и строка уезжала
    # за правый край (поймано отрисовкой 18.09).
    длина = len(к["крупно"]) + (len(к.get("врамке", "")) + 1 if к.get("врамке") else 0)
    верх_текста = 640 + (120 if длина > 16 else 0)
    if len(к["под"]) > 110 and к.get("сцена"):
        raise SystemExit(f"кадр «{к['крупно']}»: текст в {len(к['под'])} знаков не влезает "
                         f"в две строки над фото — сократить до 110")
    # Фото занимает полосу между текстом и служебной зоной: 760…1105.
    фото = (f'<img class=фото src="{к["сцена"]}.jpg" style="top:760px;height:345px;bottom:auto">'
            if к.get("сцена") else "")
    кот_ = кот(к["кот"]) if к.get("кот") else ""
    return голова(тёмный) + f"""<div class=кадр>
  {метки(к)}
  {фото}
  <div class=рука style="top:150px">{к['рука']}</div>
  <div class=крупно style="top:270px;font-size:{кегль_заголовка(к['крупно'] + (' ' + к['врамке'] if к.get('врамке') else ''))}px">{к['крупно']}{рамка}</div>
  <div class=под style="top:{верх_текста}px;width:{к.get("ширина_текста", 600 if обложка else 900)}px">{к['под']}</div>
  <div class=капсула>4xSoft · нейросети по делу</div>
  {кот_}
  {знак_и_полоса(доля, тёмный)}
</div>""" + ХВОСТ


ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


def картинки(пост: dict, папка: Path) -> list[Path]:
    файлы = []
    for к in пост["кадры"] + [пост["обложка"], пост["финал"]]:
        if not к.get("сцена"):
            continue
        цель = папка / f'{латиницей(к["сцена"])}.jpg'
        if not цель.exists():
            дуотон(ТУТ.parent / "промпты/картинки" / f'{к["сцена"]}.png', цель)
            файлы.append(цель)
    места = [пост.get("обложка", {}), пост.get("обложка_число", {}), пост.get("обложка_допосле", {}),
             пост.get("финал", {}), *пост.get("кадры", [])]
    for к in (м["кот"] for м in места if м.get("кот")):
        цель = папка / f'kot-{латиницей(к["поза"])}.webp'
        if цель.exists():
            continue
        with Image.open(стиль.ПОЗЫ / f'{к["поза"]}.png') as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((900, round(к["высота"] * 1.6)), Image.LANCZOS)
            и.save(цель, quality=84, method=6)
        файлы.append(цель)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def обложка_число(о: dict, доля: float) -> str:
    """Б — число: гигант лаймом вместо крупной фразы, метки сверху, кот внизу."""
    return кадр({"метки": о["метки"], "рука": о["рука"], "крупно": о["число"],
                 "под": о["под"], "кот": о.get("кот")}, доля, True, обложка=True)


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: зачёркнутое «печатать» и слово в рамке «говорить»."""
    return кадр({"метки": о["метки"], "рука": о["рука"], "крупно": о["крупно"],
                 "врамке": о["врамке"], "под": о["под"], "кот": о.get("кот")},
                доля, True, обложка=True)


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    # Сцены названы по-русски, а помощник холста принимает только латиницу.
    for к in пост["кадры"] + [пост["обложка"], пост["финал"]]:
        if к.get("сцена"):
            к["_файл"] = латиницей(к["сцена"])

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: холст без них не выкладывается.
    обложки = {
        "сцена": lambda: кадр(dict(пост["обложка"], сцена=пост["обложка"].get("_файл")), 1 / всего,
                              тёмный=True, обложка=True),
        "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
        "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
    главная = пост.get("главная", "сцена")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['крупно'][:20]}",
                      кадр(dict(к, сцена=к.get("_файл")), (н + 1) / всего, тёмный=н % 2 == 0)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  кадр(dict(пост["финал"], сцена=пост["финал"].get("_файл")), 1.0, тёмный=True)))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html, encoding="utf-8")

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 4 * 1180, "y": i // 4 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)],
                 "launch": {"view": "canvas"}}
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1), encoding="utf-8")

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    картинки(пост, папка)          # картинки и коты рядом с досками
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
