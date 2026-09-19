# -*- coding: utf-8 -*-
"""Стиль «светофор»: python3 холст.py посты/<пост>.json

Снят с карусели Instagram `Dc5fI9uGe1G` (разбор — `референс/паспорт.md`, ДНК — `ДНК.md`).
Устройство кадра: одна колонка из трёх равных полос-регистров, в каждой конвейер слева
направо «слово-оценка на цветной пилюле → тройной шеврон растущего размера → плитка
со снимком сервиса и его именем». Сверху — категория одним крупным словом и подзаголовок-
критерий, внизу подвал «Сохрани» / «Дальше». Обложка и финал тёмные, на графите.

Главная правка против автора — контраст. У него слово-оценка набрано цветом по кремовому
(жёлтый даёт ≈1,6:1, красный ≈4:1), и треть текста лежит ниже нашего порога 8:1. У нас
слово-оценка стоит графитом или белым **на цветной пилюле**: контраст держит пилюля, цвет
остаётся кодом шкалы. Лайм текстом по светлому не ставится нигде.

Доски холста 1080×1440; дальше как у «светлого разбора»: Artifact → «готово» → `../выпуск.py`.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

# ── Палитра ──────────────────────────────────────────────────────────────────
# Грунт средних кадров — крем, обложка и финал — графит: у автора все пять кадров одной
# светлоты (L 0.72–0.79) и в сетке профиля сливаются в одну картинку, показанную пять раз.
КРЕМ, КАРТА = стиль.КРЕМ, "#FBFBF6"
ГРАФИТ = "#1C1C1A"                       # чернила по крему: 15,2:1
МЯГКИЙ = "#3A3E33"                       # пояснения по крему: 9,6:1
СВЕТЛЫЙ, ТИХИЙ = стиль.СВЕТЛЫЙ, "#C3C8B8"  # текст по графиту: 14,5:1 и 10,1:1
ЛАЙМ, ОЛИВА = стиль.ЛАЙМ, стиль.ОЛИВА

# ── Три уровня шкалы ─────────────────────────────────────────────────────────
# `фон` + `текст` — расчётные пары из сценария: контраст держит пилюля, а не краска буквы.
# `линия` — цвет шеврона по крему: взят затемнённый вариант уровня, иначе янтарная линия
# по кремовому даёт ≈1,9:1 и указатель взгляда пропадает. `линия_тёмн` — то же по графиту,
# там наоборот нужен светлый вариант.
УРОВНИ = {
    "плохо":  {"слово": "ПЛОХО",  "фон": "#8C0F20", "текст": "#FFFFFF",
               "линия": "#8C0F20", "линия_тёмн": "#F2647A"},
    "хорошо": {"слово": "ХОРОШО", "фон": "#F0B92E", "текст": ГРАФИТ,
               "линия": "#8A6A08", "линия_тёмн": "#F0B92E"},
    "лучше":  {"слово": "ЛУЧШЕ",  "фон": ЛАЙМ,      "текст": ГРАФИТ,
               "линия": ОЛИВА,     "линия_тёмн": ЛАЙМ},
}

К = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.02em"
Т = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif"

W, H = 1080, 1440                        # доска холста; на стол уходит тот же JPG 1080×1440
ПОЛЕ = 80                                # боковое поле, 7,4% ширины


def голова(тёмный: bool = False) -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            "</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))
            + f"\n    body {{ margin: 0; background: {ГРАФИТ if тёмный else КРЕМ}; }}\n  </style>\n</helmet>\n")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"

# Какие снимки уже сняты. Файла нет — на его месте рисуется заглушка, и холст всё равно
# собирается: снимки это отдельный шаг и сеть, а править код под них потом не надо.
ЕСТЬ = {п.stem for п in (ТУТ / "снимки").glob("*.png")} | {п.stem for п in (ТУТ / "снимки").glob("*.jpg")}


def жирным(текст: str) -> str:
    """`**слово**` из файла поста → <b>: в сценарии так помечена суть строки."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", текст)


