# -*- coding: utf-8 -*-
"""Вариация «сервисов»: один сервис на кадр (пост с `"вид": "один"`).

Рерайт @nik_kukuytsev «Бесплатные нейросети для создания контента», 17.09.2026. Устройство
кадра то же, что у «сервисов» — сверху имя, в середине значок, снизу строка, — но:
вместо ряда плоских кружков один крупный пушистый 3D-значок (`значки/3d/`, рисует
`значки-3d.sh`), имя сервиса огромным узким шрифтом синим, вместо карточки одна строка,
номера-пилюли нет. Цвета автора (слово владельца: «как в референсе»); логотип канала на каждом кадре, полосы нет.

Доски холста 1080×1440; зовётся из `холст.py`.
"""
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

ТУТ = Path(__file__).parent
ФОН, СИНИЙ, ЧЕРНИЛА, НОЧЬ = "#ECEFF6", "#0169FB", "#0E0F12", "#0B1020"
ФОН_RGB = (236, 239, 246)
УЗКИЙ = "font-family: Oswald, 'Arial Narrow', sans-serif; font-weight: 600; text-transform: uppercase"
ГРОТЕСК = "font-family: Inter, 'Helvetica Neue', Arial, sans-serif"
ШИРИНА = 920                       # поле под имя: 1080 без полей по 80


def фейсы(стиль) -> str:
    return стиль.фейсы(("Oswald", "oswald-600", 600), ("Inter", "inter-400", 400), ("Inter", "inter-800", 800))


def узко(текст: str, кегль: int) -> str:
    """Узкое имя в поле 920: Oswald сжат по ширине, длинное имя сжимается сильнее.

    У автора сверхузкая гарнитура; Oswald шире, поэтому сжатие от 0,8 до 0,5 по длине.
    Ширина знака Oswald 600 в верхнем регистре ≈0,52 кегля у латиницы и ≈0,62 у кириллицы
    (Ы, Ж, Щ широкие) — замерено снимком: с общим 0,52 «5 БЕСПЛАТНЫХ» упиралось в края.
    """
    ширина_знака = 0.62 if any("а" <= б.lower() <= "я" or б in "ёЁ" for б in текст) else 0.52
    сжатие = max(0.5, min(0.8, ШИРИНА / (len(текст) * ширина_знака * кегль)))
    return (f'<div style="{УЗКИЙ}; font-size: {кегль}px; line-height: 0.95; color: {СИНИЙ}; white-space: nowrap; '
            f'transform: scaleX({сжатие:.2f}); letter-spacing: -0.01em;">{текст}</div>')


def выделение(текст: str, кегль: int) -> str:
    """Слово «выделено курсором», как у автора: голубая плашка и две каретки с точками."""
    каретка = (f'<span style="position: absolute; top: -4px; bottom: -4px; width: 3px; background: {СИНИЙ};'
               f' {{сторона}}: -3px;"><span style="position: absolute; left: -4px; {{точка}}: -10px; width: 11px;'
               f' height: 11px; border-radius: 50%; background: {СИНИЙ};"></span></span>')
    return (f'<span style="position: relative; display: inline-block; padding: 0 6px; background: rgba(1,105,251,0.16);'
            f' color: {СИНИЙ}; font-size: {кегль}px;">{текст}'
            + каретка.replace("{сторона}", "left").replace("{точка}", "top")
            + каретка.replace("{сторона}", "right").replace("{точка}", "bottom") + "</span>")


def доска(тело: str, фон: str = ФОН, цвет: str = ЧЕРНИЛА) -> str:
    """Логотип канала на каждом кадре (слово владельца 17.09.2026: «верни наш логотип на каждый
    слайд»). Левый нижний угол, ниже любого текста: строка кадра кончается на y≈1210, а в
    привычном месте «сервисов» (bottom 205) логотип лёг бы на неё. На светлом грунте лайм
    не читается — приглушён тем же фильтром, что у «сервисов»; на тёмном остаётся родным."""
    приглушить = "" if фон == НОЧЬ else " filter: brightness(.45) saturate(1.4);"
    return (f'<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {фон};'
            f' color: {цвет};">\n{тело}\n  <img src="logo.png" style="position: absolute; left: 70px; bottom: 60px;'
            f' height: 72px; z-index: 5;{приглушить}">\n</div>')


