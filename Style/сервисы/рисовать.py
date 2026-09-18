# -*- coding: utf-8 -*-
"""Фото-Карусель, стиль «подборка сервисов»: навык → значки сервисов → карточка с пояснением.

`python3 рисовать.py посты/<пост>.json [02 05]` — кадры 1620×2160 в `кадры/<пост>/`; без номеров
ещё и JPG 1080×1440 с подписью на стол, в папку из поля «папка».

Вёрстка повторяет холст согласования (claude.ai, поле «холст» в посте): там кадр 1080×1440,
здесь всё ×1,5. Координаты кота в посте — в мерах холста, как их сдвинул владелец.
Общее для стилей (лайм и олива, шрифты, знак с полосой, кот, замер запаса) — `../стиль.py`.
"""
import json, sys, time
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
from стиль import W, H, СТОЛ, КРЕМ, ОЛИВА, ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ, данные, кот  # noqa: E402
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

К = 1.5                                  # холст согласования 1080×1440 → кадр 1620×2160
ЧЕРНИЛА, МЯГКИЙ, ТИХИЙ = "#12130E", "#3A3E33", "#A3A69A"
П: dict = {}


def px(холст: float) -> int:
    return round(холст * К)


def фейсы() -> str:
    return стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
                       латиница=стиль.ЛАТИНИЦА + ",U+2192")


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{КРЕМ};color:{ЧЕРНИЛА};font-family:Golos,sans-serif;position:relative;-webkit-font-smoothing:antialiased}}
.крупно{{font-family:Onest;font-weight:800;letter-spacing:-.03em;text-wrap:balance}}
/* кадр навыка */
.стопка{{position:absolute;left:{px(80)}px;right:{px(80)}px;top:{px(120)}px;bottom:{px(350)}px;display:flex;
  flex-direction:column;align-items:center;justify-content:center;gap:{px(52)}px;text-align:center}}
.шапка{{display:flex;flex-direction:column;align-items:center;gap:{px(22)}px}}
.номер{{font-family:Onest;font-weight:800;font-size:{px(44)}px;color:{КРЕМ};background:{ОЛИВА};
  border-radius:{px(44)}px;padding:{px(8)}px {px(34)}px}}
.навык{{font-size:{px(88)}px;line-height:1.05}}
.сервисы{{display:flex;flex-direction:column;align-items:center;gap:{px(26)}px}}
.круги{{display:flex;gap:{px(30)}px;justify-content:center}}
.круг{{width:{px(184)}px;height:{px(184)}px;border-radius:50%;background:#FFFFFF;display:flex;align-items:center;
  justify-content:center;box-shadow:0 {px(10)}px {px(30)}px rgba(18,19,14,.10)}}
.круг img{{width:{px(118)}px;height:{px(118)}px;object-fit:contain}}
.имена{{font-weight:700;font-size:{px(40)}px;color:{МЯГКИЙ}}}
.карточка{{font-size:{px(45)}px;line-height:1.3;background:#FFFFFF;border-radius:{px(44)}px;padding:{px(50)}px {px(56)}px;
  display:flex;flex-direction:column;gap:{px(26)}px;text-wrap:pretty;align-self:stretch;
  box-shadow:0 {px(16)}px {px(50)}px rgba(18,19,14,.07)}}
/* обложка */
.обложка{{position:absolute;left:{px(80)}px;right:{px(80)}px;top:{px(170)}px;display:flex;flex-direction:column;
  align-items:flex-start;gap:{px(36)}px}}
.над{{font-weight:700;font-size:{px(34)}px;letter-spacing:.12em;text-transform:uppercase;color:{ОЛИВА}}}
.заголовок{{font-size:{px(104)}px;line-height:1.02}}
.под{{font-size:{px(46)}px;line-height:1.3;color:{МЯГКИЙ};text-wrap:pretty;max-width:{px(760)}px}}
/* финал */
.тёмный{{background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}}}
.финал{{position:absolute;left:{px(80)}px;right:{px(80)}px;top:{px(230)}px;display:flex;flex-direction:column;
  align-items:flex-start;gap:{px(40)}px}}