def знак(доля: float, тёмный: bool = True) -> str:
    """Знак канала с лаймовой полосой — на каждой доске, включая обе запасные обложки.
    У автора логотипа нет вовсе; у нас он обязателен, и полоса заодно добирает акцент."""
    подкраска = "" if тёмный else " filter: brightness(.45) saturate(1.4);"
    цвет = ЛАЙМ if тёмный else ОЛИВА
    свечение = f" box-shadow: 0 0 26px rgba({стиль.ЛАЙМ_RGB},.45);" if тёмный else ""
    return (f'  <img src="logo.png" style="position: absolute; left: {ПОЛЕ}px; bottom: 58px; height: 40px;{подкраска}">\n'
            f'  <div style="position: absolute; left: 0; bottom: 30px; height: 6px;'
            f' width: {доля * 100:.1f}%; background: {цвет};{свечение}"></div>')


def шевроны(цвет: str, масштаб: float = 1.0) -> str:
    """Тройной шеврон растущего размера, смотрит ВПРАВО. У автора он смотрит влево —
    это прямая ошибка: карусель листают вправо, и указатель тащит взгляд назад."""
    куски = []
    for высота, толщина in ((30, 6), (42, 7), (54, 8)):
        ширина = высота * 0.55
        о = толщина / 2 + 1
        куски.append(
            f"<svg viewBox='0 0 {ширина:.0f} {высота}' width='{ширина * масштаб:.0f}'"
            f" height='{высота * масштаб:.0f}' fill='none' stroke='{цвет}' stroke-width='{толщина}'"
            f" stroke-linecap='round' stroke-linejoin='round'>"
            f"<path d='M{о:.0f} {о:.0f}L{ширина - о:.0f} {высота / 2:.0f}L{о:.0f} {высота - о:.0f}'/></svg>")
    return (f'<div style="flex: none; display: flex; align-items: center;'
            f' gap: {8 * масштаб:.0f}px;">{"".join(куски)}</div>')


def плитка(снимок: str | None, имя: str, сторона: int) -> str:
    """Ответ — скруглённый квадрат с радиусом 26% стороны (параметр автора, взят как есть).

    Внутри свой снимок сервиса: правило проекта — подборка находок показывается своими
    снимками, чужие 3D-логотипы приложений не переносятся. Снимка ещё нет — на его месте
    заглушка: графитовый квадрат с первой буквой имени лаймом и лаймовой каймой. Лайм по
    графиту даёт 11,8:1, обратное сочетание (лайм по светлому) у нас запрещено.
    """
    радиус = round(сторона * 0.26)
    if снимок and снимок in ЕСТЬ:
        нутро = (f'<img src="{снимок}.jpg" style="width: 100%; height: 100%; object-fit: cover;'
                 f' object-position: top center; display: block;">')
        подложка = f"background: #FFFFFF; box-shadow: 0 6px 18px rgba(28,28,26,.18);"
    else:
        нутро = (f'<span style="{К}; font-size: {round(сторона * 0.46)}px; color: {ЛАЙМ};'
                 f' line-height: 1;">{имя.strip()[:1].upper()}</span>')
        подложка = (f"background: {ГРАФИТ}; box-shadow: inset 0 0 0 3px rgba({стиль.ЛАЙМ_RGB},.40),"
                    f" 0 6px 18px rgba(28,28,26,.18);")
    return (f'<div style="position: relative; overflow: hidden; flex: none; width: {сторона}px;'
            f' height: {сторона}px; border-radius: {радиус}px; {подложка} display: flex;'
            f' align-items: center; justify-content: center;">{нутро}</div>')


def пилюля(у: dict, кегль: int = 44, высота: int = 72) -> str:
    """Слово-оценка на цветной пилюле — ключевая правка против автора (см. шапку файла)."""
    return (f'<div style="display: inline-flex; align-items: center; height: {высота}px;'
            f' padding: 0 {round(высота * 0.46)}px; border-radius: {высота // 2}px;'
            f' background: {у["фон"]}; color: {у["текст"]}; {К}; font-size: {кегль}px;'
            f' letter-spacing: 0.04em; line-height: 1;">{у["слово"]}</div>')


# ── Средний кадр ─────────────────────────────────────────────────────────────

