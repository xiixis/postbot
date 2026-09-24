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
#
# Грунт не плоская заливка (слово владельца 24.09.2026: «можно на фоне сделать небольшой
# интересный градиент»): лаймовое свечение из правого верхнего угла, оливковый подтон в
# левом нижнем и еле заметная сетка поверх — тот же приём, что держит кадр у автора.
БУМАГА = ("radial-gradient(64% 46% at 92% 2%, rgba(199,226,75,.34) 0%, rgba(199,226,75,0) 62%),"
          "radial-gradient(58% 42% at 2% 98%, rgba(86,105,12,.13) 0%, rgba(86,105,12,0) 64%),"
          "linear-gradient(168deg, #FCFDF8 0%, #F0F2E7 54%, #E5E8DA 100%)")
СЕТКА = (  # 40 px клетка, тоньше волоса: кадр перестаёт быть пустым листом
    '<div style="position: absolute; inset: 0; pointer-events: none; opacity: .5; '
    'background-image: linear-gradient(rgba(18,19,14,.045) 1px, transparent 1px), '
    'linear-gradient(90deg, rgba(18,19,14,.045) 1px, transparent 1px); '
    'background-size: 40px 40px;"></div>')
ЧЕРНИЛА, ВТОРОЙ, ТИХИЙ = "#12130E", "#1E1F17", "#3A3E33"
БЕЛАЯ = "#FFFFFF"
# Зачёркивают красным и от руки (слово владельца 24.09.2026: «если зачёркиваешь — зачёркивай
# прям; зелёным непонятно»). Тот же #FF5A4E, что в вариации «фразы».
КРАСНЫЙ = "#FF3B30"
РАМКА = "rgba(18,19,14,.09)"
ТЕНЬ = "0 18px 44px rgba(18,19,14,.10)"
СЕРЫЙ_ЧИП = "#E7E9DF"

КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
ЧЕК = "font-family: JetBrains, 'SFMono-Regular', Menlo, monospace;"   # цифры на бумажном чеке
CSS, ШРИФТЫ = дх.шрифты(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                        ("Golos", "golos-700", 700), ("JetBrains", "jetbrains-400", 400),
                        ("JetBrains", "jetbrains-700", 700))


def грунт() -> str:
    """Фон кадра: градиент плюс сетка. Один вызов на доску, самым первым слоем."""
    return f'<div style="position: absolute; inset: 0; background: {БУМАГА};"></div>{СЕТКА}'


