# -*- coding: utf-8 -*-
"""Холст стиля «отчёт»: python3 холст.py посты/<пост>.json

Стиль вырос из темы, а не из вкусовых предпочтений: речь о китайской лаборатории,
открытых весах и таблицах бенчмарков — значит и кадр устроен как страница технического
отчёта. Отсюда всё остальное.

**Бумага холодная, серо-голубая** (#E8EAED), а не наш кремовый: крем — бумага статьи о
сервисах, а здесь отчёт о результатах. **Акцент — киноварь** (#C1272D), цвет китайского
оттиска-печати; номер кадра и стоит красным квадратом-печатью, а не пилюлей.
**Число — герой кадра:** в разобранном ролике счёт всё время шёл деньгами и временем
(2,8 триллиона, ×3, 20 часов, 10 часов против 7 лет), поэтому кадр строится вокруг одного
числа, набранного антиквой Cormorant, а поясняет его гротеск Golos. Контраст антиквы и
гротеска — то, чего нет ни в одном другом нашем стиле.

Ноль скруглений, ноль теней, тонкие линии как в таблице результатов. Фирменный лайм
остаётся только в полосе со знаком — это подпись канала, а не часть стиля.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

БУМАГА, ГРАФИТ = "#E8EAED", "#15181C"
КИНОВАРЬ = "#C1272D"                     # к бумаге 5,6:1 — только для крупного и для печати
ЛИНИЯ = "#C3C8CE"
ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ = стиль.ТЁМНЫЙ, стиль.ЛАЙМ, стиль.СВЕТЛЫЙ
А = "font-family:Cormorant,Georgia,serif;font-weight:700"     # антиква — числа и заголовки
Г = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"      # гротеск — пояснения

ПОЛЕ, ВЕРХ = 84, 120
НИЗ_КОНТЕНТА = 1164                      # ниже начинается служебная зона знака и полосы


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Cormorant", "cormorant-700", 700), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;
        background:{БУМАГА};color:{ГРАФИТ} }}
    /* Печать с номером: оттиск, а не пилюля — номер кадра как штамп в углу документа. */
    .печать {{ position:absolute;right:{ПОЛЕ}px;top:{ВЕРХ}px;width:76px;height:76px;
        background:{КИНОВАРЬ};color:{БУМАГА};{А};font-size:46px;
        display:flex;align-items:center;justify-content:center }}
    .число {{ position:absolute;left:{ПОЛЕ}px;{А};font-size:300px;
        line-height:.9;letter-spacing:-.02em;color:{ГРАФИТ} }}
    .единица {{ position:absolute;left:{ПОЛЕ}px;{Г};font-weight:700;font-size:38px;
        color:{КИНОВАРЬ} }}
    .заголовок {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;{А};font-size:104px;
        line-height:1.0;letter-spacing:-.01em }}
    .текст {{ position:absolute;left:{ПОЛЕ}px;width:820px;{Г};font-size:44px;line-height:1.34 }}
    .текст p {{ margin:0 0 28px }}
    .черта {{ position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;height:1px;background:{ЛИНИЯ} }}
    /* Снимок в рамке в одну линию: так выглядит иллюстрация в отчёте, без теней и скруглений. */
    .снимок {{ position:absolute;left:{ПОЛЕ}px;width:912px;height:250px;object-fit:cover;
        object-position:top center;border:1px solid {ЛИНИЯ} }}
    .кот {{ position:absolute;z-index:3 }}
    .знак {{ position:absolute;left:80px;bottom:205px;height:44px;z-index:4 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;z-index:4;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{ЛАЙМ}"></div>')


def кегль_числа(текст: str) -> int:
    """Число-герой занимает строку целиком: короткое ставится крупнее длинного."""
    знаков = len(текст)
    return 300 if знаков <= 3 else 210 if знаков <= 6 else 140 if знаков <= 10 else 104


ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                "yu", "ya"]))


def латиницей(имя: str) -> str:
    """Помощник холста берёт имена картинок только латиницей."""
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


def кот(к: dict) -> str:
    """Кот файлом: вшитый данными PNG раздувает доску за предел помощника холста (2 МБ)."""
    где = ";".join(f"{ключ}:{к[ключ]}px" for ключ in ("left", "top", "right", "bottom") if ключ in к)
    return f'<img class=кот src="kot-{латиницей(к["поза"])}.webp" style="height:{к["высота"]}px;{где}">' 


def обложка(о: dict, доля: float) -> str:
    return голова() + f"""<div class=кадр>
  <div class=черта style="top:{ВЕРХ + 110}px"></div>
  <div class=заголовок style="top:{ВЕРХ + 170}px;font-size:132px">{о['заголовок']}</div>
  <div class=текст style="top:{ВЕРХ + 560}px;width:640px;font-size:46px"><p>{о['под']}</p></div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def обложка_число(о: dict, доля: float) -> str:
    """Б — число-герой прямо на обложке: стиль и так держится на числах."""
    return голова() + f"""<div class=кадр>
  <div class=число style="font-size:{кегль_числа(о['число'])}px;top:auto;bottom:980px">{о['число']}</div>
  <div class=единица style="top:470px">{о['единица']}</div>
  <div class=черта style="top:540px"></div>
  <div class=заголовок style="top:580px;font-size:96px">{о['заголовок']}</div>
  <div class=текст style="top:860px;width:660px;font-size:44px"><p>{о['под']}</p></div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: две строки отчёта, старая зачёркнута."""
    строка = "position:absolute;left:120px;right:420px;font-size:52px;line-height:1.3"   # справа стоит кот
    return голова() + f"""<div class=кадр>
  <div class=черта style="top:{ВЕРХ + 110}px"></div>
  <div class=заголовок style="top:{ВЕРХ + 170}px;font-size:110px">{о['заголовок']}</div>
  <div style="{строка};top:760px;color:#7C7F76;text-decoration:line-through">{о['было']}</div>
  <div style="{строка};top:880px;font-weight:700">{о['стало']}</div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def страница(номер: int, к: dict, доля: float) -> str:
    """Кадр-страница отчёта. Зоны заданы числами и не зависят от величины числа-героя:
    иначе короткое «K3» и длинное «10 часов» двигают заголовок и текст по-разному, и
    соседние страницы перестают совпадать — а отчёт держится именно на одинаковой сетке."""
    размер = кегль_числа(к["число"])
    со_снимком = bool(к.get("снимок"))
    текст = "\n".join(f"    <p>{а}</p>" for а in к["текст"])
    знаков = sum(len(а) for а in к["текст"])
    кегль = 40 if со_снимком or знаков > 180 else 46
    снимок = (f'<img class=снимок src="{к["снимок"]}.jpg" style="top:964px">'
              if со_снимком else "")
    return голова() + f"""<div class=кадр>
  <div class=печать>{номер:02d}</div>
  <div class=число style="font-size:{размер}px;top:auto;bottom:1085px">{к['число']}</div>
  <div class=единица style="top:378px">{к['единица']}</div>
  <div class=черта style="top:448px"></div>
  <div class=заголовок style="top:486px;font-size:84px">{к['заголовок']}</div>
  <div class=текст style="top:700px;font-size:{кегль}px">
{текст}
  </div>
  {снимок}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div class=черта style="top:230px;background:rgba(255,255,255,.22)"></div>
  <div class=заголовок style="top:290px;font-size:128px;color:{ЛАЙМ}">{ф['крупно']}</div>
  <div class=текст style="top:640px;width:620px;color:{СВЕТЛЫЙ};font-weight:700">
    <p>{ф['текст']}</p>
    <p style="font-weight:400;font-size:38px">{ф['под']}</p>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    файлы = []
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
    for к in пост["кадры"]:
        if not к.get("снимок"):
            continue
        цель = папка / f'{к["снимок"]}.jpg'
        with Image.open(ТУТ.parent / "подборка-сайтов/сайты" / f'{к["снимок"]}.png') as и:
            и = и.convert("RGB")
            ширина, высота = и.size
            и = и.crop((0, 0, ширина, min(int(высота * 0.8), int(ширина / (912 / 250)))))
            и.thumbnail((1100, 1100), Image.LANCZOS)
            и.save(цель, quality=78, optimize=True)
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

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: холст без них не выкладывается.
    обложки = {"страница": lambda: обложка(пост["обложка"], 1 / всего),
               "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
               "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
    главная = пост.get("главная", "страница")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['заголовок']}",
                      страница(н, к, (н + 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)],
                 "launch": {"view": "canvas"}}
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    картинки(пост, папка)          # картинки и коты рядом с досками
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
