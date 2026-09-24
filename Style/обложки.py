# -*- coding: utf-8 -*-
"""Каталог запасных обложек: проверенные макеты в теме стиля поста.

Главная обложка рисуется по референсу — это работа стиля. Две запасные берутся отсюда
(решение владельца 24.09.2026): они изобретались заново на каждом посте и чаще всего уходили
в круг правок. Макет задаёт устройство (штамп поверх суммы, колонки замен, лента кадров),
тема стиля — цвета, шрифты и поля. Макет может держать свою светлоту: «списание» — тёмный кадр
и в светлом стиле (его владелец выбрал главной 24.09).

Каждый макет проходит приёмку досок в теме каждого подключённого стиля —
`tests/test_обложки.py`. В посте: `"запасные": {"<макет>": {поля}, …}`; `"главная"` —
своя обложка стиля или имя запасной, если владелец выбрал её.

Сцена с котом — картинка из `.claude/маскот/сцены/` с карточкой `<сцена>.json`:
`{"тёмная", "пусто": [x0, y0, x1, y1], "кот": [x0, y0, x1, y1]}` в координатах доски. Текст
ложится в «пусто», а кот встаёт в доску невидимым блоком `кот-сцены`: без него приёмка
считает сцену фоном и не видит, что текст сел на кота (24.09 «нашёлся» легло на ухо кота
при вердикте «годен»).
"""
import json
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

import стиль
import дизайн_холст as дх

СЦЕНЫ = Path.home() / "4xSoft/.claude/маскот/сцены"
КРАСНЫЙ = "#FF3B30"                 # зачёркивают красным и от руки (правка владельца 24.09)
ПРИГЛУШИТЬ = "filter: brightness(.45) saturate(1.4);"   # логотип на светлом грунте


@dataclass(frozen=True)
class Тема:
    """Цвета, шрифты и поля стиля — объявляет стиль (`ТЕМА = обложки.Тема(...)`)."""
    грунт: str                  # CSS background доски: цвет или слои градиентов
    тёмная: bool
    чернила: str                # главный текст
    второй: str                 # подпись
    тихий: str                  # служебное: подписи колонок, левая «платная» сторона
    карточка: str               # подложка выделенной карточки
    карточка_тихая: str         # подложка второстепенной карточки
    рамка: str
    тень: str
    стрелка: str                # стрелки и тонкие акценты
    крупный: str                # CSS шрифта заголовка
    текст: str                  # CSS шрифта подписи
    акцент: str = стиль.ЛАЙМ
    на_акценте: str = "#12130E"
    край: int = 80
    сетка: str = ""             # слой поверх грунта во весь кадр (у «пар» — клетка 40 px)
    логотип: str = ""           # CSS-фильтр логотипа: на светлом грунте он приглушён

    @property
    def ширина(self) -> int:
        return 1080 - 2 * self.край


@dataclass(frozen=True)
class Макет:
    рисовать: Callable[[dict, Тема, dict], str]
    поля: tuple
    данные: tuple
    крючок: str
    тёмный: bool = False        # своя светлота: рисуется тёмным и в светлом стиле


# ── Общие куски ──────────────────────────────────────────────────────────────

def подложка(т: Тема, свечение: str = "") -> str:
    """Грунт кадра во весь размер; `свечение` — слои градиента поверх грунта темы."""
    фон = f"{свечение}, {т.грунт}" if свечение else т.грунт
    return f'<div style="position: absolute; inset: 0; background: {фон};"></div>{т.сетка}'


def низ(т: Тема) -> str:
    """Логотип канала слева внизу — на каждом кадре (слово владельца 17.09.2026)."""
    фильтр = f" {т.логотип}" if т.логотип else ""
    return (f'<img src="logo.png" style="position: absolute; left: {т.край}px; top: 1191px; '
            f'height: 44px;{фильтр}">')


def маркер(т: Тема, текст: str) -> str:
    return дх.маркер(текст, тёмный_фон=т.тёмная, чернила=т.на_акценте)


def зачёркнуто(т: Тема, текст: str, кегль: int, цвет: str = "", наклон: float = -5,
               доля: float = .11) -> str:
    """Сумма под толстой красной чертой наискось — не `line-through` (правка владельца 24.09)."""
    толщина = max(9, round(кегль * доля))
    return (f'<span style="position: relative; display: inline-block; {т.крупный} font-size: {кегль}px; '
            f'line-height: 1; color: {цвет or т.чернила};">{текст}'
            f'<span style="position: absolute; left: -4px; right: -4px; top: 50%; height: {толщина}px; '
            f'margin-top: -{толщина // 2}px; background: {КРАСНЫЙ}; border-radius: {толщина}px; '
            f'transform: rotate({наклон}deg); box-shadow: 0 2px 0 rgba(18,19,14,.12);"></span></span>')