def кадр(к: dict) -> str:
    return доска(f"""  <div style="position: absolute; left: 80px; right: 80px; top: 150px; display: flex; justify-content: center;">{узко(к['заголовок'], 240)}</div>
  <img src="{файл_значка(к['значок'])}" style="position: absolute; left: 260px; top: 440px; width: 560px; height: 560px; object-fit: contain;">
  <div style="position: absolute; left: 80px; right: 80px; top: 1150px; {ГРОТЕСК}; font-size: 48px; line-height: 1.2; letter-spacing: -0.03em; text-align: center; text-wrap: balance;">{к['текст']}</div>""")


def обложка(о: dict) -> str:
    """А — как у автора: огромное «бесплатные», под ним выделенное слово, значок «деньги под запретом»."""
    return доска(f"""  <div style="position: absolute; left: 80px; top: 170px; {ГРОТЕСК}; font-weight: 800; font-size: 170px; line-height: 0.9; letter-spacing: -0.065em;">{о['заголовок']}</div>
  <div style="position: absolute; left: 250px; top: 350px; {ГРОТЕСК}; font-size: 60px; letter-spacing: -0.03em; display: flex; gap: 70px; align-items: baseline;">{выделение(о['выделить'], 60)}<span>{о['под']}</span></div>
  <img src="{файл_значка(о['значок'])}" style="position: absolute; left: 150px; top: 560px; width: 700px; height: 700px; object-fit: contain;">""")


def обложка_сетка(о: dict, значки: list[str]) -> str:
    """Б — «сетка»: имя поста узким синим, веер пяти значков, кот с табличкой «$0»."""
    веер = "\n".join(
        f'  <img src="{файл_значка(з)}" style="position: absolute; left: {40 + i * 190}px; top: {570 + abs(i - 2) * 45}px;'
        f' width: 250px; height: 250px; object-fit: contain; transform: rotate({(i - 2) * 9}deg);">'
        for i, з in enumerate(значки))
    т = о["табличка"]
    return доска(f"""  <div style="position: absolute; left: 80px; right: 80px; top: 120px; display: flex; flex-direction: column; align-items: center; gap: 50px;">{узко(о['строки'][0], 190)}{узко(о['строки'][1], 190)}</div>
{веер}
  <img src="{файл_кота(о['кот']['поза'])}" style="position: absolute; left: {о['кот']['left']}px; top: {о['кот']['top']}px; height: {о['кот']['высота']}px;">
  <div style="position: absolute; left: {т['left']}px; top: {т['top']}px; width: {т['w']}px; height: {т['h']}px; display: flex; align-items: center; justify-content: center; {УЗКИЙ}; font-size: {т['кегль']}px; color: {СИНИЙ}; transform: rotate({т.get('поворот', 0)}deg);">$0</div>""")


def обложка_маркер(о: dict) -> str:
    """В — «маркер»: тёмный кадр, гигантская цифра, строка и маркер «без оплаты», кот с монетой."""
    return доска(f"""  <div style="position: absolute; left: 60px; top: 40px; {УЗКИЙ}; font-size: 900px; line-height: 1; color: {СИНИЙ};">{о['цифра']}</div>
  <div style="position: absolute; left: 540px; right: 70px; top: 250px; {ГРОТЕСК}; font-weight: 800; font-size: 82px; line-height: 1.0; letter-spacing: -0.05em; color: #FFFFFF; text-wrap: balance;">{о['строка']}</div>
  <div style="position: absolute; left: 540px; top: 560px; {ГРОТЕСК}; font-weight: 800; font-size: 80px; letter-spacing: -0.04em; color: #FFFFFF; background: {СИНИЙ}; padding: 6px 24px; border-radius: 14px; transform: rotate(-3deg);">{о['маркер']}</div>
  <img src="{файл_кота(о['кот']['поза'])}" style="position: absolute; left: {о['кот']['left']}px; top: {о['кот']['top']}px; height: {о['кот']['высота']}px;">""",
                 фон=НОЧЬ, цвет="#FFFFFF")