def прогресс(номер: int, всего: int) -> str:
    """Лаймовая полоса `1/5 … 5/5` — прибавка, которой у автора нет. Он не даёт зрителю
    понять, где тот находится; полоса стоит недорого и одновременно добирает акцент."""
    доля = номер / всего
    return (f'  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 50px;'
            f' display: flex; align-items: center; gap: 20px;">'
            f'<div style="flex: 1; height: 10px; border-radius: 5px; background: rgba(28,28,26,.10);">'
            f'<div style="width: {доля * 100:.0f}%; height: 100%; border-radius: 5px; background: {ЛАЙМ};"></div></div>'
            f'<div style="{Т}; font-weight: 700; font-size: 26px; color: {МЯГКИЙ};">{номер}/{всего}</div></div>')


def категория(слово: str, критерий: str) -> str:
    """Одно крупное слово вверху плюс подзаголовок-критерий мелким.

    Кегль подбирается под длину слова: на ширине 1080 «КАРТИНКИ» при едином кегле уходит за
    поля. Множитель 0,71 на знак снят с отрисовки самих кадров (Onest 800 даёт 0,67–0,70 em на
    заглавную кириллицу), 20 px — запас на выносные. Литера выходит 117–151 px, то есть 8–10,5%
    высоты кадра против 7,1% у автора. Вдвое по литере на нашей ширине не получается физически:
    слову из восьми знаков это дало бы строку в 1400 px при поле 920 — см. отступление в
    `ДИЗАЙН.md`. Зато эти 8–10,5% набраны буквой, а не размытой тенью-каплей, которой автор
    добирал свои 13,9–14,8%, и которую мы не переносим.
    """
    кегль = min(210, int((W - 2 * ПОЛЕ - 20) / (len(слово) * 0.71)))
    return (f'  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 118px; {К};'
            f' font-size: {кегль}px; line-height: 1.0; color: {ГРАФИТ};">{слово}</div>\n'
            f'  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 350px; {Т};'
            f' font-size: 34px; line-height: 1.25; color: {МЯГКИЙ};">{критерий}</div>')


def регистр(с: dict, последний: bool) -> str:
    """Одна полоса-регистр: оценка → шеврон → ответ, слева направо."""
    у = УРОВНИ[с["уровень"]]
    рамка = "" if последний else f" border-bottom: 4px solid {ГРАФИТ};"
    return (f'    <div style="flex: 1; display: flex; align-items: center; gap: 24px;'
            f' padding: 14px 28px; box-sizing: border-box;{рамка}">'
            f'<div style="flex: 1;">{пилюля(у)}'
            f'<div style="{Т}; font-size: 26px; line-height: 1.3; color: {МЯГКИЙ}; margin-top: 14px;">'
            f'{жирным(с["текст"])}</div></div>'
            f'{шевроны(у["линия"])}'
            f'<div style="flex: none; width: 158px; text-align: center;">'
            f'{плитка(с.get("снимок"), с["сервис"], 158)}'
            f'<div style="{К}; font-size: 28px; line-height: 1.2; color: {ГРАФИТ}; margin-top: 10px;">'
            f'{с["сервис"]}</div></div></div>')


def подвал() -> str:
    """Подвал из двух частей: «Сохрани» слева, указатель «Дальше» справа — приём автора,
    но по-русски и со стрелкой вправо, а не влево."""
    закладка = ("<svg viewBox='0 0 24 24' width='30' height='30' fill='currentColor'>"
                "<path d='M6 2h12a1 1 0 0 1 1 1v19l-7-5-7 5V3a1 1 0 0 1 1-1z'/></svg>")
    return (f'  <div style="position: absolute; left: {ПОЛЕ}px; top: 1236px; display: flex;'
            f' align-items: center; gap: 14px; color: {ГРАФИТ}; {К}; font-size: 32px;">'
            f'{закладка}<span>Сохрани</span></div>\n'
            f'  <div style="position: absolute; right: {ПОЛЕ}px; top: 1236px; display: inline-flex;'
            f' align-items: center; gap: 14px; height: 60px; padding: 0 28px; border-radius: 30px;'
            f' background: {ЛАЙМ}; color: {ГРАФИТ}; {К}; font-size: 30px;">'
            f'<span>Дальше</span>{шевроны(ГРАФИТ, 0.42)}</div>')


