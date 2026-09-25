# -*- coding: utf-8 -*-
"""Вариация стиля «сервисы»: цепочка сервисов по шагам, один шаг на кадр.

    python3 шаги.py посты/<пост>.json [--без-снимка]

Снята с карусели TikTok @vidiq.tiktok «Learn YouTube Automation in 6 easy steps»
(references №19, 1,7 млн просмотров). Устройство автора: обложка — снимок статистики канала
с белой плашкой-заголовком; дальше по шагу на кадр на тёмно-синей сетке-чертеже: крупная серая
цифра слева, большой значок сервиса (иногда два внахлёст), жирное имя и одна-две строки.

Что перенесено: сетка-чертёж во весь кадр, цифра шага крупнее всего в кадре, значок-приложение
героем, два значка внахлёст там, где шаг делают два сервиса, имя под значком, короткая строка,
белая плашка на обложке.

Что наше:
* сетка графитовая с лаймовыми линиями вместо синей (фирменные цвета, слово владельца 25.09);
* строка пояснения светлее авторской: у автора 5,5:1, у нас от 8:1 — в ленте кадр втрое мельче;
* обложка — сцена Gemini с котом и графиком без сумм, а не снимок чужого дохода: наш «доход»
  на картинке был бы выдумкой;
* финал — вся цепочка значками по шагам и плашка-призыв, кот; логотип на каждом кадре.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402
import обложки  # noqa: E402

ГРУНТ = стиль.ТЁМНЫЙ                 # #12130F
БЕЛЫЙ, ВТОРОЙ = "#F4F5EE", "#DCDFD2"
ЦИФРА = "#8F9484"                    # серая, как у автора: крупно, но не спорит с именем
ТИХИЙ = "#A7AC9B"
ЛАЙМ = стиль.ЛАЙМ

КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ЦИФРЫ = "font-family: Rubik, 'Arial Rounded MT Bold', sans-serif; font-weight: 800;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Rubik", "rubik-800", 800),
                        ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))

КРАЙ = 70
СВЕЧЕНИЕ = ("radial-gradient(72% 48% at 50% 40%, rgba(84,102,14,.50) 0%, rgba(18,19,15,0) 70%), "
            "radial-gradient(60% 40% at 50% 110%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 70%)")
# Сетка-чертёж автора: крупная клетка 216 px и мелкая 54 px, к краям гаснет.
СЕТКА = ('<div style="position: absolute; inset: 0; background-image: '
         'linear-gradient(rgba(199,226,75,.16) 2px, transparent 2px), '
         'linear-gradient(90deg, rgba(199,226,75,.16) 2px, transparent 2px), '
         'linear-gradient(rgba(199,226,75,.07) 1px, transparent 1px), '
         'linear-gradient(90deg, rgba(199,226,75,.07) 1px, transparent 1px); '
         'background-size: 216px 216px, 216px 216px, 54px 54px, 54px 54px; '
         'background-position: 0 -26px, -54px 0, 0 -26px, -54px 0; '
         '-webkit-mask-image: radial-gradient(95% 78% at 50% 44%, #000 30%, rgba(0,0,0,.25) 100%); '
         'mask-image: radial-gradient(95% 78% at 50% 44%, #000 30%, rgba(0,0,0,.25) 100%);"></div>')
СТЕКЛО = "linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(10,11,9,.6) 100%)"
РАМКА = "rgba(242,244,234,.13)"

ТЕМА = обложки.Тема(грунт=f"{СВЕЧЕНИЕ}, {ГРУНТ}", тёмная=True, чернила=БЕЛЫЙ, второй=ВТОРОЙ, тихий=ТИХИЙ,
                    карточка=СТЕКЛО, карточка_тихая="rgba(255,255,255,.06)", рамка=РАМКА,
                    тень="0 18px 44px rgba(0,0,0,.4)", стрелка=ЛАЙМ, крупный=КРУП, текст=ТЕКСТ,
                    край=КРАЙ, сетка=СЕТКА)


def низ() -> str:
    return f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px;">'


def грунт() -> str:
    return f'<div style="position: absolute; inset: 0; background: {СВЕЧЕНИЕ}, {ГРУНТ};"></div>{СЕТКА}'


def плитка(с: dict, размер: int, скругление: float = .225) -> str:
    """Значок-приложение: картинка во весь квадрат с родным скруглением; логотип без своей
    подложки (`"плитка": "#FFFFFF"`) ложится на плитку этого цвета с полями."""
    р = round(размер * скругление)
    if с.get("плитка"):
        нутро = (f'<img src="{с["значок"]}" style="width: {с.get("размер", 64)}%; height: {с.get("размер", 64)}%; '
                 f'object-fit: contain;">')
        фон = f'background: {с["плитка"]}; display: flex; align-items: center; justify-content: center;'
    else:
        нутро = f'<img src="{с["значок"]}" style="width: 100%; height: 100%; object-fit: cover;">'
        фон = f'background: {ГРУНТ};'
    return (f'<div style="width: {размер}px; height: {размер}px; border-radius: {р}px; overflow: hidden; {фон} '
            f'box-shadow: 0 {размер // 10}px {размер // 5}px rgba(0,0,0,.55), 0 0 0 2px rgba(255,255,255,.10);">'
            f'{нутро}</div>')


def герой(н: int, ш: dict) -> str:
    """Цифра шага и значок одним блоком: они нарочно стоят вплотную, как у автора. Значок — по оси
    кадра, второй сервис — внахлёст справа снизу; свечение за ним — подложка (`pointer-events`)."""
    свет = (f'<div style="position: absolute; left: 246px; top: -30px; width: 420px; height: 420px; '
            f'border-radius: 50%; background: {ш.get("цвет", ЛАЙМ)}; opacity: .30; filter: blur(70px); '
            f'pointer-events: none;"></div>')
    цифра = (f'<div style="position: absolute; left: 0; top: 10px; width: 250px; text-align: right; {ЦИФРЫ} '
             f'font-size: 330px; line-height: 1; color: {ЦИФРА}; text-shadow: 0 10px 0 rgba(0,0,0,.35);">{н}</div>')
    if ш.get("второй"):
        значки = (f'<div style="position: absolute; left: 264px; top: -18px;">{плитка(ш["первый"], 290)}</div>'
                  f'<div style="position: absolute; left: 436px; top: 160px;">{плитка(ш["второй"], 230)}</div>')
    else:
        значки = f'<div style="position: absolute; left: 276px; top: 0;">{плитка(ш["первый"], 360)}</div>'
    return (f'<div style="position: absolute; left: 84px; top: 280px; width: 700px; height: 390px;">'
            f'{свет}{цифра}{значки}</div>')


def кадр(н: int, ш: dict) -> str:
    имя = ш["имя"]
    кегль = 96 if len(имя) <= 10 else 84
    return (грунт()
            + герой(н, ш)
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 718px; width: {1080 - 2 * КРАЙ}px; '
              f'text-align: center; {КРУП} font-size: {кегль}px; line-height: 1; color: {БЕЛЫЙ};">{имя}</div>'
            + f'<div style="position: absolute; left: 180px; top: 850px; width: 720px; text-align: center; {ТЕКСТ} '
              f'font-weight: 700; font-size: 42px; line-height: 1.28; color: {ВТОРОЙ};">{ш["текст"]}</div>'
            + низ())


def обложка(о: dict) -> str:
    """Главная как у автора: картинка во весь кадр и белая плашка крупным чёрным текстом."""
    строки = "<br>".join(о["строки"])
    return (f'<div style="position: absolute; inset: 0; background: {ГРУНТ};"></div>'
            + f'<img src="{Path(о["сцена"]).stem}.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; '
              f'height: 1440px; object-fit: cover;">'
            + обложки.кот_по_сцене(о["сцена"])
            + f'<div style="position: absolute; left: {КРАЙ}px; top: {о.get("top", 110)}px; width: {1080 - 2 * КРАЙ}px; '
              f'display: flex; flex-direction: column; align-items: center; gap: 26px;">'
              f'<div style="box-sizing: border-box; padding: 26px 44px 34px; border-radius: 34px; background: #FFFFFF; '
              f'box-shadow: 0 30px 70px rgba(0,0,0,.45); text-align: center; {КРУП} font-size: {о.get("кегль", 112)}px; '
              f'line-height: 1.02; color: #111210;">{строки}</div>'
              f'<div style="padding: 16px 30px 20px; border-radius: 22px; background: rgba(18,19,15,.86); '
              f'border: 2px solid {РАМКА}; {ТЕКСТ} font-weight: 700; font-size: 44px; color: {БЕЛЫЙ};">'
              f'{о["под"]}</div></div>'
            + низ())


def финал(ф: dict, шаги: list[dict]) -> str:
    """Вся цепочка одним взглядом: шесть значков по шагам со стрелками и плашка-призыв."""
    клетки = ""
    for н, ш in enumerate(шаги, 1):
        стрелка = "" if н % 3 == 0 else (
            f'<svg viewBox="0 0 24 24" fill="none" stroke="{ЛАЙМ}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round" style="position: absolute; right: -30px; top: 50px; width: 34px; height: 34px;">'
            f'<path d="M5 12h14M13 6l6 6-6 6"/></svg>')
        клетки += (f'<div style="position: relative; display: flex; flex-direction: column; align-items: center; gap: 14px;">'
                   f'<div style="position: relative;">{плитка(ш["первый"], 134)}'
                   f'<div style="position: absolute; left: -14px; top: -14px; width: 48px; height: 48px; border-radius: 50%; '
                   f'background: {ЛАЙМ}; border: 3px solid {ГРУНТ}; display: flex; align-items: center; justify-content: center; '
                   f'{ЦИФРЫ} font-size: 28px; color: #12130E;">{н}</div></div>'
                   f'<div style="{ТЕКСТ} font-weight: 700; font-size: 32px; line-height: 1.1; color: {БЕЛЫЙ}; '
                   f'text-align: center;">{ш["итог"]}</div>{стрелка}</div>')
    return (грунт()
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 96px; width: 700px; {КРУП} font-size: 96px; '
              f'line-height: 1.0; color: {БЕЛЫЙ};">{ф["строки"][0]}<br><span style="color: {ЛАЙМ};">{ф["строки"][1]}</span></div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" style="position: absolute; left: 800px; top: 70px; height: 250px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 390px; width: 830px; box-sizing: border-box; '
              f'padding: 48px 40px 44px; border-radius: 40px; background: {СТЕКЛО}; border: 2px solid {РАМКА}; '
              f'box-shadow: 0 30px 70px rgba(0,0,0,.4); display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); '
              f'row-gap: 40px; column-gap: 40px;">{клетки}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 930px; width: 830px; box-sizing: border-box; '
              f'padding: 28px 36px 32px; border-radius: 32px; background: {ЛАЙМ};">'
              f'<div style="{КРУП} font-size: 52px; line-height: 1.04; color: #12130E;">{ф["призыв"]}</div>'
              f'<div style="margin-top: 10px; {ТЕКСТ} font-weight: 700; font-size: 32px; color: #2A3106;">{ф["ссылка"]}</div></div>'
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
    сцена = обложки.СЦЕНЫ / f'{Path(пост["обложка"]["сцена"]).stem}.jpg'
    файлы.append(дх.снимок_сайта(сцена, врем, 1080))
    значки = {}
    for ш in пост["шаги"]:
        for ключ in ("первый", "второй"):
            с = ш.get(ключ)
            if с:
                путь = ТУТ / "значки" / с["файл"]
                значки[путь.name] = путь
                с["значок"] = путь.name
    файлы += list(значки.values())
    # Запасные обложки каталога ждут ряд значков: по одному на шаг, как в цепочке.
    ряд = [dict(ш["первый"], имя=ш["имя"], во_весь=not ш["первый"].get("плитка"), цвет=ш.get("цвет"))
           for ш in пост["шаги"]]
    своя = ("пост-плашка", ГРУНТ, обложка(пост["обложка"]))
    обл = обложки.доски_обложек(пост, своя, ТЕМА, {"значки": ряд}, CSS)
    доски = обл[:1]
    for н, ш in enumerate(пост["шаги"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · шаг {н} · {ш['имя']}",
                      дх.доска(ш["имя"], кадр(н, ш), ГРУНТ, CSS)))
    всего = len(пост["шаги"]) + 2
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"], пост["шаги"]), ГРУНТ, CSS)))
    доски += обл[1:]
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")
    import приёмка_досок
    приёмка_досок.доложить(проект, снимки="--без-снимка" not in sys.argv[2:])


if __name__ == "__main__":
    main()
