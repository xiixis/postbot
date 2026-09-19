# -*- coding: utf-8 -*-
"""Стиль «справочник»: python3 холст.py посты/<пост>.json

Снят с карусели TikTok @whygolding «Секретні слеш-команди Claude» (кадры — `референс/`,
полный разбор — `референс/паспорт.md`, числа — `ДНК.md`). Устройство кадра: белый лист
целиком, заголовок-рубрика прижат влево, под ним ровный столбец однотипных строк
«иконка-метка + имя со слешем + ` - ` + описание» **без подложек**; имя и описание сидят на
одной базовой линии, перенос описания идёт под себя «лесенкой», а не под иконку. Одна и та же
иконка повторяется у всех пунктов кадра: это метка рубрики, а не метка пункта. Призыв
сохранить стоит на каждом кадре. Обложка и финал двухполосные: светлая плита и графитовое
поле, граница строго прямая при полностью скруглённых остальных формах, и **ровно один
элемент** эту границу пересекает, с белой обводкой.

Четыре правки против оригинала — ради них стиль и заведён (подробно в `ДИЗАЙН.md`):
серый описания `#646464` (5,9:1) заменён графитом `#3A3E33` (11,0:1), имя и описание
различаются весом, а не светлотой; интерлиньяж описания поднят с 1,15 до 1,35; пунктов на
кадре 8, а не 10; введён свой носитель акцента (у автора акцента нет вовсе, 1%) и разбит ритм
ленты — каждый третий списочный кадр инверсный.

Доски холста 1080×1440; дальше как у «светлого разбора»: Artifact → «готово» → `../выпуск.py`.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
sys.path.insert(0, str(ТУТ.parent / "до-после"))
import стиль  # noqa: E402

# ── Палитра ──────────────────────────────────────────────────────────────────
# Белый лист — как у автора, годится без правки. Графит нашего тёмного поля светлее
# авторского чистого чёрного: по нему лайм и олива не проваливаются в дыру.
БЕЛЫЙ, ГРАФИТ_ФОН = "#FFFFFF", "#2A2E26"
ГРАФИТ = "#3A3E33"          # текст по белому — 11,0:1; авторский #646464 давал 5,9:1
ЛАЙМ, ОЛИВА, КРЕМ = стиль.ЛАЙМ, стиль.ОЛИВА, стиль.КРЕМ
БЕЛЫЙ_ТЕКСТ = "#F4F6EE"    # текст по графиту — ~13:1
ГЛУШЕ = "#9AA08F"          # только для неактивных строк выпадающего списка на обложке «поле ввода»

# Одна гарнитура на весь пост, роли разведены весом — это признак семейства.
# У Manrope в наборе есть 400 и 800; авторский «средний» вес описания 500 берём как 400.
ГЛАВНЫЙ = "font-family:Manrope,'Helvetica Neue',Arial,sans-serif;font-weight:800"
ОБЫЧНЫЙ = "font-family:Manrope,'Helvetica Neue',Arial,sans-serif;font-weight:400"

# ── Сетка доски 1080×1440 ───────────────────────────────────────────────────
КРАЙ = 70                   # 100 px кадра 1620 → 70 на доске 1080
ЗАГ_ВЕРХ, ЗАГ_КЕГЛЬ = 84, 84
СПИСОК_ВЕРХ, ШАГ = 348, 92  # 8 пунктов: последний начинается на 992, чистый просвет 46 px
ИМЯ_КЕГЛЬ, ЧТО_КЕГЛЬ = 42, 28          # перепад заголовок/описание 84/28 = 3,0:1
ТЕКСТ_ОТСТУП = 116          # колонка текста: 70 + 116 = 186; иконка стоит левее, в своей колонке


# ── Иконки-метки ────────────────────────────────────────────────────────────
# Рисуем вектором прямо в разметке, а не картинкой: внешний файл по file:// Chrome молча не
# рисует, а вшитый в url(data:…) адрес с кавычками рвёт атрибут style. Инлайновый <svg> не
# знает ни той, ни другой беды и перекрашивается одним currentColor.
ЗНАЧКИ = {
    "ключ": "M18.9 3.1l-2.9 2.9 2 2 2.9-2.9a5 5 0 0 1-6.6 6.4l-7.6 7.6a2.1 2.1 0 1 1-3-3"
            "l7.6-7.6a5 5 0 0 1 7.6-5.4z",
    "чертёж": "M3 5h18v14H3zM9 5v14M13 10h8M13 14h8",
    "лампочка": "M9 19h6M10 22h4M12 2a6.5 6.5 0 0 0-3.8 11.8c.5.4.8 1 .8 1.6V16h6v-.6c0-.6.3-1.2.8-1.6"
                "A6.5 6.5 0 0 0 12 2z",
    "весы": "M12 3v18M6 21h12M4 7h16M4 7l-3 7h6zM20 7l-3 7h6z",
    "ножницы": "M7.6 16.4L19 4M16.4 16.4L5 4",
    "телефон": "M6 2h12v20H6zM10 18.6h4",
    "рукопожатие": "M2 10l4-4 3.2 2.4L12 7l2.8 1.4L18 6l4 4M6 13l3.2 3.2M9.6 16.6l2.4 2.4"
                   "M12.6 14.4l2.8 2.8M15.6 12.2l2.8 2.8",
    "папка": "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM8 12h8M8 15.5h5",
    "росток": "M12 21v-7M12 14C12 10 9 7.5 4.5 7.5 4.5 12 7.5 14 12 14zM12 14c0-4 3-6.5 7.5-6.5"
              "C19.5 12 16.5 14 12 14z",
    "будильник": "M12 21a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM12 9v4l2.6 2M5 4L2.4 6.6M19 4l2.6 2.6",
}
КРУЖОК = {"ножницы": "M6 18.4m-2.6 0a2.6 2.6 0 1 0 5.2 0a2.6 2.6 0 1 0-5.2 0"
                     "M18 18.4m-2.6 0a2.6 2.6 0 1 0 5.2 0a2.6 2.6 0 1 0-5.2 0"}


def значок(имя: str, цвет: str, сторона: int = 46, класс: str = "значок") -> str:
    путь = ЗНАЧКИ[имя] + (КРУЖОК.get(имя, ""))
    return (f'<svg class="{класс}" viewBox="0 0 24 24" width="{сторона}" height="{сторона}" fill="none" '
            f'stroke="{цвет}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{путь}"/></svg>')


# ── Голова доски ────────────────────────────────────────────────────────────
def знак_css(светлый: bool) -> str:
    """Знак и полоса берутся из общего `стиль.py`, но их места сняты с кадра 1620×2160.
    Доска холста 1080×1440 — те же места, умноженные на 2/3; правило «всё важное выше
    y≈1760» превращается в «выше y≈1170», ниже идёт зона, которую закрывает лента."""
    return (стиль.знак_и_полоса_css(светлый_грунт=светлый)
            + ".знак{left:80px;bottom:205px;height:44px}\n"
              ".полоса{bottom:176px;height:6px}\n")


def знак(доля: float) -> str:
    """Логотип уходит файлом рядом с доской: вшитый data: раздувает доску за предел
    помощника в 2 МБ, и она молча не собирается."""
    return стиль.знак_и_полоса(доля).replace(f"src='{стиль.ЛОГО}'", 'src="logo.png"')


def голова(тёмный: bool = False, знак_на_тёмном: bool | None = None) -> str:
    """`знак_на_тёмном` отделяет грунт под логотипом от грунта доски: у финала лист светлый,
    а знак стоит на графитовом поле внизу, и приглушённый вариант там пропадает."""
    если_тёмный = тёмный if знак_на_тёмном is None else знак_на_тёмном
    фон = ГРАФИТ_ФОН if тёмный else БЕЛЫЙ
    чернила = БЕЛЫЙ_ТЕКСТ if тёмный else ГРАФИТ
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Manrope", "manrope-800", 800), ("Manrope", "manrope-400", 400))
            + f"""
    body {{ margin:0;background:{фон} }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;
        background:{фон};color:{чернила} }}
    /* position задаёт сам блок, а не общая палитра: иначе absolute перебивается и блок
       уезжает за кадр (ловушка, проверенная отрисовкой). */
    .кот {{ position:absolute }}
    .рубрика {{ position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:{ЗАГ_ВЕРХ}px;{ГЛАВНЫЙ};
        font-size:{ЗАГ_КЕГЛЬ}px;line-height:1.0;letter-spacing:-.025em;text-transform:uppercase }}
    .брусок {{ position:absolute;left:{КРАЙ}px;top:286px;width:260px;height:18px;border-radius:9px }}
    .рейка {{ position:absolute;left:{КРАЙ}px;top:340px;width:20px;height:704px;border-radius:10px }}
    .строка {{ position:absolute;left:{КРАЙ}px;right:{КРАЙ}px }}
    .значок {{ position:absolute;left:38px;top:2px }}
    .текст {{ margin-left:{ТЕКСТ_ОТСТУП}px;{ОБЫЧНЫЙ};font-size:{ЧТО_КЕГЛЬ}px;line-height:1.35 }}
    /* Интерлиньяж 1,35 — правка авторского брака: при его 1,15 вторая строка описания
       налезала на нижние выносные имени команды. */
    .имя {{ {ГЛАВНЫЙ};font-size:{ИМЯ_КЕГЛЬ}px;line-height:1.0 }}
    .слеш {{ {ГЛАВНЫЙ};font-size:{ИМЯ_КЕГЛЬ}px;line-height:1.0 }}
    .тире {{ {ОБЫЧНЫЙ};font-size:{ЧТО_КЕГЛЬ}px }}
    .призыв {{ position:absolute;left:{КРАЙ}px;top:1086px;height:64px;display:flex;
        align-items:center;padding:0 28px;border-radius:32px;{ГЛАВНЫЙ};font-size:24px }}
    .капсула {{ position:absolute;right:{КРАЙ}px;top:1086px;width:96px;height:64px;display:flex;
        align-items:center;justify-content:center;border-radius:32px;{ГЛАВНЫЙ};font-size:34px }}
    .плита {{ position:absolute;left:0;right:0;top:0;background:{БЕЛЫЙ} }}
    .поле {{ position:absolute;left:0;right:0;bottom:0;background:{ГРАФИТ_ФОН} }}
    .шапка {{ position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;{ГЛАВНЫЙ};line-height:.95;
        letter-spacing:-.03em;text-transform:uppercase;color:{ГРАФИТ} }}
    .подзаг {{ position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;{ОБЫЧНЫЙ};line-height:1.32;color:{ГРАФИТ} }}
{знак_css(not если_тёмный)}  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


