# -*- coding: utf-8 -*-
"""Окна интерфейса claude.ai вёрсткой — «снимки» для кадров-шагов стиля «разбор».

Свои снимки вместо чужих (паспорт `референс-проекты/паспорт.md`, улучшение 5): окно набрано
HTML, поэтому чёткое при снимке ×1,5, правится на холсте и не несёт личных данных аккаунта.
Устройство повторяет живой интерфейс: кремовая подложка `#FAF9F5`, заголовок окна с засечками,
белые поля с тонкой рамкой, чёрная главная кнопка, файлы проекта карточками DOCX со шкалой
заполнения. Кегли — в полтора раза крупнее экранных: доска уменьшается в ленте втрое.

Каждая функция отдаёт HTML-блок с абсолютной позицией внутри доски 1080×1440.
"""

КРЕМ_ОКНА = "#FAF9F5"
РАМКА = "#E3E0D6"
ЧЕРН = "#141413"
СЕР = "#3D3C38"           # подписи полей: 9,9:1 к белому, не «серые»
ЗАСЕЧКИ = "font-family: Cormorant, Georgia, serif; font-weight: 700;"
UI = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
ТЕНЬ = "0 2px 4px rgba(20,20,19,.06), 0 24px 60px rgba(20,20,19,.16)"
# Рукописные пометки поверх окна — лайм с графитовым контуром (правка владельца 09.10.2026:
# оливковый штрих 7 px в ленте терялся). Лайм один по светлому — 1,7:1, контур даёт ему края.
ЛАЙМ_ШТРИХ, КОНТУР = "#C7E24B", "#12130F"


def _иконка(svg: str, цвет: str, размер: int) -> str:
    return svg.replace("<svg ", f'<svg style="width: {размер}px; height: {размер}px; color: {цвет}; '
                                 f'display: block; flex-shrink: 0;" ', 1)


def боковая(x: int, y: int, w: int, значки: dict, выделить: str = "Projects", обвести: bool = False,
            строка: int = 60) -> str:
    """Боковая панель Claude: знак, пункты меню, выделенный пункт подложкой.

    Строки ровно по `строка` px с зазором 4: строка i стоит на y + 100 + (строка + 4)·i — по
    этому числу кадр целит стрелку. Обводка рисуется внутри строки и едет вместе с ней.
    """
    пункты = [("plus", "New chat"), ("magnifying-glass", "Search"), ("chats-circle", "Chats"),
              ("folders", "Projects"), ("squares-four", "Artifacts")]
    строки = ""
    for значок, имя in пункты:
        своя = имя == выделить
        фон = f"background: {ЛАЙМ_ШТРИХ};" if своя else ""
        жирно = "font-weight: 700;" if своя else ""
        круг = обводка(-18, -14, w - 44 + 36, строка + 28) if своя and обвести else ""
        строки += (f'<div style="position: relative; height: {строка}px; display: flex; align-items: center; gap: 22px; padding: 0 22px; '
                   f'border-radius: 14px; {фон}">{_иконка(значки[значок], ЧЕРН, 34)}'
                   f'<span style="{UI} font-size: 34px; color: {ЧЕРН}; {жирно}">{имя}</span>{круг}</div>')
    return (f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; box-sizing: border-box; padding: 30px 22px 26px; '
            f'border-radius: 26px; background: {КРЕМ_ОКНА}; border: 1px solid {РАМКА}; box-shadow: {ТЕНЬ};">'
            f'<div style="{ЗАСЕЧКИ} font-size: 52px; line-height: 52px; height: 70px; color: {ЧЕРН}; padding: 0 22px; box-sizing: border-box;">Claude</div>'
            f'<div style="display: flex; flex-direction: column; gap: 4px;">{строки}</div></div>')


