# -*- coding: utf-8 -*-
"""Холст стиля «сетка» — повтор присланного набора шаблонов один в один, меняются только
текст и цвет: python3 холст.py посты/<пост>.json

Геометрия снята замером с кадров референса (`../дуотон/референс/`), в долях кадра:

| Блок | У референса | У нас на 1080×1440 |
|---|---|---|
| строка-метки | 6,6–7,6% высоты, во всю ширину | 95…110 px |
| курсивный зачин | 18,8–22,6%, левая треть | 270…325 px |
| гигант | с 24,4%, во всю ширину, буквы упираются в поля | с 352 px |
| объект | внахлёст с заголовком, до низа | нижние 55% кадра |
| подпись-капсула | 85,8–93,6% | заменена нашим знаком с полосой |

Главное отличие от прежних наших стилей: **объект и заголовок стоят слоями**. У автора
кот с рупором перекрывает гигантские буквы, а не стоит под ними. Поэтому объект здесь —
вырезанная по контуру картинка с прозрачностью, а не полоса фото.

Фиолетовый не переносится: где у автора фиолетовый, у нас лайм и тёмный грунт.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

ЛАЙМ, ТЁМНЫЙ, СВЕТЛЫЙ = стиль.ЛАЙМ, стиль.ТЁМНЫЙ, стиль.СВЕТЛЫЙ
БУМАГА, ЧЕРНИЛА = "#F1F2EA", "#12130E"
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"
Р = "font-family:Caveat,'Bradley Hand',cursive;font-weight:700"

ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


ПОЛЕ = 62                                # 5,7% ширины — как у референса


def голова(грунт: str, цвет: str) -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700), ("Caveat", "caveat-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;
        background:{грунт};color:{цвет} }}
    .метки {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:95px;display:flex;
        justify-content:space-between;{Т};font-weight:700;font-size:24px;letter-spacing:.24em }}
    .зачин {{ position:absolute;left:{ПОЛЕ}px;top:262px;{Р};font-size:78px;line-height:1 }}
    /* Гигант уходит к самым полям: у референса буквы упираются в края кадра. */
    .гигант {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:352px;{К};line-height:.88;
        letter-spacing:-.05em;z-index:2 }}
    .врамке {{ display:inline-block;border:7px solid currentColor;padding:0 20px 12px 20px }}
    /* Объект перекрывает буквы — это и есть приём набора, слои вместо блоков. */
    .объект {{ position:absolute;z-index:3;filter:drop-shadow(0 30px 60px rgba(0,0,0,.35)) }}
    .фото {{ position:absolute;left:0;right:0;bottom:280px;width:100%;height:520px;
        object-fit:cover;z-index:1 }}
    .подпись {{ position:absolute;left:{ПОЛЕ}px;{Т};font-size:38px;line-height:1.3;z-index:4 }}
    .знак {{ position:absolute;left:{ПОЛЕ}px;bottom:205px;height:44px;z-index:6 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;z-index:6;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool) -> str:
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{ЛАЙМ}"></div>')


def кегль(строка: str, предел: int = 230) -> int:
    """Гигант занимает всю ширину между полями: кегль считается по длине строки."""
    return min(предел, int((1080 - 2 * ПОЛЕ) / (0.70 * max(len(строка), 1))))


def кадр(к: dict, доля: float) -> str:
    тёмный = к.get("грунт", "тёмный") == "тёмный"
    грунт = ТЁМНЫЙ if тёмный else (ЛАЙМ if к.get("грунт") == "лайм" else БУМАГА)
    цвет = СВЕТЛЫЙ if тёмный else ЧЕРНИЛА
    строки = к["гигант"].split("|")
    размер = min(кегль(с) for с in строки)
    гигант = "<br>".join(
        f'<span class=врамке>{с[1:]}</span>' if с.startswith("*") else с for с in строки)
    фото = (f'<img class=фото src="{к["фото"]}.jpg">' if к.get("фото") else "")
    объект = ""
    if к.get("кот") and к.get("объект"):
        о = к["объект"]
        где = ";".join(f"{п}:{о[п]}px" for п in ("left", "right", "bottom", "top") if п in о)
        объект = (стиль.кот(к["кот"]["поза"], к["кот"]["высота"], класс="объект",
                            **{п: к["кот"][п] for п in ("left", "right", "bottom", "top")
                               if п in к["кот"]})
                  + f'<img class=объект src="{латиницей(о["файл"])}.png" '
                    f'style="height:{о["высота"]}px;{где}">')
    elif к.get("кот"):
        объект = стиль.кот(к["кот"]["поза"], к["кот"]["высота"], класс="объект",
                           **{п: к["кот"][п] for п in ("left", "right", "bottom", "top")
                              if п in к["кот"]})
    elif к.get("объект"):
        о = к["объект"]
        где = ";".join(f"{п}:{о[п]}px" for п in ("left", "right", "bottom", "top") if п in о)
        объект = f'<img class=объект src="{латиницей(о["файл"])}.png" style="height:{о["высота"]}px;{где}">'
    return голова(грунт, цвет) + f"""<div class=кадр>
  <div class=метки style="color:{ЛАЙМ if тёмный else ЧЕРНИЛА}">
    {"".join(f"<span>{м}</span>" for м in к["метки"])}
  </div>
  <div class=зачин style="color:{ЛАЙМ if тёмный else ЧЕРНИЛА}">{к['зачин']}</div>
  <div class=гигант style="font-size:{размер}px;color:{ЛАЙМ if тёмный else ЧЕРНИЛА}">{гигант}</div>
  {фото}
  {объект}
  <div class=подпись style="top:{к.get('подпись_верх', 980)}px;width:{к.get('ширина', 560)}px">{к['подпись']}</div>
  {знак_и_полоса(доля, тёмный)}