# ── Кирпичи списочного кадра ────────────────────────────────────────────────
def рубрика(строки: list[str], цвет: str) -> str:
    return f'  <div class=рубрика data-блок style="color:{цвет}">{"<br>".join(строки)}</div>'


def строка(п: dict, верх: int, метка: str, цвета: dict) -> str:
    """Иконка-метка + /имя + ` - ` + описание на одной базовой линии.

    Перенос описания идёт под себя, по левому краю колонки текста, а не под иконку:
    иконка стоит своей колонкой и в поток строки не входит.
    """
    return (f'  <div class=строка data-блок style="top:{верх}px">'
            f'{значок(метка, цвета["значок"])}'
            f'<div class=текст style="color:{цвета["что"]}">'
            f'<span class=слеш style="color:{цвета["слеш"]}">/</span>'
            f'<span class=имя style="color:{цвета["имя"]}">{п["имя"]}</span>'
            f'<span class=тире> - </span>{п["что"]}</div></div>')


def подвал(призыв: str, цвета: dict) -> str:
    """Призыв сохранить — на каждом кадре, а не только в финале: на этом и держатся
    6% сохранений у оригинала. Текст свой, приём авторский."""
    return (f'  <div class=призыв data-блок style="background:{цвета["призыв_фон"]};'
            f'color:{цвета["призыв_текст"]}">{призыв}</div>\n'
            f'  <div class=капсула data-блок style="background:{цвета["капсула_фон"]};'
            f'color:{цвета["капсула_текст"]}">&#8594;</div>')


