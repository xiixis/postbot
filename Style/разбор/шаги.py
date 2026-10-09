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


def шапка(номер: str, заголовок: str, кегль: int = 84) -> str:
    """«Шаг N.» лаймовой капсулой и заголовок шага под ней — как «Шаг 1. Создай Проект» у автора."""
    return (f'<div style="position: absolute; left: 80px; top: 70px; {КРУП} font-size: 54px; line-height: 1;">{маркер(номер)}</div>'
            f'<div style="position: absolute; left: 80px; top: 160px; width: 920px; {КРУП} font-size: {кегль}px; '
            f'line-height: 1.02; color: {ЧЕРН};">{заголовок}</div>')


def столбик(top: int, блоки: list[str], gap: int = 20, width: int = 920) -> str:
    """Текст под картинкой одной колонкой: при переносе строки блоки сдвигаются, а не наезжают."""
    return (f'<div style="position: absolute; left: 80px; top: {top}px; width: {width}px; display: flex; '
            f'flex-direction: column; gap: {gap}px;">' + "".join(блоки) + '</div>')


def абзац(текст: str, кегль: int = 36, жирно: bool = False) -> str:
    return (f'<div style="{ТЕКСТ} font-size: {кегль}px; line-height: 1.28; color: {ЧЕРН}; '
            f'{"font-weight: 700;" if жирно else ""}">{текст}</div>')


def список(пункты: list[str], значок_: str, кегль: int = 34) -> str:
    """Четыре пункта сеткой 2×2 с лаймовой плиткой-значком: у автора — столбик с эмодзи."""
    ячейки = "".join(
        f'<div style="display: flex; align-items: center; gap: 16px; {ТЕКСТ} font-size: {кегль}px; line-height: 1.15; color: {ЧЕРН};">'
        f'<div style="width: 46px; height: 46px; border-radius: 12px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок(значок_, ЧЕРН, 26)}</div>{п}</div>' for п in пункты)
    return f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px;">{ячейки}</div>'


# ── Кадры ────────────────────────────────────────────────────────────────────

def открытие(о: dict) -> str:
    """«В Claude есть функция… — ПРОЕКТЫ»: крупное слово, боковая панель с обведённым пунктом."""
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 70px; width: 920px; text-align: center; {ТЕКСТ} font-weight: 700; '
              f'font-size: 34px; line-height: 1.2; color: {ЧЕРН};">{claude(о["над"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 150px; width: 920px; text-align: center; {КРУП} font-size: 124px; '
              f'line-height: 1;">{маркер(о["крупно"])}</div>'
            + ок.боковая(300, 300, 480, ЗНАЧКИ, обвести=True)
            + ок.стрелка(110, 420, 200, 240, "M30 10 C 0 110, 50 196, 180 202")
            + столбик(784, [абзац(о["абзац"]),
                            абзац(claude(о["список_над"]), 38, жирно=True),
                            список(о["список"], "check"),
                            абзац(о["итог"], 40, жирно=True)], gap=16)
            + низ())


def шаг1(ш: dict) -> str:
    """Шаг 1: окно «Create a personal project», кнопка обведена, наклейка «бесплатно»."""
    наклейка = (f'<div style="position: absolute; left: 640px; top: 72px; padding: 10px 22px 12px; border-radius: 16px; '
                f'background: {ЛАЙМ}; transform: rotate(4deg); box-shadow: 0 10px 24px rgba(60,74,12,.22); {КРУП} '
                f'font-size: 26px; color: {ЧЕРН}; z-index: 2;">{ш["сноска"]}</div>')
    return (подложка() + шапка(ш["номер"], ш["заголовок"])
            + ок.новый_проект(80, 300, 820, ш["проект"], ш["цель"], обвести=True)
            + наклейка
            + ок.стрелка(840, 470, 120, 240, "M90 10 C 130 90, 110 170, 44 220")
            + столбик(836, [абзац(ш["абзац"]),
                            абзац(claude(f'{ш["итог"].split(" всё")[0]} ') + маркер("всё") + ш["итог"].split(" всё", 1)[1], 40, жирно=True)])
            + низ())


