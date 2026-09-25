# -*- coding: utf-8 -*-
"""Вариация «пар»: «так не пиши | пиши вот так» — две колонки фраз на одном кадре.

    python3 фразы.py посты/<пост>.json [01 04]

Рерайт @ythemark «Слова, которые нельзя писать в ChatGPT, Gemini и Claude», 17.09.2026.
Устройство кадра то же, что у «пар» (две колонки, шапка «тонко + крупно лаймом»), но вместо
плиток сервисов — по 9 строк-плашек в каждой колонке, выровненных по рядам. Вид, шрифты, знак,
кот и замер — из `рисовать.py`; своё здесь — шпаргалка, кадр «почему», финал и три обложки
(обложки и финал в этом стиле у каждого поста свои: TikTok считает одинаковые кадры повтором).
Номера без JPG, как у `рисовать.py`; без номеров — JPG 1080×1440 и подпись на стол.
"""
import json, sys, time
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ))
import рисовать as р  # noqa: E402  CSS, страница, почему, замер — общие со стилем
from рисовать import стиль, W, H, СТОЛ, ЛАЙМ, ЛАЙМ_RGB, кот, браузер, Image  # noqa: E402

КРАСНЫЙ, КРАСНЫЙ_RGB = "#FF5A4E", "255,90,78"
КЕГЛЬ = 36                     # строка шпаргалки; длинная фраза слева ужимается от него