def кадр(к: dict, номер: int, всего: int) -> str:
    полосы = "\n".join(регистр(с, н == len(к["строки"]) - 1) for н, с in enumerate(к["строки"]))
    return голова() + f"""<div style="position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {КРЕМ};">
{прогресс(номер - 1, всего - 2)}
{категория(к['категория'], к['критерий'])}
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 430px; height: 760px;
 box-sizing: border-box; border: 4px solid {ГРАФИТ}; border-radius: 36px; background: {КАРТА};
 overflow: hidden; display: flex; flex-direction: column;">
{полосы}
  </div>
{подвал()}
{знак(номер / всего, тёмный=False)}
</div>""" + ХВОСТ


# ── Обложки ──────────────────────────────────────────────────────────────────

def обложка_строка(о: dict, всего: int) -> str:
    """1 «Красная строка» — главная. Провокация известным именем: приём автора (самое
    известное имя в строке «плохо») у него вышел случайно, мы ставим его нарочно и
    вытаскиваем в заголовок. Верхние две трети — заголовок, нижняя — одна строка светофора."""
    с = о["строка"]
    у = УРОВНИ[с["уровень"]]
    строки = "<br>".join(о["заголовок"])
    return голова(True) + f"""<div style="position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {ГРАФИТ};">
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 140px; {К}; font-size: 118px;
 line-height: 1.06; color: {СВЕТЛЫЙ};">{строки}<br><span style="color: {ЛАЙМ};">{о['лайм']}</span></div>
  <div style="position: absolute; left: {ПОЛЕ}px; top: 570px; {Т}; font-weight: 700; font-size: 38px;
 letter-spacing: 0.04em; color: {ТИХИЙ};">{о['под']}</div>
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 850px; height: 430px;
 box-sizing: border-box; border-radius: 36px; background: rgba(255,255,255,.05);
 box-shadow: inset 0 0 0 4px rgba(255,255,255,.14); display: flex; align-items: center;
 gap: 28px; padding: 0 40px;">
    <div style="flex: none;">{пилюля(у, 52, 86)}</div>
    <div style="flex: 1; display: flex; justify-content: center;">{шевроны(у['линия_тёмн'], 1.15)}</div>
    <div style="flex: none; width: 240px; text-align: center;">{плитка(с.get('снимок'), с['сервис'], 240)}
      <div style="{К}; font-size: 30px; color: {СВЕТЛЫЙ}; margin-top: 10px;">{с['сервис']}</div></div>
  </div>
{знак(1 / всего)}
</div>""" + ХВОСТ


def обложка_светофор(о: dict, всего: int) -> str:
    """2 «Светофор без слов» — чистый цветовой код, читается вообще без чтения.
    Снимков нет ни одного. На красной и янтарной слова затемнены почти до фона
    (они здесь декор, смысл несёт цвет), на лаймовой «ЛУЧШЕ» графитом в полную силу."""
    тише = {"плохо": "#6E0C19", "хорошо": "#C99A24", "лучше": ГРАФИТ}
    кегли = {"плохо": 120, "хорошо": 120, "лучше": 150}
    пилюли = "".join(
        f'<div style="flex: 1; border-radius: 60px; background: {УРОВНИ[и]["фон"]};'
        f' display: flex; align-items: center; justify-content: center; {К};'
        f' font-size: {кегли[и]}px; letter-spacing: 0.02em; color: {тише[и]};">'
        f'{УРОВНИ[и]["слово"]}</div>' for и in ("плохо", "хорошо", "лучше"))
    return голова(True) + f"""<div style="position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {ГРАФИТ};">
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 88px; {К}; font-size: 44px;
 line-height: 1.2; color: {СВЕТЛЫЙ};">{о['заголовок']}</div>
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 230px; height: 1050px;
 display: flex; flex-direction: column; gap: 30px;">{пилюли}</div>
{знак(1 / всего)}
</div>""" + ХВОСТ


