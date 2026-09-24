# -*- coding: utf-8 -*-
"""Стиль «окно»: белое окно приложения на тёмном фоне. python3 холст.py посты/<пост>.json

Снят с 7 кадров @mike.mozg «Агент HERMES» (кадры — `референс/`, разбор — `референс/паспорт.md`,
числа — `ДНК.md`). Устройство: окно macOS на 81,6% высоты доски лежит на графитовом
текстурированном фоне (фон виден рамкой ~5,5%), под окном отдельная пилюля-колонтитул
с логотипом слева и нумерацией «N / 7» справа. Внутри окна — заголовок в одну строку,
абзац, ровно одна акцентная фраза и прямоугольник с доказательством.

⛔️ Окно рисуется вёрсткой, а не вставляется снимком (решение владельца 19.09.2026).
Снимок настоящего экрана в плитке ленты ~300 px превращается в кашу — ровно на этом сгорели
схемы у автора оригинала. У нарисованного окна кегли и контраст под полным контролем,
и в кадр не попадут ни ключи, ни личные пути, ни названия внутренних заметок.
Тот же приём у «нативного-экрана»: там вёрсткой нарисован экран телефона с клавиатурой.

Закон стиля, который даёт оригиналу контраст 17,9:1: **текст никогда не лежит на картинке**.
Доказательство живёт в своём прямоугольнике и под буквы не заходит.

Доски холста 1080×1440; дальше как у «сервисов»: Artifact → «готово» → `../выпуск.py`.
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
# Красный автора `#F5372B` не переносим ни в одной роли: у нас олива, лайм, графит.
ГРАФИТ, ОЛИВА, ЛАЙМ = "#121310", "#56690C", стиль.ЛАЙМ
ОКНО_СВЕТ, ОКНО_НОЧЬ = "#FFFFFF", "#1E1F1C"
ЧЕРНИЛА, МЯГКИЙ = "#14150F", "#5B5F53"              # текст и приглушённый текст на белом
НОЧЬ_ТЕКСТ, НОЧЬ_МЯГКИЙ = "#F1F2EA", "#9DA291"      # то же на графитовом окне
ПРОБА_СВЕТ, ПРОБА_НОЧЬ = "#F3F4EC", "#15170F"       # подложка прямоугольника-доказательства

# ── Геометрия доски 1080×1440 (пересчёт паспорта с 1620×2160 делением на 1,5) ──
ПОЛЕ, ВЕРХ = 60, 72                 # боковое и верхнее поле кадра
ОКНО_В = 1175                       # высота окна — 81,6% доски
ЗАЗОР, ПИЛЮЛЯ_В = 30, 78            # окно ↔ колонтитул и высота колонтитула
РАДИУС, ШАПКА, ВНУТР = 38, 90, 45   # скругление окна, высота шапки, внутреннее поле окна
ШИР = 1080 - 2 * ПОЛЕ - 2 * ВНУТР   # 870 — рабочая ширина строки внутри окна

К = "font-family: Oswald, 'Arial Narrow', sans-serif; font-weight: 600"
Т = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif"
М = "font-family: JetBrains, 'SF Mono', Menlo, monospace"

# Зерно — адрес без кавычек и процент-кодирован: двойные кавычки внутри style рвут атрибут,
# и разметка вываливается текстом в кадр (ловушка из `ПУБЛИКАЦИЯ.md`, поймана 18.09).
ЗЕРНО = ("background-image: url(data:image/svg+xml;utf8,"
         "%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%27200%27%20height%3D%27200%27%3E"
         "%3Cfilter%20id%3D%27n%27%3E%3CfeTurbulence%20type%3D%27fractalNoise%27%20baseFrequency%3D%27.85%27"
         "%20numOctaves%3D%272%27/%3E%3C/filter%3E%3Crect%20width%3D%27200%27%20height%3D%27200%27"
         "%20filter%3D%27url%28%23n%29%27/%3E%3C/svg%3E);"
         " opacity: .07; mix-blend-mode: screen;")
# Фон кадра — не заливка, а текстура: вертикальные потёртости и подсвет к правому верху,
# как у автора. Без неё графит выглядит пустой плашкой, и окно на нём не «лежит».
ПОДЛОЖКА = ('<div style="position: absolute; inset: 0; background:'
            ' radial-gradient(130% 80% at 96% 8%, rgba(255,255,255,.11) 0%, rgba(255,255,255,0) 58%),'
            ' linear-gradient(180deg, #181A11 0%, #0E0F0A 100%);"></div>'
            '<div style="position: absolute; inset: 0; background-image: repeating-linear-gradient(90deg,'
            ' rgba(255,255,255,.035) 0px, rgba(255,255,255,.035) 1px, rgba(255,255,255,0) 1px,'
            ' rgba(255,255,255,0) 7px);"></div>'
            f'<div style="position: absolute; inset: 0; {ЗЕРНО}"></div>')


def _дп():
    import importlib.util
    спека = importlib.util.spec_from_file_location("холст_до_после", ТУТ.parent / "до-после" / "холст.py")
    м = importlib.util.module_from_spec(спека)
    sys.modules["холст_до_после"] = м
    спека.loader.exec_module(м)
    return м


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            "</head>\n<body>\n<x-dc>\n  <style>\n"
            + стиль.фейсы(("Oswald", "oswald-600", 600), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700), ("JetBrains", "jetbrains-400", 400),
                          ("JetBrains", "jetbrains-700", 700))
            + f"\n    body {{ margin: 0; background: {ГРАФИТ}; }}\n  </style>\n")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


# ── Кегль заголовка: строка одна, значит кегль считается по ширине ───────────
# Ширины сняты в браузере (canvas.measureText, Oswald 600, кегль 100 px) с наших же
# заголовков: «КОМАНДА ПОМОЩНИКОВ» = 10,63 em, «ЧИНИТ БАГИ САМ» = 7,18 em и так далее.
# Таблица подобрана под эти замеры, наибольшая ошибка ≈4% — её закрывает ЗАПАС_ШИРИНЫ.
_ШИРИНЫ = {" ": .25, "О": .62, "К": .60, "М": .70, "Ш": .70, "Ю": .70, "Ж": .70, "Ф": .70,
           "Ы": .70, "Щ": .80, "Г": .42, "Е": .42, "Ё": .42, "Т": .42,
           "L": .45, "E": .45, "C": .55, "I": .30, "J": .45}
_ПО_УМОЛЧАНИЮ, ЗАПАС_ШИРИНЫ = .58, .96


def ширина_капса(текст: str) -> float:
    """Ширина строки капсом в em при кегле 1."""
    return sum(_ШИРИНЫ.get(з, _ПО_УМОЛЧАНИЮ) for з in текст.upper())


def кегль_в_строку(текст: str, ширина: int = ШИР, потолок: int = 132) -> int:
    """Самый крупный кегль, при котором заголовок ещё умещается в одну строку.

    Потолок 132 px = 200 px в пересчёте на кадр 1620 — нижняя граница, назначенная сценарием.
    Выше поднимать нельзя: у 18-значных заголовков одна строка физически не бывает крупнее
    (870 px колонки на 18 знаков — это 48 px на знак).
    """
    return min(потолок, int(ширина * ЗАПАС_ШИРИНЫ / ширина_капса(текст)))


# ── Кирпичи окна ─────────────────────────────────────────────────────────────
def светофор() -> str:
    """Три кружка справа в шапке. Родные цвета macOS — почерк Apple, поэтому свои:
    графит, крем, лайм. Оливы среди кружков нет нарочно: шапка сама оливковая,
    оливковый кружок на ней не виден."""
    кружки = "".join(
        f'<span style="width: 25px; height: 25px; border-radius: 50%; background: {ц};'
        f' box-shadow: inset 0 -2px 4px rgba(0,0,0,.18);"></span>'
        for ц in ("#22241E", "#F1F2EA", ЛАЙМ))
    return (f'<div style="position: absolute; right: {ВНУТР}px; top: 0; height: {ШАПКА}px;'
            f' display: flex; align-items: center; gap: 16px;">{кружки}</div>')


def шапка_окна(подсказка: str = "") -> str:
    """Оливковая шапка: она же главный носитель акцента (90×960 = 5,6% доски).
    Подсказка слева на финале снимается — листать некуда, деталь автора."""
    текст = ("" if not подсказка else
             f'<div style="position: absolute; left: {ВНУТР}px; top: 0; height: {ШАПКА}px;'
             f' display: flex; align-items: center; {Т}; font-size: 26px; color: #FFFFFF;">{подсказка}</div>')
    return (f'<div style="position: absolute; left: 0; right: 0; top: 0; height: {ШАПКА}px;'
            f' border-radius: {РАДИУС}px {РАДИУС}px 0 0; background: {ОЛИВА};">{текст}{светофор()}</div>')


def окно(нутро: str, ночь: bool = False, подсказка: str = "смотри дальше",
         верх: int = ВЕРХ, высота: int = ОКНО_В) -> str:
    """Скруглённое окно на тёмном фоне. Обводки у окна нет — оно отделяется светлотой;
    ночному добавлена волосяная кромка, иначе графит на графите пропадает."""
    кромка = ("box-shadow: 0 0 0 1px rgba(255,255,255,.10), 0 30px 70px rgba(0,0,0,.55);" if ночь
              else "box-shadow: 0 30px 70px rgba(0,0,0,.45);")
    return (f'  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: {верх}px;'
            f' height: {высота}px; overflow: hidden; border-radius: {РАДИУС}px;'
            f' background: {ОКНО_НОЧЬ if ночь else ОКНО_СВЕТ}; {кромка}">'
            f'{шапка_окна(подсказка)}{нутро}</div>')


def колонтитул(номер: int, всего: int) -> str:
    """Пилюля под окном: логотип слева, «N / 7» справа. Нумерация вынесена из содержимого —
    внутри окна ничто не спорит с текстом. Цифра сидит в лаймовой плашке (добор акцента)."""
    верх = ВЕРХ + ОКНО_В + ЗАЗОР
    return (f'  <div style="position: absolute; left: {ПОЛЕ}px; right: {ПОЛЕ}px; top: {верх}px;'
            f' height: {ПИЛЮЛЯ_В}px; border-radius: {ПИЛЮЛЯ_В // 2}px; background: #FFFFFF;'
            f' display: flex; align-items: center; justify-content: space-between;'
            f' padding: 0 34px 0 40px; box-sizing: border-box;'
            f' box-shadow: 0 10px 26px rgba(0,0,0,.35);">'
            f'<img src="logo.png" style="height: 32px; filter: brightness(.45) saturate(1.4);">'
            f'<div style="display: flex; align-items: center; gap: 12px; {Т}; font-weight: 700;'
            f' font-size: 30px; color: {МЯГКИЙ};">'
            f'<span style="display: inline-flex; align-items: center; justify-content: center;'
            f' min-width: 54px; height: 46px; padding: 0 12px; border-radius: 13px; background: {ЛАЙМ};'
            f' color: {ЧЕРНИЛА};">{номер:02d}</span>/ {всего}</div></div>')


def полоса(доля: float) -> str:
    """Лаймовая полоса по нижнему краю доски — наш знак прогресса; логотип есть на каждой
    доске (в колонтитуле у кадров, слева внизу у обложек), полоса — на всех без исключения."""
    return (f'  <div style="position: absolute; left: 0; bottom: 0; height: 6px;'
            f' width: {доля * 100:.1f}%; background: {ЛАЙМ};"></div>')


def знак_слева() -> str:
    """Логотип обложек: у них нет колонтитула, знак встаёт внизу слева."""
    return '  <img src="logo.png" style="position: absolute; left: 72px; bottom: 54px; height: 40px;">'


# ── Текст внутри окна ────────────────────────────────────────────────────────
def заголовок(текст: str, ночь: bool, кегль: int | None = None) -> str:
    кегль = кегль or кегль_в_строку(текст)
    цвет = НОЧЬ_ТЕКСТ if ночь else ЧЕРНИЛА
    return (f'<div style="{К}; font-size: {кегль}px; line-height: 1.0; letter-spacing: .005em;'
            f' white-space: nowrap; color: {цвет};">{текст}</div>')


def абзац(текст: str, ночь: bool, кегль: int = 40) -> str:
    цвет = НОЧЬ_ТЕКСТ if ночь else "#1E2018"
    return (f'<div style="{Т}; font-size: {кегль}px; line-height: 1.34; color: {цвет};">{текст}</div>')


def акцент(текст: str, ночь: bool, кегль: int = 40) -> str:
    """Ровно одна смысловая фраза на кадр. На светлом — олива буквами с лаймовой подчёркой;
    на ночном — лайм буквами. Лайм текстом по светлому не ставим (правило из памяти),
    поэтому на белом он идёт только полоской под строками."""
    if ночь:
        оформление = f"color: {ЛАЙМ};"
    else:
        оформление = (f"color: {ОЛИВА}; background: linear-gradient(transparent 88%, {ЛАЙМ} 88%,"
                      f" {ЛАЙМ} 96%, transparent 96%); -webkit-box-decoration-break: clone;"
                      " box-decoration-break: clone;")
    return (f'<div style="{Т}; font-weight: 700; font-size: {кегль}px; line-height: 1.34;">'
            f'<span style="{оформление}">{текст}</span></div>')


# ── Доказательство: прямоугольник в нижней части окна ────────────────────────
def доказательство(нутро: str, высота: int, ночь: bool, поля: int = 26) -> str:
    """Своя подложка, оливковая рамка 2 px, прижат к низу окна. Текст кадра сюда не заходит —
    это и есть закон, который даёт оригиналу 17,9:1."""
    return (f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px; bottom: {ВНУТР}px;'
            f' height: {высота}px; box-sizing: border-box; overflow: hidden; border-radius: 14px;'
            f' border: 2px solid {ОЛИВА}; background: {ПРОБА_НОЧЬ if ночь else ПРОБА_СВЕТ};'
            f' padding: {поля}px;">{нутро}</div>')


def диалог(строки: list[dict], ночь: bool) -> str:
    """Кадр 02: просьба человеческим языком и ответ. Реплики — пузырями, как в переписке."""
    куски = []
    for с in строки:
        свой = с.get("кто") == "ты"
        фон = (ЧЕРНИЛА if not ночь else "#2C2F26") if свой else ("#FFFFFF" if not ночь else "#24261F")
        цвет = ("#F1F2EA" if свой else ЧЕРНИЛА) if not ночь else НОЧЬ_ТЕКСТ
        куски.append(
            f'<div style="display: flex; justify-content: {"flex-end" if свой else "flex-start"};">'
            f'<div style="max-width: 78%; border-radius: 18px; padding: 16px 22px; background: {фон};'
            f' {М}; font-size: 28px; line-height: 1.3; color: {цвет};'
            f' box-shadow: 0 3px 10px rgba(0,0,0,{".12" if not ночь else ".35"});">{с["текст"]}</div></div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 16px;">{"".join(куски)}</div>')


def файл(ф: dict, ночь: bool) -> str:
    """Кадр 03: вопрос обычными словами и найденный файл с подсветкой одной строки."""
    вопрос = (f'<div style="{Т}; font-size: 28px; color: {НОЧЬ_МЯГКИЙ if ночь else МЯГКИЙ};'
              f' margin-bottom: 18px;">{ф["вопрос"]}</div>')
    имя = (f'<div style="display: flex; align-items: center; gap: 12px; {М}; font-weight: 700;'
           f' font-size: 26px; color: {ОЛИВА}; margin-bottom: 12px;">'
           f'<span style="width: 14px; height: 18px; border-radius: 3px; background: {ОЛИВА};'
           f' display: inline-block;"></span>{ф["имя"]}</div>')
    строки = ""
    for н, с in enumerate(ф["строки"], ф.get("с_номера", 11)):
        найдена = н == ф["найдена"]
        подсветка = (f'background: {ЛАЙМ}; border-radius: 6px;' if найдена and not ночь else
                     f'background: rgba(199,226,75,.22); border-radius: 6px;' if найдена else "")
        цвет = (ЧЕРНИЛА if найдена else "#3A3E33") if not ночь else (ЛАЙМ if найдена else НОЧЬ_ТЕКСТ)
        строки += (f'<div style="display: flex; gap: 18px; padding: 3px 8px; {подсветка}">'
                   f'<span style="{М}; font-size: 26px; color: {НОЧЬ_МЯГКИЙ if ночь else "#9A9E90"};'
                   f' width: 34px; text-align: right;">{н}</span>'
                   f'<span style="{М}; font-size: 26px; white-space: pre; color: {цвет};">{с}</span></div>')
    return вопрос + имя + строки


def проверки(п: dict, ночь: bool) -> str:
    """Кадр 04: список готовых проверок с галочками. По-русски, крупно, читаемо в ленте."""
    шапка = (f'<div style="{М}; font-size: 26px; color: {НОЧЬ_МЯГКИЙ if ночь else МЯГКИЙ};'
             f' margin-bottom: 16px;">{п["шапка"]}</div>')
    строки = ""
    for с in п["пункты"]:
        строки += (f'<div style="display: flex; align-items: center; gap: 18px; margin-bottom: 12px;">'
                   f'<span style="flex: none; width: 30px; height: 30px; border-radius: 9px;'
                   f' background: {ЛАЙМ}; color: {ЧЕРНИЛА}; {Т}; font-weight: 700; font-size: 22px;'
                   f' display: flex; align-items: center; justify-content: center;">✓</span>'
                   f'<span style="{Т}; font-size: 32px; color: {НОЧЬ_ТЕКСТ if ночь else ЧЕРНИЛА};">{с}</span>'
                   f'</div>')
    return шапка + строки


def схема(блоки: list[str], ночь: bool) -> str:
    """Кадр 05 — единственная схема в карусели: 4 блока в ряд, подписи 28 px (это 42 px
    в пересчёте на 1620, при пороге 40). У автора схем было пять, подписи по 10 px."""
    ячейки = ""
    for н, б in enumerate(блоки, 1):
        ячейки += (f'<div style="flex: 1; display: flex; flex-direction: column; align-items: center;'
                   f' gap: 12px; border-radius: 12px; padding: 14px 8px;'
                   f' background: {"rgba(255,255,255,.05)" if ночь else "#FFFFFF"};'
                   f' box-shadow: 0 2px 8px rgba(0,0,0,{".10" if not ночь else ".30"});">'
                   f'<span style="width: 38px; height: 38px; border-radius: 50%; background: {ЛАЙМ};'
                   f' color: {ЧЕРНИЛА}; {Т}; font-weight: 700; font-size: 24px; display: flex;'
                   f' align-items: center; justify-content: center;">{н}</span>'
                   f'<span style="{Т}; font-weight: 700; font-size: 28px; line-height: 1.16;'
                   f' text-align: center; color: {НОЧЬ_ТЕКСТ if ночь else ЧЕРНИЛА};">{б}</span></div>')
    return (f'<div style="display: flex; align-items: stretch; gap: 14px; height: 100%;">{ячейки}</div>')


def заметки(з: dict, ночь: bool) -> str:
    """Кадр 06: папка заметок памяти — список названий по-русски, нарисованный, не снятый."""
    шапка = (f'<div style="display: flex; align-items: center; gap: 12px; {М}; font-weight: 700;'
             f' font-size: 26px; color: {ЛАЙМ if ночь else ОЛИВА}; margin-bottom: 16px;">'
             f'<span style="width: 22px; height: 16px; border-radius: 4px; background: currentColor;'
             f' display: inline-block;"></span>{з["папка"]}</div>')
    строки = ""
    for с in з["имена"]:
        строки += (f'<div style="display: flex; align-items: center; gap: 16px; padding: 5px 0;">'
                   f'<span style="flex: none; width: 8px; height: 8px; border-radius: 50%;'
                   f' background: {НОЧЬ_МЯГКИЙ if ночь else "#9A9E90"};"></span>'
                   f'<span style="{М}; font-size: 27px; color: {НОЧЬ_ТЕКСТ if ночь else "#2B2E26"};">'
                   f'{с}</span></div>')
    return шапка + строки


ДОКАЗАТЕЛЬСТВА = {"диалог": диалог, "файл": файл, "проверки": проверки,
                  "схема": схема, "заметки": заметки}


# ── Кадры ────────────────────────────────────────────────────────────────────
def кадр(к: dict, номер: int, всего: int) -> str:
    ночь = к.get("ночь", False)
    кегль_абзаца = к.get("абзац_кегль", 40)
    части = [заголовок(к["заголовок"], ночь, к.get("кегль"))]
    # У автора на кадре 04 акцент стоит над абзацем — деталь берём.
    if к.get("акцент_сверху"):
        части.append(акцент(к["акцент"], ночь))
        части += [абзац(а, ночь, кегль_абзаца) for а in к.get("абзацы", [])]
    else:
        абзацы = list(к.get("абзацы", []))
        if абзацы:
            части.append(абзац(абзацы[0], ночь, кегль_абзаца))
        части.append(акцент(к["акцент"], ночь))
        части += [абзац(а, ночь, кегль_абзаца) for а in абзацы[1:]]
    текст = (f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px;'
             f' top: {ШАПКА + 40}px; display: flex; flex-direction: column; gap: 40px;">'
             f'{"".join(части)}</div>')
    вид = к["доказательство"]
    нутро = ДОКАЗАТЕЛЬСТВА[вид["вид"]](вид["данные"], ночь)
    проба = доказательство(нутро, вид["высота"], ночь, вид.get("поля", 26))
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРАФИТ};">
  {ПОДЛОЖКА}
{окно(текст + проба, ночь)}
{колонтитул(номер, всего)}
{полоса(номер / всего)}
</div>""" + ХВОСТ


