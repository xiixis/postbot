# -*- coding: utf-8 -*-
"""Стиль «разбор», вид «шаги_ночь»: тёмный вариант «шагов» — python шаги_ночь.py посты/<пост>.json

Второй вариант того же рерайта (референс №25 «Проекты в Claude»), сделан по слову владельца
09.10.2026: «ещё один вариант, подключи скилы, сделай красиво, чтобы набрали просмотры».
Светлый вариант (`шаги.py`) остаётся как есть.

Откуда решения:
- `Style/КРЮЧКИ.md`: на обложке — сама вещь и число (3), главная строка 3–5 слов; второй
  слайд Instagram показывает тем, кто не листнул, — он собран как вторая обложка («ПРОЕКТЫ»
  крупно, обещание, панель Claude).
- склад `design-taste-frontend`: один акцент (лайм), одна шкала скруглений (24/пилюля),
  без неона; `impeccable` (craft-floor): вместо надписи-над-заголовком номер шага стал
  огромной цифрой — порядок здесь несёт смысл; `high-end-visual-design`: «стекло для ИИ»
  и «каскад по оси Z» — светлые окна Claude с лёгким наклоном на графите, они и есть герой.

Доска 1080×1440: всё важное выше 1105, знак в полосе 1191..1235, правее 900 в полосе 720–1190
текста нет. Чёрный кот на графите пропадает — за ним всегда лаймовое свечение.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402
import обложки  # noqa: E402
import окна_claude as ок  # noqa: E402
import шаги as св  # noqa: E402  светлый вариант: значки, шрифты, окна, лапа

ЛАЙМ, ГРАФ, ЧЕРН = стиль.ЛАЙМ, стиль.ТЁМНЫЙ, "#12130E"
СВЕТ, ВТОР = стиль.СВЕТЛЫЙ, "#C9CCBF"          # подпись по графиту — 11:1, не «серая»
КАРТА = "#1C1E16"                               # тёмная карточка на графите
ЛИНИЯ = "rgba(241,243,234,.16)"
# Ровный графит без цветных пятен: `genjutsu` («украшение без смысла»: что пропадёт, если убрать?).
# Свет в кадре один и с источником — за котом, иначе чёрный кот на графите не виден.
ФОН = f"background: {ГРАФ};"
ТЕНЬ = "0 2px 6px rgba(0,0,0,.35), 0 30px 70px rgba(0,0,0,.55)"
КРУП, ТЕКСТ = св.КРУП, св.ТЕКСТ
CSS, ШРИФТЫ = св.CSS, св.ШРИФТЫ

ТЕМА = обложки.Тема(грунт=ГРАФ, тёмная=True, чернила=СВЕТ, второй=ВТОР, тихий="#9EA294", карточка=КАРТА,
                    карточка_тихая="rgba(241,243,234,.06)", рамка=ЛИНИЯ, тень=ТЕНЬ, стрелка=ЛАЙМ,
                    крупный=КРУП, текст=ТЕКСТ, логотип="")


def значок(имя: str, цвет: str, размер: int) -> str:
    return св.значок(имя, цвет, размер)


def лайм(текст: str) -> str:
    return f'<span style="color: {ЛАЙМ};">{текст}</span>'


def claude(текст: str) -> str:
    return св.claude(текст)


def низ() -> str:
    return f'<img src="logo.png" style="position: absolute; left: 80px; top: {дх.ЗНАК_ВЕРХ}px; height: 44px;">'


def подложка() -> str:
    return f'<div style="position: absolute; inset: 0; {ФОН} pointer-events: none;"></div>'


def наклон(градусы: float, html: str, ось: str = "50% 50%") -> str:
    """Каскад по оси Z: окно чуть повёрнуто, как карточка, брошенная на стол."""
    return (f'<div style="position: absolute; inset: 0; transform: rotate({градусы}deg); transform-origin: {ось}; '
            f'pointer-events: none;">{html}</div>')


def цифра(н: str, строки: list[str]) -> str:
    """Огромная лаймовая цифра шага и заголовок справа от неё: порядок шагов — смысл, не украшение."""
    return (f'<div style="position: absolute; left: 80px; top: 22px; {КРУП} font-size: 300px; line-height: .86; '
            f'letter-spacing: -0.06em; color: {ЛАЙМ};">{н}</div>'
            f'<div style="position: absolute; left: 310px; top: 64px; {КРУП} font-size: 92px; line-height: 1.0; '
            f'color: {СВЕТ};">{строки[0]}<br>{строки[1]}</div>')


def столбик(top: int, блоки: list[str], gap: int = 20, width: int = 920) -> str:
    return св.столбик(top, блоки, gap, width)


def абзац(текст: str, кегль: int = 40, цвет: str = СВЕТ) -> str:
    return (f'<div style="{ТЕКСТ} font-weight: 700; font-size: {кегль}px; line-height: 1.25; color: {цвет};">'
            f'{claude(текст)}</div>')


def плашка(текст: str, кегль: int = 40) -> str:
    """Главная мысль кадра: тёмная карточка с лаймовой рамкой, часть в `[…]` — лаймом.

    Сплошная лаймовая плашка на графите давала акцент 10–12% кадра (норма 4–6%, выше 8% он
    перестаёт быть акцентом): на тёмном лайм и так самое яркое, ему хватает рамки и слова.
    """
    текст = claude(текст).replace("[", f'<span style="display: inline-block; padding: 0 .18em .06em; border-radius: .2em; '
                                  f'background: {ЛАЙМ}; color: {ЧЕРН};">').replace("]", "</span>")
    return (f'<div style="box-sizing: border-box; max-width: 920px; padding: 22px 32px 26px; border-radius: 24px; '
            f'background: {КАРТА}; border: 3px solid {ЛАЙМ}; {КРУП} font-size: {кегль}px; line-height: 1.15; '
            f'color: {СВЕТ};">{текст}</div>')


def пункты(список: list[str], значок_: str, кегль: int = 36, колонки: int = 2) -> str:
    ячейки = "".join(
        f'<div style="display: flex; align-items: center; gap: 16px; {ТЕКСТ} font-weight: 700; font-size: {кегль}px; '
        f'line-height: 1.12; color: {СВЕТ};">'
        f'<div style="width: 52px; height: 52px; border-radius: 26px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок(значок_, ЧЕРН, 28)}</div>{п}</div>' for п in список)
    return (f'<div style="display: grid; grid-template-columns: repeat({колонки}, minmax(0, 1fr)); gap: 18px 24px;">'
            f'{ячейки}</div>')


# ── Кадры ────────────────────────────────────────────────────────────────────

def открытие(о: dict) -> str:
    """Вторая обложка: «ПРОЕКТЫ» лаймом во всю ширину, обещание, панель Claude и что он помнит."""
    знает = (f'<div style="position: absolute; left: 590px; top: 470px; width: 310px; display: flex; flex-direction: column; gap: 20px;">'
             f'<div style="{КРУП} font-size: 44px; line-height: 1; color: {ЛАЙМ};">Claude знает:</div>'
             + пункты(о["список"], "check", 32, колонки=1) + '</div>')
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 64px; width: 920px; {ТЕКСТ} font-weight: 700; font-size: 36px; '
              f'line-height: 1.2; color: {ВТОР};">{claude(о["над"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 122px; {КРУП} font-size: 172px; line-height: 1; '
              f'letter-spacing: -0.035em; color: {ЛАЙМ};">{о["крупно"]}</div>'
            + f'<div style="position: absolute; left: 80px; top: 306px; width: 920px; {ТЕКСТ} font-weight: 700; font-size: 42px; '
              f'line-height: 1.22; color: {СВЕТ};">{claude(о["обещание"])}</div>'
            + наклон(-2, ок.боковая(80, 460, 470, св.ЗНАЧКИ, обвести=True, строка=56), "315px 670px")
            + знает
            + столбик(946, [плашка(о["итог"])])
            + низ())


def шаг1(ш: dict) -> str:
    наклейка = (f'<div style="position: absolute; left: 676px; top: 70px; padding: 10px 22px 12px; border-radius: 16px; '
                f'background: {ЛАЙМ}; transform: rotate(5deg); {КРУП} font-size: 24px; color: {ЧЕРН}; '
                f'box-shadow: 0 12px 28px rgba(0,0,0,.4);">{ш["сноска"]}</div>')
    return (подложка() + цифра("1", ш["строки"]) + наклейка
            + наклон(-1.5, ок.новый_проект(80, 300, 820, ш["проект"], ш["цель"], обвести=True), "490px 545px")
            + ок.стрелка(842, 470, 120, 240, "M90 10 C 130 90, 110 170, 44 220")
            + столбик(830, [абзац(ш["абзац"]), плашка(ш["итог"], 38)], gap=20)
            + низ())


def шаг2(ш: dict) -> str:
    плюс = (f'<div class=окно data-рядом=окно style="position: absolute; left: 466px; top: 456px; width: 72px; height: 72px; '
            f'border-radius: 36px; background: {ЛАЙМ}; box-shadow: 0 0 0 8px {ГРАФ}; display: flex; align-items: center; '
            f'justify-content: center; z-index: 3;">{значок("plus", ЧЕРН, 38)}</div>')
    return (подложка() + цифра("2", ш["строки"])
            + ок.файлы(86, 300, 456, ш["файлы"], св.ЗНАЧКИ)
            + ок.инструкции(500, 332, 400, ш["инструкция"], "Посты-карусели", св.ЗНАЧКИ, маркер="•")
            + плюс
            + столбик(818, [абзац(ш["список_над"], 34, ВТОР), пункты(ш["список"], "folder-simple"),
                            плашка(ш["итог"], 36)], gap=14)
            + низ())


def узел(н: str, текст: str, left: int, top: int) -> str:
    return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: 300px; height: 78px; box-sizing: border-box; '
            f'padding-left: 84px; border-radius: 39px; background: {КАРТА}; border: 2px solid {ЛИНИЯ}; box-shadow: {ТЕНЬ}; '
            f'display: flex; align-items: center; {ТЕКСТ} font-weight: 700; font-size: 36px; color: {СВЕТ};">'
            f'<div style="position: absolute; left: 8px; top: 8px; min-width: 58px; height: 58px; box-sizing: border-box; padding: 0 9px; '
            f'border-radius: 29px; background: {ЛАЙМ}; {КРУП} font-size: 26px; line-height: 58px; text-align: center; color: {ЧЕРН};">{н}</div>'
            f'{текст}</div>')


def колонка(к: dict, left: int, top: int, значок_: str) -> str:
    шаг, сдвиг = 112, 70
    out = (f'<div style="position: absolute; left: {left}px; top: {top}px; display: flex; align-items: center; gap: 14px; '
           f'{КРУП} font-size: 60px; line-height: 1; color: {СВЕТ};">'
           f'<div style="width: 62px; height: 62px; border-radius: 18px; background: {ЛАЙМ}; display: flex; align-items: center; '
           f'justify-content: center;">{значок(значок_, ЧЕРН, 36)}</div>{к["название"]}</div>')
    for i, (н, текст) in enumerate(к["узлы"]):
        х = left + (сдвиг if i % 2 else 0)
        у = top + 96 + i * шаг
        out += узел(н, текст, х, у)
        if i + 1 < len(к["узлы"]):
            if i % 2 == 0:
                out += ок.стрелка(х + 250, у + 70, 70, 44, "M6 4 C 36 6, 54 16, 56 38")
            else:
                out += ок.стрелка(х - 26, у + 70, 70, 44, "M54 4 C 22 6, 6 18, 12 38")
    return out


def схема(с: dict) -> str:
    к1, к2 = с["колонки"]
    return (подложка() + цифра("3", с["строки"])
            + f'<div style="position: absolute; left: 80px; top: 290px; {ТЕКСТ} font-weight: 700; font-size: 36px; color: {ВТОР};">{с["над"]}</div>'
            + колонка(к1, 80, 368, "sparkle") + колонка(к2, 530, 368, "chat-text")
            + столбик(1008, [плашка(f'[{с["совет"]}]', 32)])
            + низ())


def доказательство(д: dict) -> str:
    ш, в, зазор = 196, 261, 14
    левый = (1080 - 3 * ш - 2 * зазор) // 2
    плитки = ""
    for i, файл in enumerate(д["обложки"][:9]):
        х, у = левый + i % 3 * (ш + зазор), 290 + i // 3 * (в + зазор)
        плитки += (f'<img class=плитка data-рядом=плитка src="{файл}" style="position: absolute; left: {х}px; top: {у}px; '
                   f'width: {ш}px; height: {в}px; object-fit: cover; border-radius: 16px; border: 2px solid {ЛИНИЯ}; box-shadow: {ТЕНЬ};">')
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 64px; width: 920px; {КРУП} font-size: 92px; line-height: 1.02; '
              f'color: {СВЕТ};">{д["строки"][0]}<br>{лайм(д["строки"][1])}</div>'
            + плитки + низ())


def свечение(left: int, top: int, w: int, h: int) -> str:
    """Чёрный кот на графите пропадает: за ним всегда мягкое лаймовое пятно."""
    return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; border-radius: 50%; '
            f'background: radial-gradient(closest-side, rgba(199,226,75,.42), rgba(199,226,75,0)); pointer-events: none;"></div>')


def финал(ф: dict) -> str:
    список = "".join(
        f'<div style="display: flex; align-items: center; gap: 18px; {ТЕКСТ} font-weight: 700; font-size: 38px; color: {СВЕТ};">'
        f'<div style="width: 52px; height: 52px; border-radius: 26px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок("check", ЧЕРН, 30)}</div>{п}</div>' for п in ф["пункты"])
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 64px; width: 920px; {КРУП} font-size: 104px; line-height: 1.0; '
              f'color: {СВЕТ};">{ф["строки"][0]}<br>{ф["строки"][1]}<br>{лайм(ф["акцент"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 440px; width: 580px; box-sizing: border-box; padding: 34px; '
              f'border-radius: 28px; background: {КАРТА}; border: 2px solid {ЛИНИЯ}; box-shadow: {ТЕНЬ}; display: flex; '
              f'flex-direction: column; gap: 22px;">{список}</div>'
            + свечение(640, 414, 340, 320)
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" data-кот style="position: absolute; left: 686px; top: 420px; height: 290px;">'
            + столбик(780, [плашка(ф["призыв_ночь"], 50)], width=820)
            + низ())


def обложка(о: dict) -> str:
    """Главная: сцена с котом и папкой, строка 3–5 слов и число — по `КРЮЧКИ.md`, приёмы 1, 3, 4."""
    к = обложки.карточка(о["сцена"])
    сдвиг = -190
    x0, y0, x1, y1 = к["пусто"]
    y0, y1 = max(60, y0 + сдвиг), y1 + сдвиг
    кегль = обложки.кегль(о["строки"], x1 - x0, 150, (y1 - y0) - 150)
    return (f'<img src="{о["сцена"]}.jpg" style="position: absolute; left: 0; top: {сдвиг}px; width: 1080px; height: 1440px; object-fit: cover;">'
            + f'<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 360px; pointer-events: none; '
              f'background: linear-gradient(0deg, {ГРАФ} 0%, {ГРАФ} 34%, rgba(18,19,15,0) 100%);"></div>'
            + обложки.кот_сцены(к, сдвиг)
            + f'<div style="position: absolute; left: {x0}px; top: {y0}px; width: {x1 - x0}px; display: flex; flex-direction: column; '
              f'align-items: flex-start; gap: 26px;">'
              f'<div style="{КРУП} font-size: {кегль}px; line-height: .96; color: {СВЕТ};">{о["строки"][0]}<br>{лайм(о["строки"][1])}</div>'
              f'<div style="{ТЕКСТ} font-weight: 700; font-size: 46px; line-height: 1.15; color: {СВЕТ};">'
              f'{дх.маркер(о["число"], чернила=ЧЕРН)} {claude(о["под"])}</div></div>'
            + низ())


def доски_кадров(пост: dict) -> list[tuple[str, str, str]]:
    н = пост["ночь"]
    кадры = [("Открытие", открытие({**пост["открытие"], **н["открытие"]})),
             ("Шаг 1", шаг1({**пост["шаг1"], **н["шаг1"]})),
             ("Шаг 2", шаг2({**пост["шаг2"], **н["шаг2"]})),
             ("Шаг 3 · схема", схема({**пост["схема"], **н["схема"]})),
             ("Наши обложки", доказательство(пост["доказательство"])),
             ("Финал", финал({**пост["финал"], **н["финал"]}))]
    return [(f"Kadr{i:02d}.dc.html", f"{i:02d} · {имя}", дх.доска(имя, тело, ГРАФ, CSS))
            for i, (имя, тело) in enumerate(кадры, 2)]


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    try:
        CSS = дх.шрифты_холста(CSS, корень)
    except SystemExit as е:
        print(f"⚠️  {е} — собираю с локальными шрифтами (до выкладки загрузить)")
    врем = корень / "_файлы"
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот(пост["финал"]["поза"], врем)]
    файлы += обложки.файлы(пост.get("запасные", {}), врем)
    файлы += [обложки.СЦЕНЫ / f'{пост["ночь"]["обложка"]["сцена"]}.jpg']
    файлы += [ТУТ / "картинки" / "oblozhki" / ф for ф in пост["доказательство"]["обложки"]]
    нет = [ф for ф in файлы if not ф.exists()]
    if нет:
        print("для снабженца (snabzhenets):\n  " + "\n  ".join(str(ф) for ф in нет))
        raise SystemExit(2)
    своя = ("ночь", ГРАФ, обложка(пост["ночь"]["обложка"]))
    обл = обложки.доски_обложек(пост, своя, ТЕМА, {}, CSS)
    доски = обл[:1] + доски_кадров(пост) + обл[1:]
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")
    import приёмка_досок
    приёмка_досок.доложить(проект, снимки="--без-снимка" not in sys.argv[2:])


if __name__ == "__main__":
    main()
