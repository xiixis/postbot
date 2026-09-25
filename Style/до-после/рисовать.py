# -*- coding: utf-8 -*-
"""Фото-Карусель, стиль «до-после»: промпт, маленькая плитка «до» и крупная «после».

Что рисовать, лежит в файле поста: `python3 рисовать.py посты/<пост>.json [02 05]`.
Номера перерисовывают только их; без номеров кадры ещё и уезжают JPG 1080×1440 на стол.

Ход референса @skilzhub (Instagram DdJl4xIE53S): фото-обложка с гигантским заголовком и
рукописным словом поверх → кадры «пилюля + имя приёма, до → после, текст промпта» на
светло-сером → белый финал «подпишись». Размеры сняты с его кадров 1440×1920 и
умножены на 1,125. Цвета собраны в ТОН: шаг 1 — тон референса, шаг 2 — наш.
"""
import json, sys, time
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
from стиль import W, H, СТОЛ, данные  # noqa: E402
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

П: dict = {}

# Тон кадра. «референс» — значения, снятые пипеткой с его кадров.
ТОНЫ = {
    "референс": {"грунт": "#EEEEEE", "текст": "#000000", "пилюля": "#047C04", "на_пилюле": "#FFFFFF",
                 "финал": "#FFFFFF", "финал_акцент": "#482C94", "закладка": "#FF9700",
                 "рука": "#DDF20C", "метка": "#F8C000", "на_метке": "#000000",
                 "телеграм": "#229ED9"},
}
ТОН: dict = {}


ШРИФТЫ = ТУТ / "шрифты"


def фейсы() -> str:
    """Google Sans — шрифт самого референса (Google Fonts, OFL, переменный 400–700, есть
    кириллица); Bad Script — тонкое слитное письмо одной толщины, как «Viral» у автора."""
    css = []
    for семья, файл, вес in (("GS", "googlesans", "400 700"), ("Рука", "badscript", "400")):
        for набор, диапазон in (("latin", стиль.ЛАТИНИЦА), ("cyrillic", стиль.КИРИЛЛИЦА)):
            css.append(f"@font-face{{font-family:{семья};font-weight:{вес};font-display:block;"
                       f"src:url({данные(ШРИФТЫ / f'{файл}-{набор}.woff2', 'font/woff2')}) "
                       f"format('woff2');unicode-range:{диапазон}}}")
    return "\n".join(css)


ТЕЛЕГРАМ = (стиль.ПОСТБОТ / "assets/значки/telegram.svg").read_text(encoding="utf-8")


def свой_кот(имя: str, высота: int, класс: str = "кот", рядом: str = "", **где) -> str:
    """Кот, нарисованный под этот стиль (`кот.py`), из `коты/`: как `стиль.кот`, но не с полки поз."""
    import base64
    from io import BytesIO
    with Image.open(ТУТ / "коты" / f"{имя}.png") as и:
        и = и.convert("RGBA")
        и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
        буф = BytesIO()
        и.save(буф, "PNG")
    с = ";".join(f"{к}:{в}px" for к, в in где.items())
    рядом_ = f" data-рядом='{рядом}'" if рядом else ""
    return (f"<img class='{класс}' data-блок{рядом_} style='height:{высота}px;{с}' "
            f"src='data:image/png;base64,{base64.b64encode(буф.getvalue()).decode()}'>")


СТРЕЛКА = ("<svg viewBox='0 0 50 60' fill='none' stroke='currentColor' stroke-width='5' "
           "stroke-linecap='round' stroke-linejoin='round'><path d='M6 4l38 26L6 56'/></svg>")