def финал(ф: dict) -> str:
    return доска(f"""  <div style="position: absolute; left: 80px; right: 80px; top: 150px; display: flex; justify-content: center;">{узко(ф['крупно'], 240)}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 400px; {ГРОТЕСК}; font-size: 52px; letter-spacing: -0.03em; text-align: center;">{ф['под_крупным']}</div>
  <img src="{файл_кота(ф['кот']['поза'])}" style="position: absolute; left: {ф['кот']['left']}px; top: {ф['кот']['top']}px; height: {ф['кот']['высота']}px;">
  <div style="position: absolute; left: 80px; right: 80px; top: 1130px; {ГРОТЕСК}; font-size: 50px; line-height: 1.35; letter-spacing: -0.03em; text-align: center;">{ф['текст']} {выделение(ф['выделить'], 50)}</div>""")


def лат(имя: str) -> str:
    """Помощник холста принимает имена картинок только латиницей."""
    from холст import латиницей
    return латиницей(имя)


def файл_значка(имя: str) -> str:
    return f"3d-{лат(имя)}.webp"


def файл_кота(поза: str) -> str:
    return f"kot-{лат(поза)}.webp"


def без_фона(исходник: Path, цель: Path, сторона: int = 420) -> None:
    """Значок из Gemini лежит на заливке #ECEFF6: заливку в прозрачность мягким порогом.

    Край меха полупрозрачный, поэтому порог плавный (6–28 по расстоянию до цвета фона), а не
    резкий: иначе вокруг шерсти остаётся ореол. Тень под значком темнее фона и частично остаётся.
    Webp с альфой: PNG той же стороны весит 300+ КБ, а предел картинки холста ≈70 КБ.
    """
    with Image.open(исходник) as и:
        и = и.convert("RGB")
        м = np.asarray(и).astype(np.float32)
        даль = np.sqrt(((м - np.array(ФОН_RGB, np.float32)) ** 2).sum(-1))
        альфа = np.clip((даль - 6) / 22, 0, 1) * 255
        итог = Image.fromarray(np.dstack([м, альфа]).astype(np.uint8), "RGBA")
        итог = итог.crop(итог.getchannel("A").point(lambda а: 255 if а > 40 else 0).getbbox())
        итог.thumbnail((сторона, сторона), Image.LANCZOS)
        итог.save(цель, "WEBP", quality=82, method=6)


def доски(пост: dict) -> list[tuple[str, str, str]]:
    """(файл, подпись, тело) по порядку карусели; запасные обложки — в конце, выпуск их не путает."""
    всего = len(пост["кадры"]) + 2
    д = [("Main.dc.html", "01 · Обложка А · как у автора", обложка(пост["обложка"]))]
    for н, к in enumerate(пост["кадры"], 2):
        д.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['заголовок']}", кадр(к)))
    д.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    д.append(("Oblozhka2.dc.html", "Обложка Б · сетка",
              обложка_сетка(пост["обложка_сетка"], [к["значок"] for к in пост["кадры"]])))
    д.append(("Oblozhka3.dc.html", "Обложка В · маркер", обложка_маркер(пост["обложка_маркер"])))
    return д


def картинки(пост: dict, папка: Path, стиль) -> list[Path]:
    файлы = []
    for имя in {к["значок"] for к in пост["кадры"]} | {пост["обложка"]["значок"]}:
        цель = папка / файл_значка(имя)
        без_фона(ТУТ / "значки/3d" / f"{имя}.png", цель)
        файлы.append(цель)
    for к in (пост["обложка_сетка"]["кот"], пост["обложка_маркер"]["кот"], пост["финал"]["кот"]):
        цель = папка / файл_кота(к["поза"])
        исходник = стиль.ПОЗЫ / f"{к['поза']}.png"
        if not исходник.exists():
            исходник = ТУТ.parent / "до-после/коты" / f"{к['поза']}.png"
        with Image.open(исходник) as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((1000, round(к["высота"] * 1.5)), Image.LANCZOS)
            и.save(цель, quality=86)
        файлы.append(цель)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
        и.thumbnail((240, 240), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return sorted(файлы) + [папка / "logo.png"]
