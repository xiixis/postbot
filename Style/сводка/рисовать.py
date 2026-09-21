# -*- coding: utf-8 -*-
"""Стиль «сводка»: карточка новости со снимком. `python3 рисовать.py посты/<пост>.json [02 05]`

Номера кадров перерисовывают только их; без номеров кадры ещё и уезжают JPG 1080×1440
на стол, в папку из поля «папка», вместе с подписью.

Скелет референса @whygolding (серый грунт, белая карточка, тёмная плашка-рубрика,
сверхжирный заголовок, серый абзац, крупный снимок на нижние 38%) в нашем виде: наши
цвета, наш знак с полосой вместо его ника и кнопок. Разбор — в `референс/паспорт.md`,
устройство и сознательные отклонения — в `ДИЗАЙН.md`.

Снимок в кадре обязателен: на нём стиль и держится. Кадр без снимка поднимает
ValueError, а не рисуется наполовину пустым.
"""
import base64
import json
import sys
import time
from io import BytesIO
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
from стиль import W, H, СТОЛ, данные  # noqa: E402
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

П: dict = {}

ГРУНТ, КАРТОЧКА = "#E7E7E7", "#FFFFFF"
ПЛАШКА, НА_ПЛАШКЕ = "#363636", "#FFFFFF"
ЧЕРНИЛА, СЕРЫЙ = "#111111", "#5C6152"

# Раскладка кадра 1620×2160. Низ отдан знаку и полосе (они сидят на bottom 264–308),
# поэтому карточка заканчивается на 1800, а не у края кадра.
ПОЛЕ, РАДИУС = 39, 36
НИЗ_КАРТОЧКИ = 1800
ВНУТРИ = 76
СЛЕВА = ПОЛЕ + ВНУТРИ
ШИРИНА_ТЕКСТА = W - СЛЕВА * 2


def картинка(путь: str, ширина: int = 1390) -> str:
    """Снимок, вшитый данными: по file:// Chrome молча не рисует, а PNG на 5 МБ странице ни к чему."""
    ф = Path(путь)
    if not ф.is_absolute():
        ф = ТУТ / путь
    with Image.open(ф) as и:
        и = и.convert("RGB")
        if и.width > ширина:
            и = и.resize((ширина, round(и.height * ширина / и.width)), Image.LANCZOS)
        буф = BytesIO()
        и.save(буф, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(буф.getvalue()).decode()


def фейсы() -> str:
    return стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                       ("Golos", "golos-700", 700))


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{ГРУНТ};color:{ЧЕРНИЛА};font-family:Golos,sans-serif;position:relative;
  -webkit-font-smoothing:antialiased}}
{стиль.знак_и_полоса_css(светлый_грунт=True)}
.карточка{{position:absolute;left:{ПОЛЕ}px;top:{ПОЛЕ}px;width:{W - ПОЛЕ * 2}px;
  height:{НИЗ_КАРТОЧКИ - ПОЛЕ}px;background:{КАРТОЧКА};border-radius:{РАДИУС}px;
  box-shadow:0 24px 70px rgba(17,17,17,.10)}}
.рубрика{{position:absolute;left:{СЛЕВА}px;top:{ПОЛЕ + ВНУТРИ}px;background:{ПЛАШКА};
  color:{НА_ПЛАШКЕ};font-family:Onest,sans-serif;font-weight:800;font-size:40px;
  letter-spacing:.02em;padding:18px 34px 22px;border-radius:999px;
  box-shadow:0 10px 26px rgba(17,17,17,.18)}}
.заголовок{{position:absolute;left:{СЛЕВА}px;width:{ШИРИНА_ТЕКСТА}px;
  font-family:Onest,sans-serif;font-weight:800;letter-spacing:-.025em;line-height:1.06;
  color:{ЧЕРНИЛА}}}
.пояснение{{position:absolute;left:{СЛЕВА}px;width:{ШИРИНА_ТЕКСТА}px;font-size:48px;
  line-height:1.32;color:{СЕРЫЙ}}}
.пояснение b{{font-weight:700;color:{ЧЕРНИЛА}}}
.снимок{{position:absolute;left:{СЛЕВА}px;width:{ШИРИНА_ТЕКСТА}px;border-radius:18px;
  overflow:hidden;background:{ГРУНТ};box-shadow:0 18px 48px rgba(17,17,17,.16)}}
.снимок img{{width:100%;height:100%;object-fit:cover;object-position:top center;display:block}}
.число{{position:absolute;left:{СЛЕВА}px;font-family:Onest,sans-serif;font-weight:800;
  font-size:300px;line-height:.9;letter-spacing:-.04em;color:{ЧЕРНИЛА}}}