def цвета_кадра(инверсный: bool) -> dict:
    if инверсный:
        return {"заголовок": ЛАЙМ, "имя": БЕЛЫЙ_ТЕКСТ, "что": БЕЛЫЙ_ТЕКСТ, "слеш": ЛАЙМ,
                "значок": ЛАЙМ, "рейка": ОЛИВА, "брусок": ЛАЙМ,
                "призыв_фон": ЛАЙМ, "призыв_текст": ГРАФИТ_ФОН,
                "капсула_фон": "rgba(244,246,238,.12)", "капсула_текст": БЕЛЫЙ_ТЕКСТ}
    # Лайм текстом по белому даёт 1,7:1 и запрещён: по светлому он идёт только заливкой.
    return {"заголовок": ГРАФИТ, "имя": ГРАФИТ, "что": ГРАФИТ, "слеш": ОЛИВА,
            "значок": ОЛИВА, "рейка": ЛАЙМ, "брусок": ОЛИВА,
            "призыв_фон": ОЛИВА, "призыв_текст": "#FFFFFF",
            "капсула_фон": ГРАФИТ, "капсула_текст": "#FFFFFF"}


def кадр(к: dict) -> str:
    инв = bool(к.get("инверсный"))
    ц = цвета_кадра(инв)
    части = [рубрика(к["заголовок"], ц["заголовок"]),
             f'  <div class=брусок style="background:{ц["брусок"]}"></div>',
             f'  <div class=рейка style="background:{ц["рейка"]}"></div>']
    for н, п in enumerate(к["пункты"]):
        части.append(строка(п, СПИСОК_ВЕРХ + н * ШАГ, к["значок"], ц))
    части.append(подвал(к.get("призыв", "Сохрани, чтобы не искать"), ц))
    части.append("  " + знак(0.34 if инв else 0.52))
    return голова(тёмный=инв) + '<div class=кадр>\n' + "\n".join(части) + "\n</div>" + ХВОСТ


