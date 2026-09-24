# -*- coding: utf-8 -*-
"""Вариация стиля «пары»: светлый кадр, категория и две карточки «платно | бесплатно».

    python3 категории.py посты/<пост>.json

Снята с карусели TikTok @dunai.dev (106 тыс. показов, 6 547 сохранений, кадры — `референс-dunai/`).
Устройство автора: светлый холодный грунт, счётчик `01/07` слева вверху, заголовок категории
сверху, под ним две белые карточки рядом — чип «Платно» / «Бесплатно», имя, цена, логотип
сервиса в родных цветах. Финал — текстовый.

Что перенесено: светлая лента целиком, счётчик, заголовок категории, две карточки в ряд,
порядок внутри карточки (чип → имя → цена → значок), настоящие логотипы.

Что наше: фирменные крем/графит/лайм вместо синего, логотип канала на каждом кадре, кот на
обложке и финале, и один сквозной приём, которого у автора нет — **накопительный счёт
экономии** внизу каждого кадра ($20 → $50 → $79 → $89 → $109). Он держит дочитывание до
финала и даёт финалу расплату: у автора последний кадр — просто просьба подписаться.

Доски 1080×1440 (`../дизайн_холст.py`); дальше Artifact → «готово» → `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

# ── Палитра ──────────────────────────────────────────────────────────────────
# У автора холодный голубой градиент и синий текст. Берём его светлоту и воздух, но
# уводим в наш крем: синий у нас не фирменный, а лайм по синему не звучит.
БУМАГА = "linear-gradient(170deg, #FBFCF7 0%, #EDEFE4 58%, #E4E7D9 100%)"
ЧЕРНИЛА, ВТОРОЙ, ТИХИЙ = "#12130E", "#1E1F17", "#3A3E33"
БЕЛАЯ = "#FFFFFF"
РАМКА = "rgba(18,19,14,.09)"
ТЕНЬ = "0 18px 44px rgba(18,19,14,.10)"
СЕРЫЙ_ЧИП = "#E7E9DF"

КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                        ("Golos", "golos-700", 700))

# Сетка доски 1080×1440: край 80, всё важное выше 1105, знак в полосе 1191.
КРАЙ = 80
КАРТА_ВЕРХ, КАРТА_В = 240, 670          # карточки; низ на 910
ВЫВОД_ВЕРХ = 950                        # строка-вывод: запас 40 от карточек, низ ≈1091 (порог 1105)


def кегль(текст: str, большой: int, малый: int, предел: int) -> int:
    """Имя сервиса длиннее предела набирается мельче: на доске нет автоужатия рисовальщика."""
    return большой if len(текст) <= предел else малый


def низ(справа: str = "") -> str:
    """Логотип канала слева (на каждом кадре) и мелкая подпись справа."""
    с = (f'<div style="position: absolute; right: {КРАЙ}px; top: 1198px; {ТЕКСТ} font-weight: 700; '
         f'font-size: 26px; color: {ТИХИЙ};">{справа}</div>') if справа else ""
    return (f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px; '
            f'filter: brightness(.45) saturate(1.4);">' + с)


def значок(с: dict) -> str:
    """Круглый значок сервиса в родных цветах: белый диск, глиф внутри."""
    масштаб = с.get("размер", 58)
    фон = с.get("фон", БЕЛАЯ)
    рамка = "rgba(18,19,14,.08)" if фон == БЕЛАЯ else "rgba(18,19,14,.14)"
    инверсия = "filter: invert(1);" if с.get("инверсия") else ""
    if с.get("во_весь"):
        нутро = (f'<img src="{с["значок"]}" style="width: 100%; height: 100%; object-fit: cover; '
                 f'border-radius: 50%;">')
    else:
        нутро = (f'<img src="{с["значок"]}" style="width: {масштаб}%; height: {масштаб}%; '
                 f'object-fit: contain; {инверсия}">')
    return (f'<div style="width: 156px; height: 156px; border-radius: 50%; background: {фон}; '
            f'border: 2px solid {рамка}; box-shadow: inset 0 2px 0 rgba(255,255,255,.7), '
            f'0 10px 24px rgba(18,19,14,.10); display: flex; align-items: center; '
            f'justify-content: center; overflow: hidden; flex-shrink: 0;">{нутро}</div>')


def карточка(с: dict, бесплатно: bool, left: int) -> str:
    """Карточка стороны: чип → значок → имя → цена → строка «чем берёт»."""
    # Бесплатная сторона выделена лаймом трижды: чип, рамка карточки и её отсвет. Так «кто
    # выиграл» видно за полсекунды, и доля акцента дотягивает до нормы 4–6% (замер 24.09).
    чип = (f'<div style="padding: 12px 36px 16px; border-radius: 999px; background: {стиль.ЛАЙМ}; '
           f'{ТЕКСТ} font-weight: 700; font-size: 30px; letter-spacing: .01em; color: {ЧЕРНИЛА};">Бесплатно</div>'
           if бесплатно else
           f'<div style="padding: 12px 36px 16px; border-radius: 999px; background: {СЕРЫЙ_ЧИП}; '
           f'{ТЕКСТ} font-weight: 700; font-size: 30px; letter-spacing: .01em; color: {ТИХИЙ};">Платно</div>')
    оправа = (f'border: 4px solid {стиль.ЛАЙМ}; box-shadow: 0 18px 44px rgba(18,19,14,.10), '
              f'0 0 0 10px rgba(199,226,75,.18)' if бесплатно else f'border: 2px solid {РАМКА}; box-shadow: {ТЕНЬ}')
    цена_цвет = ЧЕРНИЛА if бесплатно else ТИХИЙ
    хвост = (f'<span style="{ТЕКСТ} font-weight: 700; font-size: 30px; color: {ТИХИЙ}; '
             f'letter-spacing: 0;">/мес</span>')
    имя_кегль = кегль(с["имя"], 52, 40, 11)
    # Слово «Claude» всегда фирменным цветом Claude (правило владельца, `дизайн_холст.CLAUDE`).
    имя_цвет = дх.CLAUDE if с["имя"].lower().startswith("claude") else ЧЕРНИЛА
    return f"""<div style="position: absolute; left: {left}px; top: {КАРТА_ВЕРХ}px; width: 440px; height: {КАРТА_В}px; box-sizing: border-box; padding: 30px 28px 34px; border-radius: 44px; background: {БЕЛАЯ}; {оправа}; display: flex; flex-direction: column; align-items: center; justify-content: space-between; gap: 18px;">
{чип}
{значок(с)}
<div style="{КРУП} font-size: {имя_кегль}px; line-height: 1.05; color: {имя_цвет}; text-align: center;">{с["имя"]}</div>
<div style="{КРУП} font-size: 76px; line-height: 1; color: {цена_цвет};">{с["цена"]}{хвост}</div>
<div style="{ТЕКСТ} font-size: 28px; line-height: 1.25; color: {ТИХИЙ}; text-align: center;">{с["чем"]}</div>
</div>"""


def кадр(н: int, всего: int, к: dict) -> str:
    """Категория, две карточки и накопительный счёт экономии."""
    счёт = (f'<div style="position: absolute; right: {КРАЙ}px; top: 70px; {ТЕКСТ} font-weight: 700; '
            f'font-size: 30px; color: {ТИХИЙ};">{н:02d}<span style="color: #9AA08F;">/{всего:02d}</span></div>')
    стрелка = ('<svg viewBox="0 0 80 24" fill="none" stroke="#12130E" stroke-width="3.4" '
               'stroke-linecap="round" stroke-linejoin="round" style="width: 72px; height: 22px;">'
               '<path d="M4 12h68M60 4l12 8-12 8"/></svg>')
    return f"""<div style="position: absolute; left: {КРАЙ}px; top: 60px; {ТЕКСТ} font-weight: 700; font-size: 30px; letter-spacing: .02em; color: {стиль.ОЛИВА};">{к["рубрика"]}</div>
{счёт}
<div style="position: absolute; left: {КРАЙ}px; top: 112px; width: 920px; {КРУП} font-size: {кегль(к["категория"], 88, 72, 18)}px; line-height: 1.02; color: {ЧЕРНИЛА};">{к["категория"]}</div>
<div style="position: absolute; left: 506px; top: {КАРТА_ВЕРХ + КАРТА_В // 2 - 34}px; width: 68px; height: 68px; border-radius: 50%; background: {БЕЛАЯ}; border: 2px solid {РАМКА}; box-shadow: {ТЕНЬ}; display: flex; align-items: center; justify-content: center; z-index: 2;">{стрелка}</div>
{карточка(к["платно"], False, КРАЙ)}
{карточка(к["бесплатно"], True, 560)}
<div style="position: absolute; left: {КРАЙ}px; top: {ВЫВОД_ВЕРХ}px; width: 600px; {ТЕКСТ} font-weight: 700; font-size: 38px; line-height: 1.24; color: {ВТОРОЙ};">{к["вывод"]}</div>
<div style="position: absolute; right: {КРАЙ}px; top: {ВЫВОД_ВЕРХ - 4}px; width: 330px; box-sizing: border-box; padding: 22px 26px 26px; border-radius: 28px; background: {стиль.ЛАЙМ}; text-align: center;">
<div style="{ТЕКСТ} font-weight: 700; font-size: 24px; letter-spacing: .02em; color: {ЧЕРНИЛА}; opacity: .72;">не платим уже</div>
<div style="{КРУП} font-size: 62px; line-height: 1.05; color: {ЧЕРНИЛА}; margin-top: 4px;">{к["экономия"]}<span style="{ТЕКСТ} font-weight: 700; font-size: 26px;">/мес</span></div>
</div>
{низ(к.get("сноска", ""))}"""


def сцена(файл: str, сдвиг: int = 0) -> str:
    return (f'<img src="{файл}" style="position: absolute; left: 0; top: {сдвиг}px; width: 1080px; '
            f'height: 1440px; object-fit: cover;">')


def обложка_чек(о: dict) -> str:
    """Главная: кот с длинным чеком, заголовок и подпись в пустом левом верхнем углу.

    Заголовок крупный (правило владельца 23.09.2026: обложка должна остановить ленту),
    слово-акцент — в лаймовой капсуле.
    """
    строки = о["строки"]
    заголовок = f'{строки[0]}<br>{строки[1]} {дх.маркер(строки[2])}'
    return (f'<div style="position: absolute; inset: 0; background: {БУМАГА};"></div>'
            + сцена("kot-chek.jpg", о.get("сдвиг", 0))
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 76px; width: 900px; {КРУП} '
              f'font-size: 116px; line-height: 1.0; color: {ЧЕРНИЛА};">{заголовок}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 470px; width: 560px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 46px; line-height: 1.22; color: {ВТОРОЙ};">{о["под"]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 660px; display: inline-flex; '
              f'align-items: center; gap: 18px; padding: 16px 30px 20px; border-radius: 26px; '
              f'background: {ЧЕРНИЛА}; {КРУП} font-size: 52px; color: {стиль.ЛАЙМ};">{о["плашка"]}</div>'
            + низ())


def обложка_ценники(о: dict, значки: list[dict]) -> str:
    """Запасная 1: два ряда ценников — слева с суммами, справа с нулями, кот выбирает правый."""
    ряд = ""
    for i, с in enumerate(значки[:5]):
        ряд += (f'<div style="display: flex; align-items: center; gap: 16px; padding: 12px 22px; '
                f'border-radius: 999px; background: {БЕЛАЯ}; border: 2px solid {РАМКА}; '
                f'box-shadow: {ТЕНЬ};">'
                f'<img src="{с["значок"]}" style="width: 44px; height: 44px; object-fit: contain; '
                f'{"filter: invert(1);" if с.get("инверсия") else ""}">'
                f'<div style="{КРУП} font-size: 34px; color: {ЧЕРНИЛА};">{с["цена"]}</div></div>')
    return (f'<div style="position: absolute; inset: 0; background: {БУМАГА};"></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 96px; width: 920px; {КРУП} '
              f'font-size: 104px; line-height: 1.0; color: {ЧЕРНИЛА};">{о["строки"][0]}<br>'
              f'{дх.маркер(о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 390px; width: 800px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 44px; line-height: 1.2; color: {ВТОРОЙ};">{о["под"]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 556px; width: 620px; display: flex; '
              f'flex-wrap: wrap; gap: 16px;">{ряд}</div>'
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; right: 24px; '
              f'top: 700px; height: 400px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 900px; width: 600px; box-sizing: border-box; '
              f'padding: 26px 32px 30px; border-radius: 30px; background: {ЧЕРНИЛА}; {КРУП} font-size: 54px; '
              f'line-height: 1.1; color: {стиль.ЛАЙМ};">{о["плашка"]}</div>'
            + низ())


def обложка_ноль(о: dict) -> str:
    """Запасная 2: тёмный кадр, гигантский ноль и кот рядом — другой макет и другая светлота."""
    return (f'<div style="position: absolute; inset: 0; background: radial-gradient(120% 90% at 78% 26%, '
            f'rgba(199,226,75,.20) 0%, rgba(18,19,15,0) 62%), {стиль.ТЁМНЫЙ};"></div>'
            + f'<div style="position: absolute; right: -40px; top: 60px; {КРУП} font-size: 720px; '
              f'line-height: .8; color: {стиль.ЛАЙМ}; opacity: .92;">0</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 112px; width: 780px; {КРУП} '
              f'font-size: 96px; line-height: 1.0; color: {стиль.СВЕТЛЫЙ};">{о["строки"][0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{о["строки"][1]}</span></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 420px; width: 600px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 44px; line-height: 1.24; color: #C9CCBF;">{о["под"]}</div>'
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; left: 60px; '
              f'top: 660px; height: 470px;">'
            + f'<div style="position: absolute; right: {КРАЙ}px; top: 900px; width: 430px; box-sizing: border-box; '
              f'padding: 26px 30px 30px; border-radius: 30px; background: {стиль.ЛАЙМ}; {КРУП} font-size: 48px; '
              f'line-height: 1.08; color: {ЧЕРНИЛА};">{о["плашка"]}</div>'
            + f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px;">')


def финал(ф: dict) -> str:
    """Итог: сумма расплаты, три пункта «что сохраняешь», тёмная плашка-призыв и кот."""
    # Метка пункта — лаймовый кружок в тёмной обводке: на светлом лайм читается только так,
    # и он же добирает долю акцента до нормы (замер 24.09.2026 давал 3,9% при оливковых галочках).
    пункты = ""
    for т in ф["пункты"]:
        пункты += (f'<div style="display: flex; gap: 22px; align-items: flex-start;">'
                   f'<div style="width: 26px; height: 26px; border-radius: 50%; background: {стиль.ЛАЙМ}; '
                   f'border: 4px solid {ЧЕРНИЛА}; box-sizing: border-box; flex-shrink: 0; margin-top: 8px;"></div>'
                   f'<div>{т}</div></div>')
    return (f'<div style="position: absolute; inset: 0; background: {БУМАГА};"></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 96px; width: 920px; {КРУП} '
              f'font-size: 96px; line-height: 1.0; color: {ЧЕРНИЛА};">{ф["строки"][0]}<br>'
              f'{дх.маркер(ф["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 390px; width: 620px; box-sizing: border-box; '
              f'padding: 34px 38px 38px; border-radius: 36px; background: {БЕЛАЯ}; border: 2px solid {РАМКА}; '
              f'box-shadow: {ТЕНЬ}; display: flex; flex-direction: column; gap: 22px; {ТЕКСТ} font-weight: 700; '
              f'font-size: 34px; line-height: 1.22; color: {ВТОРОЙ};">{пункты}</div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" style="position: absolute; right: 20px; '
              f'top: 380px; height: 400px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 820px; width: 920px; box-sizing: border-box; '
              f'padding: 32px 40px 36px; border-radius: 34px; background: {ЧЕРНИЛА}; {КРУП} font-size: 54px; '
              f'line-height: 1.1; color: {стиль.ЛАЙМ};">{ф["призыв"]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 1010px; {ТЕКСТ} font-weight: 700; '
              f'font-size: 42px; color: {ВТОРОЙ};">{ф["ссылка"]}</div>'
            + низ())


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    CSS = дх.шрифты_холста(CSS, корень)
    врем = корень / "_файлы"
    позы = {пост["обложка_ценники"]["поза"], пост["обложка_ноль"]["поза"], пост["финал"]["поза"]}
    файлы = list(ШРИФТЫ) + [дх.логотип(врем)] + [дх.кот(п, врем) for п in позы]
    файлы.append(дх.снимок_сайта(ТУТ / пост["обложка"]["сцена"], врем, 1080))
    for к in пост["кадры"]:
        for сторона in ("платно", "бесплатно"):
            с = к[сторона]
            путь = ТУТ / "значки" / с["файл"]
            файлы.append(путь)
            с["значок"] = путь.name
    всего = len(пост["кадры"]) + 2
    значки = [к["платно"] for к in пост["кадры"]]
    доски = [("Main.dc.html", "01 · Обложка · чек",
              дх.доска("Обложка", обложка_чек(пост["обложка"]), "#EDEFE4", CSS))]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['категория_кратко']}",
                      дх.доска(к["категория_кратко"], кадр(н, всего, к), "#EDEFE4", CSS)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"]), "#EDEFE4", CSS)))
    доски.append(("Oblozhka2.dc.html", "Обложка 2 · ценники",
                  дх.доска("Обложка 2", обложка_ценники(пост["обложка_ценники"], значки), "#EDEFE4", CSS)))
    доски.append(("Oblozhka3.dc.html", "Обложка 3 · ноль",
                  дх.доска("Обложка 3", обложка_ноль(пост["обложка_ноль"]), стиль.ТЁМНЫЙ, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
