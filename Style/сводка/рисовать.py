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

# Палитра наша, а не авторская. У @whygolding кадр нейтрально-серый с чёрными
# плашками; фирменные цвета канала — крем, графит, олива и лайм, и кадр должен
# читаться нашим ещё до того, как зритель дочитает текст.
ГРУНТ, КАРТОЧКА = стиль.КРЕМ, "#FFFFFF"
ПЛАШКА, НА_ПЛАШКЕ = стиль.ТЁМНЫЙ, стиль.СВЕТЛЫЙ
ЧЕРНИЛА, СЕРЫЙ = стиль.ТЁМНЫЙ, "#5C6152"
# Лайм заливкой под графитовый текст, а не текстом по светлому: по кремовому он
# даёт около 2:1 и пропадает (правило бренда, проверено на кадрах).
АКЦЕНТ, НА_АКЦЕНТЕ = стиль.ЛАЙМ, стиль.ТЁМНЫЙ

# Раскладка кадра 1620×2160. Низ отдан знаку и полосе (они сидят на bottom 264–308),
# поэтому карточка заканчивается на 1800, а не у края кадра.
ПОЛЕ, РАДИУС = 39, 36
НИЗ_КАРТОЧКИ = 1800
ВНУТРИ = 76
СЛЕВА = ПОЛЕ + ВНУТРИ
ШИРИНА_ТЕКСТА = W - СЛЕВА * 2