def кот(поза: str, left: int, top: int, высота: int) -> str:
    return (f'<img src="kot-{стиль.латиницей(поза)}.webp" style="position: absolute; left: {left}px; '
            f'top: {top}px; height: {высота}px;">')


def карточка(сцена: str, сцены: Path = СЦЕНЫ) -> dict:
    return json.loads((Path(сцены) / f"{сцена}.json").read_text(encoding="utf-8"))


def кот_сцены(к: dict) -> str:
    """Невидимый блок по рамке кота на картинке: приёмка судит его за «впритык».

    Край и зону кнопок TikTok он не судит (`data-вылет`, класс не «кот»): кота на готовой
    картинке не подвинуть, а сцены 24.09 с котом справа приняты владельцем.
    """
    x0, y0, x1, y1 = к["кот"]
    return (f'<div class="кот-сцены" data-вылет style="position: absolute; left: {x0}px; top: {y0}px; '
            f'width: {x1 - x0}px; height: {y1 - y0}px;"></div>')


# ── Макеты ───────────────────────────────────────────────────────────────────

def _значок_в_строке(з: dict, размер: int = 42) -> str:
    return (f'<img src="{з["значок"]}" style="width: {размер}px; height: {размер}px; object-fit: contain; '
            f'border-radius: {"50%" if з.get("во_весь") else "0"};">')


def замена(о: dict, т: Тема, д: dict) -> str:
    """Весь пост на обложке: платные слева, их бесплатные двойники справа, итог зачёркнут.

    Самый «сохраняемый» макет: подмена видна целиком, листают, чтобы прочитать имена.
    Снят с «платно/бесплатно по категориям» (24.09.2026).
    """
    левая = правая = стрелки = ""
    for п in д["пары"]:
        левая += (f'<div style="display: flex; align-items: center; gap: 14px; height: 78px; padding: 0 20px; '
                  f'border-radius: 22px; background: {т.карточка_тихая}; border: 2px solid {т.рамка};">'
                  f'{_значок_в_строке(п["платно"])}'
                  f'<div style="{т.текст} font-weight: 700; font-size: 27px; color: {т.тихий}; flex-grow: 1;">{п["платно"]["имя"]}</div>'
                  f'<div style="{т.крупный} font-size: 34px; color: {т.тихий};">{п["платно"]["цена"]}</div></div>')
        правая += (f'<div style="display: flex; align-items: center; gap: 14px; height: 78px; padding: 0 20px; '
                   f'border-radius: 22px; background: {т.карточка}; border: 3px solid {т.акцент}; box-shadow: {т.тень};">'
                   f'{_значок_в_строке(п["бесплатно"])}'
                   f'<div style="{т.текст} font-weight: 700; font-size: 27px; color: {т.чернила}; flex-grow: 1;">{п["бесплатно"]["имя"]}</div>'
                   f'<div style="{т.крупный} font-size: 34px; color: {т.чернила};">$0</div></div>')
        стрелки += (f'<div style="height: 78px; display: flex; align-items: center; justify-content: center; '
                    f'{т.крупный} font-size: 38px; color: {т.стрелка};">→</div>')
    колонки = f"grid-template-columns: 1fr 60px 1fr; gap: 12px;"
    шапка = (f'<div style="position: absolute; left: {т.край}px; top: 486px; width: {т.ширина}px; display: grid; '
             f'{колонки} {т.текст} font-weight: 700; font-size: 26px; '
             f'letter-spacing: .02em; color: {т.тихий};"><div>платишь</div><div></div>'
             f'<div style="color: {т.чернила};">можешь не платить</div></div>')
    итог = (f'<div style="position: absolute; left: {т.край}px; top: 1014px; display: inline-flex; '
            f'align-items: baseline; gap: 18px; {т.крупный} font-size: 54px; color: {т.чернила};">'
            + зачёркнуто(т, о["было"], 54, наклон=-2, доля=.16) +
            f'<span>→</span>'
            f'<span style="padding: 0 16px 6px; border-radius: 16px; background: {т.акцент}; '
            f'color: {т.на_акценте};">$0</span></div>')
    return (подложка(т)
            + f'<div style="position: absolute; left: {т.край}px; top: 108px; width: {т.ширина}px; {т.крупный} '
              f'font-size: 92px; line-height: 1.0; color: {т.чернила};">{о["строки"][0]}<br>'
              f'{маркер(т, о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 344px; width: 800px; {т.текст} '
              f'font-weight: 700; font-size: 40px; line-height: 1.2; color: {т.второй};">{о["под"]}</div>'
            + шапка
            + f'<div style="position: absolute; left: {т.край}px; top: 534px; width: {т.ширина}px; display: grid; '
              f'{колонки}">'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{левая}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{стрелки}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{правая}</div></div>'
            + итог
            + низ(т))


