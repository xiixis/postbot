# -*- coding: utf-8 -*-
"""Вариация стиля «сервисы»: тёмный кадр, один сервис в карточке по центру.

    python3 карточка.py посты/<пост>.json

Снята с карусели TikTok @aplus_tech_ (273 тыс. показов, 13 394 сохранения, кадры —
`референс-aplus/`). Устройство автора: тёмный кадр с градиентом из тёплого в фиолетовый,
обложка — только текст слева, дальше по одному сервису на кадр: карточка по центру, круглый
значок сверху, имя капсом, три коротких строки и отдельная строка «есть ли бесплатная версия».

Что перенесено: тёмная лента, центрированная карточка, круглый значок героем кадра, имя капсом,
ровно три строки на сервис, строка про бесплатную версию, отсутствие номеров у пунктов.

Что наше:
* градиент кадра красится **родным цветом сервиса** — у автора один и тот же фон на всех
  кадрах, и в сетке профиля они сливаются в одно пятно;
* три строки выровнены по левому краю и помечены лаймовыми точками: у автора они по центру,
  и глазу негде зацепиться;
* имя набрано крупно (перепад кеглей 3:1) — у автора 2,1:1, кадр читается серой массой;
* «✅ Free version» эмодзи заменено нарисованной галочкой в лаймовой капсуле;
* логотип канала на каждом кадре, кот на обложке и финале.

Доски 1080×1440 (`../дизайн_холст.py`); дальше Artifact → «готово» → `../выпуск.py`.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
import дизайн_холст as дх  # noqa: E402

ГРУНТ = стиль.ТЁМНЫЙ                 # #12130F
СВЕТЛЫЙ, ВТОРОЙ = "#F2F4EA", "#CBCFBE"
ТИХИЙ = "#9AA08F"
# Карточка не просто прозрачная: снизу она темнее фона. Иначе цветное гало значка
# высветляет подложку, и 28% текста уходило ниже 8:1 (замер 24.09.2026).
СТЕКЛО = "linear-gradient(180deg, rgba(255,255,255,.075) 0%, rgba(10,11,9,.55) 100%)"
РАМКА = "rgba(242,244,234,.12)"

УЗКИЙ = "font-family: Oswald, 'Arial Narrow', sans-serif; font-weight: 600; text-transform: uppercase;"
КРУП = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.025em;"
ТЕКСТ = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif;"
CSS, ШРИФТЫ = дх.шрифты(("Oswald", "oswald-600", 600), ("Onest", "onest-800", 800),
                        ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))

КРАЙ = 70
КАРТА = (70, 196, 940, 880)          # left, top, width, height — низ на 1076, выше порога 1105


def кегль(текст: str, большой: int, малый: int, предел: int) -> int:
    return большой if len(текст) <= предел else малый


def низ(справа: str = "") -> str:
    с = (f'<div style="position: absolute; right: {КРАЙ}px; top: 1198px; {ТЕКСТ} font-weight: 700; '
         f'font-size: 26px; color: {ТИХИЙ};">{справа}</div>') if справа else ""
    return (f'<img src="logo.png" style="position: absolute; left: {КРАЙ}px; top: 1191px; height: 44px;">' + с)


def фон(цвет: str, сила: float = .40) -> str:
    """Грунт кадра, подкрашенный родным цветом сервиса: лента перестаёт быть однотонной."""
    return (f'<div style="position: absolute; inset: 0; background: '
            f'radial-gradient(88% 64% at 74% 70%, {цвет}{int(сила * 100):02d} 0%, rgba(18,19,15,0) 66%), '
            f'radial-gradient(72% 48% at 10% 6%, rgba(199,226,75,.16) 0%, rgba(18,19,15,0) 62%), '
            f'{ГРУНТ};"></div>')


def значок(с: dict, размер: int = 244) -> str:
    """Круглый значок в родных цветах, в лаймово-цветном гало — герой кадра."""
    внутри = с.get("размер", 58)
    заливка = с.get("фон", "#FFFFFF")
    нутро = (f'<img src="{с["значок"]}" style="width: 100%; height: 100%; object-fit: cover;">'
             if с.get("во_весь") else
             f'<img src="{с["значок"]}" style="width: {внутри}%; height: {внутри}%; object-fit: contain;">')
    return (f'<div style="position: relative; width: {размер}px; height: {размер}px; flex-shrink: 0;">'
            f'<div style="position: absolute; inset: -26px; border-radius: 50%; background: {с["цвет"]}; '
            f'opacity: .26; filter: blur(34px);"></div>'
            f'<div style="position: absolute; inset: 0; border-radius: 50%; overflow: hidden; '
            f'background: {заливка}; border: 3px solid rgba(255,255,255,.22); '
            f'box-shadow: 0 22px 46px rgba(0,0,0,.45), inset 0 3px 0 rgba(255,255,255,.35); '
            f'display: flex; align-items: center; justify-content: center;">{нутро}</div></div>')


ГАЛКА = ('<svg viewBox="0 0 24 24" fill="none" stroke="#12130E" stroke-width="3.6" stroke-linecap="round" '
         'stroke-linejoin="round" style="width: 30px; height: 30px; flex-shrink: 0;"><path d="M4 13l6 6L21 5"/></svg>')


def кадр(н: int, всего: int, с: dict) -> str:
    строки = ""
    for т in с["строки"]:
        строки += (f'<div style="display: flex; gap: 20px; align-items: flex-start;">'
                   f'<div style="width: 14px; height: 14px; border-radius: 50%; background: {стиль.ЛАЙМ}; '
                   f'flex-shrink: 0; margin-top: 13px;"></div><div>{т}</div></div>')
    return f"""{фон(с["цвет"])}