def телефон() -> str:
    """Финал: телефон под наклоном с экраном нашего канала — нарисован вёрсткой, как и окно.
    Число подписчиков не показываем (решение паспорта), адрес канала не выдумываем."""
    плитки = "".join(
        f'<div style="background: {ц}; border-radius: 4px;"></div>'
        for ц in ("#2B2E26", ЛАЙМ, "#43483B", "#5C6450", "#2B2E26", ОЛИВА))
    кнопки = "".join(
        f'<div style="flex: 1; height: 44px; border-radius: 12px; background: #E7E9DF;"></div>'
        for _ in range(4))
    return f"""<div style="position: absolute; left: 62px; bottom: -30px; width: 330px; height: 660px;
       transform: rotate(-8deg); transform-origin: bottom left; border-radius: 42px; padding: 12px;
       box-sizing: border-box; background: #2A2C25; box-shadow: 0 28px 60px rgba(0,0,0,.30);">
    <div style="position: relative; width: 100%; height: 100%; overflow: hidden; border-radius: 32px; background: #F7F8F3;">
      <div style="display: flex; justify-content: space-between; padding: 14px 24px 0; {Т}; font-size: 18px; color: #6E7269;">
        <span>9:41</span><span>▮▮▮</span>
      </div>
      <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 14px 0 0;">
        <img src="kot-profil.webp" style="width: 96px; height: 96px; border-radius: 50%; object-fit: cover; background: #E7E9DF;">
        <div style="{Т}; font-weight: 700; font-size: 26px; color: {ЧЕРНИЛА};">4xTube</div>
        <div style="{Т}; font-size: 19px; color: #7E8278;">разборы и находки</div>
      </div>
      <div style="display: flex; gap: 10px; padding: 16px 20px 0;">{кнопки}</div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; padding: 18px 20px 0; height: 240px;">{плитки}</div>
    </div>
  </div>"""