def css() -> str:
    т = ТОН
    return f"""{фейсы()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{т['грунт']};color:{т['текст']};font-family:GS,sans-serif;position:relative;
  -webkit-font-smoothing:antialiased}}
.стрелка{{position:absolute;left:1519px;top:1050px;width:50px;height:60px;color:#222}}

/* Кадр-приём */
.приём{{position:absolute;left:0;right:0;top:376px;height:88px;display:flex;justify-content:center;
  align-items:center;gap:40px;white-space:nowrap}}
.пилюля{{background:{т['пилюля']};color:{т['на_пилюле']};font-weight:500;font-size:72px;line-height:1;
  height:82px;padding:0 18px;border-radius:24px;display:flex;align-items:center;letter-spacing:-.04em}}
.имя{{font-size:120px;line-height:1;letter-spacing:-.062em;font-weight:500}}
.плитка{{position:absolute;overflow:hidden;background:#fff}}
.плитка img{{width:100%;height:100%;display:block;object-fit:cover}}
.до{{left:176px;width:365px;height:360px;top:917px;border-radius:80px}}
.до img{{object-fit:contain;padding:22px}}
.до.фото-до img{{object-fit:cover;padding:0}}
.после{{left:586px;width:801px;border-radius:125px}}
.метка{{position:absolute;font-size:45px;font-weight:500;letter-spacing:-.02em;transform:translateX(-50%);white-space:nowrap}}
.промпт{{position:absolute;left:129px;right:120px;top:1628px;font-size:45px;line-height:1.2;
  letter-spacing:-.035em}}
.промпт b{{font-weight:700}}

/* Обложка */
.обложка{{background:#1F519A}}
.фото{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.лого{{position:absolute;left:111px;top:112px;height:135px}}
.угол{{position:absolute;right:108px;top:112px;color:#fff;font-size:40px}}
/* Заголовок как у автора: один переход на оба слова по диагонали, от чисто белого слева
   сверху к полупрозрачному справа снизу — сквозь буквы просвечивает небо. */
.заголовок{{position:absolute;left:50%;top:540px;transform:translateX(-50%);text-align:center;
  font-weight:700;letter-spacing:-.045em;line-height:.8;width:max-content;
  background:linear-gradient(155deg,#fff 28%,rgba(255,255,255,.93) 52%,rgba(230,240,252,.72) 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent}}
.заголовок div{{font-size:290px;white-space:nowrap}}
.рука{{position:absolute;left:0;right:0;top:395px;text-align:center;font-family:Рука;font-weight:400;
  font-size:185px;color:{т['рука']};transform:rotate(-8deg) translateX(30px);z-index:2;white-space:nowrap;
  line-height:1;letter-spacing:-.01em}}
.часть{{position:absolute;left:50%;top:800px;transform:translateX(-62%);z-index:2;background:{т['метка']};
  color:{т['на_метке']};font-weight:700;font-size:58px;height:92px;padding:0 26px;border-radius:30px;
  display:flex;align-items:center;letter-spacing:-.03em;white-space:nowrap}}
.обложка .стрелка{{color:#fff}}
/* «Симба»: кот поднимает плитку над головой — заголовок уходит выше плитки, в одну строку. */
.симба .заголовок{{top:300px;line-height:1;filter:drop-shadow(0 8px 22px rgba(0,30,90,.45))}}
.симба .заголовок div{{font-size:200px;display:inline}}
.симба .заголовок div+div{{margin-left:.22em}}
.симба .рука{{top:150px;font-size:150px;transform:rotate(-7deg) translateX(-150px)}}
.симба .часть{{top:215px;left:auto;right:170px;transform:rotate(-4deg)}}

/* Финал */
.финал{{background:{т['финал']}}}
.финал .лого{{left:50%;transform:translateX(-50%);top:146px;height:150px;
  filter:brightness(.55) saturate(1.2)}}
.зов{{position:absolute;left:250px;right:110px;top:740px;font-size:230px;line-height:.86;
  letter-spacing:-.05em;font-weight:500}}
.зов div{{white-space:nowrap}}
.зов .акцент{{color:{т['телеграм']}}}
.сохрани{{position:absolute;left:250px;top:1222px;display:flex;gap:32px;align-items:center}}
.тг svg{{width:126px;height:126px;fill:{т['телеграм']};display:block}}
.кнопка{{height:126px;padding:0 40px;border:2.5px solid #9A9A9A;border-radius:26px;display:flex;
  align-items:center;font-size:66px;font-weight:500;letter-spacing:-.03em;white-space:nowrap}}
.низ{{position:absolute;left:0;right:0;top:1890px;text-align:center;font-size:40px;color:#222}}

/* Кот. За плиткой «После» — под ней по слою, отражён: срез позы прячется за край плитки. */
.кот{{position:absolute;z-index:1}}
.плитка{{z-index:2}}
.кот.над-краем{{z-index:3;filter:drop-shadow(0 10px 14px rgba(0,0,0,.25))}}
.финал .кот{{z-index:3}}

/* Финал-сцена: как обложка «сцена», но кот с логотипом Telegram в его голубом свете.
   Текст чёрный — по слову владельца не синий; белый на светло-голубом верху сцены не читался. */
.финал-сцена{{background:#0B2C45}}
.финал-сцена .лого{{left:50%;transform:translateX(-50%);top:120px;height:130px}}
.финал-сцена .зов{{left:0;right:0;top:330px;text-align:center;color:#111;font-weight:700;font-size:210px;
  line-height:.9;letter-spacing:-.05em}}
.финал-сцена .зов .акцент{{color:#111}}
.финал-сцена .сохрани{{left:50%;transform:translateX(-50%);top:790px;background:#fff;border-radius:70px;
  padding:14px 46px 14px 16px;box-shadow:0 20px 50px rgba(0,20,50,.3)}}
.финал-сцена .кнопка{{border:none;height:110px;padding:0;color:#111}}
.финал-сцена .тг svg{{width:110px;height:110px}}

/* Обложка «цифра»: гигантская 5 на грунте карусели, подпись с маркером, три «после». */
.цифра{{background:{т['грунт']}}}
.цифра .пять{{position:absolute;left:120px;top:250px;font-size:1150px;font-weight:700;line-height:.8;
  letter-spacing:-.07em}}
.цифра .подпись{{position:absolute;left:830px;right:100px;top:420px;font-size:150px;font-weight:700;
  line-height:.98;letter-spacing:-.05em}}
.цифра .подпись span{{background:linear-gradient(transparent 52%,{т['метка']} 52%,{т['метка']} 92%,transparent 92%);
  padding:0 10px;margin:0 -10px;-webkit-box-decoration-break:clone}}
.цифра .ещё{{position:absolute;left:836px;top:1080px;font-size:80px;font-weight:500;letter-spacing:-.03em}}
.цифра .ещё b{{background:{т['пилюля']};color:{т['на_пилюле']};font-weight:500;padding:4px 18px;border-radius:18px}}
.ряд{{position:absolute;left:110px;right:110px;top:1330px;display:flex;gap:40px}}
.ряд .плитка{{position:relative;flex:1;height:440px;border-radius:90px}}
.цифра .лого{{top:auto;bottom:130px;left:50%;transform:translateX(-50%);height:110px;
  filter:brightness(.55) saturate(1.2)}}

/* Обложка «сцена»: картинка «после» на весь кадр, текст прямо на ней, кот. */
.сцена{{background:#111}}
/* Сцена нарисована с котом и пустым светлым верхом: текст чёрный прямо по золотому свету. */
.сцена .текст{{position:absolute;left:120px;right:110px;top:320px;z-index:2;color:{т['текст']}}}
.сцена .верх{{font-size:66px;font-weight:500;letter-spacing:-.03em}}
.сцена .крупно{{font-size:196px;font-weight:700;line-height:.92;letter-spacing:-.05em;margin-top:30px}}
.сцена .крупно em{{font-style:normal;color:{т['на_пилюле']};background:{т['пилюля']};border-radius:40px;
  padding:0 28px 14px;margin-left:-6px;display:inline-block;line-height:1}}
.сцена .рука2{{font-family:Рука;font-size:130px;color:{т['текст']};transform:rotate(-6deg);
  margin:30px 0 0 600px;line-height:1;white-space:nowrap}}
.сцена .лого{{filter:brightness(.45) saturate(1.3)}}
.сцена .лого{{z-index:3}}
.сцена .кот{{z-index:3}}
"""