def списание(о: dict, т: Тема, д: dict) -> str:
    """Тёмный кадр и карточка списания с лаймовым штампом «Отменено» поверх суммы.

    Работает сюжет: знакомый всем счёт за подписки и печать поверх него. Обе правки
    владельца с холста 24.09.2026 оставлены как он их сделал: штамп лежит ПОВЕРХ суммы и
    наполовину её закрывает («создаётся тайна»), красной черты нет; кот левее колонки
    кнопок TikTok («чтобы его не закрывало поле с лайками»).
    """
    ряд = "".join(
        f'<div style="width: 58px; height: 58px; border-radius: 50%; background: #FFFFFF; flex-shrink: 0; '
        f'display: flex; align-items: center; justify-content: center; overflow: hidden;">'
        f'<img src="{с["значок"]}" style="width: {"100%" if с.get("во_весь") else "62%"}; '
        f'height: {"100%" if с.get("во_весь") else "62%"}; object-fit: {"cover" if с.get("во_весь") else "contain"};">'
        f'</div>' for с in д["значки"][:5])
    штамп = (
        f'<span style="position: absolute; left: 69px; top: 4px; transform: rotate(-9deg); '
        f'padding: 12px 30px 16px; border: 7px solid {т.акцент}; border-radius: 18px; '
        f'{т.крупный} font-size: 66px; line-height: 1; letter-spacing: .02em; color: {т.акцент}; '
        f'text-transform: uppercase; background: rgba(18,19,15,.7);">{о["штамп"]}</span>')
    сумма = (f'<div style="position: relative; {т.крупный} font-size: 124px; line-height: 1.05; '
             f'color: {стиль.СВЕТЛЫЙ}; margin-top: 8px;">−{о["сумма"]}{штамп}</div>')
    карта = (
        f'<div style="position: absolute; left: {т.край}px; top: 452px; width: {т.ширина}px; box-sizing: border-box; '
        f'padding: 38px 44px 42px; border-radius: 40px; background: #1B1D17; border: 2px solid rgba(242,244,234,.12); '
        f'box-shadow: 0 34px 80px rgba(0,0,0,.5);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; {т.текст} '
        f'font-weight: 700; font-size: 28px; color: #9AA08F;"><span>Подписки на ИИ</span><span>ежемесячно</span></div>'
        f'{сумма}'
        f'<div style="display: flex; gap: 14px; margin-top: 24px;">{ряд}</div></div>')
    return (f'<div style="position: absolute; inset: 0; background: '
            f'radial-gradient(70% 48% at 84% 8%, rgba(199,226,75,.22) 0%, rgba(18,19,15,0) 62%), '
            f'radial-gradient(60% 40% at 6% 96%, rgba(199,226,75,.10) 0%, rgba(18,19,15,0) 60%), '
            f'{стиль.ТЁМНЫЙ};"></div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 104px; width: {т.ширина}px; {т.крупный} '
              f'font-size: 84px; line-height: 1.0; color: {стиль.СВЕТЛЫЙ};">{о["строки"][0]}<br>'
              f'<span style="color: {т.акцент};">{о["строки"][1]}</span></div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 312px; width: 720px; {т.текст} '
              f'font-weight: 700; font-size: 40px; line-height: 1.2; color: #C9CCBF;">{о["под"]}</div>'
            + карта
            + кот(о["поза"], 674, 819, 300)
            + f'<div style="position: absolute; left: {т.край}px; top: 900px; display: inline-flex; '
              f'align-items: center; padding: 20px 32px 24px; border-radius: 26px; background: {т.акцент}; '
              f'{т.крупный} font-size: 46px; line-height: 1.08; color: {т.на_акценте};">{о["плашка"]}</div>'
            + f'<img src="logo.png" style="position: absolute; left: {т.край}px; top: 1191px; height: 44px;">')