def зачёркнуто(текст: str, кегль: int, цвет: str = ЧЕРНИЛА, наклон: float = -5,
               доля: float = .11) -> str:
    """Сумма, перечёркнутая толстой красной чертой наискось — как ручкой по бумаге.

    `text-decoration: line-through` даёт волосяную линию: при кегле 128 она 8 px и в ленте
    не читается вовсе, а лаймовая читается как подчёркивание, а не как отмена (правка
    владельца 24.09.2026). Поэтому черта — отдельный блок высотой ~11% кегля, с наклоном.
    """
    т = max(9, round(кегль * доля))
    return (f'<span style="position: relative; display: inline-block; {КРУП} font-size: {кегль}px; '
            f'line-height: 1; color: {цвет};">{текст}'
            f'<span style="position: absolute; left: -4px; right: -4px; top: 50%; height: {т}px; '
            f'margin-top: -{т // 2}px; background: {КРАСНЫЙ}; border-radius: {т}px; '
            f'transform: rotate({наклон}deg); box-shadow: 0 2px 0 rgba(18,19,14,.12);"></span></span>')

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
    return f"""{СЕТКА}
<div style="position: absolute; left: {КРАЙ}px; top: 60px; {ТЕКСТ} font-weight: 700; font-size: 30px; letter-spacing: .02em; color: {стиль.ОЛИВА};">{к["рубрика"]}</div>
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


def обложка_чек(о: dict, строки_чека: list[tuple[str, str]], итог: str) -> str:
    """Главная: кот держит настоящий чек — на нём набраны имена и цены, внизу итог.

    Пустой чек в сцене — просто предмет; чек с цифрами читается за полсекунды и сам
    задаёт вопрос заголовка (правка владельца 24.09.2026: «обложки должны останавливать»).
    Цифры набраны моношрифтом поверх бумаги и чуть повёрнуты по её наклону.
    """
    позиции = "".join(
        f'<div style="display: flex; justify-content: space-between; gap: 10px;">'
        f'<span>{имя}</span><span>{цена}</span></div>' for имя, цена in строки_чека)
    # Итог на самом чеке тоже вычеркнут: красная черта на бумаге договаривает заголовок.
    чек = (f'<div style="position: absolute; left: 578px; top: 800px; width: 188px; transform: rotate(-1.2deg); '
           f'{ЧЕК} font-size: 21px; line-height: 1.55; color: #24261C;">{позиции}'
           f'<div style="margin: 9px 0 7px; border-top: 2px dashed rgba(18,19,14,.45);"></div>'
           f'<div style="position: relative; display: flex; justify-content: space-between; '
           f'font-weight: 700; font-size: 29px;"><span>ИТОГО</span><span>{итог}</span>'
           f'<span style="position: absolute; left: 2px; right: 8px; top: 50%; height: 7px; '
           f'margin-top: -3px; background: {КРАСНЫЙ}; border-radius: 7px; '
           f'transform: rotate(-2deg);"></span></div>'
           f'<div style="margin-top: 12px; text-align: right; font-weight: 700; font-size: 27px; '
           f'color: #24261C;">$0</div></div>')
    строки = о["строки"]
    return (грунт()
            + сцена("kot-chek.jpg", о.get("сдвиг", 0))
            + чек
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 88px; width: 880px; {КРУП} '
              f'font-size: 112px; line-height: .98; color: {ЧЕРНИЛА};">{строки[0]}<br>{строки[1]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 330px; display: inline-flex; '
              f'align-items: baseline; gap: 22px;">'
              + зачёркнуто(итог, 132) +
              f'<span style="{КРУП} font-size: 72px; line-height: 1; color: {ТИХИЙ};">→</span>'
              f'<span style="{КРУП} font-size: 132px; line-height: 1; padding: 0 22px 10px; '
              f'border-radius: 22px; background: {стиль.ЛАЙМ}; color: {ЧЕРНИЛА};">$0</span></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 516px; width: 440px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 44px; line-height: 1.2; color: {ВТОРОЙ};">{о["под"]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 680px; display: inline-flex; '
              f'align-items: center; gap: 18px; padding: 16px 30px 20px; border-radius: 26px; '
              f'background: {стиль.ЛАЙМ}; {КРУП} font-size: 48px; color: {ЧЕРНИЛА};">{о["плашка"]}</div>'
            + низ())


def обложка_замена(о: dict, пары: list[dict]) -> str:
    """Запасная 1: весь пост на обложке — пять платных слева, их бесплатные двойники справа.

    Самый «сохраняемый» макет: человек видит подмену целиком и листает, чтобы прочитать
    имена. Колонки помечены сверху, между ними столбик стрелок.
    """
    левая = правая = стрелки = ""
    for п in пары:
        левая += (f'<div style="display: flex; align-items: center; gap: 14px; height: 78px; padding: 0 20px; '
                  f'border-radius: 22px; background: rgba(255,255,255,.72); border: 2px solid {РАМКА};">'
                  f'<img src="{п["платно"]["значок"]}" style="width: 42px; height: 42px; object-fit: contain; '
                  f'border-radius: {"50%" if п["платно"].get("во_весь") else "0"};">'
                  f'<div style="{ТЕКСТ} font-weight: 700; font-size: 27px; color: {ТИХИЙ}; flex-grow: 1;">{п["платно"]["имя"]}</div>'
                  f'<div style="{КРУП} font-size: 34px; color: {ТИХИЙ};">{п["платно"]["цена"]}</div></div>')
        правая += (f'<div style="display: flex; align-items: center; gap: 14px; height: 78px; padding: 0 20px; '
                   f'border-radius: 22px; background: {БЕЛАЯ}; border: 3px solid {стиль.ЛАЙМ}; box-shadow: {ТЕНЬ};">'
                   f'<img src="{п["бесплатно"]["значок"]}" style="width: 42px; height: 42px; object-fit: contain; '
                   f'border-radius: {"50%" if п["бесплатно"].get("во_весь") else "0"};">'
                   f'<div style="{ТЕКСТ} font-weight: 700; font-size: 27px; color: {ЧЕРНИЛА}; flex-grow: 1;">{п["бесплатно"]["имя"]}</div>'
                   f'<div style="{КРУП} font-size: 34px; color: {ЧЕРНИЛА};">$0</div></div>')
        стрелки += (f'<div style="height: 78px; display: flex; align-items: center; justify-content: center; '
                    f'{КРУП} font-size: 38px; color: {стиль.ОЛИВА};">→</div>')
    шапка = (f'<div style="position: absolute; left: {КРАЙ}px; top: 486px; width: 920px; display: grid; '
             f'grid-template-columns: 1fr 60px 1fr; gap: 12px; {ТЕКСТ} font-weight: 700; font-size: 26px; '
             f'letter-spacing: .02em; color: {ТИХИЙ};"><div>платишь</div><div></div>'
             f'<div style="color: {ЧЕРНИЛА};">можешь не платить</div></div>')
    итог = (f'<div style="position: absolute; left: {КРАЙ}px; top: 1014px; display: inline-flex; '
            f'align-items: baseline; gap: 18px; {КРУП} font-size: 54px; color: {ЧЕРНИЛА};">'
            + зачёркнуто("$109 в месяц", 54, наклон=-2, доля=.16) +
            f'<span>→</span>'
            f'<span style="padding: 0 16px 6px; border-radius: 16px; background: {стиль.ЛАЙМ};">$0</span></div>')
    return (грунт()
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 108px; width: 920px; {КРУП} '
              f'font-size: 92px; line-height: 1.0; color: {ЧЕРНИЛА};">{о["строки"][0]}<br>'
              f'{дх.маркер(о["строки"][1])}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 344px; width: 800px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 40px; line-height: 1.2; color: {ВТОРОЙ};">{о["под"]}</div>'
            + шапка
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 534px; width: 920px; display: grid; '
              f'grid-template-columns: 1fr 60px 1fr; gap: 12px;">'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{левая}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{стрелки}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 12px;">{правая}</div></div>'
            + итог
            + низ())


def обложка_списание(о: dict, значки: list[dict]) -> str:
    """Запасная 2: тёмный кадр и карточка списания $109 с лаймовым штампом «ОТМЕНЕНО».

    Здесь работает не число, а сюжет: знакомый всем счёт за подписки и печать поверх него.
    Прежний вариант (гигантский ноль) был красив, но ничего не обещал.
    """
    ряд = "".join(
        f'<div style="width: 58px; height: 58px; border-radius: 50%; background: #FFFFFF; flex-shrink: 0; '
        f'display: flex; align-items: center; justify-content: center; overflow: hidden;">'
        f'<img src="{с["значок"]}" style="width: {"100%" if с.get("во_весь") else "62%"}; '
        f'height: {"100%" if с.get("во_весь") else "62%"}; object-fit: {"cover" if с.get("во_весь") else "contain"};">'
        f'</div>' for с in значки[:5])
    # Обе правки владельца с холста 24.09.2026 оставлены как он их сделал.
    # Штамп лежит ПОВЕРХ суммы и наполовину её закрывает — это замысел, а не помеха:
    # «тут я „отменено“ поместил на сумму, будто штамп. Плюс не понятно какая сумма и
    # создаётся тайна». Поэтому здесь нет красной черты: отмену говорит штамп, а сумму
    # зритель досматривает внутри поста.
    # Кота он сдвинул влево, «чтобы его не закрывало поле с лайками» — правая колонка
    # кнопок TikTok. Ничего важного правее 900 px на кадре быть не должно.
    штамп = (
        f'<span style="position: absolute; left: 69px; top: 4px; transform: rotate(-9deg); '
        f'padding: 12px 30px 16px; border: 7px solid {стиль.ЛАЙМ}; border-radius: 18px; '
        f'{КРУП} font-size: 66px; line-height: 1; letter-spacing: .02em; color: {стиль.ЛАЙМ}; '
        f'text-transform: uppercase; background: rgba(18,19,15,.7);">{о["штамп"]}</span>')
    сумма = (f'<div style="position: relative; {КРУП} font-size: 124px; line-height: 1.05; '
             f'color: {стиль.СВЕТЛЫЙ}; margin-top: 8px;">−{о["сумма"]}{штамп}</div>')
    карточка = (
        f'<div style="position: absolute; left: {КРАЙ}px; top: 452px; width: 920px; box-sizing: border-box; '
        f'padding: 38px 44px 42px; border-radius: 40px; background: #1B1D17; border: 2px solid rgba(242,244,234,.12); '
        f'box-shadow: 0 34px 80px rgba(0,0,0,.5);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; {ТЕКСТ} '
        f'font-weight: 700; font-size: 28px; color: #9AA08F;"><span>Подписки на ИИ</span><span>ежемесячно</span></div>'
        f'{сумма}'
        f'<div style="display: flex; gap: 14px; margin-top: 24px;">{ряд}</div></div>')
    return (f'<div style="position: absolute; inset: 0; background: '
            f'radial-gradient(70% 48% at 84% 8%, rgba(199,226,75,.22) 0%, rgba(18,19,15,0) 62%), '
            f'radial-gradient(60% 40% at 6% 96%, rgba(199,226,75,.10) 0%, rgba(18,19,15,0) 60%), '
            f'{стиль.ТЁМНЫЙ};"></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 104px; width: 920px; {КРУП} '
              f'font-size: 84px; line-height: 1.0; color: {стиль.СВЕТЛЫЙ};">{о["строки"][0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{о["строки"][1]}</span></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 312px; width: 720px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 40px; line-height: 1.2; color: #C9CCBF;">{о["под"]}</div>'
            + карточка
            # Кота на холсте передвинул владелец (24.09.2026): левее и на 7 px ниже.
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; left: 674px; '
              f'top: 819px; height: 300px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 900px; display: inline-flex; '
              f'align-items: center; padding: 20px 32px 24px; border-radius: 26px; background: {стиль.ЛАЙМ}; '
              f'{КРУП} font-size: 46px; line-height: 1.08; color: {ЧЕРНИЛА};">{о["плашка"]}</div>'
            + f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px;">')


def финал(ф: dict, пары: list[dict]) -> str:
    """Итог — шпаргалка: все пять замен подряд и сумма, ради которой это сохраняют.

    Прежний финал перечислял три мысли словами; их читать незачем — их и так проговорил
    пост. Сохраняют не мысль, а список: кто кого заменяет (правка владельца 24.09.2026).
    """
    строки = ""
    for п in пары:
        строки += (
            f'<div style="display: grid; grid-template-columns: 1fr 52px 1fr; align-items: center; gap: 10px; '
            f'height: 76px; padding: 0 22px; border-radius: 24px; background: rgba(255,255,255,.78); '
            f'border: 2px solid {РАМКА};">'
            f'<div style="display: flex; align-items: center; gap: 14px; min-width: 0;">'
            f'<img src="{п["платно"]["значок"]}" style="width: 40px; height: 40px; object-fit: contain; '
            f'flex-shrink: 0; border-radius: {"50%" if п["платно"].get("во_весь") else "0"};">'
            f'<span style="{ТЕКСТ} font-weight: 700; font-size: 28px; color: {ТИХИЙ};">{п["платно"]["имя"]}</span>'
            f'<span style="{КРУП} font-size: 28px; color: {ТИХИЙ};">{п["платно"]["цена"]}</span></div>'
            f'<div style="{КРУП} font-size: 34px; color: {стиль.ОЛИВА}; text-align: center;">→</div>'
            # Правая половина строки залита лаймом: «бесплатная сторона» видна одним взглядом,
            # и доля акцента в финале дотягивает до нормы (замер 24.09 давал 3,0%).
            f'<div style="display: flex; align-items: center; gap: 14px; min-width: 0; height: 100%; '
            f'margin: 0 -22px 0 0; padding: 0 22px; border-radius: 0 24px 24px 0; '
            f'background: rgba(199,226,75,.42);">'
            f'<img src="{п["бесплатно"]["значок"]}" style="width: 40px; height: 40px; object-fit: contain; '
            f'flex-shrink: 0; border-radius: {"50%" if п["бесплатно"].get("во_весь") else "0"};">'
            f'<span style="{ТЕКСТ} font-weight: 700; font-size: 28px; color: {ЧЕРНИЛА};">{п["бесплатно"]["имя"]}</span>'
            f'<span style="{КРУП} font-size: 28px; padding: 2px 12px 5px; border-radius: 12px; '
            f'background: {стиль.ЛАЙМ}; color: {ЧЕРНИЛА};">$0</span></div></div>')
    счёт = (f'<div style="position: absolute; right: {КРАЙ}px; top: 104px; display: flex; flex-direction: column; '
            f'align-items: flex-end; gap: 10px;">'
            + зачёркнуто(ф["было"], 72, цвет=ТИХИЙ, наклон=-6) +
            f'<span style="{КРУП} font-size: 104px; line-height: 1; padding: 0 20px 8px; border-radius: 20px; '
            f'background: {стиль.ЛАЙМ}; color: {ЧЕРНИЛА};">{ф["стало"]}</span></div>')
    return (грунт()
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 112px; width: 640px; {КРУП} '
              f'font-size: 80px; line-height: 1.0; color: {ЧЕРНИЛА};">{ф["строки"][0]}<br>{ф["строки"][1]}</div>'
            + счёт
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 352px; width: 920px; display: flex; '
              f'flex-direction: column; gap: 12px;">{строки}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 828px; width: 570px; box-sizing: border-box; '
              f'padding: 30px 36px 34px; border-radius: 32px; background: {ЧЕРНИЛА};">'
              f'<div style="{КРУП} font-size: 48px; line-height: 1.08; color: {стиль.ЛАЙМ};">{ф["призыв"]}</div>'
              f'<div style="{ТЕКСТ} font-weight: 700; font-size: 30px; color: #C9CCBF; margin-top: 12px;">'
              f'{ф["ссылка"]}</div></div>'
            # Кот не у правого края: там колонка лайков и репостов TikTok (правка владельца
            # 24.09.2026). Ничего важного правее ≈900 px.
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" style="position: absolute; left: 690px; '
              f'top: 800px; height: 300px;">'
            + низ())


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    CSS = дх.шрифты_холста(CSS, корень)
    врем = корень / "_файлы"
    позы = {пост["обложка_списание"]["поза"], пост["финал"]["поза"]}
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
    чек = [(к["платно"]["имя"], к["платно"]["цена"]) for к in пост["кадры"]]
    доски = [("Main.dc.html", "01 · Обложка · чек",
              дх.доска("Обложка", обложка_чек(пост["обложка"], чек, пост["обложка"]["итог"]), БУМАГА, CSS))]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['категория_кратко']}",
                      дх.доска(к["категория_кратко"], кадр(н, всего, к), БУМАГА, CSS)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"], пост["кадры"]), БУМАГА, CSS)))
    доски.append(("Oblozhka2.dc.html", "Обложка 2 · замена",
                  дх.доска("Обложка 2", обложка_замена(пост["обложка_замена"], пост["кадры"]), БУМАГА, CSS)))
    доски.append(("Oblozhka3.dc.html", "Обложка 3 · списание",
                  дх.доска("Обложка 3", обложка_списание(пост["обложка_списание"], значки),
                           стиль.ТЁМНЫЙ, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
