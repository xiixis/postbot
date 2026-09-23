# -*- coding: utf-8 -*-
"""Подборка сайтов, вид «пункты»: python холст.py посты/<пост>.json

Вариация от @vnuk_m (23.09.2026, `референс-vnuk/`, `ВАРИАЦИИ.md`): у каждого пункта номер
и имя, строка «что это», настоящий снимок сервиса, плашка «можно» с тремя пунктами и строка
«кому». Кадры пунктов чередуют тёмный и светлый грунт — у автора все тёмные, и в сетке
профиля они сливаются. Контраст держим от 8:1 (у автора 3,5:1).

Собирает правимый холст `холсты/<пост>/project/` (`../дизайн_холст.py`); выкладка — одним
вызовом Artifact, после «готово» — `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

СВЕТ = {"фон": стиль.КРЕМ, "текст": "#12130E", "второй": "#34372C", "акцент": "#3F4D08",  # олива темнее: #56690C по крему 5,4:1
        "плашка": "#FFFFFF", "рамка": "rgba(18,19,14,.10)", "лого": "filter: brightness(.45) saturate(1.4);"}
ТЬМА = {"фон": стиль.ТЁМНЫЙ, "текст": стиль.СВЕТЛЫЙ, "второй": "#C9CCBF", "акцент": стиль.ЛАЙМ,
        "плашка": "#1E2019", "рамка": "rgba(241,243,234,.10)", "лого": ""}
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.02em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))


def низ(п: dict, справа: str = "") -> str:
    """Логотип слева внизу (на каждом кадре) и подпись справа — адрес сайта или счёт."""
    с = (f'<div style="position: absolute; right: 80px; top: 1196px; {ТЕКСТ} font-size: 28px; '
         f'color: {п["второй"]};">{справа}</div>') if справа else ""
    return (f'<img src="logo.png" style="position: absolute; left: 80px; top: 1191px; height: 44px; {п["лого"]}">'
            + с)


def пункт(н: int, всего: int, с: dict) -> str:
    п = ТЬМА if н % 2 else СВЕТ
    пункты = "".join(
        f'<div style="display: flex; gap: 22px; align-items: baseline;">'
        f'<div style="width: 14px; height: 14px; border-radius: 7px; background: {п["акцент"]}; flex-shrink: 0; '
        f'transform: translateY(-6px);"></div><div>{т}</div></div>' for т in с["можно"])
    пометка = (f'<div style="{ТЕКСТ} font-size: 26px; color: {п["второй"]};">{с["пометка"]}</div>'
               if с.get("пометка") else "")
    return f"""<div style="position: absolute; left: 80px; top: 70px; width: 920px; {КРУП} font-size: 72px; line-height: 1.05; color: {п["текст"]};"><span style="color: {п["акцент"]};">{н}.</span> {с["имя"]}</div>
<div style="position: absolute; left: 80px; top: 166px; width: 920px; {ТЕКСТ} font-weight: 700; font-size: 40px; line-height: 1.2; color: {п["текст"]};">{с["что"]}</div>
<img src="{с["снимок"]}" style="position: absolute; left: 80px; top: 246px; width: 920px; height: 380px; object-fit: cover; object-position: top; border-radius: 28px; border: 2px solid {п["рамка"]}; box-shadow: 0 18px 50px rgba(0,0,0,.18);">
<div style="position: absolute; left: 80px; top: 664px; width: 920px; box-sizing: border-box; padding: 32px 40px; border-radius: 28px; background: {п["плашка"]}; border: 2px solid {п["рамка"]}; display: flex; flex-direction: column; gap: 12px; {ТЕКСТ} font-size: 32px; line-height: 1.2; color: {п["текст"]};">
<div style="font-weight: 700; color: {п["акцент"]};">Можно:</div>
{пункты}
<div style="font-weight: 700; margin-top: 6px;">{с["кому"]}</div>
{пометка}
</div>
{низ(п, с["адрес"])}"""


def обложка_число(о: dict) -> str:
    п = СВЕТ
    return f"""<div style="position: absolute; left: 0; top: 20px; width: 1080px; text-align: center; {КРУП} font-size: 520px; line-height: 1; color: {п["акцент"]};">{о["число"]}</div>
<div style="position: absolute; left: 80px; top: 520px; width: 920px; text-align: center; {КРУП} font-size: 92px; line-height: 1.02; color: {п["текст"]};">{о["строки"][0]}<br><span style="color: {п["акцент"]};">{о["строки"][1]}</span></div>
<div style="position: absolute; left: 80px; top: 840px; width: 920px; text-align: center; {ТЕКСТ} font-size: 44px; line-height: 1.3; color: {п["второй"]};">{о["под"]}</div>
{низ(п)}"""


def обложка_коллаж(о: dict, снимки: list[str]) -> str:
    п = ТЬМА
    плитки = "".join(f'<img src="{с}" style="width: 100%; height: 170px; object-fit: cover; object-position: top; '
                     f'border-radius: 18px; border: 2px solid {п["рамка"]};">' for с in снимки[:9])
    return f"""<div style="position: absolute; left: 60px; top: 60px; width: 960px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px;">{плитки}</div>