# ── Обложки ─────────────────────────────────────────────────────────────────
def стикер_шва(верх: int, сторона: int = 253) -> str:
    """Единственный источник глубины в плоской вёрстке: ровно один элемент пересекает
    строго прямую границу плит, с белой обводкой. Скругление 28% стороны — авторское."""
    return (f'  <div data-блок style="position:absolute;left:96px;top:{верх}px;width:{сторона}px;'
            f'height:{сторона}px;border-radius:{round(сторона * .28)}px;background:{ОЛИВА};'
            f'box-shadow:0 0 0 9px #FFFFFF;display:flex;align-items:center;justify-content:center;'
            f'{ГЛАВНЫЙ};font-size:150px;line-height:1;color:{ЛАЙМ}">/</div>')


def обложка_кот(о: dict) -> str:
    """А — «кот в темноте»: плита с обещанием через чужую боль + графитовое поле с котом,
    чей собственный тёмный корпус сливается с полем, как студийный фон у автора."""
    шов = о.get("шов", 648)
    return голова(тёмный=True) + f"""<div class=кадр>
  <div class=плита style="height:{шов}px"></div>
  <div class=поле style="top:{шов}px"></div>
  {стиль.кот_файлом(о["кот"])}
  <div class=шапка style="top:84px;font-size:110px">{"<br>".join(о["заголовок"])}</div>
  <div class=подзаг style="top:424px;font-size:41px">{"<br>".join(о["под"])}</div>
{стикер_шва(шов - 63)}
  <div data-блок style="position:absolute;left:300px;top:1074px;width:200px;height:64px;
      border-radius:32px;border:2px solid {ЛАЙМ};display:flex;align-items:center;
      justify-content:center;{ГЛАВНЫЙ};font-size:34px;color:{ЛАЙМ}">&#8594;</div>
  {знак(0.34)}
</div>""" + ХВОСТ