def обложка_сетка(о: dict, всего: int) -> str:
    """3 «Сетка 15» — количество как довод: мозаика из пятнадцати снимков во весь кадр,
    десять притушены почти до графита, пять обведены лаймом. Поверх — графитовая плашка."""
    ячейки = ""
    for имя in о["все"]:
        горит = имя in о["горят"]
        отделка = (f'box-shadow: inset 0 0 0 5px {ЛАЙМ};' if горит else
                   'box-shadow: inset 0 0 0 1px rgba(255,255,255,.06);')
        тень = '' if горит else 'filter: brightness(.34) saturate(.5);'
        если_снимка_нет = (f'<span style="{К}; font-size: 92px; color: {ЛАЙМ if горит else "#4A4E44"};'
                           f' line-height: 1;">{имя.strip()[:1].upper()}</span>')
        нутро = (f'<img src="{имя}.jpg" style="width: 100%; height: 100%; object-fit: cover; {тень}">'
                 if имя in ЕСТЬ else если_снимка_нет)
        ячейки += (f'<div style="position: relative; overflow: hidden; background: #26261F;'
                   f' display: flex; align-items: center; justify-content: center; {отделка}">{нутро}</div>')
    заголовок = "<br>".join(о["заголовок"])
    return голова(True) + f"""<div style="position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {ГРАФИТ};">
  <div style="position: absolute; inset: 0; display: grid; grid-template-columns: repeat(3, 1fr);
 grid-template-rows: repeat(5, 1fr);">{ячейки}</div>
  <div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(28,28,26,.30) 0%,
 rgba(28,28,26,0) 30%, rgba(28,28,26,0) 70%, rgba(28,28,26,.88) 100%);"></div>
  <div style="position: absolute; left: 70px; right: 70px; top: 560px; padding: 46px 40px;
 border-radius: 36px; background: rgba(28,28,26,.94); box-shadow: inset 0 0 0 4px {ЛАЙМ};
 {К}; font-size: 78px; line-height: 1.1; text-align: center; color: {СВЕТЛЫЙ};">{заголовок}</div>
{знак(1 / всего)}
</div>""" + ХВОСТ


# ── Финал ────────────────────────────────────────────────────────────────────

def финал(ф: dict, всего: int) -> str:
    """Не шестая категория, а сводка: полос-регистров здесь нет вовсе, раскладка другая.
    У автора карусель кончается пятой категорией и ничем — сохранять нечего. Сводка и есть
    тот единственный кадр, ради которого пост держат в сохранённом."""
    строки = ""
    for л in ф["лучшие"]:
        строки += (f'<div style="display: flex; align-items: center; gap: 22px; height: 92px;">'
                   f'{плитка(л.get("снимок"), л["сервис"], 76)}'
                   f'<div><div style="{Т}; font-size: 24px; letter-spacing: 0.06em; color: {ТИХИЙ};">'
                   f'{л["категория"].upper()}</div>'
                   f'<div style="{К}; font-size: 40px; line-height: 1.1; color: {ЛАЙМ};">{л["сервис"]}</div>'
                   f'</div></div>')
    п = ф["призыв"]
    # Кот отдельным webp: вшитая данными поза раздувает доску за предел помощника в 2 МБ.
    кот = (f'<img src="kot-{стиль.латиницей(ф["кот"]["поза"])}.webp" style="position: absolute;'
           f' right: 30px; bottom: 120px; height: {ф["кот"]["высота"]}px;">') if ф.get("кот") else ""
    return голова(True) + f"""<div style="position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {ГРАФИТ};">
  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: 110px; {К}; font-size: 88px;
 line-height: 1.08; color: {СВЕТЛЫЙ};">{'<br>'.join(ф['заголовок'])}</div>
  <div style="position: absolute; left: {ПОЛЕ}px; top: 330px; width: 6px; height: 532px;
 border-radius: 3px; background: {ЛАЙМ};"></div>
  <div style="position: absolute; left: {ПОЛЕ + 30}px; top: 330px; width: 600px; display: flex;
 flex-direction: column; gap: 18px;">{строки}</div>
  <div style="position: absolute; left: {ПОЛЕ}px; top: 930px; width: 620px;">
    <div style="{К}; font-size: 96px; line-height: 1; color: {ЛАЙМ};">{п['крупно']}</div>
    <div style="{Т}; font-size: 34px; line-height: 1.25; color: {ТИХИЙ}; margin-top: 10px;">{п['крупно_под']}</div>
    <div style="{К}; font-size: 56px; line-height: 1.1; color: {СВЕТЛЫЙ}; margin-top: 26px;">{п['мельче']}</div>
    <div style="{Т}; font-size: 30px; line-height: 1.3; color: {ТИХИЙ}; margin-top: 8px;">{п['мельче_под']}</div>
  </div>
  {кот}
{знак(1.0)}
</div>""" + ХВОСТ


# ── Сборка ───────────────────────────────────────────────────────────────────