<div style="position: absolute; left: 80px; top: 660px; width: 920px; {КРУП} font-size: 96px; line-height: 1.02; color: {п["текст"]};">{о["строки"][0]}<br><span style="color: {п["акцент"]};">{о["строки"][1]}</span></div>
<div style="position: absolute; left: 80px; top: 900px; padding: 20px 34px; border-radius: 20px; background: {п["акцент"]}; {КРУП} font-size: 56px; color: #12130E;">{о["плашка"]}</div>
{низ(п)}"""


def обложка_кот(о: dict) -> str:
    п = СВЕТ
    return f"""<div style="position: absolute; left: 80px; top: 100px; width: 920px; {КРУП} font-size: 104px; line-height: 1.0; color: {п["текст"]};">{о["строки"][0]}<br><span style="color: {п["акцент"]};">{о["строки"][1]}</span></div>
<div style="position: absolute; left: 80px; top: 380px; {КРУП} font-size: 280px; line-height: 1; color: #12130E; background: {стиль.ЛАЙМ}; padding: 10px 44px 24px; border-radius: 40px;">{о["плашка"]}</div>
<div style="position: absolute; left: 80px; top: 760px; width: 440px; {ТЕКСТ} font-size: 42px; line-height: 1.3; color: {п["второй"]};">{о["под"]}</div>
<img src="kot-moneta.webp" style="position: absolute; right: 40px; top: 470px; height: 640px;">
{низ(п)}"""


def финал(ф: dict, имена: list[str]) -> str:
    п = СВЕТ
    чипы = "".join(f'<div style="padding: 14px 24px; border-radius: 999px; background: #FFFFFF; border: 2px solid {п["рамка"]}; '
                   f'{ТЕКСТ} font-weight: 700; font-size: 30px; color: {п["текст"]};"><span style="color: {п["акцент"]};">{i}</span> {и}</div>'
                   for i, и in enumerate(имена, 1))
    return f"""<div style="position: absolute; left: 80px; top: 110px; width: 920px; {КРУП} font-size: 88px; line-height: 1.04; color: {п["текст"]};">{ф["строки"][0]}<br><span style="color: {п["акцент"]};">{ф["строки"][1]}</span></div>
<div style="position: absolute; left: 80px; top: 330px; width: 920px; display: flex; flex-wrap: wrap; gap: 16px;">{чипы}</div>
<div style="position: absolute; left: 80px; top: 610px; width: 540px; {ТЕКСТ} font-weight: 700; font-size: 42px; line-height: 1.25; color: {п["текст"]};">{ф["вопрос"]}</div>
<div style="position: absolute; left: 80px; top: 840px; width: 540px; box-sizing: border-box; padding: 34px 38px; border-radius: 28px; background: {стиль.ТЁМНЫЙ}; {ТЕКСТ} font-weight: 700; font-size: 36px; line-height: 1.3; color: {стиль.ЛАЙМ};">{ф["плашка"]}</div>
<img src="kot-ukazyvaet.webp" style="position: absolute; right: 30px; top: 560px; height: 560px;">
{низ(п)}"""


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    врем = корень / "_файлы"
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот("moneta", врем), дх.кот("ukazyvaet", врем)]
    for с in пост["пункты"]:
        снимок = дх.снимок_сайта(ТУТ / с["снимок_файл"], врем)
        с["снимок"] = снимок.name
        файлы.append(снимок)
    всего = len(пост["пункты"]) + 2
    обложки = {"число": lambda: обложка_число(пост["обложка"]),
               "коллаж": lambda: обложка_коллаж(пост["обложка_коллаж"], [с["снимок"] for с in пост["пункты"]]),
               "кот": lambda: обложка_кот(пост["обложка_кот"])}
    фон = {"число": СВЕТ["фон"], "коллаж": ТЬМА["фон"], "кот": СВЕТ["фон"]}
    порядок = [пост.get("главная", "число")] + [и for и in обложки if и != пост.get("главная", "число")]
    доски = [("Main.dc.html", f"01 · Обложка · {порядок[0]}", дх.доска("Обложка", обложки[порядок[0]](), фон[порядок[0]], CSS))]
    for н, с in enumerate(пост["пункты"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {с['имя']}",
                      дх.доска(с["имя"], пункт(н, всего, с), (ТЬМА if н % 2 else СВЕТ)["фон"], CSS)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"], [с["имя"] for с in пост["пункты"]]), СВЕТ["фон"], CSS)))
    for н, и in enumerate(порядок[1:], 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", дх.доска(f"Обложка {н}", обложки[и](), фон[и], CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=6,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