# Рисованная стрелка-дуга от текста к телефону — приём автора; у него красная, у нас лаймовая.
СТРЕЛКА = f"""<svg viewBox="0 0 300 200" style="position: absolute; left: 430px; top: 830px; width: 300px; height: 200px;" fill="none">
    <path d="M272 14C266 86 202 146 78 172" stroke="{ЛАЙМ}" stroke-width="9" stroke-linecap="round"/>
    <path d="M116 146L72 174L112 196" stroke="{ЛАЙМ}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>"""


def финал(ф: dict, всего: int) -> str:
    """Окно без подсказки в шапке — листать некуда, аккуратная деталь автора.
    Нарастание в одной фразе: обычное → полужирное → акцентное."""
    строки = ""
    for с in ф["заголовок"]:
        # Подсветка — на span, а не на блоке: у блока она тянется во всю ширину окна,
        # и полоса торчит за словами (поймано отрисовкой 19.09).
        вид = {"обычное": f"font-weight: 400; color: {ЧЕРНИЛА};",
               "полужирное": f"font-weight: 700; color: {ЧЕРНИЛА};",
               "акцентное": (f"font-weight: 700; color: {ОЛИВА};"
                             f" background: linear-gradient(transparent 86%, {ЛАЙМ} 86%, {ЛАЙМ} 96%,"
                             " transparent 96%);")}[с["вид"]]
        строки += (f'<div style="{Т}; font-size: 66px; line-height: 1.14;">'
                   f'<span style="{вид}">{с["текст"]}</span></div>')
    нутро = (f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px; top: {ШАПКА + 40}px;">'
             f'{строки}</div>'
             f'{телефон()}'
             f'{СТРЕЛКА}'
             f'<div style="position: absolute; left: 420px; right: {ВНУТР}px; top: 545px; {Т};'
             f' font-size: 36px; line-height: 1.3; color: {МЯГКИЙ};">{ф["серым"]}</div>'
             f'<div style="position: absolute; left: 420px; right: {ВНУТР}px; top: 685px; {Т};'
             f' font-weight: 700; font-size: 40px; line-height: 1.24; color: {ОЛИВА};">'
             f'<span style="background: linear-gradient(transparent 86%, {ЛАЙМ} 86%, {ЛАЙМ} 96%,'
             f' transparent 96%); -webkit-box-decoration-break: clone;">{ф["акцент"]}</span></div>')
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРАФИТ};">
  {ПОДЛОЖКА}
{окно(нутро, ночь=False, подсказка="")}
{колонтитул(всего, всего)}
{полоса(1.0)}
</div>""" + ХВОСТ


# ── Три обложки ──────────────────────────────────────────────────────────────
def обложка_обещание(о: dict, доля: float) -> str:
    """A — «Обещание и кот»: выгода словами, в лоб. Белый по графиту ≈15,8:1,
    ни одной тонкой строки, цветного текста по светлому нет вовсе."""
    кегль = min(128, кегль_в_строку(max(о["крупно"], key=ширина_капса), 936, 200))
    строки = ""
    for с in о["крупно"]:
        части = ""
        for слово in с.split(" "):
            if слово == о.get("на_плашке"):
                # Плашка — inline-block с собственной высотой, а не фон строчного
                # элемента. У строчного фон рисуется по content-area шрифта, она
                # выше межстрочного интервала 1.02 — и лаймовый прямоугольник
                # свисал на строку ниже, накрывая верх букв (поймано владельцем
                # 19.09.2026). Здесь высота задана явно и в строку укладывается.
                # Высота 1.1 кегля, а не 0.98: у «Д», «Ц», «Щ» есть подстрочные
                # ножки, и плашка впритык по кеглю их срезала. Строка при этом
                # разрежена до 1.16, иначе плашка упирается в буквы снизу.
                части += (f'<span style="display: inline-block; background: {ЛАЙМ};'
                          f' color: {ЧЕРНИЛА}; border-radius: 10px; padding: 0 14px;'
                          f' margin-right: 6px; line-height: {int(кегль * 1.06)}px;'
                          f' height: {int(кегль * 1.1)}px; vertical-align: top;">{слово}</span>')
            else:
                части += слово + " "
        строки += (f'<div style="{К}; font-size: {кегль}px; line-height: {int(кегль * 1.16)}px;'
                   f' white-space: nowrap; color: #FFFFFF;">{части.strip()}</div>')
    # Надстрочника-визитки здесь больше нет: по замеру OpusClip (34 635 клипов)
    # представление и «а вы задумывались» — стабильные аутсайдеры среди крючков,
    # а медиана прорывных обложек — пять слов на всю обложку (vidIQ, 500 штук).
    # Имя инструмента ушло внутрь карусели, на обложке стоит результат.
    # Кот поднят с 700 до 880 px: в нише, забитой скриншотами интерфейсов, он и
    # есть то, чего нет у соседей по ленте — актив, а не украшение в углу.
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРАФИТ};">
  {ПОДЛОЖКА}
  <img src="kot-{стиль.латиницей(о['кот'])}.webp" style="position: absolute; right: -60px; bottom: 0; height: 880px;">
  <div style="position: absolute; left: 72px; top: 190px;">{строки}</div>
  <div style="position: absolute; left: 72px; right: 430px; top: {190 + len(о['крупно']) * int(кегль * 1.02) + 46}px; {Т}; font-weight: 700; font-size: 40px; line-height: 1.25; color: #C3C7B8;">{о['под']}</div>
{знак_слева()}
{полоса(доля)}
</div>""" + ХВОСТ


