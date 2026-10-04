# -*- coding: utf-8 -*-
"""Лента промптов: python холст.py посты/<пост>.json

Рерайт @theromanknox (instagram.com/p/DY45Vg1iHU4, разбор — `референс/паспорт.md`, `ДИЗАЙН.md`).
Повторено: светлый лист в клетку, слева линия-хребет с квадратными метками, вдоль неё три карточки
промптов (плашка-заголовок + плитка-значок + промпт в ёлочках), заголовок кадра крупно в две строки,
служебная полоса со счётом и «листай», обложка-постер с тремя плашками, бонус с 3D-окном, финал с
3D-документом. Наше: лайм→олива вместо красно-оранжевого (плашки — тёмный текст на лайме, лайм
текстом по светлому не читается), графитовые плитки с лаймовыми значками Phosphor, знак канала вместо
ника, кот на обложках и в финале, Telegram вместо воронки «Comment PDF».

Доска 1080×1440: всё важное выше 1105, знак в полосе 1191..1235 (`../замер.py`). Собирает правимый
холст `холсты/<пост>/project/` (`../дизайн_холст.py`); после «готово» — `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

ЗНАЧКИ = стиль.ПОСТБОТ / "reels" / "node_modules" / "@phosphor-icons" / "core" / "assets" / "fill"
ЛАЙМ, ОЛИВА, ГРАФ, ЧЕРН, СЕР = стиль.ЛАЙМ, стиль.ОЛИВА, стиль.ТЁМНЫЙ, "#141413", "#3A3A33"
ЛИСТ = "#F6F5EF"
# Лист в клетку, как у автора: тонкие линии через 44 px и мягкое лаймовое свечение в углу.
ФОН = (f"background-color: {ЛИСТ}; background-image: radial-gradient(circle at 96% 2%, rgba(199,226,75,.28), "
       f"rgba(199,226,75,0) 30%), linear-gradient(rgba(20,20,19,.05) 1px, transparent 1px), "
       f"linear-gradient(90deg, rgba(20,20,19,.05) 1px, transparent 1px); background-size: auto, 44px 44px, 44px 44px;")
ГРАДИЕНТ = f"linear-gradient(90deg, {ЛАЙМ}, #A9C83A)"          # плашки: у автора красный→оранжевый
ТЕНЬ = "0 1px 2px rgba(20,20,19,.05), 0 14px 34px rgba(60,74,12,.12)"
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.03em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CLAUDE = дх.CLAUDE
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))


def значок(имя: str, цвет: str = ЛАЙМ, размер: int = 52) -> str:
    svg = (ЗНАЧКИ / f"{имя}-fill.svg").read_text(encoding="utf-8")
    return svg.replace("<svg ", f'<svg style="width: {размер}px; height: {размер}px; color: {цвет}; display: block;" ', 1)


def маркер(текст: str) -> str:
    return дх.маркер(текст, чернила=ЧЕРН)


def claude(текст: str) -> str:
    return текст.replace("Claude", f'<span style="color: {CLAUDE};">Claude</span>')


def низ(н: int = 0, всего: int = 0, тёмный: bool = False) -> str:
    """Служебная полоса как у автора: слева знак, справа счёт N / M и «листай»."""
    лого = "" if тёмный else "filter: brightness(.45) saturate(1.4);"
    out = f'<img src="logo.png" style="position: absolute; left: 80px; top: 1191px; height: 44px; {лого}">'
    if н:
        out += (f'<div style="position: absolute; left: 700px; top: 1192px; height: 42px; padding: 0 18px; border-radius: 21px; '
                f'background: rgba(199,226,75,.35); {ТЕКСТ} font-weight: 700; font-size: 24px; line-height: 42px; color: {ЧЕРН};">'
                f'{н} / {всего}</div>'
                f'<div style="position: absolute; left: 820px; top: 1190px; height: 46px; display: flex; align-items: center; gap: 12px; '
                f'padding: 0 8px 0 22px; border-radius: 23px; border: 2px solid {ЧЕРН}; {ТЕКСТ} font-weight: 700; font-size: 24px; color: {ЧЕРН};">'
                f'листай<div style="width: 52px; height: 32px; border-radius: 16px; background: {ЛАЙМ}; display: flex; align-items: center; '
                f'justify-content: center;">{значок("arrow-right", ЧЕРН, 22)}</div></div>')
    return out


def карточка(п: dict) -> str:
    """Плашка-заголовок над светлым телом; в теле плитка-значок и промпт. Метка на хребте — слева."""
    return (f'<div style="position: relative;">'
            f'<div style="position: absolute; left: -62px; top: 12px; width: 36px; height: 36px; border-radius: 9px; background: {ЛАЙМ}; '
            f'box-shadow: 0 0 0 4px {ЛИСТ}; display: flex; align-items: center; justify-content: center;">{значок("caret-right", ЧЕРН, 22)}</div>'
            f'<div style="display: inline-block; padding: 10px 26px 12px; border-radius: 14px 14px 14px 0; background: {ГРАДИЕНТ}; '
            f'{КРУП} font-size: 35px; line-height: 1.1; color: {ЧЕРН};">{п["плашка"]}:</div>'
            f'<div style="display: flex; gap: 28px; padding: 28px 32px 30px 28px; border-radius: 0 22px 22px 22px; '
            f'background: linear-gradient(90deg, #FFFFFF 60%, rgba(255,255,255,.55)); box-shadow: {ТЕНЬ};">'
            f'<div style="width: 96px; height: 96px; flex-shrink: 0; border-radius: 24px; background: {ГРАФ}; display: flex; '
            f'align-items: center; justify-content: center; box-shadow: 0 10px 20px rgba(18,19,15,.25);">{значок(п["значок"])}</div>'
            f'<div style="{ТЕКСТ} font-size: 27px; line-height: 1.3; color: {ЧЕРН}; font-weight: 400;">{claude(п["промпт"])}</div>'
            f'</div></div>')


def кадр_промптов(пост: dict, тройка: list, н: int, всего: int) -> str:
    з = пост["заголовок_промптов"]
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            f'<div style="position: absolute; left: 80px; top: 52px; {КРУП} font-size: 72px; line-height: 1.04; color: {ЧЕРН};">'
            f'{з[0]}<br>{маркер(з[1])}</div>'
            # линия-хребет: от первой метки до последней карточки
            f'<div style="position: absolute; left: 95px; top: 268px; width: 6px; height: 800px; border-radius: 3px; background: {ГРАФ}; pointer-events: none;"></div>'
            f'<div style="position: absolute; left: 140px; top: 244px; width: 870px; display: flex; flex-direction: column; gap: 22px;">'
            + "".join(карточка(п) for п in тройка) + '</div>' + низ(н, всего))


def вступление(в: dict, н: int, всего: int) -> str:
    з = в["заголовок"]
    строки = f'{з[0]}<br>{з[1]}<br>{маркер(з[2])}<br>{з[3]}'
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            f'<div style="position: absolute; left: 80px; top: 120px; width: 940px; {КРУП} font-size: 88px; line-height: 1.08; '
            f'color: {ЧЕРН};">{строки.replace('CLAUDE', f'<span style="color: {CLAUDE};">CLAUDE</span>')}</div>'
            f'<div style="position: absolute; left: 80px; top: 620px; width: 900px; {ТЕКСТ} font-weight: 700; font-size: 44px; '
            f'line-height: 1.25; color: {ЧЕРН};">{в["жирно"]}</div>'
            f'<div style="position: absolute; left: 80px; top: 770px; width: 900px; {ТЕКСТ} font-size: 38px; line-height: 1.38; '
            f'color: {СЕР};">{claude(в["абзац"])}</div>'
            f'<div style="position: absolute; left: 80px; top: 950px; width: 900px; {ТЕКСТ} font-weight: 700; font-size: 44px; '
            f'line-height: 1.25; color: {ЧЕРН};">{в["итог"]} ↓</div>'
            + низ(н, всего))


def бонус(б: dict, н: int, всего: int) -> str:
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            f'<img src="bonus-window.png" style="position: absolute; left: 80px; top: 46px; width: 400px;">'
            f'<div style="position: absolute; left: 80px; top: 478px; {ТЕКСТ} font-weight: 700; font-size: 36px; color: {ЧЕРН};">{б["над"]}</div>'
            f'<div style="position: absolute; left: 76px; top: 560px; width: 940px; {КРУП} font-size: 104px; line-height: 1.02; color: {ЧЕРН};">'
            f'{б["строки"][0]}<br>{маркер(б["строки"][1])}</div>'
            f'<div style="position: absolute; left: 80px; top: 822px; width: 920px; {ТЕКСТ} font-weight: 700; font-size: 37px; '
            f'line-height: 1.3; color: {ЧЕРН};">{claude(б["промпт"])}</div>'
            + низ(н, всего))


def финал(ф: dict, н: int, всего: int) -> str:
    return (f'<div style="position: absolute; inset: 0; {ФОН}"></div>'
            f'<img src="final-doc.png" style="position: absolute; left: 350px; top: 46px; width: 380px;">'
            f'<div style="position: absolute; left: 80px; top: 540px; width: 580px; height: 540px; border-radius: 30px; pointer-events: none; '
            f'background: linear-gradient(160deg, rgba(199,226,75,.28), rgba(255,255,255,.7) 60%); box-shadow: {ТЕНЬ};"></div>'
            f'<div style="position: absolute; left: 80px; top: 590px; width: 8px; height: 150px; border-radius: 4px; background: {ГРАФ}; pointer-events: none;"></div>'
            f'<div style="position: absolute; left: 130px; top: 580px; width: 500px; {КРУП} font-size: 58px; line-height: 1.08; color: {ЧЕРН};">'
            f'{ф["строки"][0]}<br>{ф["строки"][1]}</div>'
            f'<div style="position: absolute; left: 80px; top: 800px; width: 8px; height: 200px; border-radius: 4px; background: {ГРАФ}; pointer-events: none;"></div>'
            f'<div style="position: absolute; left: 130px; top: 794px; width: 490px; {ТЕКСТ} font-weight: 700; font-size: 44px; line-height: 1.2; '
            f'color: {ЧЕРН};">{ф["главное"]} {маркер(ф["акцент"])}</div>'
            f'<div style="position: absolute; left: 130px; top: 960px; width: 490px; {ТЕКСТ} font-size: 32px; line-height: 1.35; '
            f'color: {СЕР};">{ф["под"]}</div>'
            f'<img src="kot-ukazyvaet.webp" data-кот style="position: absolute; left: 640px; top: 730px; height: 360px;">'
            + низ(н, всего))


# ── Обложки: три разных подхода ─────────────────────────────────────────────

def плашка(текст: str, фон: str, цвет: str, кегль: int, хвост: str = "") -> str:
    х = f'<span style="font-size: {int(кегль * .42)}px; letter-spacing: 0;">{хвост}</span>' if хвост else ""
    return (f'<div style="display: inline-block; padding: 6px 34px 14px; border-radius: 26px; background: {фон}; '
            f'box-shadow: 0 18px 40px rgba(0,0,0,.35), inset 0 2px 0 rgba(255,255,255,.35); {КРУП} font-size: {кегль}px; '
            f'line-height: 1.08; color: {цвет}; white-space: nowrap;">{текст}{х}</div>')


def знак(символ: str) -> str:
    return (f'<div style="width: 64px; height: 50px; border-radius: 12px; background: {ЛАЙМ}; {КРУП} font-size: 44px; '
            f'line-height: 46px; text-align: center; color: {ЧЕРН}; margin: -6px auto; position: relative; z-index: 2;">{символ}</div>')


def обложка_постер(о: dict) -> str:
    """Как у автора: постер из объёмных предметов, внизу три плашки «A + B = сумма»."""
    п = о["плашки"]
    return (f'<div style="position: absolute; inset: 0; background: #0D0E0A; pointer-events: none;"></div>'
            f'<img src="cover-poster.jpg" style="position: absolute; left: 0; top: -170px; width: 1080px; height: 1446px; pointer-events: none;">'
            f'<div style="position: absolute; left: 0; top: 520px; width: 1080px; height: 920px; pointer-events: none; '
            f'background: linear-gradient(rgba(13,14,10,0), rgba(13,14,10,.8) 32%);"></div>'
            f'<div style="position: absolute; left: 0; top: 660px; width: 1080px; text-align: center;">'
            + плашка(п[0], f"linear-gradient(90deg, #E58A62, {CLAUDE})", "#FFFFFF", 112)
            + знак("+") + плашка(п[1], "#F6F5EF", ГРАФ, 88) + знак("=")
            + плашка(п[2], ГРАДИЕНТ, ГРАФ, 112, о.get("хвост", "")) + '</div>'
            + низ(тёмный=True))


def обложка_авто(о: dict) -> str:
    """Запасная: «без камеры, лица и голоса» — сцена с котом за ноутбуком, текст сверху на светлом."""
    return (f'<img src="cover-auto.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; object-fit: cover;">'
            f'<div style="position: absolute; left: 80px; top: 90px; width: 940px; {КРУП} font-size: 132px; line-height: 1.0; color: {ЧЕРН};">'
            f'{о["строки"][0]}<br>{маркер(о["строки"][1])}</div>'
            f'<div style="position: absolute; left: 84px; top: 380px; width: 860px; {ТЕКСТ} font-weight: 700; font-size: 46px; '
            f'line-height: 1.25; color: {ЧЕРН};">{claude(о["под"])}</div>'
            + низ())


def обложка_число(о: dict) -> str:
    """Запасная: огромное «12» лаймом на тёмном, кот со свитком выглядывает справа снизу."""
    с = о["строки"]
    return (f'<img src="cover-twelve.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; object-fit: cover;">'
            f'<div style="position: absolute; left: 80px; top: 40px; {КРУП} font-size: 440px; line-height: 1; color: {ЛАЙМ}; '
            f'text-shadow: 0 30px 80px rgba(199,226,75,.25);">{о["число"]}</div>'
            f'<div style="position: absolute; left: 80px; top: 500px; width: 900px; {КРУП} font-size: 92px; line-height: 1.04; '
            f'color: {стиль.СВЕТЛЫЙ};">{с[0]}<br>{с[1]}<br><span style="color: {ЛАЙМ};">{с[2]}</span></div>'
            f'<div style="position: absolute; left: 80px; top: 830px; padding: 14px 26px; border-radius: 16px; border: 2px solid '
            f'rgba(241,243,234,.25); {ТЕКСТ} font-weight: 700; font-size: 34px; color: #D7DACB;">{claude(о["плашка"])}</div>'
            + низ(тёмный=True))


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    try:
        CSS = дх.шрифты_холста(CSS, корень)
    except SystemExit as е:
        # проба до выкладки: шрифты ещё не загружены на холст, локальные файлы рядом с досками
        print(f"⚠️  {е} — собираю с локальными шрифтами (до выкладки загрузить)")
    врем = корень / "_файлы"
    картинки = ["cover-poster.jpg", "cover-auto.jpg", "cover-twelve.jpg", "bonus-window.png", "final-doc.png"]
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот("ukazyvaet", врем)] + [ТУТ / "картинки" / к for к in картинки]
    нет = [ф for ф in файлы if not ф.exists()]
    if нет:
        print("для снабженца:", ", ".join(ф.name for ф in нет))
        raise SystemExit(2)
    тройки = [пост["промпты"][i:i + 3] for i in range(0, 12, 3)]
    всего = 2 + len(тройки) + 1                       # вступление, промпты, бонус, финал — счёт как у автора: 1 / 7 … 7 / 7
    обложки = {"постер": lambda: обложка_постер(пост["обложка_постер"]),
               "авто": lambda: обложка_авто(пост["обложка_авто"]),
               "число": lambda: обложка_число(пост["обложка_число"])}
    главная = пост.get("главная", "постер")
    порядок = [главная] + [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", дх.доска("Обложка", обложки[главная](), ЛИСТ, CSS)),
             ("Kadr02.dc.html", "02 · Вступление", дх.доска("Вступление", вступление(пост["вступление"], 1, всего), ЛИСТ, CSS))]
    for к, т in enumerate(тройки):
        доски.append((f"Kadr{к + 3:02d}.dc.html", f"{к + 3:02d} · Промпты {к * 3 + 1}–{к * 3 + 3}",
                      дх.доска(f"Промпты {к * 3 + 1}–{к * 3 + 3}", кадр_промптов(пост, т, к + 2, всего), ЛИСТ, CSS)))
    н = len(доски) + 1
    доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · Бонус", дх.доска("Бонус", бонус(пост["бонус"], всего - 1, всего), ЛИСТ, CSS)))
    доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · Финал", дх.доска("Финал", финал(пост["финал"], всего, всего), ЛИСТ, CSS)))
    for к, и in enumerate(порядок[1:], 2):
        доски.append((f"Oblozhka{к}.dc.html", f"Обложка {к} · {и}", дх.доска(f"Обложка {к}", обложки[и](), ЛИСТ, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