def картинка(путь: str, кроп: list | None = None, ширина: int = ШИРИНА_ТЕКСТА) -> tuple[str, float]:
    """Снимок данными и его отношение высоты к ширине.

    По `file://` Chrome снимок молча не рисует, поэтому только данными. Отношение
    возвращается, чтобы рамку строить по самой картинке: с фиксированной высотой
    под снимком оставалась пустая серая полоса.
    """
    ф = Path(путь)
    if not ф.is_absolute():
        ф = ТУТ / путь
    with Image.open(ф) as и:
        и = и.convert("RGB")
        if кроп:
            # Доли, а не пиксели: снимки приходят разного размера. Нужно, чтобы
            # у страницы издания не занимала полкадра пустая шапка с меню, а у
            # GitHub читалось имя репозитория, а не мелочь по всей странице.
            л, в_, п, н = кроп
            и = и.crop((round(и.width * л), round(и.height * в_),
                        round(и.width * п), round(и.height * н)))
        if и.width > ширина:
            и = и.resize((ширина, round(и.height * ширина / и.width)), Image.LANCZOS)
        доля = и.height / и.width
        буф = BytesIO()
        и.save(буф, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(буф.getvalue()).decode(), доля


def рамка(путь: str, предел: int, кроп: list | None = None) -> str:
    """Снимок в скруглённой рамке: вписан по ширине, высокий обрезается снизу.

    `предел` — сколько высоты стиль готов отдать снимку. Рамка прижата к низу
    колонки (`margin-top:auto`), поэтому воздух при коротком тексте остаётся
    между текстом и снимком, а не под ним.
    """
    данные_, доля = картинка(путь, кроп)
    высота = min(предел, round(ШИРИНА_ТЕКСТА * доля))
    return (f"<div class=снимок style='height:{высота}px'>"
            f"<img src='{данные_}'></div>")


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
/* Блоки идут потоком в колонке, а не по вычисленным координатам. Считать высоту
   заголовка формулой по длине строки нельзя: на кадре 07 «Учителям дарят год
   Claude» перенеслось на вторую строку, которой формула не ждала, и пояснение
   налезло сверху на 61 px. Поток такую ошибку исключает как класс. */
.содержимое{{position:absolute;left:{СЛЕВА}px;top:{ПОЛЕ + ВНУТРИ}px;width:{ШИРИНА_ТЕКСТА}px;
  height:{НИЗ_КАРТОЧКИ - ПОЛЕ - ВНУТРИ * 2}px;display:flex;flex-direction:column;gap:44px}}
.рубрика{{align-self:flex-start;background:{АКЦЕНТ};color:{НА_АКЦЕНТЕ};
  font-family:Onest,sans-serif;font-weight:800;font-size:40px;
  letter-spacing:.02em;padding:18px 34px 22px;border-radius:999px;
  box-shadow:0 10px 26px rgba(18,19,15,.16)}}
/* Логотип стоит там, где у автора был его ник: место в кадре то же, подпись наша.
   Нижний знак при этом гасим, иначе логотип в кадре удвоится, а полоса остаётся —
   она показывает, сколько карусели прочитано. */
.шапка{{display:flex;align-items:center;gap:18px;margin-bottom:8px}}
.шапка img{{height:60px;display:block;filter:brightness(.35) saturate(1.5)}}
.шапка span{{font-family:Onest,sans-serif;font-weight:800;font-size:30px;
  letter-spacing:.14em;text-transform:uppercase;color:{СЕРЫЙ}}}
.знак{{display:none}}
.заголовок{{font-family:Onest,sans-serif;font-weight:800;letter-spacing:-.025em;
  line-height:1.06;color:{ЧЕРНИЛА}}}
.пояснение{{font-size:48px;line-height:1.32;color:{СЕРЫЙ}}}
.пояснение b{{font-weight:700;color:{ЧЕРНИЛА}}}
.снимок{{margin-top:auto;width:100%;border-radius:18px;overflow:hidden;min-height:0;
  background:{ГРУНТ};box-shadow:0 18px 48px rgba(17,17,17,.16)}}
/* Снимок вписывается по ШИРИНЕ и обрезается снизу, а не по сторонам: сайт, у
   которого срезаны поля, читается как чужой мусор — на пробе у worklouder от
   «More Talking» осталось «re Talking». */
.снимок img{{width:100%;height:auto;display:block}}
/* Финал: вывод занимает середину колонки, призыв прижат к низу карточки. */
.вывод{{margin:auto 0;display:flex;flex-direction:column;gap:44px}}
/* Телеграм на финале: значок, ник крупно, строка-обещание. Это наша воронка,
   а не перенесённая чужая: у автора на этом месте был снимок его канала. */
.телеграм{{display:flex;align-items:center;gap:30px;background:{ПЛАШКА};
  border-radius:30px;padding:34px 40px;box-shadow:0 16px 40px rgba(18,19,15,.20)}}
.телеграм .значок{{width:96px;height:96px;border-radius:26px;background:{АКЦЕНТ};
  display:flex;align-items:center;justify-content:center;flex:0 0 auto}}
.телеграм .значок svg{{width:56px;height:56px;fill:{НА_АКЦЕНТЕ}}}
.телеграм .ник{{font-family:Onest,sans-serif;font-weight:800;font-size:64px;
  letter-spacing:-.02em;color:{НА_ПЛАШКЕ};line-height:1.05}}
.телеграм .под{{font-size:34px;line-height:1.3;color:#A9AF9C;margin-top:8px}}
.призыв{{align-self:flex-start;background:{ПЛАШКА};color:{НА_ПЛАШКЕ};
  font-family:Onest,sans-serif;font-weight:800;font-size:44px;line-height:1.25;
  padding:26px 38px 30px;border-radius:26px;max-width:{ШИРИНА_ТЕКСТА}px;
  box-shadow:0 14px 34px rgba(17,17,17,.20)}}
"""


def страница(тело: str, доля: float) -> str:
    return (f"<html><head><meta charset='utf-8'><style>{фейсы()}{CSS}</style></head>"
            f"<body><div class=карточка></div>{тело}{стиль.знак_и_полоса(доля)}</body></html>")


ШАПКА = f"<div class=шапка><img src='{стиль.ЛОГО}'><span>4xSoft</span></div>"

САМОЛЁТ = ("<svg viewBox='0 0 24 24'><path d='M21.6 3.2 2.9 10.4c-1.3.5-1.3 1.2-.2 1.6l4.8 1.5 "
           "1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.7c.3-1.3-.5-1.9-1.4-1.1z"
           "M8.9 13.1l9.6-6c.5-.3.9-.1.5.2l-8.2 7.4-.3 3.4-1.6-5z'/></svg>")


def телеграм(ник: str, под: str) -> str:
    return (f"<div class=телеграм><div class=значок>{САМОЛЁТ}</div>"
            f"<div><div class=ник>{ник}</div><div class=под>{под}</div></div></div>")


def _колонка(куски: str) -> str:
    return f"<div class=содержимое>{ШАПКА}{куски}</div>"


def кадр(с: dict, доля: float) -> str:
    """Кадр-новость: рубрика, заголовок, абзац, снимок. Без снимка не рисуется."""
    if not с.get("снимок"):
        raise ValueError("кадру нужен снимок: стиль «сводка» держится на нём")

    кегль = 108 if len(с["заголовок"]) <= 46 else 92
    return страница(_колонка(
        f"<div class=рубрика>{с['рубрика']}</div>"
        f"<div class=заголовок style='font-size:{кегль}px'>{с['заголовок']}</div>"
        f"<div class=пояснение>{с.get('текст', '')}</div>"
        f"{рамка(с['снимок'], 900, с.get('кроп'))}"), доля)


def обложка(доля: float, о: dict | None = None) -> str:
    """Первый кадр: рубрика, заголовок крупнее обычного, снимок ниже.

    `о` передаётся, когда рисуется запасная обложка для холста: в холсте их три,
    и каждая должна быть другим подходом, а не перекраской первой.
    """
    о = о or П["обложка"]
    if not о.get("снимок"):
        raise ValueError("обложке нужен снимок: стиль «сводка» держится на нём")

    кегль = 132 if len(о["заголовок"]) <= 40 else 112
    пояснение = f"<div class=пояснение>{о['текст']}</div>" if о.get("текст") else ""
    return страница(_колонка(
        f"<div class=рубрика>{о['рубрика']}</div>"
        f"<div class=заголовок style='font-size:{кегль}px'>{о['заголовок']}</div>"
        f"{пояснение}"
        f"{рамка(о['снимок'], 1000, о.get('кроп'))}"), доля)


def финал(доля: float) -> str:
    """Последний кадр: вывод и призыв. Снимка нет — показывать больше нечего.

    Заголовок стоит по центру карточки, а призыв прижат к её низу: на пробе текст
    сидел вверху, и нижняя половина кадра оставалась пустым белым полем.
    """
    ф = П["финал"]
    кегль = 120 if len(ф["заголовок"]) <= 40 else 100
    текст = f"<div class=пояснение>{ф['текст']}</div>" if ф.get("текст") else ""
    низ = (телеграм(ф["телеграм"]["ник"], ф["телеграм"].get("под", ""))
           if ф.get("телеграм")
           else f"<div class=призыв>{ф.get('призыв') or 'Сохрани, чтобы вернуться'}</div>")
    return страница(_колонка(
        f"<div class=рубрика>Итог</div>"
        f"<div class=вывод><div class=заголовок style='font-size:{кегль}px'>{ф['заголовок']}</div>"
        f"{текст}</div>{низ}"), доля)


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
    П = json.loads(файл.read_text(encoding="utf-8"))
    выход = ТУТ / "картинки" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)

    кадры_поста = П["кадры"]
    всего = len(кадры_поста) + 2
    кадры = [("01", обложка(1 / всего))]
    кадры += [(f"{н:02d}", кадр(с, н / всего)) for н, с in enumerate(кадры_поста, 2)]
    кадры.append((f"{всего:02d}", финал(1.0)))
    # Запасные обложки для холста: владелец выбирает из трёх, поэтому они рисуются
    # вместе с каруселью, а не отдельным заходом.
    for н, з in enumerate(П.get("запасные_обложки") or [], 2):
        кадры.append((f"oblozhka{н}", обложка(1 / всего, з)))

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
    # Запасные обложки на стол не уезжают: выкладывается одна, выбранная владельцем.
    for имя, _ in кадры:
        if имя.startswith("oblozhka"):
            continue
        with Image.open(выход / f"{имя}.png") as к:
            к.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(П["подпись"] + "\n\n" + " ".join(П["хештеги"]), encoding="utf-8")
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
