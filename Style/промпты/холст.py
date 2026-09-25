# -*- coding: utf-8 -*-
"""Холст согласования стиля «промпты»: python3 холст.py посты/<пост>.json

Стиль снят с разобранного референса (`референсы/bezikovkirill-DcqI7Zhjt0m/паспорт.md`):
фотореалистичная сцена служит фоном кадра, текст стоит прямо на ней — не на плашке и не
под затемняющей вуалью, а на высветленной части сцены. Сцена обесцвечена почти до серого,
поэтому одного тёмного акцентного цвета хватает на весь кадр.

Числа вёрстки — из раздела 11 паспорта, пересчитанные на меру холста 1080×1440 (снимок
×1,5 даёт наш кадр 1620×2160): левая рейка 7,5% ширины, верх текста 8% высоты, заголовок
12–14% высоты строкой, три уровня кегля с перепадом не ниже 4:1.

Акцент — наш оливковый, а не кирпичный красный автора: фирменный цвет один на все стили.
Он затемнён до #2F3A07, потому что #56690C даёт к кремовому 4,9:1 и не берёт наш порог 8:1.
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

КРЕМ, ЧЕРНИЛА = "#EAE4DE", "#12130E"
# Акцент — фирменный оливковый, затемнённый до нашего порога: #56690C даёт к крему 4,9:1
# и мелкую метку не держит, #2F3A07 — 9,6:1 при том же тоне. Красного в стиле нет: у
# референса он свой, у нас акцент один на все стили.
АКЦЕНТ = "#2F3A07"
ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ = стиль.ТЁМНЫЙ, стиль.ЛАЙМ, стиль.СВЕТЛЫЙ
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"

РЕЙКА, ВЕРХ = 81, 115        # 7,5% ширины и 8% высоты холста


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;background:{КРЕМ};color:{ЧЕРНИЛА} }}
    .сцена {{ position:absolute;inset:0;width:100%;height:100%;object-fit:cover }}
    /* Высветление вместо вуали: текст читается по осветлённой сцене, а не по затемнённой.
       Затемнение здесь ломает главный приём — сцена должна оставаться светлой. */
    .свет {{ position:absolute;inset:0;background:linear-gradient(180deg,
        rgba(234,228,222,.98) 0%, rgba(234,228,222,.96) 44%,
        rgba(234,228,222,.62) 60%, rgba(234,228,222,0) 76%) }}
    .текст {{ position:absolute;left:{РЕЙКА}px;right:{РЕЙКА}px;top:{ВЕРХ}px }}
    /* Подвал: служебная зона стоит на чистом кремовом, а не на фотосцене. Без него знак
       тонул в тёмных местах снимка — оливковая «четвёрка» по цепи или по камню не читается. */
    .подвал {{ position:absolute;left:0;right:0;bottom:0;height:320px;
        background:linear-gradient(180deg, rgba(234,228,222,0) 0%, rgba(234,228,222,.86) 42%,
        rgba(234,228,222,.98) 66%, {КРЕМ} 100%) }}
    .бейдж {{ {К};display:inline-block;font-size:40px;color:{КРЕМ};background:{АКЦЕНТ};
        border-radius:36px;padding:8px 30px;letter-spacing:.04em }}
    .заголовок {{ {К};line-height:1.0;letter-spacing:-.035em;margin:26px 0 0;
        text-shadow:0 4px 18px rgba(18,19,14,.16) }}
    .обещание {{ {Т};font-weight:700;font-size:46px;line-height:1.28;margin:28px 0 0;
        max-width:900px;text-wrap:pretty }}
    .метка {{ {Т};font-weight:700;font-size:38px;letter-spacing:.14em;color:{АКЦЕНТ};
        margin:44px 0 0 }}
    .тело {{ {Т};font-size:38px;line-height:1.36;margin:14px 0 0;max-width:920px;text-wrap:pretty }}
    .тело p {{ margin:0 }}
    .кот {{ position:absolute;z-index:3 }}
    .знак {{ position:absolute;left:80px;bottom:205px;height:44px }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    """Полоса — фирменный лайм на всех кадрах, светлых и тёмных: это знак бренда, и он
    должен быть одного цвета во всей карусели. На светлом лайм бледный сам по себе, поэтому
    под ним лежит тонкая тёмная линия — она держит край, не перекрашивая полосу."""
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    цвет = ЛАЙМ
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{цвет}"></div>')


def кегль(слово: str) -> int:
    """Заголовок в одно слово держит высоту строки 12–14% кадра. Длинное слово на ширине
    918 px в такой кегль не влезает, поэтому кегль привязан к длине — без этого строка
    уезжает за рейку, и вёрстка рвётся молча."""
    ширина = 1080 - 2 * РЕЙКА
    средняя = 0.63          # доля кегля на знак у Onest 800: широкие Д, Ш, В режутся при 0,54
    return min(240, int(ширина / (средняя * max(len(слово), 1))))


def сцена_файл(к: dict) -> str:
    """Имя сцены на холсте: помощник принимает только латиницу, цифры, точки и дефисы."""
    return латиницей(Path(к["картинка"]).stem) + ".jpg"


def кот(к: dict) -> str:
    где = {ключ: к[ключ] for ключ in ("left", "top", "right", "bottom") if ключ in к}
    return стиль.кот(к["поза"], к["высота"], класс="кот", **где)


def обложка(о: dict, доля: float) -> str:
    return голова() + f"""<div class=кадр>
  <div class=текст>
    <div class=метка style="margin:0">{о['над']}</div>
    <div class=заголовок style="font-size:{кегль(о['заголовок'])}px;margin-top:34px">{о['заголовок']}</div>
    <div class=обещание style="font-size:48px">{о['под']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def приём(номер: int, к: dict, доля: float) -> str:
    строки = "\n".join(f"      <p>{с}</p>" for с in к["промпт"])
    return голова() + f"""<div class=кадр>
  <img class=сцена src="{сцена_файл(к)}">
  <div class=свет></div>
  <div class=подвал></div>
  <div class=текст>
    <div class=бейдж>{номер:02d}</div>
    <div class=заголовок style="font-size:{кегль(к['заголовок'])}px">{к['заголовок']}</div>
    <div class=обещание>{к['обещание']}</div>
    <div class=метка>ПРОМПТ</div>
    <div class=тело>
{строки}
    </div>
  </div>
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div class=текст style="top:210px">
    <div class=заголовок style="font-size:{кегль(ф['крупно'])}px;color:{ЛАЙМ};text-shadow:none">{ф['крупно']}</div>
    <div class=обещание style="font-size:52px;color:{СВЕТЛЫЙ}">{ф['текст']}</div>
    <div class=обещание style="font-size:40px;color:{СВЕТЛЫЙ};margin-top:20px">{ф['под']}</div>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Сцены ужимаются до ширины кадра и уходят в JPEG: восемь исходников по 2 МБ дают
    страницу холста тяжелее допустимых 16 МБ, а в кадре 1080 px разницы не видно."""
    файлы = []
    for к in пост["кадры"]:
        цель = папка / сцена_файл(к)
        with Image.open(ТУТ / "картинки" / к["картинка"]) as и:
            и = и.convert("RGB")
            и.thumbnail((1080, 1080 * 4), Image.LANCZOS)
            и.save(цель, quality=74, optimize=True)     # холст просит держать файл под 70 КБ
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
    пост = json.loads(файл.read_text(encoding="utf-8"))
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    всего = len(пост["кадры"]) + 2
    доски = [("Main.dc.html", "01 · Обложка", обложка(пост["обложка"], 1 / всего))]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['заголовок']}",
                      приём(н, к, (н + 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for имя, _, html in доски:
        (папка / имя).write_text(html, encoding="utf-8")

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600,
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
