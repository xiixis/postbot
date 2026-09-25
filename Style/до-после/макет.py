# -*- coding: utf-8 -*-
"""Макет поста в ленте: python3 макет.py посты/<пост>.json

Телефоны с лентой Instagram — по одному на каждую обложку — и под ними все кадры
карусели в ряд, как при пролистывании. Берёт готовые кадры из `кадры/<пост>/`, кладёт
`макет.png` туда же и JPG на стол рядом с кадрами. Ник условный: настоящий в пост
подставляет владелец, числа лайков не рисуются вовсе — выдумывать их нельзя.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
from стиль import СТОЛ, данные  # noqa: E402
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

ТЕЛЕФОН, ЗАЗОР, В = 640, 90, 2150
НИК = "ваш_аккаунт"

ИКОНКИ = {
    "сердце": "<path d='M12 20s-7-4.4-9.3-8.6C1.2 8.5 2.8 5 6.2 5c2 0 3.3 1.1 3.8 2 .5-.9 1.8-2 3.8-2 3.4 0 5 3.5 3.5 6.4C19 15.6 12 20 12 20z'/>",
    "коммент": "<path d='M20 11.5a8 8 0 0 1-11.6 7.1L4 20l1.4-4.2A8 8 0 1 1 20 11.5z'/>",
    "отправить": "<path d='M21 3 3 10.5l7 2.5 2.5 7L21 3zM10 13l5-5'/>",
    "закладка": "<path d='M6 3h12v18l-6-4.5L6 21z'/>",
}


def иконка(имя: str) -> str:
    return (f"<svg viewBox='0 0 24 24' fill='none' stroke='#111' stroke-width='1.8' "
            f"stroke-linejoin='round'>{ИКОНКИ[имя]}</svg>")


def телефон(кадр: Path, подпись: str, всего: int) -> str:
    точки = "".join(f"<i class='{'вкл' if н == 0 else ''}'></i>" for н in range(всего))
    return f"""<div class=телефон><div class=экран>
  <div class=статус><b>9:41</b><span>●●●  ▮</span></div>
  <div class=шапка><div class=ава><img src='{стиль.ЛОГО}'></div><b>{НИК}</b><span>•••</span></div>
  <img class=пост src='{данные(кадр)}'>
  <div class=действия>{иконка('сердце')}{иконка('коммент')}{иконка('отправить')}
    <div class=точки>{точки}</div>{иконка('закладка')}</div>
  <div class=текст><b>{НИК}</b> {подпись}</div>
</div></div>"""


def main():
    файл = Path(sys.argv[1])
    п = json.loads(файл.read_text(encoding="utf-8"))
    кадры = ТУТ / "кадры" / файл.stem
    карусель = sorted(кадры.glob("[0-9][0-9].png"))
    обложки = [кадры / "01.png"] + [кадры / f"обложка-{н}.png" for н in (2, 3, 4) if (кадры / f"обложка-{н}.png").exists()]
    первая = п["подпись"].split("\n")[0]
    лента = "".join(
        f"<div class=колонка><div class=имя>Обложка {н}</div>{телефон(о, первая, len(карусель))}</div>"
        for н, о in enumerate(обложки, 1))
    Ш = max(2400, len(обложки) * (ТЕЛЕФОН + ЗАЗОР) + 200)   # четвёртый телефон шире холста 2400
    ряд = "".join(f"<img src='{данные(к)}'>" for к in карусель)
    html = f"""<!doctype html><html><head><meta charset=utf-8><style>
{стиль.фейсы(("Golos", "golos-400", 400), ("Golos", "golos-700", 700))}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{Ш}px;height:{В}px;background:#D9DBD3;font-family:Golos,sans-serif;color:#111;
  -webkit-font-smoothing:antialiased;overflow:hidden}}
.лента{{display:flex;justify-content:center;gap:90px;padding-top:70px}}
.имя{{text-align:center;font-size:40px;font-weight:700;margin-bottom:26px;color:#333}}
.телефон{{width:640px;height:1320px;border-radius:92px;background:#0E0E0E;padding:22px;
  box-shadow:0 40px 90px rgba(0,0,0,.28)}}
.экран{{width:100%;height:100%;border-radius:72px;background:#fff;overflow:hidden;position:relative}}
.статус{{display:flex;justify-content:space-between;padding:26px 50px 10px;font-size:28px}}
.шапка{{display:flex;align-items:center;gap:18px;padding:18px 26px;font-size:28px}}
.шапка span{{margin-left:auto;letter-spacing:2px}}
.ава{{width:64px;height:64px;border-radius:50%;background:#111;display:grid;place-items:center;
  box-shadow:0 0 0 3px #fff,0 0 0 6px #E1306C}}
.ава img{{width:42px}}
.пост{{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}}
.действия{{display:flex;align-items:center;gap:20px;padding:22px 26px;position:relative}}
.действия svg{{width:44px;height:44px}}
.действия svg:last-child{{margin-left:auto}}
.точки{{position:absolute;left:58%;transform:translateX(-50%);display:flex;gap:9px}}
.точки i{{width:11px;height:11px;border-radius:50%;background:#C9C9C9;display:block}}
.точки i.вкл{{background:#3897F0}}
.текст{{padding:0 26px;font-size:28px;line-height:1.35}}
.подвал{{position:absolute;left:0;right:0;top:1560px}}
.подвал .имя{{margin-bottom:24px}}
.ряд{{display:flex;justify-content:center;gap:22px}}
.ряд img{{width:300px;height:400px;object-fit:cover;border-radius:22px;box-shadow:0 14px 34px rgba(0,0,0,.18)}}
</style></head><body>
<div class=лента>{лента}</div>
<div class=подвал><div class=имя>Карусель целиком</div><div class=ряд>{ряд}</div></div>
</body></html>"""
    снимок = кадры / "макет.png"
    ошибки = []
    if not браузер.снять(html, Ш, В, снимок, ошибки):
        raise SystemExit(f"макет не вышел: {ошибки}")
    with Image.open(снимок) as к:
        к = к.convert("RGB").resize((Ш, В), Image.LANCZOS)
        к.save(снимок)
        if п.get("папка"):
            к.save(СТОЛ / п["папка"] / "макет.jpg", quality=90)
    print(снимок)


if __name__ == "__main__":
    main()