def превращение(о: dict, т: Тема, д: dict) -> str:
    """Строка текста превращается в три кадра ролика — приём вместо сцены.

    Снят с «ролика из текста» (24.09.2026): стрелка 72 px посреди просвета между строкой и
    кадриками, кот левее колонки кнопок TikTok.
    """
    кадрики = ""
    for с in д["значки"][:3]:
        кадрики += (f'<div style="width: 268px; height: 200px; border-radius: 26px; overflow: hidden; '
                    f'background: linear-gradient(150deg, {с.get("цвет", т.акцент)}44, rgba(18,19,15,.9)); '
                    f'border: 2px solid {т.рамка}; display: flex; align-items: center; justify-content: center;">'
                    f'<img src="{с["значок"]}" style="width: 96px; height: 96px; object-fit: contain; '
                    f'border-radius: {"50%" if с.get("во_весь") else "0"};"></div>')
    стрелка = (f'<svg viewBox="0 0 40 120" fill="none" stroke="{т.стрелка}" stroke-width="4" stroke-linecap="round" '
               'stroke-linejoin="round" style="width: 30px; height: 72px;"><path d="M20 6v96M8 88l12 14 12-14"/></svg>')
    return (подложка(т, "radial-gradient(80% 60% at 20% 10%, rgba(199,226,75,.16), rgba(18,19,15,0) 60%)")
            + f'<div style="position: absolute; left: {т.край}px; top: 100px; width: {т.ширина}px; {т.крупный} '
              f'font-size: {кегль(о["строки"], т.ширина, 96)}px; line-height: 1.0; color: {т.чернила};">{о["строки"][0]}<br>'
              f'{маркер(т, о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 360px; width: {т.ширина}px; box-sizing: border-box; '
              f'padding: 30px 36px; border-radius: 26px; background: {т.карточка}; border: 2px dashed {т.рамка}; '
              f'{т.текст} font-weight: 700; font-size: 40px; line-height: 1.24; color: {т.чернила};">{о["строка_текста"]}</div>'
            + f'<div style="position: absolute; left: 525px; top: 553px;">{стрелка}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 656px; width: {т.ширина}px; display: flex; '
              f'gap: 18px;">{кадрики}</div>'
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; left: 680px; '
              f'top: 900px; height: 260px;">'
            + f'<div style="position: absolute; left: {т.край}px; top: 920px; width: 560px; box-sizing: border-box; '
              f'padding: 24px 30px 28px; border-radius: 28px; background: {т.акцент}; {т.крупный} font-size: 46px; '
              f'line-height: 1.1; color: {т.на_акценте};">{о["плашка"]}</div>'
            + низ(т))


def плёнка(о: dict, т: Тема, д: dict) -> str:
    """Лента кадров с пятью значками идёт через весь кадр наискось, заголовок под ней.

    Лента нарочно выходит за оба края (`data-вылет`). Снята с «ролика из текста» (24.09.2026).
    """
    клетки = ""
    for с in д["значки"][:5]:
        клетки += (f'<div style="width: 220px; height: 220px; border-radius: 22px; background: {т.карточка_тихая}; '
                   f'border: 2px solid {т.рамка}; display: flex; align-items: center; justify-content: center; '
                   f'flex-shrink: 0;">'
                   f'<img src="{с["значок"]}" style="width: 128px; height: 128px; object-fit: contain; '
                   f'border-radius: {"50%" if с.get("во_весь") else "0"};"></div>')
    лента = (f'<div data-вылет style="position: absolute; left: -60px; top: 300px; width: 1240px; padding: 26px 30px; '
             f'background: rgba(0,0,0,.45); border-top: 3px solid {т.рамка}; border-bottom: 3px solid {т.рамка}; '
             f'transform: rotate(-7deg); display: flex; gap: 22px;">{клетки}</div>')
    return (подложка(т, "radial-gradient(70% 50% at 82% 82%, rgba(199,226,75,.20), rgba(18,19,15,0) 62%)")
            + лента
            + кот(о["поза"], 640, 660, 380)
            + f'<div style="position: absolute; left: {т.край}px; top: 684px; width: 560px; {т.крупный} '
              f'font-size: 96px; line-height: .98; color: {т.чернила};">{о["строки"][0]}<br>'
              f'{маркер(т, о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 1002px; width: 540px; {т.текст} '
              f'font-weight: 700; font-size: 38px; line-height: 1.2; color: {т.второй};">{о["под"]}</div>'
            + низ(т))