</div>""" + ХВОСТ


def дуотон_с_альфой(исходник: Path, цель: Path, тень=(18, 19, 15), свет=(199, 226, 75)) -> None:
    """Дуотон поверх выреза: цвет меняется, прозрачность остаётся. Без сохранения альфы
    объект теряет вырез и снова становится прямоугольником."""
    from PIL import ImageOps
    with Image.open(исходник) as и:
        и = и.convert("RGBA")
        альфа = и.getchannel("A")
        серое = ImageOps.autocontrast(ImageOps.grayscale(и.convert("RGB")), cutoff=2)
        цвет = ImageOps.colorize(серое, black=тень, white=свет).convert("RGBA")
        цвет.putalpha(альфа)
        цвет.thumbnail((1100, 1100), Image.LANCZOS)
        цвет.save(цель, optimize=True)


def картинки(пост: dict, папка: Path) -> list[Path]:
    from PIL import ImageOps
    файлы = []
    for к in пост["кадры"]:
        if not к.get("фото"):
            continue
        цель = папка / f'{к["фото"]}.jpg'
        with Image.open(ТУТ.parent / "промпты/картинки" / f'{к["фото"]}.png') as и:
            серое = ImageOps.autocontrast(ImageOps.grayscale(и.convert("RGB")), cutoff=2)
            цвет = ImageOps.colorize(серое, black=(18, 19, 15), white=(199, 226, 75))
            цвет.thumbnail((1100, 1100), Image.LANCZOS)
            цвет.save(цель, quality=80, optimize=True)
        файлы.append(цель)
    for к in пост["кадры"]:
        о = к.get("объект")
        if not о:
            continue
        цель = папка / f'{латиницей(о["файл"])}.png'
        исходник = ТУТ / "объекты" / f'{о["файл"]}.png'
        if исходник.exists():
            if о.get("дуотон", True):
                дуотон_с_альфой(исходник, цель)
            else:
                with Image.open(исходник) as и:
                    и = и.convert("RGBA")
                    и.thumbnail((1100, 1100), Image.LANCZOS)
                    и.save(цель, optimize=True)
            файлы.append(цель)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    всего = len(пост["кадры"])
    доски = []
    for н, к in enumerate(пост["кадры"], 1):
        имя = "Main.dc.html" if н == 1 else f"Kadr{н:02d}.dc.html"
        доски.append((имя, f"{н:02d} · {к['гигант'][:18]}", кадр(к, н / всего)))
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 3 * 1180, "y": i // 3 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)],
                 "launch": {"view": "canvas"}}
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = sorted(Path("/private/tmp/claude-501/bundled-skills").glob("*/*/design/seed-canvas.mjs"),
               key=lambda п: п.stat().st_mtime)[-1]
    страница = папка / "setka.html"
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"),
               "--out", str(страница), "--title", пост.get("название", "Сетка"),
               "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    for к in картинки(пост, папка):
        команда += ["--image", str(к)]
    р = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)],
                              capture_output=True, text=True)
    print((р.stderr.strip()[-300:] + "\n" if р.stderr.strip() else "") + проверка.stdout.strip()[:180])
    print("страница холста:", страница)


if __name__ == "__main__":
    main()