def шаг2(ш: dict) -> str:
    """Шаг 2: файлы проекта и инструкции двумя наложенными листами, лаймовый плюс между ними."""
    плюс = (f'<div class=окно data-рядом=окно style="position: absolute; left: 470px; top: 442px; width: 64px; height: 64px; border-radius: 32px; '
            f'background: {ЛАЙМ}; box-shadow: 0 0 0 6px {ЛИСТ}; display: flex; align-items: center; justify-content: center; '
            f'z-index: 3;">{значок("plus", ЧЕРН, 34)}</div>')
    итог = f'{ш["итог"][0]}{маркер(ш["итог"][1])}'
    return (подложка() + шапка(ш["номер"], ш["заголовок"], кегль=76)
            + ок.файлы(86, 282, 456, ш["файлы"], ЗНАЧКИ)
            + ок.инструкции(500, 314, 400, ш["инструкция"], "Посты-карусели", ЗНАЧКИ)
            + плюс
            + столбик(798, [абзац(ш["список_над"], 38, жирно=True),
                            список(ш["список"], "folder-simple", 32),
                            абзац(итог, 36, жирно=True)], gap=16)
            + низ())


def узел(н: str, текст: str, left: int, top: int) -> str:
    return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: 290px; height: 66px; box-sizing: border-box; '
            f'padding-left: 70px; border-radius: 33px; background: #FFFFFF; border: 2px solid rgba(18,19,14,.12); box-shadow: {ТЕНЬ}; '
            f'display: flex; align-items: center; {ТЕКСТ} font-weight: 700; font-size: 32px; color: {ЧЕРН};">'
            f'<div style="position: absolute; left: 8px; top: 8px; min-width: 50px; height: 50px; box-sizing: border-box; padding: 0 8px; '
            f'border-radius: 25px; background: {ЛАЙМ}; {КРУП} font-size: 22px; line-height: 50px; text-align: center;">{н}</div>'
            f'{текст}</div>')


def колонка(к: dict, left: int, top: int, значок_: str) -> str:
    """Зигзаг узлов как у автора: нечётные сдвинуты вправо, дуги-стрелки от узла к узлу."""
    шаг, сдвиг = 104, 80
    out = (f'<div style="position: absolute; left: {left}px; top: {top}px; display: flex; align-items: center; gap: 14px; '
           f'{КРУП} font-size: 54px; line-height: 1; color: {ЧЕРН};">{значок(значок_, ОЛИВА, 46)}{к["название"]}</div>')
    for i, (н, текст) in enumerate(к["узлы"]):
        х = left + (сдвиг if i % 2 else 0)
        у = top + 86 + i * шаг
        out += узел(н, текст, х, у)
        if i + 1 < len(к["узлы"]):
            # дуга от края узла к следующему: вправо-вниз или влево-вниз
            if i % 2 == 0:
                out += ок.стрелка(х + 230, у + 60, 80, 50, "M8 6 C 40 8, 60 20, 62 44", ОЛИВА)
            else:
                out += ок.стрелка(х - 30, у + 60, 80, 50, "M60 6 C 24 8, 8 22, 14 44", ОЛИВА)
    return out


def схема(с: dict) -> str:
    совет = (f'<div style="position: absolute; left: 80px; top: 990px; display: flex; align-items: center; gap: 16px; '
             f'padding: 14px 26px 16px 18px; border-radius: 20px; background: rgba(199,226,75,.35); {ТЕКСТ} font-weight: 700; '
             f'font-size: 34px; color: {ЧЕРН};">{значок("lightbulb", ЧЕРН, 36)}{с["совет"]}</div>')
    к1, к2 = с["колонки"]
    return (подложка() + шапка(с["номер"], с["заголовок"])
            + f'<div style="position: absolute; left: 80px; top: 268px; {ТЕКСТ} font-size: 36px; color: {ЧЕРН};">{с["над"]}</div>'
            + колонка(к1, 80, 360, "sparkle") + колонка(к2, 530, 360, "chat-text")
            + совет + низ())


