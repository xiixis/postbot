# -*- coding: utf-8 -*-
"""Светлый разбор, вид «главы»: python главы.py посты/<пост>.json

Вариация от @ankush_ai_growth (23.09.2026, `референс-ankush/`, `ВАРИАЦИИ.md`): метка раздела
моноширинным капсом, заголовок слева в две строки с акцентным хвостом, подводка, карточка —
шаги, пункты «жирное — пояснение», код или сетка значков площадок; счётчик NN / NN у знака.
У автора все кадры светлые — здесь светлые и тёмные чередуются, акцент — наш (олива по
светлому, лайм по тёмному), а не его синий.

Всё важное — выше 1105 px доски 1080×1440: знак стоит в служебной полосе 1191..1235
(`замер.py`), ниже — подпись и кнопки площадки. Собирает правимый холст
`холсты/<пост>/project/` (`../дизайн_холст.py`); после «готово» — `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

СВЕТ = {"фон": "#F2F1EF", "текст": "#1C1C1A", "второй": "#3A3A37", "акцент": "#3F4D08",
        "карта": "#FFFFFF", "рамка": "rgba(28,28,26,.08)", "тень": "0 2px 4px rgba(23,22,20,.05), 0 14px 34px rgba(23,22,20,.08)",
        "лого": "filter: brightness(.45) saturate(1.4);", "значок": "none"}
ТЬМА = {"фон": стиль.ТЁМНЫЙ, "текст": стиль.СВЕТЛЫЙ, "второй": "#C9CCBF", "акцент": стиль.ЛАЙМ,
        "карта": "#1E2019", "рамка": "rgba(241,243,234,.10)", "тень": "none", "лого": "", "значок": "invert(1)"}
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
МОНО = "font-family: JetBrains, 'Courier New', monospace;"
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
                        ("JetBrains", "jetbrains-400", 400), ("JetBrains", "jetbrains-700", 700))


def низ(п: dict, счёт: str = "") -> str:
    с = (f'<div style="position: absolute; right: 80px; top: 1198px; {МОНО} font-size: 26px; color: {п["второй"]};">'
         f'{счёт}</div>') if счёт else ""
    return f'<img src="logo.png" style="position: absolute; left: 80px; top: 1191px; height: 44px; {п["лого"]}">' + с


def метка(п: dict, текст: str, верх: int = 80) -> str:
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; {МОНО} font-weight: 700; font-size: 26px; '
            f'letter-spacing: .14em; text-transform: uppercase; color: {п["акцент"]};">{текст}</div>')


def заголовок(п: dict, строки: list[str], верх: int, кегль: int = 88) -> str:
    хвост = f'<br><span style="color: {п["акцент"]};">{строки[1]}</span>' if len(строки) > 1 else ""
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: 920px; {КРУП} font-size: {кегль}px; '
            f'line-height: 1.04; color: {п["текст"]};">{строки[0]}{хвост}</div>')


def абзац(п: dict, текст: str, верх: int, кегль: int = 36, жирный: bool = False) -> str:
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: 900px; {ТЕКСТ} '
            f'font-weight: {700 if жирный else 400}; font-size: {кегль}px; line-height: 1.35; color: {п["второй"]};">{текст}</div>')


def карта(п: dict, верх: int, тело: str, отступ: str = "36px 40px", тёмная: bool = False, шаг: int = 34) -> str:
    фон = стиль.ТЁМНЫЙ if тёмная else п["карта"]
    return (f'<div style="position: absolute; left: 80px; top: {верх}px; width: 920px; box-sizing: border-box; '
            f'padding: {отступ}; border-radius: 28px; background: {фон}; border: 2px solid {п["рамка"]}; '
            f'box-shadow: {п["тень"]}; display: flex; flex-direction: column; gap: {шаг}px;">{тело}</div>')


def пункты(п: dict, список: list[list[str]]) -> str:
    return "".join(
        f'<div style="display: flex; gap: 20px; align-items: baseline; {ТЕКСТ} font-size: 40px; line-height: 1.3; color: {п["второй"]};">'
        f'<div style="width: 16px; height: 16px; border-radius: 8px; background: {п["акцент"]}; flex-shrink: 0; transform: translateY(-6px);"></div>'
        f'<div><span style="font-weight: 700; color: {п["текст"]};">{ж}</span> — {т}</div></div>' for ж, т in список)


def код(строки: list[list[str]]) -> str:
    """Строки кода: [[цвет, текст], ...]; цвет — «тихий», «лайм», «свет»."""
    цвета = {"тихий": "#8D9180", "лайм": стиль.ЛАЙМ, "свет": стиль.СВЕТЛЫЙ}
    return "".join(f'<div style="{МОНО} font-size: 32px; line-height: 1.5; color: {цвета[ц]}; white-space: pre;">{т}</div>'
                   for ц, т in строки)


def кадр(к: dict, н: int, всего: int) -> tuple[str, str]:
    п = ТЬМА if к.get("тёмный") else СВЕТ
    счёт = f"{н:02d} / {всего:02d}"
    вид = к["вид"]
    if вид == "код":
        тело = (метка(п, к["метка"]) + заголовок(п, к["заголовок"], 150) + абзац(п, к["подводка"], 360)
                + карта(п, 600, код(к["код"]), "40px 44px", тёмная=True, шаг=6)
                + f'<div style="position: absolute; left: 80px; top: 880px; width: 920px; {МОНО} font-size: 26px; line-height: 1.4; color: {п["второй"]};">{к["сноска"]}</div>')
    elif вид == "шаги":
        шаги = "".join(
            f'<div style="display: flex; gap: 26px; align-items: flex-start;">'
            f'<div style="width: 76px; height: 76px; border-radius: 38px; background: {п["акцент"]}; color: {стиль.ТЁМНЫЙ}; '
            f'{КРУП} font-size: 40px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{i}</div>'
            f'<div><div style="{ТЕКСТ} font-weight: 700; font-size: 46px; color: {п["текст"]};">{ш[0]}</div>'
            f'<div style="{ТЕКСТ} font-size: 38px; line-height: 1.3; color: {п["второй"]}; margin-top: 8px;">{ш[1]}</div></div></div>'
            for i, ш in enumerate(к["шаги"], 1))
        тело = метка(п, к["метка"]) + заголовок(п, к["заголовок"], 150) + карта(п, 400, шаги, "52px 48px")
    elif вид == "глава":
        имя, хвост = к["файл"].split(".")
        тело = (метка(п, к["метка"])
                + f'<div style="position: absolute; left: 76px; top: 130px; {КРУП} font-size: 150px; line-height: 1; color: {п["текст"]};">'
                  f'{имя}<span style="color: {п["акцент"]};">.{хвост}</span></div>'
                + абзац(п, к["подводка"], 310, 44, жирный=True)
                + карта(п, 480, пункты(п, к["пункты"]), "52px 48px"))
    elif вид == "сетка":
        плитки = "".join(
            f'<div style="height: 150px; border-radius: 22px; background: {п["карта"]}; border: 2px solid {п["рамка"]}; '
            f'display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px;">'
            f'<img src="{з}.svg" style="height: 50px; filter: {п["значок"]};">'
            f'<div style="{ТЕКСТ} font-size: 24px; color: {п["второй"]};">{и}</div></div>'
            for з, и in к["площадки"])
        тело = (метка(п, к["метка"]) + заголовок(п, к["заголовок"], 150) + абзац(п, к["подводка"], 360, 34)
                + f'<div style="position: absolute; left: 80px; top: 560px; width: 920px; display: grid; '
                  f'grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px;">{плитки}</div>'
                + f'<div style="position: absolute; left: 80px; top: 1080px; {МОНО} font-size: 24px; color: {п["второй"]};">{к["сноска"]}</div>')
    else:
        raise SystemExit(f"неизвестный вид кадра: {вид}")
    return тело + низ(п, счёт), п["фон"]


def обложка_сцена(о: dict) -> tuple[str, str]:
    п = ТЬМА
    return (метка(п, о["метка"], 90) + заголовок(п, о["строки"], 150, 118)
            + f'<img src="kot-noutbuk.webp" style="position: absolute; left: 190px; top: 470px; height: 700px;">'
            + низ(п)), п["фон"]


def обложка_число(о: dict) -> tuple[str, str]:
    п = ТЬМА
    return (f'<div style="position: absolute; left: 60px; top: 40px; {КРУП} font-size: 440px; line-height: 1; color: {п["акцент"]};">{о["число"]}</div>'
            + заголовок(п, о["строки"], 520, 96)
            + абзац(п, о["под"], 780, 42)
            + f'<div style="position: absolute; left: 80px; top: 900px; padding: 16px 26px; border-radius: 16px; border: 2px solid {п["рамка"]}; '
              f'{МОНО} font-size: 30px; color: {п["второй"]};">{о["плашка"]}</div>'
            + низ(п)), п["фон"]


def обложка_сетка(о: dict, площадки: list) -> tuple[str, str]:
    п = СВЕТ
    плитки = "".join(
        f'<div style="height: 118px; border-radius: 20px; background: #FFFFFF; border: 2px solid {п["рамка"]}; box-shadow: {п["тень"]}; '
        f'display: flex; align-items: center; justify-content: center;"><img src="{з}.svg" style="height: 48px;"></div>'
        for з, _ in площадки)
    ролик = (f'<div style="position: absolute; left: 80px; top: 560px; width: 300px; height: 390px; border-radius: 28px; '
             f'background: {стиль.ТЁМНЫЙ}; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px;">'
             f'<div style="width: 0; height: 0; border-top: 48px solid transparent; border-bottom: 48px solid transparent; '
             f'border-left: 80px solid {стиль.ЛАЙМ}; margin-left: 18px;"></div>'
             f'<div style="{МОНО} font-size: 28px; color: {стиль.СВЕТЛЫЙ};">ролик.mp4</div></div>')
    стрелка = (f'<div style="position: absolute; left: 400px; top: 700px; {КРУП} font-size: 90px; line-height: 1; '
               f'color: {п["акцент"]};">→</div>')
    сетка = (f'<div style="position: absolute; left: 510px; top: 560px; width: 490px; display: grid; '
             f'grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px;">{плитки}</div>')
    return (заголовок(п, о["строки"], 120, 124) + абзац(п, о["под"], 400, 44) + ролик + стрелка + сетка + низ(п)), п["фон"]


def финал(ф: dict) -> tuple[str, str]:
    п = СВЕТ
    return (заголовок(п, ф["строки"], 120, 96) + абзац(п, ф["подводка"], 350, 42)
            + f'<div style="position: absolute; left: 80px; top: 620px; width: 560px; box-sizing: border-box; padding: 34px 38px; '
              f'border-radius: 28px; background: {стиль.ТЁМНЫЙ}; {ТЕКСТ} font-weight: 700; font-size: 38px; line-height: 1.3; '
              f'color: {стиль.ЛАЙМ};">{ф["плашка"]}</div>'
            + f'<img src="kot-ukazyvaet.webp" style="position: absolute; right: 30px; top: 520px; height: 600px;">'
            + низ(п)), п["фон"]


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    врем = корень / "_файлы"
    площадки = next(к["площадки"] for к in пост["кадры"] if к["вид"] == "сетка")
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот("noutbuk", врем), дх.кот("ukazyvaet", врем)]
    файлы += [ТУТ / "значки" / f"{з}.svg" for з, _ in площадки]
    всего = len(пост["кадры"]) + 2
    обложки = {"сцена": lambda: обложка_сцена(пост["обложка_сцена"]),
               "число": lambda: обложка_число(пост["обложка_число"]),
               "сетка": lambda: обложка_сетка(пост["обложка_сетка"], площадки)}
    порядок = [пост.get("главная", "сцена")] + [и for и in обложки if и != пост.get("главная", "сцена")]
    тело, фон = обложки[порядок[0]]()
    доски = [("Main.dc.html", f"01 · Обложка · {порядок[0]}", дх.доска("Обложка", тело, фон, CSS))]
    for н, к in enumerate(пост["кадры"], 2):
        тело, фон = кадр(к, н, всего)
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['метка'][:24]}", дх.доска(к["метка"], тело, фон, CSS)))
    тело, фон = финал(пост["финал"])
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", дх.доска("Финал", тело, фон, CSS)))
    for н, и in enumerate(порядок[1:], 2):
        тело, фон = обложки[и]()
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", дх.доска(f"Обложка {н}", тело, фон, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=6)
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
