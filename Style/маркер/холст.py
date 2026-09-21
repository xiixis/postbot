# -*- coding: utf-8 -*-
"""Холст стиля «маркер»: python3 холст.py посты/<пост>.json

Разбор референса — в `ДИЗАЙН.md` рядом. Коротко: гигантская цифра у левого поля, заголовок
прописными справа от неё, фразы подсвечены маркером, шаги обведены от руки, снимок живёт
в макете телефона.

Из четырёх разобранных референсов этот единственный попал в наши пороги почти без правок:
у автора крупная строка 13,3–13,8% высоты кадра при нашем требовании 12–15%, контраст
13,5–14,2:1 при пороге 8:1. Поэтому кегли здесь перенесены как есть, а не задраны втрое.

Две вещи сделаны руками, а не средствами CSS.

**Маркер** — не ровный прямоугольник, а мазок: фон кладётся градиентом с неровным нижним
краем и лёгким наклоном. Ровная плашка читается как выделение в таблице, мазок — как след
текстовыделителя.

**Обводка-облачко** — SVG-путь с дрожанием в пару пикселей, а не `border-radius`. У
референса рамок нет ни одной: всё, что очерчено, очерчено от руки.
"""
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from помощник_холста import помощник as найти_помощника     # noqa: E402

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

БУМАГА, ЧЕРНИЛА = "#F1F2EA", "#171513"
ЛАЙМ, ТЁМНЫЙ, СВЕТЛЫЙ = стиль.ЛАЙМ, стиль.ТЁМНЫЙ, стиль.СВЕТЛЫЙ
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"

ПОЛЕ, ВЕРХ = 76, 112                    # 7% ширины и 8% высоты кадра
НИЗ_КОНТЕНТА = 1105                     # ниже — запас перед знаком и сама служебная зона