.финал .крупно{{font-size:{px(112)}px;line-height:1;color:{ЛАЙМ}}}
.финал .текст{{font-weight:700;font-size:{px(54)}px;line-height:1.25;text-wrap:balance;max-width:{px(820)}px}}
.финал .под{{font-size:{px(42)}px;color:{ТИХИЙ}}}
.кот{{position:absolute}}
"""


def страница(тело: str, доля: float, тёмный: bool = False) -> str:
    return (f"<!doctype html><meta charset=utf-8><style>{фейсы()}{CSS}"
            f"{стиль.знак_и_полоса_css(светлый_грунт=not тёмный)}</style>"
            f"<body class='{'тёмный' if тёмный else ''}'>{тело}{стиль.знак_и_полоса(доля)}</body>")


def кот_из_холста(к: dict) -> str:
    где = {ключ: px(к[ключ]) for ключ in ("left", "top", "right", "bottom") if ключ in к}
    return кот(к["поза"], px(к["высота"]), **где)


def значок(имя: str) -> str:
    путь = ТУТ / "значки" / (f"{имя}.svg" if (ТУТ / "значки" / f"{имя}.svg").exists() else f"{имя}.png")
    return данные(путь)


def обложка(доля: float) -> str:
    о = П["обложка"]
    return страница(
        f"<div class=обложка data-блок><div class=над>{о['над']}</div>"
        f"<div class='крупно заголовок'>{о['заголовок']}</div><div class=под>{о['под']}</div></div>"
        f"{кот_из_холста(о['кот'])}", доля)


def кадр(номер: int, к: dict, доля: float) -> str:
    круги = "".join(f"<div class=круг><img src='{значок(с['значок'])}'></div>" for с in к["сервисы"])
    имена = ", ".join(с["имя"] for с in к["сервисы"])
    текст = "".join(f"<p>{а}</p>" for а in к["текст"])
    return страница(
        f"<div class=стопка><div class=шапка data-блок><div class=номер>{номер:02d}</div>"
        f"<div class='крупно навык'>{к['заголовок']}</div></div>"
        f"<div class=сервисы data-блок><div class=круги>{круги}</div><div class=имена>{имена}</div></div>"
        f"<div class=карточка data-блок>{текст}</div></div>", доля)


def финал() -> str:
    ф = П["финал"]
    return страница(
        f"<div class=финал data-блок><div class=крупно>{ф['крупно']}</div><div class=текст>{ф['текст']}</div>"
        f"<div class=под>{ф['под']}</div></div>{кот_из_холста(ф['кот'])}", 1.0, тёмный=True)


ЗАМЕР = стиль.ЗАПАС_JS + """document.fonts.ready.then(() => {
  document.body.setAttribute("data-замер", JSON.stringify({
    шрифты: ![...document.fonts].some(f => f.status === "error" || f.status === "loading"),
    картинки: [...document.images].filter(и => !(и.complete && и.naturalWidth)).length,
    ...запас_кадра('')}));
})"""


def main():
    global П
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text())
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    всего = len(П["кадры"]) + 2
    кадры = [("01", обложка(1 / всего))]
    кадры += [(f"{н + 1:02d}", кадр(н, к, (н + 1) / всего)) for н, к in enumerate(П["кадры"], 1)]
    кадры.append((f"{всего:02d}", финал()))
    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        html = html.replace("</body>", f"<script>{ЗАМЕР}</script></body>")
        снимок = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", ошибки, flush=True)
            continue
        with Image.open(снимок) as и:
            и.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок)
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", браузер.замерить(html, W, H), flush=True)
    if только or not П.get("папка"):
        return
    стол = СТОЛ / П["папка"]
    стол.mkdir(parents=True, exist_ok=True)
    for имя, _ in кадры:
        with Image.open(выход / f"{имя}.png") as и:
            и.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(П["подпись"])
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