CSS = f"""
.мелко .шапка .тонко{{font-size:84px}}
.мелко .шапка .крупно{{font-size:150px}}
.шпаргалка{{position:absolute;left:100px;right:100px;top:520px;z-index:3;display:grid;
  grid-template-columns:40% 1fr;column-gap:34px;row-gap:12px}}
.заглавие{{display:flex;align-items:center;gap:20px;height:110px;padding:0 32px;border-radius:55px;
  font-family:Mn;font-weight:800;font-size:46px;text-transform:uppercase;letter-spacing:-.01em;white-space:nowrap}}
.заглавие.нет{{background:rgba({КРАСНЫЙ_RGB},.14);color:#FFD9D5;box-shadow:inset 0 0 0 3px rgba({КРАСНЫЙ_RGB},.45)}}
.заглавие.да{{background:rgba({ЛАЙМ_RGB},.14);color:{ЛАЙМ};box-shadow:inset 0 0 0 3px rgba({ЛАЙМ_RGB},.5)}}
.метка{{flex:none;width:58px;height:58px;border-radius:50%;display:grid;place-items:center;
  font-family:Golos;font-weight:700;font-size:38px;line-height:1}}
.нет .метка{{background:{КРАСНЫЙ};color:#fff}}
.да .метка{{background:{ЛАЙМ};color:#1A2006}}
.фраза{{display:flex;align-items:center;gap:18px;min-height:100px;padding:12px 24px;border-radius:30px;
  font-family:Golos;font-size:36px;line-height:1.2;text-wrap:pretty}}
.фраза.нет{{background:rgba(238,240,232,.05);color:#C9CBC2}}
.фраза.да{{background:rgba({ЛАЙМ_RGB},.07);color:#F4F6EE;box-shadow:inset 0 0 0 2px rgba({ЛАЙМ_RGB},.18)}}
.фраза .метка{{width:44px;height:44px;font-size:28px}}
.фраза.нет .метка{{background:rgba({КРАСНЫЙ_RGB},.9)}}
.фраза.да .метка{{background:{ЛАЙМ}}}
.фраза.нет span{{text-decoration:line-through;text-decoration-color:rgba({КРАСНЫЙ_RGB},.7);text-decoration-thickness:3px}}
.номер{{color:{ЛАЙМ};font-weight:700}}

/* Обложка А: кот и перечёркнутое облачко */
.обл-а .текст{{position:absolute;left:120px;right:110px;top:250px;z-index:3}}
.обл-а .тонко{{font-size:118px;line-height:1.06}}
.обл-а .крупно{{font-size:200px;line-height:1.02;margin-top:14px}}
.облачко{{position:absolute;left:130px;top:1080px;z-index:4;padding:40px 70px;border-radius:70px 70px 70px 16px;
  background:#23261E;font-family:Mn;font-weight:800;font-size:130px;color:#EEF0E8;
  box-shadow:0 0 0 4px rgba({КРАСНЫЙ_RGB},.55);transform:rotate(-4deg)}}
.облачко::after{{content:"";position:absolute;left:30px;right:30px;top:50%;height:12px;border-radius:6px;
  background:{КРАСНЫЙ};transform:rotate(-8deg);box-shadow:0 0 24px rgba({КРАСНЫЙ_RGB},.6)}}

/* Обложка Б: маркер */
.гигант{{position:absolute;left:120px;top:120px;z-index:3;font-family:Os;font-weight:600;font-size:1050px;
  line-height:1;color:{ЛАЙМ};text-shadow:0 0 80px rgba({ЛАЙМ_RGB},.25)}}
.обл-б .текст{{position:absolute;left:120px;right:110px;top:1260px;z-index:3}}
.обл-б .тонко{{font-size:110px}}
.маркер{{display:inline-block;margin-top:26px;padding:6px 30px;border-radius:16px;background:{ЛАЙМ};color:#10120C;
  font-family:Os;font-weight:600;font-size:150px;text-transform:uppercase;line-height:1.05;transform:rotate(-2deg);
  white-space:nowrap}}

/* Обложка В: до-после */
.обл-в .шапка{{top:220px}}
.обл-в .шапка .тонко{{font-size:110px}}
.обл-в .шапка .крупно{{font-size:210px}}
.сравнение{{position:absolute;left:120px;right:120px;top:600px;z-index:3;display:flex;flex-direction:column;gap:70px}}
.плашка{{border-radius:60px;padding:50px 60px;font-family:Golos;line-height:1.2}}
.плашка small{{display:flex;align-items:center;gap:18px;font-family:Mn;font-weight:800;font-size:44px;
  text-transform:uppercase;margin-bottom:20px}}
.плашка.нет{{background:rgba({КРАСНЫЙ_RGB},.12);box-shadow:inset 0 0 0 3px rgba({КРАСНЫЙ_RGB},.45);font-size:130px;
  color:#FFD9D5}}
.плашка.нет b{{text-decoration:line-through;text-decoration-color:{КРАСНЫЙ};text-decoration-thickness:8px}}
.плашка.да{{background:rgba({ЛАЙМ_RGB},.1);box-shadow:inset 0 0 0 3px rgba({ЛАЙМ_RGB},.5);font-size:92px;color:#F4F6EE}}
.плашка.нет small{{color:{КРАСНЫЙ}}}
.плашка.да small{{color:{ЛАЙМ}}}

/* Финал: кот снизу справа, призыв столбцом */
.фин .верх{{position:absolute;left:120px;right:110px;top:240px;z-index:3}}
.фин .крупно{{font-size:300px}}
.фин .тонко{{font-size:112px;margin-top:10px}}
.фин .зов{{position:absolute;left:120px;width:900px;top:900px;z-index:3;font-family:Golos;font-size:84px;line-height:1.2}}
.фин .зов b{{color:{ЛАЙМ};font-weight:700}}
.фин .зов small{{display:block;margin-top:44px;font-size:60px;color:#A3A69A}}
.фраза.нет span{{text-decoration:none}}
.фраза.нет span.одной{{white-space:nowrap;display:inline-block}}
.мишень{{position:relative;display:inline-block}}
.обводка{{position:absolute;left:-40px;right:-40px;top:-26px;bottom:-26px;z-index:1;display:block}}
.стрелка{{position:absolute;left:1120px;top:190px;width:230px;height:230px;z-index:4}}
.окно{{position:relative;z-index:2;border-radius:44px;background:rgba(14,16,12,.62);backdrop-filter:blur(26px);
  box-shadow:inset 0 0 0 3px rgba({ЛАЙМ_RGB},.35),0 30px 80px rgba(0,0,0,.45);overflow:hidden}}
.окно .верхушка{{display:flex;align-items:center;gap:18px;padding:26px 34px;background:rgba(255,255,255,.05);
  box-shadow:inset 0 -2px 0 rgba(255,255,255,.07)}}
.окно .точка{{width:26px;height:26px;border-radius:50%;background:#3C3F36}}
.окно .точка:first-child{{background:#E6584A}}.окно .точка:nth-child(2){{background:#E3B341}}
.окно .точка:nth-child(3){{background:{ЛАЙМ}}}
.окно .имя{{margin-left:16px;font-family:Mn;font-weight:400;font-size:38px;color:#9DA291;letter-spacing:.02em}}
.окно .код{{padding:40px 46px;font-family:JB;font-size:54px;line-height:1.3;color:#F4F6EE}}
.окно .код.размыто{{filter:blur(13px);user-select:none}}
.листай{{margin-top:10px;font-family:Mn;font-weight:400;font-size:54px;letter-spacing:.02em;text-transform:uppercase;color:#A3A69A;display:flex;align-items:center;gap:24px}}
.блик{{position:absolute;z-index:0;border-radius:50%;filter:blur(90px);background:rgba({ЛАЙМ_RGB},.22)}}
"""


