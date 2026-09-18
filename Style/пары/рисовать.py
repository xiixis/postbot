# -*- coding: utf-8 -*-
"""Фото-Карусель, стиль «пары»: платный сервис и его бесплатный двойник на одном кадре.

Что рисовать, лежит в файле поста: `python3 рисовать.py посты/<пост>.json [02 05]`.
Номера перерисовывают только их; без номеров кадры ещё и уезжают JPG 1080×1440 на стол,
в папку из поля «папка», вместе с подписью.

Ход референса @mike.mozg (обложка → пары «бесплатно | платно» → почему не всё
бесплатное одинаковое → «сохрани») в нашем виде: тёмный грунт, лайм вместо красного,
знак и полоса, кот вместо робота. Значки — настоящие, с сайтов самих сервисов, в родных
цветах. Шрифты и картинки встроены данными — по file:// Chrome их молча не рисует.
"""
import json, sys, time
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402  фирменное общее: лайм, шрифты, знак с полосой, кот, запас
from стиль import W, H, СТОЛ, ЛАЙМ_RGB, ЛАЙМ, данные, кот  # noqa: E402
import браузер  # noqa: E402  один живой Chrome постбота (путь положил стиль)
from PIL import Image  # noqa: E402

П: dict = {}

ГРУНТ, ТЕКСТ, ТИХИЙ = "#0B0C0A", "#EEF0E8", "#A3A69A"


def фейсы() -> str:
    """Узкий Oswald под слово-акцент, Manrope под тонкую строку и имена, Golos под текст."""
    return стиль.фейсы(("Os", "oswald-600", 600), ("Mn", "manrope-400", 400),
                       ("Mn", "manrope-800", 800), ("Golos", "golos-400", 400),
                       ("Golos", "golos-700", 700), латиница=стиль.ЛАТИНИЦА + ",U+20AC")
САМОЛЁТ = ("<svg viewBox='0 0 24 24' fill='currentColor'><path d='M21.6 3.2 2.9 10.4c-1.3.5-1.3 "
           "1.2-.2 1.6l4.8 1.5 1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8"
           "l3.1-14.7c.3-1.3-.5-1.9-1.4-1.1zM8.9 13.1l9.6-6c.5-.3.9-.1.5.2l-8.2 7.4-.3 3.4-1.6-5z'/></svg>")

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{ГРУНТ};color:{ТЕКСТ};font-family:Golos,sans-serif;position:relative;
  -webkit-font-smoothing:antialiased}}
.свет{{position:absolute;inset:0;z-index:0;
  background:radial-gradient(ellipse 70% 45% at 50% 0%,rgba({ЛАЙМ_RGB},.07),transparent 70%),
             radial-gradient(ellipse 80% 40% at 50% 100%,rgba(255,255,255,.04),transparent 70%)}}