def обложка_поле(о: dict) -> str:
    """Б — «поле ввода»: показать сам механизм, а не рассказать о нём. Плит нет вовсе,
    весь кадр графитовый, герой — раскрытое меню команд."""
    строки = ""
    for н, с in enumerate(о["список"]):
        выбрана = н == о.get("выбрана", len(о["список"]) - 1)
        фон = f"background:{ОЛИВА};" if выбрана else ""
        цвет = "#FFFFFF" if выбрана else ГЛУШЕ
        строки += (f'<div style="display:flex;align-items:center;height:58px;padding:0 26px;'
                   f'border-radius:14px;{фон}{ГЛАВНЫЙ};font-size:32px;color:{цвет}">'
                   f'<span style="color:{ЛАЙМ if выбрана else ГЛУШЕ}">/</span>{с}</div>')
    return голова(тёмный=True) + f"""<div class=кадр>
  <div data-блок style="position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:150px;{ГЛАВНЫЙ};
      font-size:70px;line-height:1.02;letter-spacing:-.03em;text-transform:uppercase;
      color:#FFFFFF">{"<br>".join(о["заголовок"])}</div>
  <div data-блок style="position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:470px;height:130px;
      border-radius:28px;background:#1E211B;border:2px solid #3A3F36;display:flex;
      align-items:center;padding:0 36px;{ГЛАВНЫЙ};font-size:54px;color:{ЛАЙМ}">/
    <span style="{ОБЫЧНЫЙ};font-size:40px;color:{ГЛУШЕ};margin-left:8px">{о["подсказка"]}</span>
    <span style="width:5px;height:56px;background:{ЛАЙМ};margin-left:10px"></span>
  </div>
  <div data-блок style="position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:622px;padding:16px;
      border-radius:24px;background:#1E211B;display:flex;flex-direction:column;gap:2px">{строки}</div>
  {знак(0.34)}
</div>""" + ХВОСТ


def обложка_полка(о: dict) -> str:
    """В — «полка рубрик»: обещание через объём и порядок, а не через боль. Инфографика-
    оглавление: ни картинки, ни тёмного поля, зато сразу видно, сколько всего внутри."""
    корешки = ""
    for н, р in enumerate(о["рубрики"]):
        корешки += (f'<div style="display:flex;align-items:center;justify-content:space-between;'
                    f'height:78px;padding:0 34px;border-radius:16px;background:{ОЛИВА};'
                    f'{ГЛАВНЫЙ};font-size:30px;color:#FFFFFF">'
                    f'<span>{р}</span><span>8</span></div>')
    return голова() + f"""<div class=кадр style="background:{КРЕМ}">
  <div data-блок style="position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:90px;{ГЛАВНЫЙ};
      font-size:46px;color:{ГРАФИТ}">{о["заголовок"]}</div>
  <div data-блок style="position:absolute;left:{КРАЙ}px;right:{КРАЙ}px;top:180px;display:flex;
      flex-direction:column;gap:12px">{корешки}</div>
  <div data-блок style="position:absolute;left:860px;top:360px;width:46px;height:884px;
      background:{ЛАЙМ};z-index:4;
      clip-path:polygon(0 0,100% 0,100% 100%,50% 88%,0 100%)"></div>
  {знак(0.52)}
</div>""" + ХВОСТ