def голова(тёмный: bool = False) -> str:
    грунт = ТЁМНЫЙ if тёмный else БУМАГА
    цвет = СВЕТЛЫЙ if тёмный else ЧЕРНИЛА
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;
        background:{грунт};color:{цвет} }}
    /* Цифра залита лаймом и обведена чернилами: лайм на светлой бумаге сам по себе
       бледен, обводка возвращает ему вес, не превращая в тёмное пятно. */
    .цифра {{ position:absolute;left:{ПОЛЕ}px;top:{ВЕРХ}px;{К};font-size:230px;line-height:.78;
        color:{ЛАЙМ};-webkit-text-stroke:4px {ЧЕРНИЛА};letter-spacing:-.04em }}
    .заголовок {{ position:absolute;left:{ПОЛЕ + 175}px;right:{ПОЛЕ}px;top:{ВЕРХ + 6}px;
        {К};font-size:76px;line-height:1.06;letter-spacing:-.02em;text-transform:uppercase;
        height:250px }}
    .тело {{ position:absolute;left:{ПОЛЕ}px;width:800px;{Т};font-size:46px;line-height:1.34 }}
    .тело p {{ margin:0 0 26px }}
    /* Мазок маркера: неровный нижний край и лёгкий наклон — след текстовыделителя,
       а не заливка ячейки. */
    .маркер {{ background:linear-gradient(103deg, rgba(199,226,75,0) 0%, {ЛАЙМ} 2%,
        {ЛАЙМ} 97%, rgba(199,226,75,.35) 100%);
        padding:2px 10px 4px 10px;box-decoration-break:clone;
        -webkit-box-decoration-break:clone }}
    .шаг {{ position:absolute;{Т};font-size:38px;line-height:1.22;text-align:center;
        display:flex;align-items:center;justify-content:center;padding:18px 22px }}
    .телефон {{ position:absolute;border:14px solid {ЧЕРНИЛА};border-radius:56px;
        overflow:hidden;background:{ЧЕРНИЛА};box-shadow:0 36px 80px rgba(23,21,19,.22) }}
    .телефон img {{ display:block;width:100%;height:100%;object-fit:cover }}
    .кот {{ position:absolute;z-index:3 }}
    .знак {{ position:absolute;left:{ПОЛЕ}px;bottom:205px;height:44px;z-index:4 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;z-index:4;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{ЛАЙМ}"></div>')


def обводка(ширина: int, высота: int, семя: int, цвет: str = ЧЕРНИЛА) -> str:
    """Скруглённый прямоугольник, нарисованный от руки: каждая сторона слегка гуляет.
    Ровный `border-radius` выдаёт машинную рамку — у референса таких нет ни одной."""
    т = random.Random(семя)
    дрожь = lambda: т.uniform(-3.5, 3.5)
    r = 26
    путь = (f"M{r + дрожь()},{дрожь()} L{ширина - r + дрожь()},{дрожь()} "
            f"Q{ширина + дрожь()},{дрожь()} {ширина + дрожь()},{r + дрожь()} "
            f"L{ширина + дрожь()},{высота - r + дрожь()} "
            f"Q{ширина + дрожь()},{высота + дрожь()} {ширина - r + дрожь()},{высота + дрожь()} "
            f"L{r + дрожь()},{высота + дрожь()} "
            f"Q{дрожь()},{высота + дрожь()} {дрожь()},{высота - r + дрожь()} "
            f"L{дрожь()},{r + дрожь()} Q{дрожь()},{дрожь()} {r + дрожь()},{дрожь()} Z")
    return (f'<svg width="{ширина + 8}" height="{высота + 8}" viewBox="-4 -4 {ширина + 8} {высота + 8}" '
            f'style="position:absolute;left:0;top:0;overflow:visible">'
            f'<path d="{путь}" fill="none" stroke="{цвет}" stroke-width="3" '
            f'stroke-linecap="round"/></svg>')


def стрелка(из_: tuple, в: tuple, семя: int) -> str:
    """Пунктирная связка между блоками — как у автора между шагами."""
    т = random.Random(семя)
    сх, су = из_
    кх, ку = в
    изгиб = т.uniform(-60, 60)
    return (f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1440px;'
            f'pointer-events:none"><path d="M{сх},{су} Q{(сх + кх) / 2 + изгиб},'
            f'{(су + ку) / 2} {кх},{ку}" fill="none" stroke="{ЧЕРНИЛА}" stroke-width="3" '
            f'stroke-dasharray="10 12" stroke-linecap="round"/></svg>')


def подсветить(текст: str) -> str:
    """Фразы в двойных звёздочках — под маркер. Так автор выделяет главное в абзаце."""
    части = текст.split("**")
    собрано = []
    for н, часть in enumerate(части):
        собрано.append(f'<span class=маркер>{часть}</span>' if н % 2 else часть)
    return "".join(собрано)


def кот(к: dict) -> str:
    """Кот файлом, а не данными внутри страницы: вшитый PNG раздувал доску за 2 МБ, и редактор
    холста выбрасывал её при сохранении."""
    где = ";".join(f"{ключ}:{к[ключ]}px" for ключ in ("left", "top", "right", "bottom") if ключ in к)
    return f'<img class=кот src="kot-{латиницей(к["поза"])}.webp" style="height:{к["высота"]}px;{где}">'


def коты_постa(пост: dict) -> list[dict]:
    """Все коты поста: на обложках, кадрах и финале."""
    места = [пост.get("обложка", {}), пост.get("обложка_число", {}), пост.get("обложка_допосле", {}),
             пост.get("финал", {}), *пост.get("кадры", [])]
    return [м["кот"] for м in места if м.get("кот")]


def обложка(о: dict, доля: float) -> str:
    return голова(тёмный=True) + f"""<div class=кадр>
  <div class=заголовок style="left:{ПОЛЕ}px;top:230px;font-size:104px;color:{СВЕТЛЫЙ}">
    {подсветить(о['заголовок'])}
  </div>
  <div class=тело style="top:700px;color:{СВЕТЛЫЙ};width:600px;font-size:44px">
    <p>{о['под']}</p>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def обложка_число(о: dict, доля: float) -> str:
    """Б — число: гигант лаймом во весь верх, строка под ним. Цифра и так герой стиля,
    здесь она вынесена на обложку."""
    return голова(тёмный=True) + f"""<div class=кадр>
  <div style="position:absolute;left:{ПОЛЕ}px;top:180px;{К};font-size:400px;line-height:.82;
       color:{ЛАЙМ};-webkit-text-stroke:6px {ТЁМНЫЙ};letter-spacing:-.05em">{о['число']}</div>
  <div class=заголовок style="left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:620px;font-size:92px;color:{СВЕТЛЫЙ};height:auto">
    {подсветить(о['заголовок'])}
  </div>
  <div class=тело style="top:900px;color:{СВЕТЛЫЙ};width:760px;font-size:44px"><p>{о['под']}</p></div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: зачёркнутая строка сверху, подсвеченная маркером снизу."""
    строка = f"{Т};font-size:52px;line-height:1.3;position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px"
    return голова(тёмный=True) + f"""<div class=кадр>
  <div class=заголовок style="left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:200px;font-size:96px;color:{СВЕТЛЫЙ};height:auto">
    {подсветить(о['заголовок'])}
  </div>
  <div style="{строка};top:620px;color:#9A9C92;text-decoration:line-through">{о['было']}</div>
  <div style="{строка};top:740px;color:{СВЕТЛЫЙ}"><span class=маркер style="color:{ЧЕРНИЛА}">{о['стало']}</span></div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def высота_текста(абзацы: list[str], ширина: int, кегль: int = 46) -> int:
    """Оценка высоты блока текста до отрисовки. Нужна, чтобы генератор сам ловил наложение
    на нижние блоки: у Golos знак занимает около половины кегля, отсюда знаков в строке."""
    в_строке = max(1, int(ширина / (кегль * 0.5)))
    строк = sum(max(1, -(-len(а.replace("**", "")) // в_строке)) for а in абзацы)
    return int(строк * кегль * 1.34 + (len(абзацы) - 1) * 26)


def кадр(номер: int, к: dict, доля: float) -> str:
    шаги = ""
    if к.get("шаги"):
        ширина, высота, шаг_у, старт = 300, 100, 118, 640
        низ_текста = ВЕРХ + 300 + высота_текста(к["текст"], 560 if к.get("снимок") else 880)
        if старт < низ_текста + 30:
            raise SystemExit(f"кадр {номер}: текст кончается на {низ_текста}, а шаги "
                             f"начинаются с {старт} — сократить текст или опустить шаги")
        низ = старт + (len(к["шаги"]) - 1) * шаг_у + высота
        if низ > НИЗ_КОНТЕНТА:
            raise SystemExit(f"кадр {номер}: {len(к['шаги'])} шагов кончаются на {низ}, "
                             f"а служебная зона начинается с {НИЗ_КОНТЕНТА} — убрать шаг "
                             f"или поднять начало блока")
        for i, ш in enumerate(к["шаги"]):
            if len(ш) > 18:
                raise SystemExit(f"кадр {номер}: шаг «{ш}» длиннее 18 знаков — "
                                 f"в обводку высотой {высота} px он не влезет")
            x = ПОЛЕ
            y = старт + i * шаг_у
            шаги += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{ширина}px;'
                     f'height:{высота}px">{обводка(ширина, высота, семя=номер * 10 + i)}'
                     f'<div class=шаг style="inset:0">{ш}</div></div>')
            if i:
                шаги += стрелка((x + ширина // 2, y - 16),
                                (x + ширина // 2, y - шаг_у + высота + 16),
                                семя=номер * 20 + i)
    телефон = ""
    if к.get("снимок"):
        телефон = (f'<div class=телефон style="right:-16px;top:540px;width:400px;height:570px;'
                   f'transform:rotate(7deg)"><img src="{латиницей(к["снимок"])}.jpg"></div>')
    абзацы = "\n".join(f"    <p>{подсветить(а)}</p>" for а in к["текст"])
    return голова() + f"""<div class=кадр>
  <div class=цифра>{номер}</div>
  <div class=заголовок>{к['заголовок']}</div>
  <div class=тело style="top:{ВЕРХ + 300}px;width:{560 if к.get('снимок') else 880}px">
{абзацы}
  </div>
  {телефон}
  {шаги}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова(тёмный=True) + f"""<div class=кадр>
  <div class=заголовок style="left:{ПОЛЕ}px;top:250px;font-size:104px;color:{ЛАЙМ}">{ф['крупно']}</div>
  <div class=тело style="top:560px;color:{СВЕТЛЫЙ};width:640px;font-weight:700;font-size:46px">
    <p>{ф['текст']}</p>
    <p style="font-weight:400;font-size:38px">{ф['под']}</p>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Снимки для макета телефона: вертикальная обрезка под экран 330×380."""
    файлы = []
    for к in пост["кадры"]:
        if not к.get("снимок"):
            continue
        цель = папка / f'{латиницей(к["снимок"])}.jpg'
        исходник = ТУТ.parent / "подборка-сайтов/сайты" / f'{к["снимок"]}.png'
        with Image.open(исходник) as и:
            и = и.convert("RGB")
            ширина, высота = и.size
            нужная = min(высота, int(ширина / (470 / 700)))
            и = и.crop((0, 0, int(нужная * 470 / 700), нужная))
            и.thumbnail((700, 1050), Image.LANCZOS)
            и.save(цель, quality=80, optimize=True)
        файлы.append(цель)
    for к in коты_постa(пост):
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


ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: холст без них не выкладывается.
    обложки = {"сцена": lambda: обложка(пост["обложка"], 1 / всего),
               "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
               "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
    главная = пост.get("главная", "сцена")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['заголовок'][:24]}",
                      кадр(н, к, (н + 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 4 * 1180, "y": i // 4 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)],
                 "launch": {"view": "canvas"}}
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = найти_помощника()
    страница = папка / f"{латиницей(файл.stem)}.html"
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"),
               "--out", str(страница), "--title", пост.get("название", "Холст"),
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