def _шум(зерно: str, i: int) -> float:
    """Повторяемый разброс в [-1, 1]: у одной и той же строки штрих всегда один и тот же."""
    import hashlib
    return (int(hashlib.sha1(f"{зерно}-{i}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF) * 2 - 1


def лента(зерно: str, точек: int = 26, нажим: float = 0.22, грубость: float = 1.0) -> str:
    """Путь SVG «мазок кистью» в поле 100×12: лента переменной толщины, а не ровная линия.

    Приём взят у remocn (Scribble Circle, MIT): толщина идёт по профилю нажима — тонко на входе,
    полно в середине, — а край слегка рваный. Ровная линия `text-decoration` выглядит машинной,
    рисованный штрих — рукой.
    """
    верх, низ = [], []
    for i in range(точек + 1):
        д = i / точек
        x = д * 100
        основа = 6 + 1.6 * _шум(зерно + "y", i // 3)
        толщина = 1.1 + 4.2 * (нажим + (1 - нажим) * (1 - abs(2 * д - 1)) ** 0.55)
        край = 0.5 * грубость * _шум(зерно + "к", i)
        верх.append((x, основа - толщина / 2 + край))
        низ.append((x, основа + толщина / 2 - край))
    путь = "M" + " L".join(f"{x:.1f},{y:.2f}" for x, y in верх)
    путь += " L" + " L".join(f"{x:.1f},{y:.2f}" for x, y in reversed(низ)) + " Z"
    return путь


def штрих(зерно: str, цвет: str = КРАСНЫЙ) -> str:
    """Зачёркивание от руки — фоном самой строки, а не отдельным слоем поверх ячейки.

    Слой поверх ложился по центру ячейки: у строки в два ряда он проходил между рядами.
    Фон строчного элемента браузер рисует для каждой строки отдельно, поэтому штрих идёт
    по каждой строке и ровно по её середине.
    """
    from urllib.parse import quote
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 12' preserveAspectRatio='none'>"
           f"<path d='{лента(зерно)}' fill='{цвет}' opacity='.85'/></svg>")
    # Кодируется всё: кавычки и решётки цвета внутри адреса ломают атрибут style.
    # Положение — в долях кегля от верха строки, а не в процентах её высоты: проценты считаются
    # от «высота строки минус высота фона», и на строке в два ряда штрих падал на границу между
    # рядами — выглядел подчёркиванием. 0.40em от верха при высоте 0.42em кладёт ленту по буквам.
    return ("background-image:url(data:image/svg+xml,%s);background-repeat:no-repeat;"
            "background-size:100%% 0.42em;background-position:0 0.40em" % quote(svg, safe=""))


def обводка(зерно: str, цвет: str = КРАСНЫЙ, оборот: float = 1.12) -> str:
    """Овал от руки вокруг блока: та же лента, свёрнутая в кольцо (remocn Scribble Circle)."""
    import math
    точек, верх, низ = 64, [], []
    for i in range(точек + 1):
        д = i / точек
        угол = -1.9 + 2 * math.pi * оборот * д
        r = 1 + 0.035 * _шум(зерно + "r", i // 4)
        толщина = 0.012 + 0.03 * (0.25 + 0.75 * (1 - abs(2 * д - 1)) ** 0.6)
        for список, знак in ((верх, 1), (низ, -1)):
            rx, ry = (0.47 + знак * толщина) * r, (0.42 + знак * толщина * 1.4) * r
            список.append((50 + 100 * rx * math.cos(угол), 50 + 100 * ry * math.sin(угол)))
    путь = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in верх)
    путь += " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(низ)) + " Z"
    # SVG без явных размеров тянется по пропорциям viewBox и раздувается, поэтому он внутри
    # блока с заданными краями, а сам занимает его целиком.
    return (f"<span class=обводка><svg viewBox='0 0 100 100' preserveAspectRatio=none aria-hidden=true "
            f"style='display:block;width:100%;height:100%;overflow:visible'>"
            f"<path d='{путь}' fill='{цвет}' opacity='.9'/></svg></span>")


def стрелка(цвет: str = ЛАЙМ) -> str:
    """Стрелка от руки (remocn Ink Arrow): дуга лентой и два пера наконечника."""
    дуга = ("M6,14 C26,6 52,6 74,20 C86,28 92,44 90,62")
    return (f"<span class=стрелка><svg viewBox='0 0 100 100' fill=none stroke='{цвет}' stroke-linecap=round "
            f"style='display:block;width:100%;height:100%'>"
            f"<path d='{дуга}' stroke-width='5.5'/>"
            f"<path d='M78,50 L90,64 L97,46' stroke-width='5'/></svg></span>")


def страница(тело: str, доля: float, класс: str = "") -> str:
    """Своё CSS поверх стилевого, плюс JetBrains — им набран промпт в стеклянном окне."""
    шрифт = стиль.фейсы(("JB", "jetbrains-400", 400))
    return р.страница(тело, доля, класс).replace("</style>", CSS + шрифт + "</style>", 1)


def шапка(тонко: str, крупно: str, верх: int = 190) -> str:
    return (f"<div class=черта data-блок style='top:{верх - 60}px'></div>"
            f"<div class=шапка data-блок style='top:{верх}px'><div class=тонко data-fit>{тонко}</div>"
            f"<div class='крупно лайм' data-fit>{крупно}</div></div>")


def шпаргалка(к: dict, доля: float) -> str:
    """Две колонки по рядам: у каждой пары одна высота, даже если справа три строки, а слева одна."""
    нумер = к.get("нумерация", False)
    ряды = [f"<div class='заглавие нет'><span class=метка>✕</span>{к['нет']}</div>",
            f"<div class='заглавие да'><span class=метка>✓</span>{к['да']}</div>"]
    for н, (плохо, хорошо) in enumerate(к["пары"], 1):
        номер = f"<span class=номер>{н}.</span> " if нумер else ""
        зерно = f"{к['тонко']}-{н}"
        # Левая фраза — всегда в одну строку: Chrome не рисует фон построчно даже с
        # box-decoration-break:clone, и на переносе штрих доставался только первой строке.
        # Длинная фраза ужимается кеглем, а не переносится.
        знаков = len(плохо) + (4 if нумер else 0)
        свой = КЕГЛЬ if знаков <= 22 else КЕГЛЬ - 4 if знаков <= 28 else КЕГЛЬ - 7
        ряды.append(f"<div class='фраза нет'><span class=метка>✕</span>"
                    f"<span class=одной style=\"font-size:{свой}px;{штрих(зерно)}\">{номер}{плохо}</span></div>")
        ряды.append(f"<div class='фраза да'><span class=метка>✓</span><div>{номер}{хорошо}</div></div>")
    return страница(шапка(к["тонко"], к["крупно"], 170)
                    + f"<div class=шпаргалка data-блок>{''.join(ряды)}</div>", доля, "мелко")


def обложка_кот(о: dict, доля: float) -> str:
    тонко = "".join(f"<div class=тонко data-fit>{с}</div>" for с in о["тонко"])
    крупно = "".join(f"<div class='крупно лайм' data-fit>{с}</div>" for с in о["крупно"])
    return страница(
        f"<div class=ореол style='left:700px;top:1100px;width:1000px;height:1000px;background:rgba({ЛАЙМ_RGB},.18)'></div>"
        f"{кот(о["кот"], 860, left=860, top=1220)}"
        f"<div class=черта data-блок style='top:190px'></div><div class=текст data-блок>{тонко}{крупно}</div>"
        f"<div class=облачко data-блок>{о['облачко']}</div>", доля, "обложка обл-а")


def обложка_маркер(о: dict, доля: float) -> str:
    return страница(
        f"<div class=гигант data-блок>{о['число']}</div>"
        f"{кот(о["кот"], 640, left=1110, top=640)}"
        f"<div class=текст data-блок><div class=тонко data-fit>{о['тонко']}</div>"
        f"<div class=маркер data-fit>{о['маркер']}</div></div>", доля, "обложка обл-б")


def обложка_сравнение(о: dict, доля: float) -> str:
    return страница(
        шапка(о["тонко"], о["крупно"], 220)
        + f"<div class=блик style='left:60px;top:900px;width:900px;height:700px'></div>"
          f"<div class=сравнение data-блок>"
          f"<div class='плашка нет'><small><span class=метка>✕</span>Так пишут все</small>"
          f"<span class=мишень><b>{о['плохо']}</b>{обводка('обложка')}</span></div>"
          f"{стрелка()}"
          f"<div class=окно><div class=верхушка><span class=точка></span><span class=точка></span>"
          f"<span class=точка></span><span class=имя>{о.get('окно', 'промпт')}</span></div>"
          f"<div class='код{' размыто' if о.get('размыть') else ''}'>{о['хорошо']}</div></div>"
          + (f"<div class=листай>{о['листай']}</div>" if о.get("листай") else "") + "</div>",
        доля, "обложка обл-в")


def финал(ф: dict) -> str:
    return страница(
        f"<div class=ореол style='left:900px;top:1150px;width:900px;height:900px;background:rgba({ЛАЙМ_RGB},.16)'></div>"
        f"{кот(ф['кот'], 820, left=930, top=1000)}"
        f"<div class=черта data-блок style='top:180px'></div>"
        f"<div class=верх data-блок><div class='крупно лайм' data-fit>{ф['крупно']}</div>"
        f"<div class=тонко data-fit>{ф['тонко']}</div></div>"
        f"<div class=зов data-блок>{ф['зов']}<small>{ф['под']}</small></div>", 1.0, "фин")


def main():
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text(encoding="utf-8"))
    р.П = П                                  # рисовать.почему читает свой глобальный П
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    всего = len(П["шпаргалки"]) + 3
    обложки = {"кот": lambda: обложка_кот(П["обложка"], 1 / всего),
               "маркер": lambda: обложка_маркер(П["обложка_маркер"], 1 / всего),
               "сравнение": lambda: обложка_сравнение(П["обложка_сравнение"], 1 / всего)}
    главная = П.get("главная", "кот")
    запасные = [и for и in ("кот", "маркер", "сравнение") if и != главная]
    кадры = [("01", обложки[главная]())]
    кадры += [(f"{н:02d}", шпаргалка(к, н / всего)) for н, к in enumerate(П["шпаргалки"], 2)]
    кадры.append((f"{всего - 1:02d}", р.почему((всего - 1) / всего)))
    кадры.append((f"{всего:02d}", финал(П["финал"])))
    кадры += [(f"обложка-{н}", обложки[и]()) for н, и in enumerate(запасные, 2)]
    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        html = html.replace("</body>", f"<script>{р.ЗАМЕР}</script></body>")
        снимок = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", ошибки, flush=True)
            continue
        with Image.open(снимок) as к:
            к.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок)
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", браузер.замерить(html, W, H), flush=True)
    if только or not П.get("папка"):
        return
    стол = СТОЛ / П["папка"]
    стол.mkdir(parents=True, exist_ok=True)
    for имя, _ in кадры:
        with Image.open(выход / f"{имя}.png") as к:
            к.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(П["подпись"], encoding="utf-8")
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