def картинки(пост: dict, папка: Path) -> list[Path]:
    """Снимки, кот и знак — отдельными файлами рядом с доской.

    Кот именно файлом, а не данными: вшитая поза раздувает доску за предел помощника в 2 МБ,
    и она молча не собирается. Имена картинок только латиницей — кириллицу помощник не берёт.
    """
    файлы = []
    нужны = {с.get("снимок") for к in пост["кадры"] for с in к["строки"]}
    нужны |= {л.get("снимок") for л in пост["финал"]["лучшие"]}
    нужны |= {пост["обложка"]["строка"].get("снимок")}
    нужны |= set(пост["обложка_сетка"]["все"])
    for имя in sorted(и for и in нужны if и and и in ЕСТЬ):
        исходник = next(п for п in ((ТУТ / "снимки" / f"{имя}.png"), (ТУТ / "снимки" / f"{имя}.jpg")) if п.exists())
        цель = папка / f"{имя}.jpg"        # .jpg → image/jpeg; с image/jpg Chrome не рисует
        with Image.open(исходник) as и:
            и = и.convert("RGB")
            # Страховка на случай некадрированного снимка: плитка квадратная, и растянутая
            # страница 1440×900 в 170 px превращается в кашу. Режем по центру верха.
            ш, в = и.size
            сторона = min(ш, в)
            и = и.crop(((ш - сторона) // 2, 0, (ш - сторона) // 2 + сторона, сторона))
            и.thumbnail((420, 420), Image.LANCZOS)
            и.save(цель, quality=82, optimize=True)
        файлы.append(цель)
    файлы += стиль.коты_в_файлы(пост, папка)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def помощник() -> Path:
    """Помощник холста из распакованного скила design; путь меняется с версией Claude Code."""
    найдено = sorted(Path("/private/tmp/claude-501/bundled-skills").glob("*/*/design/seed-canvas.mjs"),
                     key=lambda п: п.stat().st_mtime)
    if not найдено:
        raise SystemExit("нет помощника холста: в сессии Claude Code вызвать /design, он распакуется")
    return найдено[-1]


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: правило владельца, холст без них не выкладывается.
    обложки = {"красная-строка": lambda: обложка_строка(пост["обложка"], всего),
               "светофор": lambda: обложка_светофор(пост["обложка_светофор"], всего),
               "сетка": lambda: обложка_сетка(пост["обложка_сетка"], всего)}
    главная = пост.get("главная", "красная-строка")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['категория']}", кадр(к, н, всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"], всего)))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    если_мало = [д for д in доски if д[0].startswith(("Main", "Oblozhka"))]
    assert len(если_мало) == 3, "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    # Карусель первой строкой, запасные обложки — второй под ней.
    раскладка = {"artboards": [], "launch": {"view": "canvas"}}
    обложек = 0
    for имя, заголовок, _ in доски:
        if имя.startswith("Oblozhka"):
            обложек += 1
            x, y = (обложек - 1) * 1180, 1700
        else:
            i = len([а for а in раскладка["artboards"] if not а["file"].startswith("Oblozhka")])
            x, y = i * 1180, 0
        раскладка["artboards"].append({"file": имя, "title": заголовок, "x": x, "y": y, "w": W, "h": H})
    нет_снимков = sorted({с["снимок"] for к in пост["кадры"] for с in к["строки"]} - ЕСТЬ)
    хвост = (f" Снимков ещё нет ({len(нет_снимков)} из 15), на их месте заглушки с буквой — "
             "вид кадра они не меняют." if нет_снимков else "")
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{пост['название']}: {всего} кадров карусели сверху, запасные обложки снизу.{хвост} "
        "Двигайте и правьте прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = помощник()
    страница = папка / f"{стиль.латиницей(файл.stem)}.html"
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"), "--out", str(страница),
               "--title", пост["название"], "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    for к in картинки(пост, папка):
        команда += ["--image", str(к)]
    вывод = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)], capture_output=True, text=True)
    print((вывод.stderr.strip() + "\n") if вывод.stderr.strip() else "", end="")
    print(проверка.stdout.strip()[:300], проверка.stderr.strip()[:300])
    if нет_снимков:
        print("нет снимков, стоят заглушки:", " ".join(нет_снимков))
    print("страница холста:", страница, f"{страница.stat().st_size // 1024} КБ")


if __name__ == "__main__":
    main()