def новый_проект(x: int, y: int, w: int, название: str, цель: str, обвести: bool = False) -> str:
    """Окно «Create a personal project»: два поля и кнопки, как на claude.ai."""
    поле = (f"box-sizing: border-box; width: 100%; padding: 14px 22px; border-radius: 14px; background: #FFFFFF; "
            f"border: 2px solid {РАМКА}; {UI} color: {ЧЕРН};")
    круг = обводка(-26, -18, 0, 0, во_весь=True) if обвести else ""
    return (f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; box-sizing: border-box; padding: 32px 36px 32px; '
            f'border-radius: 28px; background: {КРЕМ_ОКНА}; border: 1px solid {РАМКА}; box-shadow: {ТЕНЬ};">'
            f'<div style="{ЗАСЕЧКИ} font-size: 48px; line-height: 1.05; color: {ЧЕРН};">Create a personal project</div>'
            f'<div style="{UI} font-size: 26px; color: {СЕР}; margin: 22px 0 10px;">What are you working on?</div>'
            f'<div style="{поле} font-size: 30px;">{название}</div>'
            f'<div style="{UI} font-size: 26px; color: {СЕР}; margin: 22px 0 10px;">What are you trying to achieve?</div>'
            f'<div style="{поле} font-size: 28px; line-height: 1.3; border-color: #8DA4C9;">{цель}</div>'
            f'<div style="display: flex; justify-content: flex-end; gap: 16px; margin-top: 24px;">'
            f'<div style="padding: 14px 28px; border-radius: 14px; border: 2px solid {РАМКА}; background: #FFFFFF; {UI} '
            f'font-size: 28px; color: {ЧЕРН};">Cancel</div>'
            f'<div style="position: relative; padding: 14px 30px; border-radius: 14px; background: {ЧЕРН}; {UI} font-weight: 700; '
            f'font-size: 28px; color: #FFFFFF;">Create project{круг}</div></div></div>')


def файлы(x: int, y: int, w: int, имена: list[str], значки: dict, наклон: float = -3) -> str:
    """Лист «Project files»: шкала заполнения, карточки DOCX 2×2, кнопка Add files."""
    карточки = ""
    for имя in имена[:4]:
        карточки += (f'<div style="position: relative; box-sizing: border-box; height: 96px; padding: 12px 16px; border-radius: 16px; '
                     f'background: #FFFFFF; border: 2px solid {РАМКА};">'
                     f'<div style="display: inline-block; padding: 3px 10px; border-radius: 6px; border: 1.5px solid {РАМКА}; {UI} '
                     f'font-weight: 700; font-size: 16px; color: {СЕР};">DOCX</div>'
                     f'<div style="{UI} font-weight: 700; font-size: 22px; line-height: 1.15; color: {ЧЕРН}; margin-top: 8px;">{имя}</div></div>')
    return (f'<div class=окно data-рядом=окно style="position: absolute; left: {x}px; top: {y}px; width: {w}px; box-sizing: border-box; padding: 26px 24px 22px; '
            f'border-radius: 28px; background: {КРЕМ_ОКНА}; border: 1px solid {РАМКА}; box-shadow: {ТЕНЬ}; transform: rotate({наклон}deg);">'
            f'<div style="{UI} font-weight: 700; font-size: 30px; color: {ЧЕРН}; text-align: center;">Project files</div>'
            f'<div style="height: 10px; border-radius: 5px; background: #E8E5DB; margin: 16px 0 14px;">'
            f'<div style="width: 6%; height: 10px; border-radius: 5px; background: #5B7FC0;"></div></div>'
            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">{карточки}</div>'
            f'<div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 14px; padding: 12px; '
            f'border-radius: 16px; background: {ЧЕРН}; {UI} font-weight: 700; font-size: 26px; color: #FFFFFF;">'
            f'{_иконка(значки["paperclip"], "#FFFFFF", 28)}Add files</div></div>')


def инструкции(x: int, y: int, w: int, строки: list[str], название: str, значки: dict, наклон: float = 3) -> str:
    """Лист «Instructions»: правила проекта списком и подсказка Claude под ними."""
    пункты = "".join(f'<div style="{UI} font-size: 28px; line-height: 1.3; color: {ЧЕРН}; margin-bottom: 10px;">— {с}</div>'
                     for с in строки)
    return (f'<div class=окно data-рядом=окно style="position: absolute; left: {x}px; top: {y}px; width: {w}px; box-sizing: border-box; padding: 30px 30px 28px; '
            f'border-radius: 28px; background: {КРЕМ_ОКНА}; border: 1px solid {РАМКА}; box-shadow: {ТЕНЬ}; transform: rotate({наклон}deg); z-index: 2;">'
            f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px;">'
            f'<div style="{UI} font-weight: 700; font-size: 34px; color: {ЧЕРН}; border-bottom: 3px solid {ЧЕРН}; padding-bottom: 4px;">Instructions</div>'
            f'<div style="width: 48px; height: 48px; border-radius: 24px; background: {ЧЕРН}; display: flex; align-items: center; '
            f'justify-content: center;">{_иконка(значки["check"], "#FFFFFF", 28)}</div></div>'
            f'<div style="box-sizing: border-box; padding: 20px 22px 12px; border-radius: 14px; background: #FFFFFF; border: 2px solid {РАМКА};">'
            f'{пункты}</div>'
            f'<div style="{UI} font-size: 22px; line-height: 1.3; color: {СЕР}; margin-top: 14px;">Instruct Claude how to respond in all chats '
            f'within {название}</div></div>')