def число(о: dict, т: Тема, д: dict) -> str:
    """Огромное число сверху, под ним заголовок, подпись и плашка; кот справа внизу.

    Самая частая запасная в стилях (7 из 18). Снята со «светлого разбора»; кот перенесён левее
    колонки кнопок TikTok, а текст под заголовком собран в колонку — подпись любой длины не
    наезжает на плашку.
    """
    цвет_числа = т.акцент if т.тёмная else т.чернила
    return (подложка(т, "radial-gradient(circle at 20% 10%, rgba(199,226,75,.20), rgba(199,226,75,0) 45%)")
            + f'<div style="position: absolute; left: {т.край}px; top: 40px; {т.крупный} font-size: 400px; '
              f'line-height: 1; color: {цвет_числа};">{о["число"]}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 470px; width: {т.ширина}px; {т.крупный} '
              f'font-size: 92px; line-height: 1.04; color: {т.чернила};">{о["строки"][0]}<br>'
              f'{маркер(т, о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {т.край}px; top: 720px; width: 480px; display: flex; '
              f'flex-direction: column; align-items: flex-start; gap: 30px;">'
              f'<div style="{т.текст} font-weight: 700; font-size: 40px; line-height: 1.25; color: {т.второй};">{о["под"]}</div>'
              f'<div style="padding: 16px 28px 20px; border-radius: 24px; background: {т.акцент}; {т.крупный} '
              f'font-size: 42px; color: {т.на_акценте};">{о["плашка"]}</div></div>'
            + кот(о["поза"], 620, 700, 380)
            + низ(т))


def кегль(строки: list[str], ширина: int, наибольший: int, высота: int = 10_000) -> int:
    """Крупнейший кегль не больше `наибольший`, при котором каждая строка заголовка — одна строка.

    Ширина строки — по таблице знаков, снятой в Chrome (`приёмка_досок.ширина_строки`), для
    Onest 800 с разрядкой −0,025 em. В теме со своими полями строка уже: «Вставляешь текст —»
    в 96 px лезет в 940 («сервисы»), но не в 920 («пары») — там ляжет лишней строкой. Запас 2%
    на кернинг и округление.
    """
    import приёмка_досок as п
    ряд = sorted({наибольший, *(к for к in (118, 104, 96, 92, 84, 76, 68) if к < наибольший)}, reverse=True)
    for к in ряд:
        if (all(п.ширина_строки(с, "Onest", 800, к, -0.025) <= ширина * .98 for с in строки)
                and len(строки) * к * .98 <= высота):
            return к
    return ряд[-1]


def сцена(о: dict, т: Тема, д: dict) -> str:
    """Сцена с котом во весь кадр, текст — в её пустом месте по карточке сцены.

    Каждая сцена рисуется под свой пост (цены на чеке, хлопушка, цифра 9) и не повторяется;
    переиспользуемо устройство: заголовок, подпись и плашка в «пусто», кот — блоком для приёмки.
    """
    к = карточка(о["сцена"], д.get("сцены", СЦЕНЫ))
    x0, y0, x1, y1 = к["пусто"]
    ширина = x1 - x0
    чернила, второй = (стиль.СВЕТЛЫЙ, "#C9CCBF") if к["тёмная"] else ("#12130E", "#1E1F17")
    # Заголовок, подпись и плашка — одной колонкой: при любом переносе они не наезжают друг на
    # друга. Под подпись (до трёх строк) и плашку оставлено ~330 px «пусто».
    к_загл = кегль(о["строки"], ширина, 118, (y1 - y0) - 330)
    return (f'<img src="{о["сцена"]}.jpg" style="position: absolute; left: 0; top: 0; width: 1080px; '
            f'height: 1440px; object-fit: cover;">'
            + кот_сцены(к)
            + f'<div style="position: absolute; left: {x0}px; top: {y0}px; width: {ширина}px; display: flex; '
              f'flex-direction: column; align-items: flex-start; gap: 30px;">'
              f'<div style="{т.крупный} font-size: {к_загл}px; line-height: .98; color: {чернила};">'
              f'{о["строки"][0]}<br>{дх.маркер(о["строки"][1], тёмный_фон=к["тёмная"])}</div>'
              f'<div style="{т.текст} font-weight: 700; font-size: 40px; line-height: 1.2; color: {второй};">{о["под"]}</div>'
              f'<div style="padding: 16px 30px 20px; border-radius: 26px; background: {т.акцент}; {т.крупный} '
              f'font-size: 46px; color: {т.на_акценте};">{о["плашка"]}</div></div>'
            # Логотип — по светлоте сцены, а не стиля: лаймовый знак на светлой сцене не виден.
            + низ(replace(т, логотип="" if к["тёмная"] else ПРИГЛУШИТЬ)))