# ── Финал ───────────────────────────────────────────────────────────────────
def финал(ф: dict) -> str:
    """Та же двухполосная схема, что у обложки, но пропорция и мысль другие: обложка
    обещает «одно слово вместо абзаца», финал говорит «их 80, сохрани»."""
    шов = ф.get("шов", 835)
    оглавление = "".join(f'<div style="margin-bottom:9px">{р}</div>' for р in ф["оглавление"])
    иконки = ("M12 20.5l-1.5-1.4C5.4 14.5 2.5 11.9 2.5 8.7 2.5 6.1 4.5 4 7.2 4c1.5 0 3 .7 3.8 1.9"
              "h2C13.8 4.7 15.3 4 16.8 4c2.7 0 4.7 2.1 4.7 4.7 0 3.2-2.9 5.8-8 10.4z")
    return голова(знак_на_тёмном=True) + f"""<div class=кадр>
  <div class=плита style="height:{шов}px"></div>
  <div class=поле style="top:{шов}px"></div>
  <div class=шапка style="top:96px;font-size:100px">{"<br>".join(ф["заголовок"])}</div>
  <div class=подзаг style="top:520px;font-size:35px">{"<br>".join(ф["под"])}</div>
  {стиль.кот_файлом(ф["кот"])}
  <div data-блок style="position:absolute;left:720px;top:910px;width:210px;height:250px;
      border-radius:26px;background:#1E211B;border:3px solid {ОЛИВА};padding:18px 14px;
      box-sizing:border-box;{ОБЫЧНЫЙ};font-size:13px;line-height:1.1;color:{ЛАЙМ}">{оглавление}</div>
  <div data-блок style="position:absolute;left:640px;top:1180px;width:370px;text-align:center;
      {ГЛАВНЫЙ};font-size:26px;color:{ЛАЙМ}">{ф["ссылка"]}</div>
  <div data-блок style="position:absolute;left:390px;top:{шов - 21}px;width:300px;height:84px;
      border-radius:42px;background:{ОЛИВА};box-shadow:0 0 0 9px #FFFFFF;display:flex;
      align-items:center;justify-content:center;gap:34px">
    <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#FFFFFF" stroke-width="1.9"
        stroke-linecap="round" stroke-linejoin="round"><path d="{иконки}"/></svg>
    <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#FFFFFF" stroke-width="1.9"
        stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-6-5-6 5z"/></svg>
    <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#FFFFFF" stroke-width="1.9"
        stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg>
  </div>
  {знак(1.0)}
</div>""" + ХВОСТ


# ── Картинки рядом с доской ─────────────────────────────────────────────────
def картинки(пост: dict, папка: Path) -> list[Path]:
    """Коты и логотип уходят файлами: имена только латиницей — кириллицу помощник отвергает."""
    файлы = стиль.коты_в_файлы(пост, папка)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def _дп():
    """Помощник холста и транслитерация имени файла живут в `до-после/холст.py`."""
    import importlib.util
    спека = importlib.util.spec_from_file_location("холст_до_после", ТУТ.parent / "до-после" / "холст.py")
    м = importlib.util.module_from_spec(спека)
    sys.modules["холст_до_после"] = м
    спека.loader.exec_module(м)
    return м


def main():
    дп = _дп()
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    # ⛔️ Три обложки обязательны: правило владельца, холст без них не выкладывается.
    обложки = {"кот": lambda: обложка_кот(пост["обложка"]),
               "поле": lambda: обложка_поле(пост["обложка_поле"]),
               "полка": lambda: обложка_полка(пост["обложка_полка"])}
    главная = пост.get("главная", "кот")
    запасные = [и for и in обложки if и != главная]

    всего = len(пост["кадры"]) + 2
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 2):
        имя = f"{н:02d} · " + " ".join(к["заголовок"])[:28] + (" · инверсный" if к.get("инверсный") else "")
        доски.append((f"Kadr{н:02d}.dc.html", имя, кадр(к)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    если_мало = [д for д in доски if д[0].startswith(("Main", "Oblozhka"))]
    assert len(если_мало) == 3, "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)], "launch": {"view": "canvas"}}
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{пост['название']}: новый стиль «справочник» — плотный список без подложек, "
        "каждый третий кадр инверсный, три кардинально разные обложки. "
        "Двигайте и правьте прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = дп.помощник()
    страница = папка / f"{дп.латиницей(файл.stem)}.html"
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"),
               "--out", str(страница), "--title", пост["название"], "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    for к in картинки(пост, папка):
        команда += ["--image", str(к)]
    вывод = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)], capture_output=True, text=True)
    print((вывод.stderr.strip() + "\n") if вывод.stderr.strip() else "", end="")
    print(проверка.stdout.strip()[:300], проверка.stderr.strip()[:300])
    print("досок:", len(доски), "· обложек:", len(если_мало))
    print("страница холста:", страница, f"{страница.stat().st_size // 1024} КБ")


if __name__ == "__main__":
    main()