def обводка(x: int, y: int, w: int, h: int, цвет: str = ЛАЙМ_ШТРИХ, во_весь: bool = False) -> str:
    """Овал «от руки» вокруг элемента окна: неровный замкнутый штрих, как маркером.

    `во_весь` — овал на весь родительский блок с выносом x/y наружу: размер кнопки заранее
    не известен, а растянутый SVG (`preserveAspectRatio="none"`) ляжет ровно по ней.
    """
    ш, в = (100, 100) if во_весь else (w, h)
    # SVG — заменяемый элемент: по left/right он не растягивается (берёт свои 300×150), поэтому
    # ширина и высота заданы явно от родителя.
    где = (f"left: {x}px; top: {y}px; width: calc(100% + {-2 * x}px); height: calc(100% + {-2 * y}px);" if во_весь
           else f"left: {x}px; top: {y}px; width: {w}px; height: {h}px;")
    путь = (f'M{ш * .52:.1f} {в * .04:.1f} C{ш * .9:.1f} {в * .02:.1f} {ш * 1.01:.1f} {в * .3:.1f} {ш * .99:.1f} {в * .55:.1f} '
            f'C{ш * .97:.1f} {в * .92:.1f} {ш * .62:.1f} {в * 1.02:.1f} {ш * .38:.1f} {в * .97:.1f} '
            f'C{ш * .08:.1f} {в * .92:.1f} {-ш * .02:.1f} {в * .62:.1f} {ш * .03:.1f} {в * .36:.1f} '
            f'C{ш * .08:.1f} {в * .1:.1f} {ш * .34:.1f} {в * .0:.1f} {ш * .6:.1f} {в * .08:.1f}')
    return (f'<svg viewBox="0 0 {ш} {в}" preserveAspectRatio="none" fill="none" style="position: absolute; {где} '
            f'overflow: visible; pointer-events: none;">' + _штрих(путь, цвет, масштаб=False) + '</svg>')


def _штрих(путь: str, цвет: str, масштаб: bool = True) -> str:
    """Два прохода одного пути: графитовый контур 15 px и лайм 9 px поверх."""
    без = "" if масштаб else ' vector-effect="non-scaling-stroke"'
    return (f'<path d="{путь}" stroke="{КОНТУР}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"{без}/>'
            f'<path d="{путь}" stroke="{цвет}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"{без}/>')


def стрелка(x: int, y: int, w: int, h: int, путь: str, цвет: str = ЛАЙМ_ШТРИХ) -> str:
    """Рукописная стрелка: кривая `путь` в системе w×h и наконечник на её конце (последние две точки)."""
    import math
    import re
    числа = [float(ч) for ч in re.findall(r"-?\d+\.?\d*", путь)]
    кх, ку, пх, пу = числа[-2], числа[-1], числа[-4], числа[-3]
    угол = math.atan2(ку - пу, кх - пх)
    кр = min(26, max(w, h) * .4)
    л = (кх - кр * math.cos(угол - .5), ку - кр * math.sin(угол - .5))
    п = (кх - кр * math.cos(угол + .5), ку - кр * math.sin(угол + .5))
    наконечник = f"M{л[0]:.0f} {л[1]:.0f} L{кх:.0f} {ку:.0f} L{п[0]:.0f} {п[1]:.0f}"
    return (f'<svg viewBox="0 0 {w} {h}" fill="none" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; '
            f'height: {h}px; overflow: visible; pointer-events: none;">'
            + _штрих(f"{путь} {наконечник}", цвет) + '</svg>')