def обложка_окно(о: dict, доля: float) -> str:
    """B — «Окно вместо рассказа»: обложка сделана из самого продукта, кота нет.
    Окно тёмное и почти во весь кадр, внутри одна набранная строка очень крупным моношрифтом."""
    # Моношрифт ровно 0,6 em на знак (замерено). Показываем пару «попросил →
    # сделано»: одна команда в окне была подводкой, а обложка должна нести
    # результат (OpusClip, 34 635 клипов: показ результата — лучший из пяти
    # замеренных крючков). Просьба набрана мелко и приглушённо, результат —
    # крупно и лаймом: в ленте из двух строк читается именно вторая.
    ширина_строки = 1000 - 2 * ВНУТР
    кегль = int(ширина_строки * 0.95 / ((len(о["строка"]) + 3) * 0.6))
    просьба = о.get("просьба", "")
    кегль_просьбы = min(52, int(ширина_строки * 0.95 / ((len(просьба) + 3) * 0.6))) if просьба else 0
    нутро = (
        (f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px; top: 330px; {М};'
         f' font-size: {кегль_просьбы}px; line-height: 1.34; color: #7F857A;">'
         f'<span style="color: #7F857A;">$ </span>{просьба}</div>' if просьба else "")
        + f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px; top: 470px; {М};'
          f' font-size: {кегль}px; line-height: 1.24; color: {ЛАЙМ};">'
          f'<span style="color: {НОЧЬ_ТЕКСТ};">✓ </span>{о["строка"]}</div>'
             f'<div style="position: absolute; left: {ВНУТР}px; right: {ВНУТР}px; bottom: 330px; {Т};'
             f' font-weight: 700; font-size: 52px; line-height: 1.24; color: #FFFFFF;">{о["внизу"]}</div>'
             f'<img src="logo.png" style="position: absolute; left: {ВНУТР}px; bottom: 70px; height: 44px;">')
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРАФИТ};">
  {ПОДЛОЖКА}
  <div style="position: absolute; left: 40px; right: 40px; top: 40px; height: 1360px; overflow: hidden;
       border-radius: {РАДИУС}px; background: {ОКНО_НОЧЬ};
       box-shadow: 0 0 0 1px rgba(255,255,255,.12), 0 30px 70px rgba(0,0,0,.55);">
    {шапка_окна()}
    {нутро}
  </div>
{полоса(доля)}
</div>""" + ХВОСТ


def обложка_оглавление(о: dict, доля: float) -> str:
    """В — «Оглавление из пяти»: зритель видит все пять выгод ещё в ленте.
    Композиция вертикальная и центрированная — ни одной черты от A."""
    пилюли = "".join(
        f'<div style="background: {ЛАЙМ}; color: {ЧЕРНИЛА}; border-radius: 999px; padding: 18px 44px;'
        f' {Т}; font-weight: 700; font-size: 40px;">{п}</div>' for п in о["пилюли"])
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРАФИТ};">
  {ПОДЛОЖКА}
  <img src="kot-{стиль.латиницей(о['кот'])}.webp" style="position: absolute; right: -40px; bottom: 0; height: 400px; z-index: 0;">
  <div style="position: absolute; left: 0; right: 0; top: 170px; text-align: center; {К}; font-size: {кегль_в_строку(о['крупно'], 900, 140)}px; line-height: 1.0; color: #FFFFFF;">{о['крупно']}</div>
  <div style="position: absolute; left: 90px; right: 90px; top: 430px; display: flex; flex-direction: column; align-items: center; gap: 28px; z-index: 1;">{пилюли}</div>
{знак_слева()}
{полоса(доля)}
</div>""" + ХВОСТ


