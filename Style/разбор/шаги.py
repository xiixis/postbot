# -*- coding: utf-8 -*-
"""Стиль «разбор», вид «шаги»: python шаги.py посты/<пост>.json [--без-снимка]

Вариация «разбора» (`ВАРИАЦИИ.md`), снята с референса №25 «Проекты в Claude» (Instagram
DT9isTujEtD, паспорт — `референс-проекты/паспорт.md`). Повторено: светлый лист, постер-обложка
с героем по центру, «секретная функция» крупным словом, три шага с окнами интерфейса, обводкой
и стрелкой «куда нажать», кадр-схема двух структур постов зигзагом, кадр-доказательство из
обложек, финал. Наше: лайм-маркер вместо терракоты (3,6:1 у автора), окна Claude вёрсткой
(`окна_claude.py`), наши обложки на доказательстве, кот на обложках и в финале, знак канала.

Доска 1080×1440: всё важное выше 1105, знак в полосе 1191..1235, правее 900 в полосе 720–1190
текста нет (кнопки TikTok). Собирает правимый холст `холсты/<пост>/project/` (`../дизайн_холст.py`)
и печатает приёмку досок; после «готово» — `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402
import обложки  # noqa: E402
import окна_claude as ок  # noqa: E402

ЛАЙМ, ОЛИВА, ГРАФ = стиль.ЛАЙМ, стиль.ОЛИВА, стиль.ТЁМНЫЙ
ЧЕРН, ВТОР = "#12130E", "#1E1F17"
ЛИСТ = "#FBFAF6"                     # тёплый почти белый, как лист автора (#FCFCFB)
ФОН = f"background: radial-gradient(70% 45% at 100% 0%, rgba(199,226,75,.14), rgba(199,226,75,0) 70%), {ЛИСТ};"
ТЕНЬ = "0 2px 4px rgba(20,20,19,.05), 0 18px 44px rgba(20,20,19,.12)"
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CLAUDE = дх.CLAUDE
ПРИГЛУШИТЬ = обложки.ПРИГЛУШИТЬ
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
                        ("Cormorant", "cormorant-700", 700))
ЗНАЧКИ = {п.stem.removesuffix("-fill"): п.read_text(encoding="utf-8") for п in (ТУТ / "значки").glob("*-fill.svg")}

ТЕМА = обложки.Тема(грунт=ЛИСТ, тёмная=False, чернила=ЧЕРН, второй=ВТОР, тихий="#3A3A33",
                    карточка="#FFFFFF", карточка_тихая="rgba(255,255,255,.72)", рамка="rgba(18,19,14,.14)",
                    тень=ТЕНЬ, стрелка=ОЛИВА, крупный=КРУП, текст=ТЕКСТ, логотип=ПРИГЛУШИТЬ)


def значок(имя: str, цвет: str, размер: int) -> str:
    return ок._иконка(ЗНАЧКИ[имя], цвет, размер)


def маркер(текст: str) -> str:
    return дх.маркер(текст, чернила=ЧЕРН)


def claude(текст: str) -> str:
    return текст.replace("Claude", f'<span style="color: {CLAUDE};">Claude</span>')


def низ() -> str:
    return f'<img src="logo.png" style="position: absolute; left: 80px; top: {дх.ЗНАК_ВЕРХ}px; height: 44px; {ПРИГЛУШИТЬ}">'


def подложка() -> str:
    return f'<div style="position: absolute; inset: 0; {ФОН} pointer-events: none;"></div>'


def шапка(номер: str, заголовок: str, кегль: int = 92) -> str:
    """«Шаг N.» лаймовой капсулой и заголовок шага под ней — как «Шаг 1. Создай Проект» у автора."""
    return (f'<div style="position: absolute; left: 80px; top: 64px; {КРУП} font-size: 60px; line-height: 1;">{маркер(номер)}</div>'
            f'<div style="position: absolute; left: 80px; top: 156px; width: 920px; {КРУП} font-size: {кегль}px; '
            f'line-height: 1.0; color: {ЧЕРН};">{заголовок}</div>')


def столбик(top: int, блоки: list[str], gap: int = 20, width: int = 920) -> str:
    """Текст под картинкой одной колонкой: при переносе строки блоки сдвигаются, а не наезжают."""
    return (f'<div style="position: absolute; left: 80px; top: {top}px; width: {width}px; display: flex; '
            f'flex-direction: column; align-items: flex-start; gap: {gap}px;">' + "".join(блоки) + '</div>')


def абзац(текст: str, кегль: int = 40, жирно: bool = False) -> str:
    return (f'<div style="{ТЕКСТ} font-size: {кегль}px; line-height: 1.25; color: {ЧЕРН}; '
            f'{"font-weight: 700;" if жирно else ""}">{текст}</div>')


def вывод(текст: str, кегль: int = 40, значок_: str = "", лайм: bool = False) -> str:
    """Главная мысль кадра — тёмной плашкой с лаймом (правка владельца 09.10.2026: «слабо
    расставлены акценты»). Тот же приём, что у призыва в финале: ловит взгляд с расстояния
    ленты и держит контраст 16:1. Лаймом — часть в `[…]`.

    `лайм` — плашка-выворот: лаймовая заливка, тёмный текст, часть в `[…]` — графитовой
    капсулой с лаймом. На кадрах, где лайм иначе только в мелких чипах (акцент 1,7%).
    """
    if лайм:
        текст = текст.replace("[", f'<span style="display: inline-block; padding: 0 .18em .06em; border-radius: .2em; '
                              f'background: {ГРАФ}; color: {ЛАЙМ};">').replace("]", "</span>")
        return (f'<div style="box-sizing: border-box; max-width: 920px; padding: 22px 32px 26px; border-radius: 24px; '
                f'background: {ЛАЙМ}; {КРУП} font-size: {кегль}px; line-height: 1.2; color: {ЧЕРН};">{текст}</div>')
    текст = claude(текст).replace("[", f'<span style="color: {ЛАЙМ};">').replace("]", "</span>")
    знак = (значок(значок_, ЛАЙМ, кегль).replace("display: block;", "display: inline-block; vertical-align: -0.12em; "
                                                                    "margin-right: 14px;") if значок_ else "")
    return (f'<div style="box-sizing: border-box; max-width: 920px; padding: 22px 32px 26px; border-radius: 24px; '
            f'background: {ГРАФ}; {КРУП} font-size: {кегль}px; line-height: 1.15; color: {стиль.СВЕТЛЫЙ};">{знак}{текст}</div>')


def список(пункты: list[str], значок_: str, кегль: int = 38) -> str:
    """Четыре пункта сеткой 2×2 с лаймовой плиткой-значком: у автора — столбик с эмодзи."""
    ячейки = "".join(
        f'<div style="display: flex; align-items: center; gap: 16px; {ТЕКСТ} font-weight: 700; font-size: {кегль}px; '
        f'line-height: 1.12; color: {ЧЕРН};">'
        f'<div style="width: 52px; height: 52px; border-radius: 14px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок(значок_, ЧЕРН, 30)}</div>{п}</div>' for п in пункты)
    return f'<div style="width: 920px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px 24px;">{ячейки}</div>'


# ── Кадры ────────────────────────────────────────────────────────────────────

def открытие(о: dict) -> str:
    """«В Claude есть функция… — ПРОЕКТЫ»: крупное слово, боковая панель с обведённым пунктом."""
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 60px; width: 920px; text-align: center; {ТЕКСТ} font-weight: 700; '
              f'font-size: 36px; line-height: 1.2; color: {ЧЕРН};">{claude(о["над"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 128px; width: 920px; text-align: center; {КРУП} font-size: 132px; '
              f'line-height: 1;">{маркер(о["крупно"])}</div>'
            + ок.боковая(300, 296, 480, ЗНАЧКИ, обвести=True, строка=56)
            + ок.стрелка(110, 400, 200, 240, "M30 10 C 0 110, 50 196, 180 196")
            + столбик(752, [абзац(claude(о["список_над"]), 40, жирно=True),
                            список(о["список"], "check"),
                            вывод(о["итог"])], gap=20)
            + низ())


def шаг1(ш: dict) -> str:
    """Шаг 1: окно «Create a personal project», кнопка обведена, наклейка «бесплатно»."""
    наклейка = (f'<div style="position: absolute; left: 540px; top: 64px; padding: 10px 24px 14px; border-radius: 16px; '
                f'background: {ЛАЙМ}; border: 3px solid {ГРАФ}; transform: rotate(4deg); box-shadow: 0 10px 24px rgba(18,19,15,.22); '
                f'{КРУП} font-size: 30px; color: {ЧЕРН}; z-index: 2;">{ш["сноска"]}</div>')
    return (подложка() + шапка(ш["номер"], ш["заголовок"])
            + ок.новый_проект(80, 300, 820, ш["проект"], ш["цель"], обвести=True)
            + наклейка
            + ок.стрелка(840, 470, 120, 240, "M90 10 C 130 90, 110 170, 44 220")
            + столбик(836, [абзац(ш["абзац"], 40, жирно=True), вывод(ш["итог"], 38, лайм=True)], gap=22)
            + низ())


def шаг2(ш: dict) -> str:
    """Шаг 2: файлы проекта и инструкции двумя наложенными листами, лаймовый плюс между ними."""
    плюс = (f'<div class=окно data-рядом=окно style="position: absolute; left: 466px; top: 448px; width: 72px; height: 72px; '
            f'border-radius: 36px; background: {ЛАЙМ}; box-shadow: 0 0 0 6px {ЛИСТ}, 0 0 0 9px {ГРАФ}; display: flex; '
            f'align-items: center; justify-content: center; z-index: 3;">{значок("plus", ЧЕРН, 38)}</div>')
    return (подложка() + шапка(ш["номер"], ш["заголовок"], кегль=84)
            + ок.файлы(86, 292, 456, ш["файлы"], ЗНАЧКИ)
            + ок.инструкции(500, 324, 400, ш["инструкция"], "Посты-карусели", ЗНАЧКИ)
            + плюс
            + столбик(808, [абзац(ш["список_над"], 40, жирно=True),
                            список(ш["список"], "folder-simple", 36),
                            вывод(ш["итог"], 36, лайм=True)], gap=16)
            + низ())


def узел(н: str, текст: str, left: int, top: int) -> str:
    return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: 300px; height: 78px; box-sizing: border-box; '
            f'padding-left: 84px; border-radius: 39px; background: #FFFFFF; border: 3px solid {ГРАФ}; box-shadow: {ТЕНЬ}; '
            f'display: flex; align-items: center; {ТЕКСТ} font-weight: 700; font-size: 36px; color: {ЧЕРН};">'
            f'<div style="position: absolute; left: 7px; top: 7px; min-width: 58px; height: 58px; box-sizing: border-box; padding: 0 9px; '
            f'border-radius: 29px; background: {ЛАЙМ}; {КРУП} font-size: 26px; line-height: 58px; text-align: center;">{н}</div>'
            f'{текст}</div>')


def колонка(к: dict, left: int, top: int, значок_: str) -> str:
    """Зигзаг узлов как у автора: нечётные сдвинуты вправо, дуги-стрелки от узла к узлу."""
    шаг, сдвиг = 112, 70
    out = (f'<div style="position: absolute; left: {left}px; top: {top}px; display: flex; align-items: center; gap: 14px; '
           f'{КРУП} font-size: 64px; line-height: 1; color: {ЧЕРН};">'
           f'<div style="width: 64px; height: 64px; border-radius: 18px; background: {ГРАФ}; display: flex; align-items: center; '
           f'justify-content: center;">{значок(значок_, ЛАЙМ, 38)}</div>{к["название"]}</div>')
    for i, (н, текст) in enumerate(к["узлы"]):
        х = left + (сдвиг if i % 2 else 0)
        у = top + 96 + i * шаг
        out += узел(н, текст, х, у)
        if i + 1 < len(к["узлы"]):
            # дуга от края узла к следующему: вправо-вниз или влево-вниз
            if i % 2 == 0:
                out += ок.стрелка(х + 250, у + 70, 70, 44, "M6 4 C 36 6, 54 16, 56 38")
            else:
                out += ок.стрелка(х - 26, у + 70, 70, 44, "M54 4 C 22 6, 6 18, 12 38")
    return out


def схема(с: dict) -> str:
    к1, к2 = с["колонки"]
    return (подложка() + шапка(с["номер"], с["заголовок"], кегль=88)
            + f'<div style="position: absolute; left: 80px; top: 280px; {ТЕКСТ} font-weight: 700; font-size: 38px; color: {ЧЕРН};">{с["над"]}</div>'
            + колонка(к1, 80, 364, "sparkle") + колонка(к2, 530, 364, "chat-text")
            + столбик(1004, [вывод(f'[{с["совет"]}]', 34, "lightbulb")])
            + низ())


def доказательство(д: dict) -> str:
    """Стена из девяти наших обложек: у автора три макета постов с его цифрами."""
    ш, в, зазор = 192, 256, 14
    левый = (1080 - 3 * ш - 2 * зазор) // 2
    плитки = ""
    for i, файл in enumerate(д["обложки"][:9]):
        х, у = левый + i % 3 * (ш + зазор), 300 + i // 3 * (в + зазор)
        плитки += (f'<img class=плитка data-рядом=плитка src="{файл}" style="position: absolute; left: {х}px; top: {у}px; '
                   f'width: {ш}px; height: {в}px; object-fit: cover; border-radius: 16px; border: 4px solid {ГРАФ}; box-shadow: {ТЕНЬ};">')
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 64px; width: 920px; {КРУП} font-size: 92px; line-height: 1.02; '
              f'color: {ЧЕРН};">{д["строки"][0]}<br>{маркер(д["строки"][1])}</div>'
            + плитки + низ())


def финал(ф: dict) -> str:
    """Заголовок, карточка «что сохраняешь» с галочками, кот, тёмная плашка-призыв."""
    пункты = "".join(
        f'<div style="display: flex; align-items: center; gap: 18px; {ТЕКСТ} font-weight: 700; font-size: 38px; color: {ЧЕРН};">'
        f'<div style="width: 52px; height: 52px; border-radius: 26px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок("check", ЧЕРН, 30)}</div>{п}</div>' for п in ф["пункты"])
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 64px; width: 920px; {КРУП} font-size: 104px; line-height: 1.0; '
              f'color: {ЧЕРН};">{ф["строки"][0]}<br>{ф["строки"][1]}<br>{маркер(ф["акцент"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 440px; width: 580px; box-sizing: border-box; padding: 34px 34px; '
              f'border-radius: 28px; background: #FFFFFF; border: 3px solid {ГРАФ}; box-shadow: {ТЕНЬ}; display: flex; '
              f'flex-direction: column; gap: 22px;">{пункты}</div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" data-кот style="position: absolute; left: 686px; top: 400px; height: 300px;">'
            + f'<div style="position: absolute; left: 80px; top: 780px; width: 820px; box-sizing: border-box; padding: 36px 40px 40px; '
              f'border-radius: 30px; background: {ГРАФ}; {КРУП} font-size: 52px; line-height: 1.1; color: {стиль.СВЕТЛЫЙ};">'
              f'<span style="color: {ЛАЙМ};">{ф["призыв"].split(" —")[0]}</span> —{ф["призыв"].split(" —", 1)[1]}</div>'
            + низ())


# ── Обложка по референсу ─────────────────────────────────────────────────────

def заголовок_с_лапой(строка: str) -> str:
    """«ХИТРО🐾ОПАЯ»: вместо «Ж» — кошачья лапа в рост прописной (слово владельца 09.10.2026)."""
    лапа = значок("paw-print", ЧЕРН, 100).replace(
        'style="', 'data-лапа style="display: inline-block; vertical-align: -0.04em; width: .82em; height: .82em; '
                   'transform: rotate(-14deg); margin: 0 .02em; ', 1)
    лапа = лапа.replace("width: 100px; height: 100px; ", "").replace("display: block; ", "")
    return строка.replace("🐾", лапа)


def обложка_постер(о: dict) -> str:
    """Постер, как у автора: заголовок капсом сверху, герой по центру — наш кот-«мажор» сценой.

    Вторая версия (слово владельца 09.10.2026: «кот топ, заголовок топ, но обложку улучшить»).
    Кот и заголовок те же. Добавлено по `КРЮЧКИ.md` и `cover-art-4x`: число на обложке
    (наклейка «3 шага» — приём 3), сцена для героя (лаймовый круг за котом), подпись тёмной
    плашкой — вторая ступень после заголовка. Кот впечатан в картинку сцены, поэтому слои такие:
    сцена → круг → вырезанный кот (`<сцена>-cut.webp`, rembg isnet). Смешение `multiply` не
    годится: кот тёмно-серый, а не чёрный, и в круге становился оливковым.
    """
    к = обложки.карточка(о["сцена"])
    x0, y0, x1, y1 = к["пусто"]
    кегль = обложки.кегль([с.replace("🐾", "Ж") for с in о["строки"]], x1 - x0, 134)
    строки = "<br>".join(заголовок_с_лапой(с) if "🐾" in с else маркер(с) for с in о["строки"])
    круг = (f'<div style="position: absolute; left: 268px; top: 520px; width: 540px; height: 540px; border-radius: 50%; '
            f'background: {ЛАЙМ}; pointer-events: none;"></div>')
    наклейка = ''
    if о.get("число"):
        цифра, слово = о["число"].split(" ", 1)
        наклейка = (f'<div data-рядом="кот-сцены" style="position: absolute; left: 700px; top: 498px; width: 196px; height: 196px; '
                    f'border-radius: 50%; background: {ГРАФ}; border: 5px solid {ЛИСТ}; box-sizing: border-box; transform: rotate(-10deg); '
                    f'box-shadow: 0 14px 30px rgba(18,19,14,.22); display: flex; flex-direction: column; align-items: center; '
                    f'justify-content: center; {КРУП} text-align: center;">'
                    f'<div style="font-size: 92px; line-height: .86; color: {ЛАЙМ};">{цифра}</div>'
                    f'<div style="font-size: 36px; line-height: 1; color: {стиль.СВЕТЛЫЙ};">{слово}</div></div>')
    сцена = f'position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; object-fit: cover;'
    return (f'<img src="{о["сцена"]}.jpg" style="{сцена}">' + круг
            + f'<img src="{о["сцена"]}-cut.webp" style="{сцена} pointer-events: none;">'
            + обложки.кот_сцены(к)
            + наклейка
            + f'<div style="position: absolute; left: {x0}px; top: {y0}px; width: {x1 - x0}px; display: flex; flex-direction: column; '
              f'align-items: center; gap: 24px; text-align: center;">'
              f'<div style="{КРУП} font-size: {кегль}px; line-height: .96; color: {ЧЕРН};">{строки}</div>'
              f'<div style="display: inline-block; padding: 12px 30px 16px; border-radius: 22px; background: {ГРАФ}; {ТЕКСТ} '
              f'font-weight: 700; font-size: 42px; line-height: 1.15; color: {стиль.СВЕТЛЫЙ};">'
              f'{claude(" ".join(о["под"]))}</div></div>'
            + низ())


# ── Сборка ───────────────────────────────────────────────────────────────────

def доски_кадров(пост: dict) -> list[tuple[str, str, str]]:
    кадры = [("Открытие", открытие(пост["открытие"])), ("Шаг 1", шаг1(пост["шаг1"])), ("Шаг 2", шаг2(пост["шаг2"])),
             ("Шаг 3 · схема", схема(пост["схема"])), ("Наши обложки", доказательство(пост["доказательство"])),
             ("Финал", финал(пост["финал"]))]
    return [(f"Kadr{н:02d}.dc.html", f"{н:02d} · {имя}", дх.доска(имя, тело, ЛИСТ, CSS))
            for н, (имя, тело) in enumerate(кадры, 2)]


def значки_превращения(папка: Path) -> list[dict]:
    """Три плитки макета «превращение»: что лежит в проекте — читатель, стиль, темы."""
    папка.mkdir(parents=True, exist_ok=True)
    итог = []
    for имя in ("user", "chat-text", "folder-simple"):
        путь = папка / f"ico-{имя}.svg"
        путь.write_text(ЗНАЧКИ[имя].replace("currentColor", ЛАЙМ), encoding="utf-8")
        итог.append({"значок": путь.name, "цвет": ЛАЙМ, "путь": путь})
    return итог


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    try:
        CSS = дх.шрифты_холста(CSS, корень)
    except SystemExit as е:
        print(f"⚠️  {е} — собираю с локальными шрифтами (до выкладки загрузить)")
    врем = корень / "_файлы"
    значки_пр = значки_превращения(врем)
    файлы = list(ШРИФТЫ) + [дх.логотип(врем), дх.кот(пост["финал"]["поза"], врем)]
    файлы += обложки.файлы(пост.get("запасные", {}), врем)
    файлы += [обложки.СЦЕНЫ / f'{пост["обложка"]["сцена"]}.jpg', обложки.СЦЕНЫ / f'{пост["обложка"]["сцена"]}-cut.webp']
    файлы += [з["путь"] for з in значки_пр]
    файлы += [ТУТ / "картинки" / "oblozhki" / ф for ф in пост["доказательство"]["обложки"]]
    нет = [ф for ф in файлы if not ф.exists()]
    if нет:
        print("для снабженца (snabzhenets):\n  " + "\n  ".join(str(ф) for ф in нет))
        raise SystemExit(2)
    своя = ("постер", ЛИСТ, обложка_постер(пост["обложка"]))
    обл = обложки.доски_обложек(пост, своя, ТЕМА, {"значки": значки_пр}, CSS)
    доски = обл[:1] + доски_кадров(пост) + обл[1:]
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")
    import приёмка_досок
    приёмка_досок.доложить(проект, снимки="--без-снимка" not in sys.argv[2:])


if __name__ == "__main__":
    main()