def страница(тело: str, класс: str = "", стрелка: bool = True) -> str:
    return (f"<!doctype html><html><head><meta charset=utf-8><style>{css()}</style></head>"
            f"<body class='{класс}'>{тело}{f'<div class=стрелка>{СТРЕЛКА}</div>' if стрелка else ''}</body></html>")


def картинка(путь: str) -> str:
    return данные((ТУТ / путь).resolve() if not Path(путь).is_absolute() else Path(путь))


def обложка(фото: str = "") -> str:
    """Главная обложка. `фото` подменяет сцену: у «симбы» тот же заголовок на другом снимке."""
    о = П["обложка"]
    строки = "".join(f"<div data-блок>{с}</div>" for с in о["заголовок"])
    return страница(
        f"<img class=фото src='{картинка(фото or о['фото'])}'>"
        f"<img class=лого src='{стиль.ЛОГО}'>"
        f"<div class=заголовок>{строки}</div>"
        f"<div class=рука>{о['рука']}</div>"
        f"<div class=часть>{о['метка']}</div>", "обложка симба" if фото else "обложка")


def приём(п: dict) -> str:
    with Image.open(ТУТ / п["после"]) as к:
        ш, в = к.size
    высота = round(801 * min(в / ш, 1.0))
    верх = 1094 - высота // 2
    до_класс = " фото-до" if п.get("до_фото") else ""   # «до» — фото во всю плитку, не товар на белом
    # Кот выглядывает из-за верхней кромки «После»: лапы лежат на плитке, срез тела прячется за неё.
    # Правее подписи «После», чтобы её не закрыть.
    кот = (свой_кот("над-краем", 330, "кот над-краем", рядом="плитка", left=1100, top=верх - 262)
           if п.get("кот") else "")
    return страница(
        f"{кот}"
        f"<div class=приём data-блок><div class=пилюля>{П['пилюля']}</div><div class=имя>{п['имя']}</div></div>"
        f"<div class=метка style='left:358px;top:825px'>{П['до']}</div>"
        f"<div class='плитка до{до_класс}' data-блок><img src='{картинка(п['до'])}'></div>"
        f"<div class=метка style='left:986px;top:{верх - 92}px'>{П['после']}</div>"
        f"<div class='плитка после' style='top:{верх}px;height:{высота}px' data-блок>"
        f"<img src='{картинка(п['после'])}'></div>"
        f"<div class=промпт data-блок><b>{П['перед_промптом']}</b> «{п['промпт']}»</div>")