# ── Сборка ───────────────────────────────────────────────────────────────────
def картинки(пост: dict, папка: Path) -> list[Path]:
    """Кот и логотип — отдельными файлами: вшитая в доску поза перерастает предел помощника
    в 2 МБ, и доска молча не собирается. Имена только латиницей."""
    файлы = []
    позы = {пост["обложка"]["кот"], пост["обложка_оглавление"]["кот"]}
    for поза in sorted(позы):
        цель = папка / f"kot-{стиль.латиницей(поза)}.webp"
        with Image.open(стиль.ПОЗЫ / f"{поза}.png") as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((900, 1200), Image.LANCZOS)
            и.save(цель, quality=84, method=6)
        файлы.append(цель)
    # Аватар канала на финале — морда кота квадратом.
    with Image.open(стиль.ПОЗЫ / f'{пост["финал"]["аватар"]}.png') as и:
        и = и.convert("RGBA")
        и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
        ш, в = и.size
        и = и.crop((0, 0, ш, min(в, ш)))
        и.thumbnail((240, 240), Image.LANCZOS)
        и.save(папка / "kot-profil.webp", quality=84, method=6)
    файлы.append(папка / "kot-profil.webp")
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def main():
    дп = _дп()
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: правило владельца, холст без них не выкладывается.
    обложки = {"обещание": lambda: обложка_обещание(пост["обложка"], 1 / всего),
               "окно": lambda: обложка_окно(пост["обложка_окно"], 1 / всего),
               "оглавление": lambda: обложка_оглавление(пост["обложка_оглавление"], 1 / всего)}
    главная = пост.get("главная", "обещание")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['заголовок']}", кадр(к, н, всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"], всего)))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600, "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)], "launch": {"view": "canvas"}}
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{пост['название']}: окно приложения нарисовано вёрсткой, не снимком. "
        "Двигайте и правьте прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    # Картинки кладутся рядом с досками ДО помощника: доски ссылаются на них по
    # имени файла, и если помощника на диске нет, падение уносило их с собой —
    # доски оставались со ссылками в пустоту (та же правка сделана в «справочнике»).
    рядом = картинки(пост, папка)

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