.зерно{{position:absolute;inset:0;z-index:0;opacity:.05;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>")}}
{стиль.знак_и_полоса_css()}.черта{{position:absolute;left:120px;width:130px;height:12px;background:{ЛАЙМ};z-index:3;
  box-shadow:0 0 30px rgba({ЛАЙМ_RGB},.35)}}
.тонко{{font-family:Mn;font-weight:400;text-transform:uppercase;letter-spacing:-.01em;
  white-space:nowrap;line-height:1.02}}
.крупно{{font-family:Os;font-weight:600;text-transform:uppercase;white-space:nowrap;line-height:.98;
  letter-spacing:-.005em}}
.лайм{{color:{ЛАЙМ}}}
.кот{{position:absolute;z-index:1}}

/* Пара */
.шапка{{position:absolute;left:120px;right:110px;top:260px;z-index:3}}
.шапка .тонко{{font-size:120px}}
.шапка .крупно{{font-size:250px;margin-top:6px}}
.колонка{{position:absolute;top:735px;width:700px;height:960px;z-index:3;text-align:center}}
.пилюля{{display:inline-flex;align-items:center;gap:22px;height:96px;padding:0 46px;border-radius:48px;
  border:3px solid rgba(238,240,232,.28);font-family:Mn;font-weight:400;font-size:50px;
  letter-spacing:.04em;text-transform:uppercase}}
.пилюля i{{width:22px;height:22px;border-radius:50%;display:block}}
.плитка{{position:relative;width:500px;height:500px;margin:60px auto 0;border-radius:118px}}
.плитка .лицо{{position:absolute;inset:0;border-radius:118px;overflow:hidden;display:grid;
  place-items:center;z-index:2}}
.плитка .лицо img.весь{{width:100%;height:100%;object-fit:cover;display:block}}
.плитка .лицо img.знак-в{{width:58%;height:58%;object-fit:contain;display:block}}
.плитка .лицо::after{{content:"";position:absolute;inset:0;border-radius:118px;pointer-events:none;
  box-shadow:inset 0 3px 0 rgba(255,255,255,.35),inset 0 0 0 3px rgba(255,255,255,.16),
             inset 0 -10px 24px rgba(0,0,0,.25)}}
.плитка .толщина{{position:absolute;left:0;right:0;top:22px;bottom:-22px;border-radius:118px;z-index:1;
  background:linear-gradient(#3A3C36,#141512);box-shadow:0 0 0 2px rgba(255,255,255,.08)}}
.плитка .отсвет{{position:absolute;left:-40px;right:-40px;top:430px;height:200px;z-index:0;
  border-radius:50%;filter:blur(38px);opacity:.55}}
.тёмная .лицо{{background:linear-gradient(160deg,#1E201C,#0A0B09)}}
.светлая .лицо{{background:linear-gradient(160deg,#FFFFFF,#E4E5E0)}}
.светлая .толщина{{background:linear-gradient(#C9CAC4,#8D8E88)}}
.имя{{font-family:Mn;font-weight:800;font-size:92px;letter-spacing:-.03em;margin-top:70px;
  white-space:nowrap;line-height:1.1}}
.подпись{{padding:0 40px}}
.строка{{font-size:54px;color:{ТИХИЙ};margin-top:10px;white-space:nowrap}}
.как{{display:inline-block;margin-top:30px;font-weight:700;font-size:48px;color:#1A2006;
  background:{ЛАЙМ};padding:10px 34px;border-radius:40px;white-space:nowrap}}
.как.сам{{background:transparent;color:{ЛАЙМ};box-shadow:inset 0 0 0 3px {ЛАЙМ}}}
.раздел{{position:absolute;left:809px;top:745px;width:2px;height:960px;z-index:2;
  background:linear-gradient(transparent,rgba(238,240,232,.25) 15%,rgba(238,240,232,.25) 85%,transparent)}}

/* Обложка */
.обложка .текст{{position:absolute;left:120px;right:110px;top:340px;z-index:3}}
.обложка .тонко{{font-size:140px;line-height:1.04}}
.обложка .крупно{{font-size:230px;line-height:1.1}}
.обложка .крупно:first-of-type{{margin-top:22px}}
.ниже{{display:flex;align-items:center;gap:40px;margin-top:70px;font-family:Mn;font-size:62px;
  text-transform:uppercase;letter-spacing:.02em}}
.ниже svg{{width:230px;height:40px}}
.ореол{{position:absolute;z-index:0;border-radius:50%;filter:blur(90px)}}

/* Почему */
.почему .шапка .тонко{{font-size:118px;line-height:1.08}}
.абзацы{{position:absolute;left:120px;width:980px;top:610px;z-index:3}}
.абзац{{font-size:66px;line-height:1.22;padding:46px 0}}
.абзац b{{color:{ЛАЙМ};font-weight:700}}
.линия{{height:3px;background:linear-gradient(90deg,{ЛАЙМ},rgba({ЛАЙМ_RGB},.3) 30%,transparent 90%);
  box-shadow:0 0 18px rgba({ЛАЙМ_RGB},.5)}}

/* Финал */
.финал .верх{{position:absolute;left:120px;right:110px;top:190px;z-index:3}}
.финал .крупно{{font-size:250px}}
.финал .крупно+.крупно{{font-size:172px;margin-top:10px}}
.телефон{{position:absolute;left:120px;top:760px;width:640px;height:980px;border-radius:110px;
  border:14px solid #2C2F25;overflow:hidden;z-index:3;
  box-shadow:0 0 0 3px rgba({ЛАЙМ_RGB},.35),0 0 90px rgba({ЛАЙМ_RGB},.12);
  background:linear-gradient(#1B1D17,#141510)}}
.бровь{{position:absolute;left:50%;top:24px;transform:translateX(-50%);width:200px;height:56px;
  border-radius:28px;background:#050605}}
.канал{{position:absolute;left:40px;right:40px;top:120px;height:116px;border-radius:58px;
  background:#23261E;display:flex;align-items:center;gap:24px;padding:0 26px}}
.канал .ава{{width:76px;height:76px;border-radius:50%;background:{ЛАЙМ};display:grid;place-items:center}}
.канал .ава img{{height:42px;filter:brightness(0)}}
.канал .текст{{font-size:42px;font-weight:700;line-height:1.1}}
.канал .текст span{{display:block;font-size:30px;font-weight:400;color:#9DA291}}
.пост{{position:absolute;left:40px;right:40px;height:180px;border-radius:38px;background:#23261E;
  padding:28px 36px;display:flex;flex-direction:column;justify-content:center;gap:16px}}
.пост .мутно{{font-family:Mn;font-weight:800;font-size:50px;letter-spacing:-.02em;
  filter:blur(12px);white-space:nowrap}}
.пост .мутно b{{color:{ЛАЙМ}}}
.пост .ссылка{{display:flex;align-items:center;gap:14px;font-size:34px;color:{ЛАЙМ};font-weight:700}}
.пост .ссылка svg{{width:36px;height:36px}}
.справа{{position:absolute;left:830px;top:830px;width:680px;z-index:3;text-align:left;
  font-family:Os;font-weight:600;font-size:96px;line-height:1.1;text-transform:uppercase}}
.справа div{{white-space:nowrap}}
.справа b{{color:{ЛАЙМ};font-weight:600}}
.справа .под{{font-family:Golos;font-weight:400;text-transform:none;font-size:60px;color:{ТИХИЙ};
  margin-top:30px;line-height:1.25;white-space:normal}}
.стрелка{{position:absolute;left:900px;top:1400px;width:330px;height:300px;z-index:4;color:{ТЕКСТ}}}
"""

СТРЕЛКА_ВПРАВО = ("<svg viewBox='0 0 230 40' fill='none' stroke='currentColor' stroke-width='5' "
                  "stroke-linecap='round'><path d='M4 20H222M200 4l22 16-22 16'/></svg>")
СТРЕЛКА_К_ТЕЛЕФОНУ = ("<svg viewBox='0 0 330 300' fill='none' stroke='currentColor' stroke-width='9' "
                      "stroke-linecap='round' stroke-linejoin='round'><path d='M250 20c50 90 20 200-190 240'/>"
                      "<path d='M110 215 55 262l70 22'/></svg>")


def страница(тело: str, доля: float, класс: str = "") -> str:
    return (f"<!doctype html><meta charset=utf-8><style>{фейсы()}{CSS}</style>"
            f"<body class='{класс}'><div class=свет></div><div class=зерно></div>{тело}"
            f"{стиль.знак_и_полоса(доля)}</body>")


def обложка(доля: float) -> str:
    о = П["обложка"]
    тонко = "".join(f"<div class=тонко>{с}</div>" for с in о["тонко"])
    а, б = о["крупно"]
    return страница(
        f"<div class=ореол style='left:900px;top:1050px;width:900px;height:1000px;"
        f"background:rgba({ЛАЙМ_RGB},.22)'></div>"
        f"<div class=ореол style='left:1200px;top:1150px;width:520px;height:600px;"
        f"background:rgba(238,240,232,.10)'></div>"
        f"{кот(о['кот'], 960, left=1110, top=1150)}"
        f"<div class=черта data-блок style='top:240px'></div>"
        f"<div class=текст data-блок>{тонко}<div class='крупно лайм' data-fit>{а}</div><div class=крупно data-fit>{б}</div>"
        f"<div class=ниже>{о['ниже']}{СТРЕЛКА_ВПРАВО}</div></div>", доля, "обложка")


def плитка(с: dict) -> str:
    вид = с["плитка"]
    img = данные(ТУТ / "значки" / с["значок"])
    стиль = f"width:{с.get('размер', 58)}%;height:{с.get('размер', 58)}%"
    фильтр = f" style='{стиль}{';filter:invert(1)' if с.get('инверсия') else ''}'"
    лицо = (f"<img class=весь src='{img}'>" if вид == "во весь"
            else f"<img class=знак-в src='{img}'{фильтр}>")
    return (f"<div class='плитка {вид}' data-блок><div class=отсвет style='background:{с['свет']}'></div>"
            f"<div class=толщина></div><div class=лицо>{лицо}</div></div>")


def колонка(с: dict, бесплатно: bool, left: int) -> str:
    метка = ("<i style='background:%s;box-shadow:0 0 14px %s'></i>Бесплатно" % (ЛАЙМ, ЛАЙМ) if бесплатно
             else "<i style='background:#8E9186'></i>Платно")
    как = ""
    if бесплатно:
        как = ("<div class='как сам'>ставишь сам</div>" if с["как"] == "сам"
               else "<div class=как>работает сразу</div>")
    return (f"<div class=колонка style='left:{left}px'><div class=пилюля data-блок>{метка}</div>"
            f"{плитка(с)}<div class=подпись data-блок><div class=имя data-fit>{с['имя']}</div>"
            f"<div class=строка>{с['строка']}</div>{как}</div></div>")


def пара(п: dict, доля: float) -> str:
    return страница(
        f"<div class=черта data-блок style='top:180px'></div>"
        f"<div class=шапка data-блок><div class=тонко data-fit>{п['тонко']}</div>"
        f"<div class='крупно лайм' data-fit>{п['крупно']}</div></div>"
        f"<div class=раздел></div>"
        f"{колонка(п['бесплатно'], True, 60)}{колонка(п['платно'], False, 860)}", доля)


def почему(доля: float) -> str:
    п = П["почему"]
    абзацы = "<div class=линия></div>".join(f"<div class=абзац>{а}</div>" for а in п["абзацы"])
    return страница(
        f"<div class=ореол style='left:1100px;top:1100px;width:700px;height:800px;"
        f"background:rgba({ЛАЙМ_RGB},.16)'></div>"
        f"{кот(п['кот'], 720, left=1150, top=1000)}"
        f"<div class=черта data-блок style='top:180px'></div>"
        f"<div class=шапка data-блок>{''.join(f'<div class=тонко data-fit>{с}</div>' for с in п['заголовок'])}</div>"
        f"<div class=абзацы data-блок>{абзацы}</div>", доля, "почему")


ЦЕПЬ = ("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' "
        "stroke-linecap='round' stroke-linejoin='round'><path d='M10 13a5 5 0 0 0 7.54.54l3-3"
        "a5 5 0 0 0-7.07-7.07l-1.72 1.71'/><path d='M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 "
        "7.07 7.07l1.71-1.71'/></svg>")


def финал(доля: float) -> str:
    ф = П["финал"]
    а, б = ф["крупно"]
    посты = "".join(
        f"<div class=пост style='top:{280 + н * 210}px'><div class=мутно>{х}<b>{у}</b></div>"
        f"<div class=ссылка>{ЦЕПЬ}инструмент №{н + 1}</div></div>"
        for н, (х, у) in enumerate(ф["мутно"]))
    return страница(
        f"<div class=ореол style='left:60px;top:900px;width:900px;height:800px;"
        f"background:rgba({ЛАЙМ_RGB},.10)'></div>"
        f"<div class=верх data-блок><div class='крупно лайм' data-fit>{а}</div><div class=крупно data-fit>{б}</div></div>"
        f"<div class=телефон data-блок><div class=бровь></div>"
        f"<div class=канал><div class=ава><img src='{стиль.ЛОГО}'></div>"
        f"<div class=текст>Наш канал<span>Telegram</span></div></div>{посты}</div>"
        f"<div class=справа data-блок>{''.join(f'<div data-fit>{с}</div>' for с in ф['справа'])}<div class=под>{ф['под']}</div></div>"
        f"<div class=стрелка data-блок>{СТРЕЛКА_К_ТЕЛЕФОНУ}</div>", доля, "финал")


# Подгонка: строка с data-fit ужимается, пока не влезет в свою ширину (не больше 10 шагов по 4%).
# Потом запас между блоками data-блок — общий замер из стиль.py.
ЗАМЕР = стиль.ЗАПАС_JS + """document.fonts.ready.then(() => {
  const ужато = [];
  for (const el of document.querySelectorAll('[data-fit]')) {
    const ст = getComputedStyle(el.parentElement);
    const поле = el.parentElement.clientWidth - parseFloat(ст.paddingLeft) - parseFloat(ст.paddingRight);
    el.style.display = 'inline-block';
    let шаг = 0;
    while (el.scrollWidth > поле && шаг < 10) {
      el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * 0.96) + 'px'; шаг++;
    }
    el.style.display = 'block';
    if (шаг) ужато.push(el.textContent + ' ×' + Math.pow(0.96, шаг).toFixed(2));
  }
  document.body.setAttribute("data-замер", JSON.stringify({
    шрифты: ![...document.fonts].some(f => f.status === "error" || f.status === "loading"),
    ужато, ...запас_кадра('')}));
})"""


def main():
    global П
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text())
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    всего = len(П["пары"]) + 3
    кадры = [("01", обложка(1 / всего))]
    кадры += [(f"{н:02d}", пара(п, н / всего)) for н, п in enumerate(П["пары"], 2)]
    кадры.append((f"{всего - 1:02d}", почему((всего - 1) / всего)))
    кадры.append((f"{всего:02d}", финал(1.0)))
    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        html = html.replace("</body>", f"<script>{ЗАМЕР}</script></body>")
        снимок = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", ошибки, flush=True)
            continue
        with Image.open(снимок) as к:
            к.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок)
        замер = браузер.замерить(html, W, H)
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", замер, flush=True)
    if только or not П.get("папка"):
        return
    стол = СТОЛ / П["папка"]
    стол.mkdir(parents=True, exist_ok=True)
    for имя, _ in кадры:
        with Image.open(выход / f"{имя}.png") as к:
            к.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(П["подпись"])
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
