# -*- coding: utf-8 -*-
"""Светлый разбор, вид «главы»: python главы.py посты/<пост>.json

Рерайт @ankush_ai_growth (23.09.2026, `референс-ankush/`, `ВАРИАЦИИ.md`) — как можно ближе к
автору (слово владельца: «у него уже набрали просмотры, а значит это работает»). Повторено:
светлый тёплый лист с мягким свечением в углу, моно-метка раздела вразрядку, заголовок слева в
две строки с цветным хвостом, серый абзац, белые карточки с мягкой тенью (шаги — каждый своей
карточкой, пункты «жирное — пояснение», код в тёмной плашке, команды — светлыми чипами), сетка
3×3 площадок, счётчик NN / NN внизу справа, обложка-постер с объёмными буквами над сценой.
Наше: цвета (олива по светлому, лайм заливками вместо его синего), логотип вместо ника, кот
на обложке и в финале, свой призыв вместо воронки «Comment PIPELINE».

Всё важное — выше 1105 px доски 1080×1440: знак в служебной полосе 1191..1235 (`замер.py`).
Собирает правимый холст `холсты/<пост>/project/` (`../дизайн_холст.py`); после «готово» —
`../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

ФОН = ("background: #F5F4EF; background-image: radial-gradient(circle at 92% 4%, rgba(199,226,75,.30), "
       "rgba(199,226,75,0) 34%), radial-gradient(circle at 0% 100%, rgba(199,226,75,.10), rgba(199,226,75,0) 40%);")
ЧЕРН, СЕР, ЛАЙМ = "#141413", "#26261F", стиль.ЛАЙМ
# Олива #3F4D08 как цвет текста сливалась с фоном (слово владельца 23.09.2026: «тусклый,
# незаметный… замени везде»). Акцент по светлому теперь — лаймовый маркер под тёмным текстом:
# ~13:1 и самое заметное пятно кадра. Чипы, номера и точки — лайм с тёмным.
ЧИП_ФОН = ЛАЙМ


# Капсула — inline-block со своим отступом сверху: строчная подсветка при плотном интерлиньяже
# залезала на строку выше («капсула у Google залазит на текст», 23.09.2026).
def маркер(текст: str) -> str:
    return (f'<span style="background: {ЛАЙМ}; color: {ЧЕРН}; display: inline-block; line-height: 1; '
            f'padding: .03em .16em .08em; margin-top: .1em; border-radius: .16em;">{текст}</span>')
CLAUDE = "#D97757"                     # фирменный цвет Claude: слово «CLAUDE.» на обложке (слово владельца 23.09.2026)
ТЕНЬ = "0 1px 2px rgba(20,20,19,.05), 0 12px 32px rgba(20,20,19,.08)"
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.03em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
МОНО = "font-family: JetBrains, 'Courier New', monospace;"
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
                        ("JetBrains", "jetbrains-400", 400), ("JetBrains", "jetbrains-700", 700))


def низ(счёт: str = "", тёмный: bool = False) -> str:
    лого = "" if тёмный else "filter: brightness(.45) saturate(1.4);"
    с = (f'<div style="position: absolute; right: 80px; top: 1200px; {МОНО} font-size: 24px; color: {СЕР};">{счёт}</div>'
         if счёт else "")
    return f'<img src="logo.png" style="position: absolute; left: 80px; top: 1191px; height: 44px; {лого}">' + с


def метка(текст: str) -> str:
    return (f'<div style="position: absolute; left: 80px; top: 76px; {МОНО} font-weight: 700; font-size: 24px; '
            f'letter-spacing: .32em; text-transform: uppercase; color: {ЧЕРН};">{маркер(текст)}</div>')


def заголовок(строки: list[str], верх: int, кегль: int = 80) -> str:
    хвост = f'<br>{маркер(строки[1])}' if len(строки) > 1 else ""
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: 920px; {КРУП} font-size: {кегль}px; '
            f'line-height: 1.05; color: {ЧЕРН};">{строки[0]}{хвост}</div>')


def абзац(текст: str, верх: int, кегль: int = 34, ширина: int = 900) -> str:
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: {ширина}px; {ТЕКСТ} font-size: {кегль}px; '
            f'line-height: 1.4; color: {СЕР};">{текст}</div>')


def чипы(текст: str, тёмный: bool = False) -> str:
    """`команда` в тексте — чип моноширинным (у автора синий на голубом)."""
    фон, цвет = ("#26271F", ЛАЙМ) if тёмный else (ЛАЙМ, ЧЕРН)
    куски = текст.split("`")
    return "".join(к if i % 2 == 0 else
                   f'<span style="{МОНО} font-size: .82em; padding: 2px 10px; border-radius: 8px; background: {фон}; '
                   f'color: {цвет}; white-space: nowrap;">{к}</span>' for i, к in enumerate(куски))


def карта(верх: int, тело: str, тёмная: bool = False, отступ: str = "44px 48px", шаг: int = 30) -> str:
    фон = ЧЕРН if тёмная else "#FFFFFF"
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: 920px; box-sizing: border-box; '
            f'padding: {отступ}; border-radius: 26px; background: {фон}; border: 1px solid rgba(20,20,19,.06); '
            f'box-shadow: {ТЕНЬ}; display: flex; flex-direction: column; gap: {шаг}px;">{тело}</div>')


def пункты(список: list[list[str]], тёмный: bool = False) -> str:
    т, с, точка = ((стиль.СВЕТЛЫЙ, "#C9CCBF", ЛАЙМ) if тёмный else (ЧЕРН, СЕР, ЛАЙМ))
    return "".join(
        f'<div style="display: flex; gap: 20px; align-items: baseline; {ТЕКСТ} font-size: 34px; line-height: 1.38; color: {с};">'
        f'<div style="width: 12px; height: 12px; border-radius: 6px; background: {точка}; border: 3px solid {т}; flex-shrink: 0; transform: translateY(-5px);"></div>'
        f'<div><span style="font-weight: 700; color: {т};">{ж}</span> — {чипы(п, тёмный)}</div></div>' for ж, п in список)


ЦВЕТ_КОДА = {"тихий": "#8D9180", "свет": "#F1F3EA", "лайм": ЛАЙМ}


def кадр(к: dict, н: int, всего: int) -> str:
    счёт = f"{н:02d} / {всего:02d}"
    вид = к["вид"]
    if вид == "инструмент":
        плитка = (f'<div style="position: absolute; left: 80px; top: 200px; display: flex; align-items: center; gap: 24px;">'
                  f'<div style="width: 92px; height: 92px; border-radius: 24px; background: #FFFFFF; box-shadow: {ТЕНЬ}; '
                  f'display: flex; align-items: center; justify-content: center;"><div style="width: 0; height: 0; '
                  f'border-top: 20px solid transparent; border-bottom: 20px solid transparent; border-left: 32px solid {ЧЕРН}; '
                  f'margin-left: 8px;"></div></div><div style="{ТЕКСТ} font-weight: 700; font-size: 44px; color: {ЧЕРН};">'
                  f'{к["инструмент"]}</div></div>')
        строки = "".join(f'<div style="{МОНО} font-size: 28px; line-height: 1.55; color: {ЦВЕТ_КОДА[ц]}; white-space: pre;">{т}</div>'
                         for ц, т in к["код"])
        тело = (метка(к["метка"]) + плитка + заголовок(к["заголовок"], 340) + абзац(к["подводка"], 540)
                + карта(760, строки, тёмная=True, отступ="34px 40px", шаг=2)
                + f'<div style="position: absolute; left: 80px; top: 990px; width: 920px; {МОНО} font-size: 20px; '
                  f'letter-spacing: .04em; color: {СЕР};">{к["сноска"]}</div>')
    elif вид == "шаги":
        карты = ""
        for i, (з, т) in enumerate(к["шаги"]):
            карты += карта(400 + i * 215, (
                f'<div style="display: flex; gap: 28px; align-items: flex-start;">'
                f'<div style="width: 60px; height: 60px; border-radius: 30px; background: {ЛАЙМ}; color: {ЧЕРН}; {КРУП} '
                f'font-size: 30px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{i + 1}</div>'
                f'<div><div style="{ТЕКСТ} font-weight: 700; font-size: 38px; color: {ЧЕРН};">{з}</div>'
                f'<div style="{ТЕКСТ} font-size: 30px; line-height: 1.38; color: {СЕР}; margin-top: 6px;">{чипы(т)}</div></div></div>'),
                отступ="30px 36px")
        тело = метка(к["метка"]) + заголовок(к["заголовок"], 180, 84) + карты
    elif вид == "глава":
        имя, хвост = к["файл"].split(".")
        тёмная = к.get("тёмная_карта", False)
        тело = (метка(к["метка"])
                + f'<div style="position: absolute; left: 74px; top: 250px; {КРУП} font-size: 140px; line-height: 1; color: {ЧЕРН};">'
                  f'{имя}{маркер("." + хвост)}</div>'
                + абзац(к["подводка"], 420, 38)
                + карта(530, пункты(к["пункты"], тёмная), тёмная=тёмная))
    elif вид == "сетка":
        плитки = "".join(
            f'<div style="height: 132px; border-radius: 22px; background: #FFFFFF; border: 1px solid rgba(20,20,19,.06); '
            f'box-shadow: {ТЕНЬ}; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;">'
            f'<img src="{з}.svg" style="height: 42px;"><div style="{ТЕКСТ} font-size: 22px; color: {СЕР};">{и}</div></div>'
            for з, и in к["площадки"])
        тело = (метка(к["метка"]) + заголовок(к["заголовок"], 180, 80) + абзац(чипы(к["подводка"]), 380, 32)
                + f'<div style="position: absolute; left: 80px; top: 590px; width: 920px; display: grid; '
                  f'grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px;">{плитки}</div>'
                + f'<div style="position: absolute; left: 80px; top: 1060px; {МОНО} font-size: 20px; letter-spacing: .04em; '
                  f'color: {СЕР};">{к["сноска"]}</div>')
    else:
        raise SystemExit(f"неизвестный вид кадра: {вид}")
    # У автора содержимое стоит ближе к середине кадра, а не у верха: опускаем его, не заходя
    # ниже 1105 (полоса знака). Метка раздела остаётся наверху.
    сдвиг = {"инструмент": 40, "шаги": 70, "глава": 60, "сетка": 0}[вид]
    метка_ = метка(к["метка"])
    тело = тело.replace(метка_, "", 1)
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>' + метка_
            + f'<div style="position: absolute; left: 0; top: {сдвиг}px; width: 1080px; height: 1100px;">{тело}</div>'
            + низ(счёт))


def объём(цвет: str, бок: str, глубина: int = 10) -> str:
    """Объёмные буквы, как на постере автора: слои тени вниз-вправо и мягкая тень под ними."""
    слои = ", ".join(f"{i * .6:.1f}px {i}px 0 {бок}" for i in range(1, глубина + 1))
    return f"color: {цвет}; text-shadow: {слои}, 0 {глубина + 14}px 30px rgba(40,25,10,.35);"


def обложка_постер(о: dict) -> str:
    стр = о["строки"]
    return (f'<img src="scena-montazh.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; object-fit: cover;">'
            f'<div style="position: absolute; left: 0; top: 60px; width: 1080px; text-align: center; {МОНО} font-size: 22px; '
            f'letter-spacing: .5em; font-weight: 700; color: #1C1B19;">{о["метка"]}</div>'
            f'<div style="position: absolute; left: 0; top: 118px; width: 1080px; text-align: center; {КРУП} font-size: 120px; '
            f'line-height: 1; {объём("#1C1B19", "#0A0A09", 8)}">{стр[0]}</div>'
            f'<div style="position: absolute; left: 0; top: 238px; width: 1080px; text-align: center; {КРУП} font-size: 158px; '
            f'line-height: 1; {объём(ЛАЙМ, "#5E7112", 12)}">{стр[1]}</div>'
            f'<div style="position: absolute; left: 150px; top: 452px; width: 780px; display: flex; align-items: center; gap: 30px;">'
            f'<div style="flex-grow: 1; height: 3px; background: #3A3530;"></div><div style="{КРУП} font-size: 64px; '
            f'{объём("#1C1B19", "#0A0A09", 5)}">{стр[2]}</div><div style="flex-grow: 1; height: 3px; background: #3A3530;"></div></div>'
            f'<div style="position: absolute; left: 0; top: 540px; width: 1080px; text-align: center; {КРУП} font-size: 150px; '
            f'line-height: 1; {объём(CLAUDE, "#9E4A2E", 12)}">{стр[3]}</div>'
            + низ(тёмный=True))


def обложка_число(о: dict) -> str:
    return (f'<div style="position: absolute; inset: 0; background: {стиль.ТЁМНЫЙ}; background-image: radial-gradient(circle at 20% 10%, '
            f'rgba(199,226,75,.20), rgba(199,226,75,0) 45%);"></div>'
            f'<div style="position: absolute; left: 60px; top: 60px; {КРУП} font-size: 400px; line-height: 1; color: {ЛАЙМ};">{о["число"]}</div>'
            f'<div style="position: absolute; left: 80px; top: 470px; width: 920px; {КРУП} font-size: 92px; line-height: 1.04; '
            f'color: {стиль.СВЕТЛЫЙ};">{о["строки"][0]}<br><span style="color: {ЛАЙМ};">{о["строки"][1]}</span></div>'
            f'<div style="position: absolute; left: 80px; top: 700px; width: 520px; {ТЕКСТ} font-size: 40px; line-height: 1.35; '
            f'color: #C9CCBF;">{о["под"]}</div>'
            f'<div style="position: absolute; left: 80px; top: 820px; padding: 14px 24px; border-radius: 14px; border: 1px solid '
            f'rgba(241,243,234,.2); {МОНО} font-size: 26px; color: #C9CCBF;">{о["плашка"]}</div>'
            f'<img src="kot-noutbuk.webp" style="position: absolute; right: 30px; top: 640px; height: 560px;">'
            + низ(тёмный=True))


def обложка_сетка(о: dict, площадки: list) -> str:
    плитки = "".join(
        f'<div style="height: 112px; border-radius: 20px; background: #FFFFFF; box-shadow: {ТЕНЬ}; display: flex; '
        f'align-items: center; justify-content: center;"><img src="{з}.svg" style="height: 44px;"></div>' for з, _ in площадки)
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            + заголовок(о["строки"], 110, 124) + абзац(о["под"], 380, 42)
            + f'<div style="position: absolute; left: 80px; top: 520px; width: 280px; height: 360px; border-radius: 28px; '
              f'background: {ЧЕРН}; box-shadow: {ТЕНЬ}; display: flex; flex-direction: column; align-items: center; '
              f'justify-content: center; gap: 22px;"><div style="width: 0; height: 0; border-top: 44px solid transparent; '
              f'border-bottom: 44px solid transparent; border-left: 74px solid {ЛАЙМ}; margin-left: 16px;"></div>'
              f'<div style="{МОНО} font-size: 26px; color: {стиль.СВЕТЛЫЙ};">ролик.mp4</div></div>'
            + f'<div style="position: absolute; left: 385px; top: 650px; {КРУП} font-size: 84px; color: {ЧЕРН};">→</div>'
            + f'<div style="position: absolute; left: 500px; top: 520px; width: 500px; display: grid; '
              f'grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px;">{плитки}</div>'
            + f'<img src="kot-ukazyvaet.webp" style="position: absolute; right: 60px; top: 900px; height: 420px;">'
            + низ())


def финал(ф: dict, счёт: str) -> str:
    """Финал читается с расстояния ленты (слово владельца 23.09.2026: «не читается текст»).

    Вместо серого абзаца — карточка «что ты сохраняешь» из трёх жирных пунктов с галочками,
    призыв — тёмной плашкой с лаймом, «ссылка в профиле» — жирной тёмной строкой.
    """
    пункты = "".join(
        f'<div style="display: flex; gap: 22px; align-items: center;">'
        f'<div style="width: 52px; height: 52px; border-radius: 26px; background: {ЛАЙМ}; flex-shrink: 0; display: flex; '
        f'align-items: center; justify-content: center; {КРУП} font-size: 30px; color: {ЧЕРН};">✓</div>'
        f'<div style="{ТЕКСТ} font-size: 40px; line-height: 1.2; color: {ЧЕРН}; white-space: nowrap;"><b>{ж}</b> {т}</div></div>'
        for ж, т in ф["итог"])
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            + заголовок(ф["строки"], 110, 112)
            + карта(380, пункты, отступ="40px 44px", шаг=28).replace("width: 920px", "width: 680px")
            + f'<div style="position: absolute; left: 80px; top: 780px; padding: 28px 44px; border-radius: 999px; '
              f'background: {ЧЕРН}; box-shadow: 0 12px 30px rgba(20,20,19,.25); {ТЕКСТ} font-weight: 700; font-size: 44px; '
              f'color: {ЛАЙМ};">{ф["кнопка"]}</div>'
            + f'<div style="position: absolute; left: 84px; top: 920px; {ТЕКСТ} font-weight: 700; font-size: 40px; '
              f'color: {ЧЕРН};">{ф["под_кнопкой"]} ↗</div>'
            + f'<img src="kot-ukazyvaet.webp" style="position: absolute; right: -40px; top: 620px; height: 540px;">'
            + низ(счёт))


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    CSS = дх.шрифты_холста(CSS, корень)
    врем = корень / "_файлы"
    площадки = next(к["площадки"] for к in пост["кадры"] if к["вид"] == "сетка")
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот("noutbuk", врем), дх.кот("ukazyvaet", врем),
                            ТУТ / "картинки" / "scena-montazh.jpg"]
    файлы += [ТУТ / "значки" / f"{з}.svg" for з, _ in площадки]
    всего = len(пост["кадры"]) + 2
    обложки = {"постер": lambda: обложка_постер(пост["обложка_постер"]),
               "число": lambda: обложка_число(пост["обложка_число"]),
               "сетка": lambda: обложка_сетка(пост["обложка_сетка"], площадки)}
    главная = пост.get("главная", "постер")
    порядок = [главная] + [и for и in обложки if и != главная]
    фон = "#F5F4EF"
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", дх.доска("Обложка", обложки[главная](), фон, CSS))]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['метка'][:24]}", дх.доска(к["метка"], кадр(к, н, всего), фон, CSS)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"], f"{всего:02d} / {всего:02d}"), фон, CSS)))
    for н, и in enumerate(порядок[1:], 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", дх.доска(f"Обложка {н}", обложки[и](), фон, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=6,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
