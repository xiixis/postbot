# -*- coding: utf-8 -*-
"""Вариация стиля «сервисы»: один навык на кадр — что это, зачем и чем он делается.

    python3 навыки.py посты/<пост>.json [--без-снимка]

Снята с карусели Instagram «AI Skills You Need in 2026» (references №23, DVs-D4JgYiB).
Устройство автора: чёрный кадр, из верхнего угла бьют оранжевые лучи и проступает сетка;
узкий жирный заголовок навыка капсом с переходом из белого в оранжевый; две капсулы-метки
«What it is» и «Why it matters», под каждой абзац с отступом; внизу ряд значков сервисов
с подписями. Обложка — персонаж-телевизор и крупное «AI Skills» с линией «You Need in 2026».

Что перенесено: чёрный грунт с лучами из угла (угол чередуется от кадра к кадру, как у автора),
сетка в свечении, узкий капс с переходом в оранжевый, две капсулы с оранжевой обводкой, отступ
абзаца, ряд значков внизу, служебная строка сверху по центру. Оранжевый оставлен авторским:
без него пропадает вид (решение 25.09, остальные посты стиля — в фирменных цветах).

Что наше: подписи по-простому вместо терминов, кот вместо персонажа-телевизора (телевизор
остался у кота в лапах), финал «с чего начать» вместо рекламного кадра автора, логотип
на каждом кадре. Контраст у автора 20:1 — держим так же.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402
import обложки  # noqa: E402
import приёмка_досок  # noqa: E402

ГРУНТ = "#0C0C0A"
БЕЛЫЙ, ВТОРОЙ = "#F5F2EE", "#E4DFD8"
ТИХИЙ = "#B9B2A8"
ОГОНЬ, ОГОНЬ_RGB = "#FF7A1A", "255,122,26"
ПЛАШКА, НА_ПЛАШКЕ = "#FF8C33", "#0B0703"      # 8,2:1 — на #FF7A1A тёмный текст давал 7,5
ПЕРЕХОД = "linear-gradient(100deg, #FFFFFF 0%, #FFE6D2 34%, #FF9A4A 66%, #FF6A0F 100%)"

УЗКИЙ = "font-family: Oswald, 'Arial Narrow', sans-serif; font-weight: 600; text-transform: uppercase;"
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CSS, ШРИФТЫ = дх.шрифты(("Oswald", "oswald-600", 600), ("Onest", "onest-800", 800),
                        ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))

КРАЙ = 70
ШИРИНА = 1080 - 2 * КРАЙ
СТЕКЛО = "linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(12,12,10,.7) 100%)"
РАМКА = "rgba(245,242,238,.14)"


def свет(угол: str = "справа") -> str:
    """Лучи, свечение и сетка из верхнего угла. Лучи — узкие светлые клинья, как у автора."""
    x = 100 if угол == "справа" else 0
    откуда = 215 if угол == "справа" else 125
    маска = f"radial-gradient(70% 52% at {x}% 0%, #000 0%, rgba(0,0,0,.4) 45%, transparent 78%)"
    return (f'<div style="position: absolute; inset: 0; background: '
            f'radial-gradient(62% 44% at {x}% 0%, rgba({ОГОНЬ_RGB},.62) 0%, rgba({ОГОНЬ_RGB},.18) 42%, rgba({ОГОНЬ_RGB},0) 72%), '
            f'radial-gradient(40% 26% at {100 - x}% 0%, rgba({ОГОНЬ_RGB},.14) 0%, rgba({ОГОНЬ_RGB},0) 70%), {ГРУНТ};"></div>'
            f'<div style="position: absolute; inset: 0; background: repeating-conic-gradient(from {откуда}deg at {x}% -4%, '
            f'rgba(255,170,100,0) 0deg 2.6deg, rgba(255,170,100,.30) 2.6deg 2.85deg, rgba(255,170,100,0) 2.85deg 5.2deg); '
            f'-webkit-mask-image: {маска}; mask-image: {маска};"></div>'
            f'<div style="position: absolute; inset: 0; background-image: '
            f'linear-gradient(rgba({ОГОНЬ_RGB},.22) 1px, transparent 1px), '
            f'linear-gradient(90deg, rgba({ОГОНЬ_RGB},.22) 1px, transparent 1px); background-size: 96px 96px; '
            f'-webkit-mask-image: {маска}; mask-image: {маска};"></div>')


ТЕМА = обложки.Тема(грунт=f"radial-gradient(60% 42% at 100% 0%, rgba({ОГОНЬ_RGB},.40) 0%, rgba({ОГОНЬ_RGB},0) 70%), {ГРУНТ}",
                    тёмная=True, чернила=БЕЛЫЙ, второй=ВТОРОЙ, тихий=ТИХИЙ, карточка=СТЕКЛО,
                    карточка_тихая="rgba(255,255,255,.06)", рамка=РАМКА, тень="0 18px 44px rgba(0,0,0,.45)",
                    стрелка=ОГОНЬ, крупный=КРУП, текст=ТЕКСТ, акцент=ОГОНЬ, на_акценте="#140A02",
                    край=КРАЙ, свет=ОГОНЬ_RGB)


def низ() -> str:
    return f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px;">'


def шапка(текст: str) -> str:
    return (f'<div style="position: absolute; left: 0; top: 64px; width: 1080px; text-align: center; {ТЕКСТ} '
            f'font-weight: 700; font-size: 28px; color: {БЕЛЫЙ}; text-shadow: 0 2px 10px rgba(0,0,0,.6);">{текст}</div>')


def кегль_узкого(текст: str, наибольший: int = 132, наименьший: int = 100) -> int:
    """Крупнейший кегль, при котором каждое слово заголовка встаёт в ширину кадра целиком."""
    слова = текст.upper().split()
    for к in range(наибольший, наименьший - 1, -4):
        if all(приёмка_досок.ширина_строки(с, "Oswald", 600, к) <= ШИРИНА for с in слова):
            return к
    return наименьший


def переход(текст: str, кегль: int) -> str:
    return (f'<div style="display: inline-block; {УЗКИЙ} font-size: {кегль}px; line-height: .94; letter-spacing: .005em; '
            f'background: {ПЕРЕХОД}; -webkit-background-clip: text; background-clip: text; '
            f'-webkit-text-fill-color: transparent; color: {ОГОНЬ};">{текст}</div>')


def капсула(текст: str) -> str:
    return (f'<div style="align-self: flex-start; padding: 8px 26px 12px; border-radius: 999px; '
            f'border: 3px solid {ОГОНЬ}; background: rgba(12,12,10,.55); {ТЕКСТ} font-weight: 700; '
            f'font-size: 36px; line-height: 1.1; color: {БЕЛЫЙ};">{текст}</div>')


def абзац(текст: str) -> str:
    return (f'<div style="margin-left: 58px; {ТЕКСТ} font-size: 40px; line-height: 1.3; color: {ВТОРОЙ};">'
            f'{текст}</div>')


def значки(сервисы: list[dict]) -> str:
    ряд = ""
    for с in сервисы:
        заливка = с.get("фон", "#FFFFFF")
        доля = "100%" if с.get("во_весь") else f'{с.get("размер", 66)}%'
        ряд += (f'<div style="width: 170px; display: flex; flex-direction: column; align-items: center; gap: 14px;">'
                f'<div style="width: 116px; height: 116px; border-radius: 28px; background: {заливка}; overflow: hidden; '
                f'display: flex; align-items: center; justify-content: center; '
                f'box-shadow: 0 16px 34px rgba(0,0,0,.5), 0 0 0 2px rgba(255,255,255,.12);">'
                f'<img src="{с["значок"]}" style="width: {доля}; height: {доля}; object-fit: {"cover" if с.get("во_весь") else "contain"};">'
                f'</div><div style="{ТЕКСТ} font-weight: 700; font-size: 26px; line-height: 1.1; color: {БЕЛЫЙ}; '
                f'text-align: center;">{с["имя"]}</div></div>')
    return f'<div style="margin-top: auto; display: flex; gap: 20px;">{ряд}</div>'



def кадр_навыка(н: int, всего: int, ш: dict, шапка_текст: str) -> str:
    угол = "справа" if н % 2 else "слева"
    загл = ш["заголовок"]
    к = кегль_узкого(загл)
    под = (f'<div style="margin-top: 14px; {ТЕКСТ} font-weight: 700; font-size: 46px; line-height: 1.15; '
           f'color: {БЕЛЫЙ};">{ш["под"]}</div>') if ш.get("под") else ""
    return (свет(угол)
            + шапка(f"{шапка_текст}&nbsp;&nbsp;|&nbsp;&nbsp;{н} из {всего}")
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 140px; width: {ШИРИНА}px; height: 950px; '
              f'display: flex; flex-direction: column; gap: 20px;">'
              f'<div style="margin-bottom: 18px;">{переход(загл, к)}{под}</div>'
              f'{капсула("Что это")}{абзац(ш["что"])}'
              f'<div style="height: 8px;"></div>'
              f'{капсула("Зачем")}{абзац(ш["зачем"])}'
              f'{значки(ш["сервисы"])}</div>'
            + низ())


def обложка(о: dict) -> str:
    """Главная как у автора: крупное слово с переходом в оранжевый и линия с годом; кот с телевизором."""
    к = обложки.карточка(о["сцена"])
    x0, y0, x1, y1 = к["пусто"]
    линия = f'<div style="flex-grow: 1; height: 4px; background: {БЕЛЫЙ}; opacity: .85;"></div>'
    return (f'<div style="position: absolute; inset: 0; background: {ГРУНТ};"></div>'
            + f'<img src="{о["сцена"]}.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; '
              f'object-fit: cover;">'
            + обложки.кот_сцены(к)
            + f'<div style="position: absolute; left: {КРАЙ}px; top: {о.get("top", y0)}px; width: {ШИРИНА}px; display: flex; '
              f'flex-direction: column; align-items: center; gap: 18px;">'
              f'<div style="{КРУП} font-size: {о.get("кегль", 156)}px; line-height: 1; white-space: nowrap; background: {ПЕРЕХОД}; '
              f'-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; '
              f'color: {БЕЛЫЙ}; text-shadow: none;">{о["заголовок"]}</div>'
              f'<div style="width: 100%; display: flex; align-items: center; gap: 26px;">{линия}'
              f'<div style="{ТЕКСТ} font-weight: 400; font-size: 64px; line-height: 1; color: {БЕЛЫЙ}; white-space: nowrap;">'
              f'{о["под"]}</div>{линия}</div></div>'
            + низ())


def финал(ф: dict) -> str:
    """С чего начать: три шага по порядку и плашка-призыв; кот сбоку."""
    пункты = ""
    for н, (что, зачем) in enumerate(ф["шаги"], 1):
        пункты += (f'<div style="display: flex; gap: 26px; align-items: flex-start;">'
                   f'<div style="width: 70px; height: 70px; flex-shrink: 0; border-radius: 50%; background: {ПЛАШКА}; '
                   f'display: flex; align-items: center; justify-content: center; {КРУП} font-size: 38px; color: {НА_ПЛАШКЕ};">{н}</div>'
                   f'<div><div style="{ТЕКСТ} font-weight: 700; font-size: 44px; line-height: 1.1; color: {БЕЛЫЙ};">{что}</div>'
                   f'<div style="margin-top: 4px; {ТЕКСТ} font-size: 32px; line-height: 1.25; color: {ВТОРОЙ};">{зачем}</div>'
                   f'</div></div>')
    return (свет("справа")
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 130px; width: 620px;">'
              f'<div>{переход(ф["строки"][0], 150)}</div><div>{переход(ф["строки"][1], 150)}</div></div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" style="position: absolute; left: 690px; top: 110px; height: 300px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 440px; width: 830px; box-sizing: border-box; '
              f'padding: 36px 40px 38px; border-radius: 40px; background: {СТЕКЛО}; border: 2px solid {РАМКА}; '
              f'display: flex; flex-direction: column; gap: 28px;">{пункты}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 948px; width: 830px; box-sizing: border-box; '
              f'padding: 24px 36px 28px; border-radius: 32px; background: {ПЛАШКА};">'
              f'<div style="{КРУП} font-size: 50px; line-height: 1.04; color: {НА_ПЛАШКЕ};">{ф["призыв"]}</div>'
              f'<div style="margin-top: 8px; {ТЕКСТ} font-weight: 700; font-size: 32px; color: {НА_ПЛАШКЕ};">{ф["ссылка"]}</div></div>'
            + низ())


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    CSS = дх.шрифты_холста(CSS, корень)
    врем = корень / "_файлы"
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот(пост["финал"]["поза"], врем)]
    файлы += обложки.файлы(пост.get("запасные", {}), врем)
    файлы += обложки.файлы({"главная": {"сцена": пост["обложка"]["сцена"]}}, врем)
    значки_файлы = {}
    for ш in пост["навыки"]:
        for с in ш["сервисы"]:
            путь = ТУТ / "значки" / с["файл"]
            значки_файлы[путь.name] = путь
            с["значок"] = путь.name
    файлы += list(значки_файлы.values())
    ряд = [с for ш in пост["навыки"] for с in ш["сервисы"]]
    ряд = list({с["значок"]: с for с in ряд}.values())
    своя = ("огонь", ГРУНТ, обложка(пост["обложка"]))
    обл = обложки.доски_обложек(пост, своя, ТЕМА, {"значки": ряд[:6]}, CSS)
    доски = обл[:1]
    всего = len(пост["навыки"])
    for н, ш in enumerate(пост["навыки"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {ш['заголовок']}",
                      дх.доска(ш["заголовок"], кадр_навыка(н, всего, ш, пост["шапка"]), ГРУНТ, CSS)))
    доски.append((f"Kadr{всего + 2:02d}.dc.html", f"{всего + 2:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"]), ГРУНТ, CSS)))
    доски += обл[1:]
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=6,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")
    приёмка_досок.доложить(проект, снимки="--без-снимка" not in sys.argv[2:])


if __name__ == "__main__":
    main()