МАКЕТЫ = {
    "замена": Макет(замена, ("строки", "под", "было"), ("пары",),
                    "полный список на обложке — сохраняют, чтобы прочитать имена"),
    "списание": Макет(списание, ("строки", "сумма", "штамп", "под", "плашка", "поза"), ("значки",),
                      "знакомая боль (счёт за подписки) и печать поверх — тайна суммы", тёмный=True),
    "превращение": Макет(превращение, ("строки", "строка_текста", "плашка", "поза"), ("значки",),
                         "до и после одним взглядом: строка текста → кадры ролика"),
    "плёнка": Макет(плёнка, ("строки", "под", "поза"), ("значки",),
                    "лента находок — сколько их, видно до чтения"),
    "число": Макет(число, ("число", "строки", "под", "плашка", "поза"), (),
                   "конкретное число в заголовке — обещание объёма"),
    "сцена": Макет(сцена, ("сцена", "строки", "под", "плашка"), (),
                   "сцена с котом останавливает ленту, текст в её пустом месте"),
}


# ── Для стилей и команды сборки ──────────────────────────────────────────────

def проверить(имя: str, о: dict, данные: dict) -> list[str]:
    """Чего не хватает макету: поля обложки, данные поста, карточка сцены. Пусто — можно рисовать."""
    if имя not in МАКЕТЫ:
        return [f"нет макета «{имя}» в каталоге: " + ", ".join(МАКЕТЫ)]
    м = МАКЕТЫ[имя]
    беды = [f"«{имя}»: нет поля «{п}»" for п in м.поля if п not in о]
    беды += [f"«{имя}»: пост не дал «{д}»" for д in м.данные if not данные.get(д)]
    if имя == "сцена" and "сцена" in о:
        сцены = Path(данные.get("сцены", СЦЕНЫ))
        for файл in (f"{о['сцена']}.jpg", f"{о['сцена']}.json"):
            if not (сцены / файл).exists():
                беды.append(f"«сцена»: нет {файл} в {сцены} — сцену и её карточку кладёт снабженец")
    return беды


def нарисовать(имя: str, о: dict, т: Тема, данные: dict) -> str:
    беды = проверить(имя, о, данные)
    if беды:
        raise SystemExit("; ".join(беды))
    return МАКЕТЫ[имя].рисовать(о, т, данные)


def грунт(имя: str, т: Тема) -> str:
    """Фон корня доски: у тёмного макета — тёмный и в светлом стиле."""
    return стиль.ТЁМНЫЙ if МАКЕТЫ[имя].тёмный else т.грунт


def файлы(запасные: dict, папка: Path, сцены: Path = СЦЕНЫ) -> list[Path]:
    """Позы кота и сцены запасных обложек — положить рядом с досками холста."""
    пути = []
    for о in запасные.values():
        if о.get("поза"):
            пути.append(дх.кот(о["поза"], папка))
        if о.get("сцена"):
            папка.mkdir(parents=True, exist_ok=True)
            пути.append(Path(shutil.copy(Path(сцены) / f"{о['сцена']}.jpg", папка)))
    return пути


def доски_обложек(пост: dict, своя: tuple[str, str, str], т: Тема, данные: dict, css: str) -> list[tuple]:
    """Main и запасные доски: своя обложка стиля плюс запасные из каталога, главная — первой.

    `своя` — (имя, фон корня, тело) обложки по референсу. `пост["главная"]` — её имя или имя
    запасной, если владелец выбрал её (24.09 «списание» стало главной).
    """
    все = {своя[0]: (своя[1], своя[2])}
    for имя, о in пост.get("запасные", {}).items():
        все[имя] = (грунт(имя, т), нарисовать(имя, о, т, данные))
    главная = пост.get("главная", своя[0])
    if главная not in все:
        raise SystemExit(f"главная «{главная}» — нет такой обложки: " + ", ".join(все))
    порядок = [главная] + [и for и in все if и != главная]
    фон, тело = все[порядок[0]]
    доски = [("Main.dc.html", f"01 · Обложка · {порядок[0]}", дх.доска("Обложка", тело, фон, css))]
    for н, имя in enumerate(порядок[1:], 2):
        фон, тело = все[имя]
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {имя}", дх.доска(f"Обложка {н}", тело, фон, css)))
    return доски
