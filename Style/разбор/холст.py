# -*- coding: utf-8 -*-
"""Холст согласования стиля «разбор»: python3 холст.py посты/<пост>.json

Стиль снят с разобранного референса (`референсы/ythemark-DdEJxI-mfRT/паспорт.md`). Это
не подборка, а разбор одного инструмента: обложка с обещанием, потом кадры «что это»,
«чем отличается», «что умеет», и у каждого — широкий снимок экрана как доказательство.

Приёмы источника: жёсткая вертикальная схема (поле → заголовок → два абзаца → снимок),
ноль радиусов, ноль границ, ноль теней, три цвета на всю карусель, приглушённого серого
нет, фон не плоский — мелкое зерно и диагональный градиент.

Числа — из раздела 11 паспорта, пересчитанные на меру холста 1080×1440: левое поле 7% =
75 px, верхнее 9% = 130 px, ширина снимка 86% = 929 px, верх снимка на 55–59% высоты.

Что изменено. Кегли подняты в 2,5–3 раза, перепад доведён до 3:1, текста на кадре втрое
меньше — иначе в ленте не прочесть. Индиго автора заменено нашими чернилами и оливой:
цвет — это подпись канала, а не приём. Подсветка строки сделана выворотом по плотной
плашке: у автора текст на полупрозрачной плашке падает до 6,8:1 при нашем пороге 8:1.
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

КРЕМ, ЧЕРНИЛА = "#F2EFE8", "#12130E"
АКЦЕНТ = "#2F3A07"                      # фирменная олива, затемнённая до 9,6:1 по крему
ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ = стиль.ТЁМНЫЙ, стиль.ЛАЙМ, стиль.СВЕТЛЫЙ
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"

ПОЛЕ, ВЕРХ = 75, 130                    # 7% ширины и 9% высоты холста
СНИМОК_ШИРИНА, СНИМОК_ВЕРХ = 929, 800   # 86% ширины; верх на 55,5% высоты


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    /* Фон не плоский: диагональный градиент с перепадом около 11% — приём источника,
       он снимает ощущение пустой заливки, оставаясь незаметным. */
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;color:{ЧЕРНИЛА};
        background:linear-gradient(140deg, #F6F3ED 0%, {КРЕМ} 52%, #E9E4DA 100%) }}
    .заголовок {{ position:absolute;left:{ПОЛЕ}px;top:{ВЕРХ}px;{К};line-height:1.06;
        letter-spacing:-.02em;font-size:88px;color:{АКЦЕНТ} }}
    .крупно {{ letter-spacing:-.035em;line-height:1.0 }}
    .абзацы {{ position:absolute;left:{ПОЛЕ}px;width:886px;{Т};font-size:52px;line-height:1.28 }}
    .абзацы p {{ margin:0 0 34px }}
    .снимок {{ position:absolute;left:{ПОЛЕ}px;top:{СНИМОК_ВЕРХ}px;width:{СНИМОК_ШИРИНА}px;
        height:330px;object-fit:cover;object-position:top center }}
    .кот {{ position:absolute;z-index:3 }}
    .знак {{ position:absolute;left:80px;bottom:205px;height:44px;z-index:4 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;z-index:4;
        box-shadow:0 1px 0 rgba(18,19,14,.30) }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    """Полоса — фирменный лайм на всех кадрах: это знак бренда, он один во всей карусели."""
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{ЛАЙМ}"></div>')


def кегль(строки: list[str], предел: int = 230) -> int:
    """По самой длинной строке: у Onest 800 знак занимает около 0,63 кегля."""
    длинная = max((len(с) for с in строки), default=1)
    return min(предел, int((1080 - 2 * ПОЛЕ) / (0.63 * max(длинная, 1))))


def кот(к: dict) -> str:
    где = {ключ: к[ключ] for ключ in ("left", "top", "right", "bottom") if ключ in к}
    return стиль.кот(к["поза"], к["высота"], класс="кот", **где)


def обложка(о: dict, доля: float) -> str:
    размер = кегль(о["заголовок"] + [о["подсветка"]], предел=140)
    строки = "<br>".join(о["заголовок"])
    под = " ".join(о["под"])
    return голова() + f"""<div class=кадр>
  <div class="заголовок крупно" style="font-size:{размер}px;top:300px;color:{ЧЕРНИЛА}">
    <!-- Подсветка — выворотка по плотной плашке: текст на полупрозрачной падает до 6,8:1. -->
    <span style="background:{АКЦЕНТ};color:{КРЕМ};padding:6px 18px">{о['подсветка']}</span><br>{строки}
  </div>
  <div class=абзацы style="top:900px"><p>{под}</p></div>
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def разбор(к: dict, доля: float) -> str:
    абзацы = "\n".join(f"    <p>{' '.join(а)}</p>" for а in к["абзацы"])
    return голова() + f"""<div class=кадр>
  <div class=заголовок>{'<br>'.join(к['заголовок'])}</div>
  <div class=абзацы style="top:{360 if len(к['заголовок']) > 1 else 280}px;font-size:{52 if к.get('снимок') else 60}px">
{абзацы}
  </div>
  {f'<img class=снимок src="{к["снимок"]}.jpg">' if к.get("снимок") else ""}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div class="заголовок крупно" style="font-size:{кегль([ф['крупно']])}px;top:230px;color:{ЛАЙМ}">{ф['крупно']}</div>
  <div class=абзацы style="top:520px;color:{СВЕТЛЫЙ}">
    <p style="font-weight:700">{ф['текст']}</p>
    <p style="font-size:40px">{ф['под']}</p>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Снимки режутся под рамку кадра: 929×330 — это пропорция 2,8, середина диапазона
    источника (2,3–3,3). Иначе cover срезает страницу по бокам."""
    файлы = []
    for к in пост["кадры"]:
        if not к.get("снимок"):          # кадр без снимка: у него текст крупнее и во всю высоту
            continue
        цель = папка / f"{к['снимок']}.jpg"
        with Image.open(ТУТ.parent / "подборка-сайтов/сайты" / f"{к['снимок']}.png") as и:
            и = и.convert("RGB")
            ширина, высота = и.size
            и = и.crop((0, 0, ширина, min(высота, int(ширина / (СНИМОК_ШИРИНА / 330)))))
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
    пост = json.loads(файл.read_text(encoding="utf-8"))
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    всего = len(пост["кадры"]) + 2
    доски = [("Main.dc.html", "01 · Обложка", обложка(пост["обложка"], 1 / всего))]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {' '.join(к['заголовок'])}",
                      разбор(к, (н + 1) / всего)))
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