<div style="position: absolute; left: {КРАЙ}px; top: 76px; {ТЕКСТ} font-weight: 700; font-size: 30px; letter-spacing: .02em; color: {стиль.ЛАЙМ};">{с["рубрика"]}</div>
<div style="position: absolute; right: {КРАЙ}px; top: 76px; {ТЕКСТ} font-weight: 700; font-size: 30px; color: {ТИХИЙ};">{н:02d}<span style="opacity: .55;">/{всего:02d}</span></div>
<div style="position: absolute; left: {КАРТА[0]}px; top: {КАРТА[1]}px; width: {КАРТА[2]}px; height: {КАРТА[3]}px; box-sizing: border-box; padding: 52px 62px 50px; border-radius: 56px; background: {СТЕКЛО}; border: 2px solid {РАМКА}; box-shadow: inset 0 2px 0 rgba(255,255,255,.10), 0 30px 70px rgba(0,0,0,.40); display: flex; flex-direction: column; align-items: center; gap: 30px;">
{значок(с)}
<div style="{УЗКИЙ} font-size: {кегль(с["имя"], 116, 92, 12)}px; line-height: 1; letter-spacing: .01em; color: {СВЕТЛЫЙ};">{с["имя"]}</div>
<div style="width: 100%; display: flex; flex-direction: column; gap: 20px; {ТЕКСТ} font-size: 38px; line-height: 1.26; color: {ВТОРОЙ};">{строки}</div>
<div style="margin-top: auto; display: inline-flex; align-items: center; gap: 16px; padding: 18px 34px 22px; border-radius: 999px; background: {стиль.ЛАЙМ}; {ТЕКСТ} font-weight: 700; font-size: 34px; color: #12130E;">{ГАЛКА}{с["задача"][0].upper() + с["задача"][1:]}</div>
</div>
{низ(с["адрес"])}"""


def сцена(файл: str, сдвиг: int = 0) -> str:
    return (f'<img src="{файл}" style="position: absolute; left: 0; top: {сдвиг}px; width: 1080px; '
            f'height: 1440px; object-fit: cover;">')


def обложка_режиссёр(о: dict) -> str:
    """Главная: кот с хлопушкой в тёмной студии, текст в пустой левой половине — как у автора."""
    строки = о["строки"]
    return (f'<div style="position: absolute; inset: 0; background: {ГРУНТ};"></div>'
            + сцена("kot-rezhisser.jpg", о.get("сдвиг", 0))
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 120px; width: 700px; {КРУП} '
              f'font-size: 118px; line-height: .98; color: {СВЕТЛЫЙ};">{строки[0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{строки[1]}</span><br>{строки[2]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 600px; width: 520px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 42px; line-height: 1.22; color: {ВТОРОЙ};">{о["под"]}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 790px; display: inline-flex; '
              f'align-items: center; gap: 16px; padding: 14px 26px 18px; border-radius: 24px; '
              f'background: {стиль.ЛАЙМ}; {КРУП} font-size: 40px; color: #12130E;">{о["плашка"]}</div>'
            + низ())


def обложка_превращение(о: dict, сервисы: list[dict]) -> str:
    """Запасная 1: строка текста превращается в три кадра ролика — приём вместо сцены."""
    кадрики = ""
    for i, с in enumerate(сервисы[:3]):
        кадрики += (f'<div style="width: 268px; height: 200px; border-radius: 26px; overflow: hidden; '
                    f'background: linear-gradient(150deg, {с["цвет"]}44, rgba(18,19,15,.9)); '
                    f'border: 2px solid {РАМКА}; display: flex; align-items: center; justify-content: center;">'
                    f'<img src="{с["значок"]}" style="width: 96px; height: 96px; object-fit: contain; '
                    f'border-radius: {"50%" if с.get("во_весь") else "0"};"></div>')
    стрелка = ('<svg viewBox="0 0 40 120" fill="none" stroke="#C7E24B" stroke-width="4" stroke-linecap="round" '
               'stroke-linejoin="round" style="width: 40px; height: 96px;"><path d="M20 6v96M8 88l12 14 12-14"/></svg>')
    return (f'<div style="position: absolute; inset: 0; background: radial-gradient(80% 60% at 20% 10%, '
            f'rgba(199,226,75,.16), rgba(18,19,15,0) 60%), {ГРУНТ};"></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 100px; width: 940px; {КРУП} '
              f'font-size: 96px; line-height: 1.0; color: {СВЕТЛЫЙ};">{о["строки"][0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{о["строки"][1]}</span></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 360px; width: 940px; box-sizing: border-box; '
              f'padding: 30px 36px; border-radius: 26px; background: {СТЕКЛО}; border: 2px dashed {РАМКА}; '
              f'{ТЕКСТ} font-weight: 700; font-size: 40px; line-height: 1.24; color: {СВЕТЛЫЙ};">{о["строка_текста"]}</div>'
            + f'<div style="position: absolute; left: 520px; top: 510px;">{стрелка}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 656px; width: 940px; display: flex; '
              f'gap: 18px;">{кадрики}</div>'
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; right: 30px; '
              f'top: 900px; height: 260px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 920px; width: 560px; box-sizing: border-box; '
              f'padding: 24px 30px 28px; border-radius: 28px; background: {стиль.ЛАЙМ}; {КРУП} font-size: 46px; '
              f'line-height: 1.1; color: #12130E;">{о["плашка"]}</div>'
            + низ())


def обложка_плёнка(о: dict, сервисы: list[dict]) -> str:
    """Запасная 2: лента кадров с пятью значками идёт через весь кадр, заголовок внизу."""
    клетки = ""
    for с in сервисы[:5]:
        клетки += (f'<div style="width: 220px; height: 220px; border-radius: 22px; background: rgba(255,255,255,.06); '
                   f'border: 2px solid {РАМКА}; display: flex; align-items: center; justify-content: center; '
                   f'flex-shrink: 0;">'
                   f'<img src="{с["значок"]}" style="width: 128px; height: 128px; object-fit: contain; '
                   f'border-radius: {"50%" if с.get("во_весь") else "0"};"></div>')
    лента = (f'<div style="position: absolute; left: -60px; top: 300px; width: 1240px; padding: 26px 30px; '
             f'background: rgba(0,0,0,.45); border-top: 3px solid {РАМКА}; border-bottom: 3px solid {РАМКА}; '
             f'transform: rotate(-7deg); display: flex; gap: 22px;">{клетки}</div>')
    return (f'<div style="position: absolute; inset: 0; background: radial-gradient(70% 50% at 82% 82%, '
            f'rgba(199,226,75,.20), rgba(18,19,15,0) 62%), {ГРУНТ};"></div>'
            + лента
            + f'<img src="kot-{стиль.латиницей(о["поза"])}.webp" style="position: absolute; right: 44px; '
              f'top: 640px; height: 420px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 660px; width: 760px; {КРУП} '
              f'font-size: 96px; line-height: .98; color: {СВЕТЛЫЙ};">{о["строки"][0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{о["строки"][1]}</span></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 920px; width: 620px; {ТЕКСТ} '
              f'font-weight: 700; font-size: 40px; line-height: 1.2; color: {ВТОРОЙ};">{о["под"]}</div>'
            + низ())


def финал(ф: dict, сервисы: list[dict]) -> str:
    """Итог — карта выбора: под каждой задачей свой сервис, и широкая плашка-призыв.

    Прежний финал был столбцом из пяти одинаковых клеток и пустым низом. Здесь пятёрка
    разложена по задачам («нужен аватар — DeepBrain»), каждый значок в своём цветном гало,
    а призыв и ссылка сведены в одну плашку во всю ширину (правка владельца 24.09.2026).
    """
    клетки = ""
    for н, с in enumerate(сервисы):
        # Значок всегда в белом круге: у части сервисов png с белой подложкой, и без круга
        # в тёмной клетке он читается как приклеенный квадрат.
        диск = (f'<div style="width: 68px; height: 68px; border-radius: 50%; background: #FFFFFF; '
                f'flex-shrink: 0; display: flex; align-items: center; justify-content: center; overflow: hidden;">'
                f'<img src="{с["значок"]}" style="width: {"100%" if с.get("во_весь") else "64%"}; '
                f'height: {"100%" if с.get("во_весь") else "64%"}; '
                f'object-fit: {"cover" if с.get("во_весь") else "contain"};"></div>')
        # Последняя клетка занимает обе колонки: одинокая половинка в ряду смотрится обрывом.
        ширина = ' grid-column: span 2;' if н == len(сервисы) - 1 and len(сервисы) % 2 else ''
        клетки += (
            f'<div style="position: relative; box-sizing: border-box; padding: 24px 24px 26px;{ширина} '
            f'border-radius: 30px; background: {СТЕКЛО}; border: 2px solid {РАМКА}; overflow: hidden;">'
            f'<div style="position: absolute; right: -40px; top: -40px; width: 160px; height: 160px; '
            f'border-radius: 50%; background: {с["цвет"]}; opacity: .30; filter: blur(30px);"></div>'
            f'<div style="position: relative; display: flex; align-items: center; gap: 18px;">'
            f'{диск}'
            f'<div style="min-width: 0;">'
            f'<div style="{ТЕКСТ} font-size: 26px; color: {ТИХИЙ};">{с["задача"]}</div>'
            f'<div style="{ТЕКСТ} font-weight: 700; font-size: 38px; line-height: 1.1; color: {СВЕТЛЫЙ};">'
            f'{с["имя"]}</div></div></div></div>')
    return (f'<div style="position: absolute; inset: 0; background: radial-gradient(76% 54% at 22% 8%, '
            f'rgba(199,226,75,.20), rgba(18,19,15,0) 62%), radial-gradient(62% 44% at 92% 96%, '
            f'rgba(199,226,75,.12), rgba(18,19,15,0) 60%), {ГРУНТ};"></div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 100px; width: 640px; {КРУП} '
              f'font-size: 88px; line-height: 1.0; color: {СВЕТЛЫЙ};">{ф["строки"][0]}<br>'
              f'<span style="color: {стиль.ЛАЙМ};">{ф["строки"][1]}</span></div>'
            + f'<img src="kot-{стиль.латиницей(ф["поза"])}.webp" style="position: absolute; right: 24px; '
              f'top: 70px; height: 280px;">'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 392px; width: 940px; display: grid; '
              f'grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px;">{клетки}</div>'
            + f'<div style="position: absolute; left: {КРАЙ}px; top: 880px; width: 940px; box-sizing: border-box; '
              f'padding: 30px 38px 34px; border-radius: 32px; background: {стиль.ЛАЙМ}; display: flex; '
              f'align-items: center; justify-content: space-between; gap: 24px;">'
              f'<div style="{КРУП} font-size: 52px; line-height: 1.06; color: #12130E;">{ф["призыв"]}</div>'
              f'<div style="{ТЕКСТ} font-weight: 700; font-size: 30px; line-height: 1.2; color: #2A3106; '
              f'text-align: right; max-width: 330px;">{ф["ссылка"]}</div></div>'
            + низ())


def main():
    global CSS
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    корень = ТУТ / "холсты" / файл.stem
    CSS = дх.шрифты_холста(CSS, корень)
    врем = корень / "_файлы"
    позы = {пост["обложка_превращение"]["поза"], пост["обложка_плёнка"]["поза"], пост["финал"]["поза"]}
    файлы = list(ШРИФТЫ) + [дх.логотип(врем)] + [дх.кот(п, врем) for п in позы]
    файлы.append(дх.снимок_сайта(ТУТ / пост["обложка"]["сцена"], врем, 1080))
    for с in пост["сервисы"]:
        путь = ТУТ / "значки" / с["файл"]
        файлы.append(путь)
        с["значок"] = путь.name
    всего = len(пост["сервисы"]) + 2
    доски = [("Main.dc.html", "01 · Обложка · режиссёр",
              дх.доска("Обложка", обложка_режиссёр(пост["обложка"]), ГРУНТ, CSS))]
    for н, с in enumerate(пост["сервисы"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {с['имя']}",
                      дх.доска(с["имя"], кадр(н, всего, с), ГРУНТ, CSS)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал",
                  дх.доска("Финал", финал(пост["финал"], пост["сервисы"]), ГРУНТ, CSS)))
    доски.append(("Oblozhka2.dc.html", "Обложка 2 · превращение",
                  дх.доска("Обложка 2", обложка_превращение(пост["обложка_превращение"], пост["сервисы"]), ГРУНТ, CSS)))
    доски.append(("Oblozhka3.dc.html", "Обложка 3 · плёнка",
                  дх.доска("Обложка 3", обложка_плёнка(пост["обложка_плёнка"], пост["сервисы"]), ГРУНТ, CSS)))
    проект = дх.собрать(корень, пост["название"], доски, файлы, пост.get("заметка", ""), в_ряд=5,
                        источник=пост.get("источник", ""))
    print(f"холст: {проект} — досок {len(доски)}")


if __name__ == "__main__":
    main()