"""


def страница(тело: str, доля: float) -> str:
    return (f"<html><head><meta charset='utf-8'><style>{фейсы()}{CSS}</style></head>"
            f"<body><div class=карточка></div>{тело}{стиль.знак_и_полоса(доля)}</body></html>")


def _строк(текст: str, на_строку: int) -> int:
    return max(1, -(-len(текст) // на_строку))


def кадр(с: dict, доля: float) -> str:
    """Кадр-новость: рубрика, заголовок, абзац, снимок. Без снимка не рисуется."""
    if not с.get("снимок"):
        raise ValueError("кадру нужен снимок: стиль «сводка» держится на нём")

    кегль = 108 if len(с["заголовок"]) <= 46 else 92
    строк_з = _строк(с["заголовок"], 26 if кегль == 108 else 31)
    верх_з = ПОЛЕ + ВНУТРИ + 78 + 52
    высота_з = round(кегль * 1.06 * строк_з)

    верх_п = верх_з + высота_з + 40
    строк_п = _строк(с.get("текст", ""), 52)
    высота_п = round(48 * 1.32 * строк_п)

    верх_с = верх_п + высота_п + 52
    низ_с = НИЗ_КАРТОЧКИ - ВНУТРИ
    высота_с = низ_с - верх_с

    return страница(
        f"<div class=рубрика>{с['рубрика']}</div>"
        f"<div class=заголовок style='top:{верх_з}px;font-size:{кегль}px'>{с['заголовок']}</div>"
        f"<div class=пояснение style='top:{верх_п}px'>{с.get('текст', '')}</div>"
        f"<div class=снимок style='top:{верх_с}px;height:{высота_с}px'>"
        f"<img src='{картинка(с['снимок'])}'></div>", доля)


def обложка(доля: float) -> str:
    """Первый кадр: рубрика, заголовок крупнее обычного, снимок ниже."""
    о = П["обложка"]
    if not о.get("снимок"):
        raise ValueError("обложке нужен снимок: стиль «сводка» держится на нём")

    кегль = 132 if len(о["заголовок"]) <= 40 else 112
    строк = _строк(о["заголовок"], 21 if кегль == 132 else 25)
    верх_з = ПОЛЕ + ВНУТРИ + 78 + 64
    высота_з = round(кегль * 1.04 * строк)

    верх_п = верх_з + высота_з + 36
    высота_п = round(48 * 1.32 * _строк(о.get("текст", ""), 52)) if о.get("текст") else 0

    верх_с = верх_п + высота_п + (52 if высота_п else 20)
    высота_с = (НИЗ_КАРТОЧКИ - ВНУТРИ) - верх_с

    пояснение = (f"<div class=пояснение style='top:{верх_п}px'>{о['текст']}</div>"
                 if о.get("текст") else "")
    return страница(
        f"<div class=рубрика>{о['рубрика']}</div>"
        f"<div class=заголовок style='top:{верх_з}px;font-size:{кегль}px'>{о['заголовок']}</div>"
        f"{пояснение}"
        f"<div class=снимок style='top:{верх_с}px;height:{высота_с}px'>"
        f"<img src='{картинка(о['снимок'])}'></div>", доля)


def финал(доля: float) -> str:
    """Последний кадр: вывод и призыв. Снимка нет — показывать больше нечего."""
    ф = П["финал"]
    кегль = 120 if len(ф["заголовок"]) <= 40 else 100
    строк = _строк(ф["заголовок"], 23 if кегль == 120 else 27)
    верх_з = ПОЛЕ + ВНУТРИ + 78 + 120
    высота_з = round(кегль * 1.06 * строк)
    return страница(
        f"<div class=рубрика>Итог</div>"
        f"<div class=заголовок style='top:{верх_з}px;font-size:{кегль}px'>{ф['заголовок']}</div>"
        f"<div class=пояснение style='top:{верх_з + высота_з + 52}px'>{ф.get('текст', '')}</div>",
        доля)


ЗАМЕР = """document.fonts.ready.then(() => {
  const r = [];
  for (const el of document.querySelectorAll('.рубрика,.заголовок,.пояснение,.снимок,.знак')) {
    let b = el.getBoundingClientRect();
    if (!['снимок','знак'].includes(el.className)) {
      const д = document.createRange(); д.selectNodeContents(el); b = д.getBoundingClientRect();
    }
    r.push({кто: el.className, л: Math.round(b.left), п: Math.round(b.right), в: Math.round(b.top),
            н: Math.round(b.bottom), ширина: el.scrollWidth, видно: el.clientWidth});
  }
  const выход = r.filter(х => х.л < 90 || х.п > %d || х.н > %d);
  const знак = r.find(х => х.кто === 'знак');
  const наезд = r.filter(х => х.кто !== 'знак' && знак && х.н > знак.в - 20 && х.л < знак.п + 20);
  document.body.setAttribute("data-замер", JSON.stringify({
    шрифты: [...document.fonts].some(f => f.status === "loaded") && ![...document.fonts].some(f => f.status === "error" || f.status === "loading"),
    выход: выход.map(х => х.кто), наезд: наезд.map(х => х.кто), блоки: r,
    ...запас_кадра('.рубрика,.заголовок,.пояснение,.снимок')}));
})""" % (W - 90, НИЗ_КАРТОЧКИ - 20)
ЗАМЕР = стиль.ЗАПАС_JS + ЗАМЕР


def main():
    global П
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text())
    выход = ТУТ / "картинки" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)

    кадры_поста = П["кадры"]
    всего = len(кадры_поста) + 2
    кадры = [("01", обложка(1 / всего))]
    кадры += [(f"{н:02d}", кадр(с, н / всего)) for н, с in enumerate(кадры_поста, 2)]
    кадры.append((f"{всего:02d}", финал(1.0)))

    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        снимок = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", flush=True)
            continue
        with Image.open(снимок) as к:
            к.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок)
        замер = браузер.замерить(html.replace("</body>", f"<script>{ЗАМЕР}</script></body>"), W, H)
        кратко = {к: в for к, в in (замер or {}).items() if к != "блоки"}
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", кратко, flush=True)

    if только or not П.get("папка"):
        return
    стол = СТОЛ / П["папка"]
    стол.mkdir(parents=True, exist_ok=True)
    for имя, _ in кадры:
        with Image.open(выход / f"{имя}.png") as к:
            к.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(П["подпись"] + "\n\n" + " ".join(П["хештеги"]))
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