def финал() -> str:
    ф = П["финал"]
    if ф.get("фото"):   # сцена с котом и логотипом Telegram нарисована целиком, кот в неё не вставляется
        return страница(
            f"<img class=фото src='{картинка(ф['фото'])}'><img class=лого src='{стиль.ЛОГО}'>"
            f"<div class=зов data-блок><div>{ф['зов'][0]}</div><div class=акцент>{ф['зов'][1]}</div></div>"
            f"<div class=сохрани data-блок><div class=тг>{ТЕЛЕГРАМ}</div><div class=кнопка>{ф['кнопка']}</div></div>",
            "финал-сцена", стрелка=False)
    return страница(
        f"<img class=лого src='{стиль.ЛОГО}'>"
        f"<div class=зов data-блок><div>{ф['зов'][0]}</div><div class=акцент>{ф['зов'][1]}</div></div>"
        f"<div class=сохрани data-блок><div class=тг>{ТЕЛЕГРАМ}</div><div class=кнопка>{ф['кнопка']}</div></div>"
        + свой_кот("с-телефоном", 760, left=1060, top=1390),
        "финал", стрелка=False)


def обложка_цифра() -> str:
    о = П["обложка_цифра"]
    ряд = "".join(f"<div class='плитка'><img src='{картинка(к)}'></div>" for к in о["картинки"])
    return страница(
        f"<div class=пять data-блок>{о['цифра']}</div>"
        f"<div class=подпись data-блок>{о['подпись']}</div>"
        f"<div class=ещё data-блок><b>{о['метка']}</b></div>"
        f"<div class=ряд data-блок>{ряд}</div>"
        f"<img class=лого src='{стиль.ЛОГО}'>", "цифра")


def обложка_сцена() -> str:
    о = П["обложка_сцена"]
    return страница(
        f"<img class=фото src='{картинка(о['фото'])}'>"
        f"<img class=лого src='{стиль.ЛОГО}'>"
        f"<div class=текст data-блок><div class=верх>{о['верх']}</div>"
        f"<div class=крупно>{о['крупно']}</div><div class=рука2>{о['рука']}</div></div>", "сцена")


ЗАМЕР = стиль.ЗАПАС_JS + """document.fonts.ready.then(() => {
  document.body.setAttribute("data-замер", JSON.stringify({
    шрифты: ![...document.fonts].some(f => f.status === "error" || f.status === "loading"),
    ...запас_кадра('')}));
})"""


def main():
    global П, ТОН
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text(encoding="utf-8"))
    ТОН = ТОНЫ[П.get("тон", "референс")]
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    # Страница собирается только для заказанного кадра: картинки ещё может не быть.
    кадры = [("01", обложка)]
    кадры += [(f"{н:02d}", lambda п=п: приём(п)) for н, п in enumerate(П["приёмы"], 2)]
    кадры.append((f"{len(кадры) + 1:02d}", финал))
    # Ещё две обложки по правилу «три разные»: на стол уходят рядом, не в счёт карусели.
    if П.get("обложка_цифра"):
        кадры.append(("обложка-2", обложка_цифра))
    if П.get("обложка_сцена"):
        кадры.append(("обложка-3", обложка_сцена))
    if П.get("обложка_симба"):
        кадры.append(("обложка-4", lambda: обложка(П["обложка_симба"])))
    только = set(sys.argv[2:])
    for имя, собрать in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        html = собрать().replace("</body>", f"<script>{ЗАМЕР}</script></body>")
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