def доказательство(д: dict) -> str:
    """Стена из девяти наших обложек: у автора три макета постов с его цифрами."""
    ш, в, зазор = 170, 226, 18
    левый = (1080 - 3 * ш - 2 * зазор) // 2
    плитки = ""
    for i, файл in enumerate(д["обложки"][:9]):
        х, у = левый + i % 3 * (ш + зазор), 380 + i // 3 * (в + зазор)
        плитки += (f'<img class=плитка data-рядом=плитка src="{файл}" style="position: absolute; left: {х}px; top: {у}px; width: {ш}px; height: {в}px; '
                   f'object-fit: cover; border-radius: 14px; border: 3px solid #FFFFFF; box-shadow: {ТЕНЬ};">')
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 70px; width: 920px; {КРУП} font-size: 84px; line-height: 1.04; '
              f'color: {ЧЕРН};">{д["строки"][0]}<br>{маркер(д["строки"][1])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 290px; width: 920px; {ТЕКСТ} font-weight: 700; font-size: 36px; '
              f'color: {ВТОР};">{д["под"]}</div>'
            + плитки + низ())


def финал(ф: dict) -> str:
    """Заголовок, карточка «что сохраняешь» с галочками, кот, тёмная плашка-призыв."""
    пункты = "".join(
        f'<div style="display: flex; align-items: center; gap: 18px; {ТЕКСТ} font-weight: 700; font-size: 36px; color: {ЧЕРН};">'
        f'<div style="width: 48px; height: 48px; border-radius: 24px; background: {ЛАЙМ}; display: flex; align-items: center; '
        f'justify-content: center; flex-shrink: 0;">{значок("check", ЧЕРН, 28)}</div>{п}</div>' for п in ф["пункты"])
    return (подложка()
            + f'<div style="position: absolute; left: 80px; top: 70px; width: 920px; {КРУП} font-size: 100px; line-height: 1.02; '
              f'color: {ЧЕРН};">{ф["строки"][0]}<br>{ф["строки"][1]}<br>{маркер(ф["акцент"])}</div>'
            + f'<div style="position: absolute; left: 80px; top: 440px; width: 560px; box-sizing: border-box; padding: 34px 34px; '
              f'border-radius: 28px; background: #FFFFFF; box-shadow: {ТЕНЬ}; display: flex; flex-direction: column; gap: 22px;">'
              f'{пункты}</div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" data-кот style="position: absolute; left: 676px; top: 400px; height: 300px;">'
            + f'<div style="position: absolute; left: 80px; top: 780px; width: 820px; box-sizing: border-box; padding: 36px 40px 40px; '
              f'border-radius: 30px; background: {ГРАФ}; {КРУП} font-size: 50px; line-height: 1.1; color: {стиль.СВЕТЛЫЙ};">'
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
    """Постер, как у автора: заголовок капсом сверху, герой по центру — наш кот-«мажор» сценой."""
    к = обложки.карточка(о["сцена"])
    x0, y0, x1, y1 = к["пусто"]
    кегль = обложки.кегль([с.replace("🐾", "Ж") for с in о["строки"]], x1 - x0, 150)
    строки = "<br>".join(заголовок_с_лапой(с) for с in о["строки"])
    return (f'<img src="{о["сцена"]}.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1440px; object-fit: cover;">'
            + обложки.кот_сцены(к)
            + f'<div style="position: absolute; left: {x0}px; top: {y0}px; width: {x1 - x0}px; display: flex; flex-direction: column; '
              f'align-items: center; gap: 22px; text-align: center;">'
              f'<div style="{КРУП} font-size: {кегль}px; line-height: .96; color: {ЧЕРН};">{строки}</div>'
              f'<div style="{ТЕКСТ} font-weight: 700; font-size: 50px; line-height: 1.12; color: {ЧЕРН};">'
              f'{claude("<br>".join(о["под"]))}</div></div>'
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
    файлы += [обложки.СЦЕНЫ / f'{пост["обложка"]["сцена"]}.jpg'] + [з["путь"] for з in значки_пр]
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
