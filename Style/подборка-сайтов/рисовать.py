# -*- coding: utf-8 -*-
"""Фото-Карусель, стиль «подборка сайтов»: обложка, по сайту на кадр, тёмный финал.

Что именно рисовать, лежит в файле поста: `python3 рисовать.py посты/<пост>.json [02 05]`.
Номера кадров перерисовывают только их; без номеров кадры ещё и уезжают JPG 1080×1440
на стол, в папку из поля «папка», вместе с подписью.

Скелет референса @zawetwarpp (имя сайта крупно, пояснение, скруглённый снимок, пилюля-ссылка,
тёмный финал с телефоном) в нашем виде: кремовый грунт и оливковый акцент
«каталога», знак и полоса, кот. Шрифты и картинки встроены данными — по file://
Chrome их молча не рисует.
"""
import base64, json, sys, time
from io import BytesIO
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402  фирменное общее: лайм, шрифты, знак с полосой, кот, запас
from стиль import W, H, СТОЛ, ЛАЙМ_RGB, ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ, данные, кот  # noqa: E402
import браузер  # noqa: E402
from PIL import Image  # noqa: E402

П: dict = {}

ГРУНТ, ЧЕРНИЛА, АКЦЕНТ, МЯГКИЙ = стиль.КРЕМ, "#12130E", стиль.ОЛИВА, "#3A3E33"


def картинка(путь: Path, обрезка=None, ширина=1500) -> str:
    """Снимок сайта ужатый до ширины кадра: 5-мегабайтный PNG странице ни к чему."""
    with Image.open(путь) as и:
        и = и.convert("RGB")
        if обрезка:
            и = и.crop(обрезка)
        и = и.resize((ширина, round(и.height * ширина / и.width)), Image.LANCZOS)
        буф = BytesIO()
        и.save(буф, "JPEG", quality=92)
        return "data:image/jpeg;base64," + base64.b64encode(буф.getvalue()).decode(), и.width / и.height


def фейсы() -> str:
    return стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                       ("Golos", "golos-700", 700))


ЦЕПЬ = ("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' "
        "stroke-linecap='round' stroke-linejoin='round'><path d='M10 13a5 5 0 0 0 7.54.54l3-3"
        "a5 5 0 0 0-7.07-7.07l-1.72 1.71'/><path d='M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 "
        "7.07 7.07l1.71-1.71'/></svg>")
САМОЛЁТ = ("<svg viewBox='0 0 24 24' fill='currentColor'><path d='M21.6 3.2 2.9 10.4c-1.3.5-1.3 "
           "1.2-.2 1.6l4.8 1.5 1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8"
           "l3.1-14.7c.3-1.3-.5-1.9-1.4-1.1zM8.9 13.1l9.6-6c.5-.3.9-.1.5.2l-8.2 7.4-.3 3.4-1.6-5z'/></svg>")

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{ГРУНТ};color:{ЧЕРНИЛА};font-family:Golos,sans-serif;position:relative;
  -webkit-font-smoothing:antialiased}}
{стиль.знак_и_полоса_css(светлый_грунт=True)}.тёмный .знак{{filter:drop-shadow(0 6px 20px rgba(0,0,0,.35))}}
.тёмный .полоса{{background:{ЛАЙМ};box-shadow:0 0 39px rgba({ЛАЙМ_RGB},.45)}}

/* Кадр сайта */
.шапка{{position:absolute;left:0;right:0;top:150px;text-align:center}}
.имя{{font-family:Onest;font-weight:800;font-size:168px;line-height:1.05;letter-spacing:-.035em;
  white-space:nowrap}}
.имя b{{color:{АКЦЕНТ};font-weight:800}}
.пояснение{{margin:34px auto 0;width:1320px;font-size:64px;line-height:1.28;color:{МЯГКИЙ};
  text-wrap:balance}}
.окно{{position:absolute;left:100px;right:100px;border-radius:54px;overflow:hidden;
  background:#fff;box-shadow:0 2px 0 rgba(18,19,14,.05),0 40px 90px -30px rgba(18,19,14,.28),
  0 0 0 2px rgba(18,19,14,.06)}}
.окно img{{width:100%;height:100%;object-fit:cover;object-position:top center;display:block}}
.пилюля{{position:absolute;left:50%;transform:translateX(-50%);height:120px;padding:0 64px;
  border-radius:60px;background:#DCE5B4;color:#2E3908;display:flex;align-items:center;gap:26px;
  font-weight:700;font-size:66px;white-space:nowrap;letter-spacing:-.01em}}
.пилюля svg{{width:64px;height:64px;flex:0 0 auto}}

/* Обложка */
.сцена{{position:absolute;inset:0;z-index:1}}
.обложка .верх{{position:absolute;left:0;right:0;top:330px;text-align:center;font-size:84px;
  line-height:1.22;letter-spacing:.01em;text-transform:uppercase;z-index:3}}
.обложка .слово{{position:absolute;left:0;right:0;top:586px;text-align:center;font-family:Onest;
  font-weight:800;font-size:200px;line-height:1;letter-spacing:-.02em;color:{АКЦЕНТ};z-index:3;
  white-space:nowrap}}
.кот{{position:absolute;z-index:2;filter:drop-shadow(0 34px 30px rgba(40,44,30,.28))}}

/* Обложка «веер»: снимки сайтов поста веером, заголовок по левому краю */
.веер .метка{{position:absolute;left:120px;top:190px;height:96px;padding:0 44px;border-radius:48px;
  background:#DCE5B4;color:#2E3908;display:flex;align-items:center;font-weight:700;font-size:54px;
  letter-spacing:-.01em;z-index:3}}
.веер .крупно{{position:absolute;left:120px;right:100px;top:340px;font-family:Onest;font-weight:800;
  font-size:158px;line-height:1.0;letter-spacing:-.035em;z-index:3}}
.веер .крупно b{{color:{АКЦЕНТ};font-weight:800}}
.карта{{position:absolute;width:760px;height:475px;border-radius:38px;overflow:hidden;background:#fff;
  box-shadow:0 0 0 2px rgba(18,19,14,.06),0 50px 90px -30px rgba(18,19,14,.35);z-index:1}}
.карта img{{width:100%;height:100%;object-fit:cover;object-position:top center;display:block}}

/* Финал */
.тёмный{{background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}}}
.клетки{{position:absolute;inset:0;
  background-image:linear-gradient(rgba({ЛАЙМ_RGB},.045) 2px,transparent 2px),
                   linear-gradient(90deg,rgba({ЛАЙМ_RGB},.045) 2px,transparent 2px);
  background-size:120px 120px;
  -webkit-mask:radial-gradient(ellipse 90% 70% at 50% 40%,#000 30%,transparent 80%)}}
.волны{{position:absolute;left:245px;top:210px;width:0;height:0}}
.волны i{{position:absolute;border:2px solid rgba({ЛАЙМ_RGB},.16);border-radius:50%;
  transform:translate(-50%,-50%)}}
.самолёт{{position:absolute;left:150px;top:120px;width:190px;height:190px;border-radius:50%;
  border:4px solid {ЛАЙМ};display:grid;place-items:center;color:{СВЕТЛЫЙ};
  box-shadow:0 0 50px rgba({ЛАЙМ_RGB},.25)}}
.самолёт svg{{width:96px;height:96px;margin-left:-8px}}
.тёмный .заголовок{{position:absolute;left:380px;top:122px;font-family:Onest;font-weight:800;
  font-size:150px;line-height:1.02;letter-spacing:-.03em;white-space:nowrap}}
.тёмный .заголовок b{{color:{ЛАЙМ};font-weight:800}}
.тёмный .под{{position:absolute;left:150px;top:390px;font-size:70px;line-height:1.3;color:#C9CCBD}}
.телефон{{position:absolute;left:330px;top:640px;width:900px;height:1110px;border-radius:120px;
  border:14px solid #2C2F25;overflow:hidden;
  box-shadow:0 0 0 3px rgba({ЛАЙМ_RGB},.35),0 0 90px rgba({ЛАЙМ_RGB},.12);
  background:linear-gradient(#1B1D17,#141510)}}
.бровь{{position:absolute;left:50%;top:26px;transform:translateX(-50%);width:230px;height:62px;
  border-radius:31px;background:#050605}}
.канал{{position:absolute;left:50px;right:50px;top:130px;height:120px;border-radius:60px;
  background:#23261E;display:flex;align-items:center;gap:26px;padding:0 30px}}
.канал .ава{{width:78px;height:78px;border-radius:50%;background:{ЛАЙМ};display:grid;place-items:center}}
.канал .ава img{{height:44px;filter:brightness(0)}}
.канал .текст{{font-size:44px;font-weight:700;line-height:1.1}}
.канал .текст span{{display:block;font-size:32px;font-weight:400;color:#9DA291}}
.пост{{position:absolute;left:50px;right:50px;height:190px;border-radius:40px;background:#23261E;
  padding:30px 40px;display:flex;flex-direction:column;justify-content:center;gap:18px}}
.пост .мутно{{font-family:Onest;font-weight:800;font-size:62px;letter-spacing:-.02em;
  filter:blur(13px);color:{СВЕТЛЫЙ};white-space:nowrap}}
.пост .мутно b{{color:{ЛАЙМ}}}
.пост .ссылка{{display:flex;align-items:center;gap:16px;font-size:38px;color:{ЛАЙМ};font-weight:700}}
.пост .ссылка svg{{width:40px;height:40px}}
"""


def страница(тело: str, доля: float, класс: str = "") -> str:
    return (f"<!doctype html><meta charset=utf-8><style>{фейсы()}{CSS}</style>"
            f"<body class='{класс}'>{тело}{стиль.знак_и_полоса(доля)}</body>")


# Холмы как у референса: светлые дюны с мягкой тенью под гребнем. Кот с
# ноутбуком садится на гребень дальнего холма — наш вайбкодер вместо кресла.
ХОЛМЫ = f"""<svg class=сцена viewBox='0 0 {W} {H}' preserveAspectRatio='none'>
<defs>
 <linearGradient id='д1' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FBFBF7'/><stop offset='.45' stop-color='#E6E8DC'/><stop offset='1' stop-color='#D4D7C8'/></linearGradient>
 <linearGradient id='д2' x1='0' y1='0' x2='.25' y2='1'><stop offset='0' stop-color='#FAFAF5'/><stop offset='.6' stop-color='#E1E3D6'/></linearGradient>
 <filter id='мягко' x='-20%' y='-40%' width='140%' height='180%'><feGaussianBlur stdDeviation='34'/></filter>
</defs>
<path d='M-40 1640 C 280 1560 640 1440 980 1445 C 1270 1450 1470 1560 1700 1640 L1700 2200 L-40 2200Z' transform='translate(0,-26)' fill='#9EA38C' opacity='.22' filter='url(#мягко)'/>
<path d='M-40 1640 C 280 1560 640 1440 980 1445 C 1270 1450 1470 1560 1700 1640 L1700 2200 L-40 2200Z' fill='url(#д1)'/>
<path d='M-40 2010 C 380 1880 820 1850 1180 1910 C 1400 1950 1560 2000 1700 2040 L1700 2200 L-40 2200Z' transform='translate(0,-22)' fill='#8F947D' opacity='.20' filter='url(#мягко)'/>
<path d='M-40 2010 C 380 1880 820 1850 1180 1910 C 1400 1950 1560 2000 1700 2040 L1700 2200 L-40 2200Z' fill='url(#д2)'/>
</svg>"""


def обложка(доля: float) -> str:
    о = П["обложка"]
    if о.get("сцена") == "веер":
        return веер(о, доля)
    return страница(
        f"<div class=обложка>{ХОЛМЫ}"
        f"<div class=верх>{о['верх']}</div>"
        f"<div class=слово>{о['слово']}</div>"
        f"{кот('noutbuk', 470, left=740, top=1010)}"
        f"{кот('spit', 150, left=250, top=1462)}</div>", доля)



# Четыре карты веером: угол, центр по x, верх. Крайние ниже — дуга, как карты в руке.
ВЕЕР = [(-12, 540, 1070), (-4, 750, 975), (5, 960, 985), (13, 1140, 1100)]


def веер(о: dict, доля: float) -> str:
    карты = ""
    for (угол, x, y), с in zip(ВЕЕР, П["сайты"]):
        снимок, _ = картинка(ТУТ / с["снимок"][0], с["снимок"][1], ширина=900)
        карты += (f"<div class=карта style='left:{x - 380}px;top:{y}px;transform:rotate({угол}deg)'>"
                  f"<img src='{снимок}'></div>")
    return страница(
        f"<div class=веер><div class=метка>{о['метка']}</div>"
        f"<div class=крупно>{о['крупно']}</div>{карты}"
        f"{кот(о.get('кот', 'lupa'), 500, left=1200, top=1330)}</div>", доля)


ВЕРХ_ОКНА, НИЗ_ПИЛЮЛИ = 640, 1760     # ниже пилюли — знак и полоса, дальше подпись TikTok


def сайт(с: dict, доля: float) -> str:
    картинка_, пропорция = картинка(ТУТ / с["снимок"][0], с["снимок"][1])
    ширина = W - 200
    высота = min(930, round(ширина / пропорция))
    # Окно и пилюля стоят блоком посередине свободного места под шапкой.
    блок = высота + 60 + 120
    верх = ВЕРХ_ОКНА + (НИЗ_ПИЛЮЛИ - ВЕРХ_ОКНА - блок) // 2
    return страница(
        f"<div class=шапка><div class=имя>{с['имя'][0]}<b>{с['имя'][1]}</b></div>"
        f"<div class=пояснение>{с['пояснение']}</div></div>"
        f"<div class=окно style='top:{верх}px;height:{высота}px'><img src='{картинка_}'></div>"
        f"<div class=пилюля style='top:{верх + высота + 60}px'>{ЦЕПЬ}{с['ссылка']}</div>", доля)


def финал(доля: float) -> str:
    волны = "".join(f"<i style='width:{р}px;height:{р}px'></i>" for р in (300, 440, 600, 780))
    посты = ""
    ф = П["финал"]
    for н, (а, б) in enumerate(ф["мутно"]):
        посты += (f"<div class=пост style='top:{300 + н * 230}px'><div class=мутно>{а}<b>{б}</b></div>"
                  f"<div class=ссылка>{ЦЕПЬ}сайт №{н + 1}</div></div>")
    return страница(
        f"<div class=клетки></div><div class=волны>{волны}</div>"
        f"<div class=самолёт>{САМОЛЁТ}</div>"
        f"<div class=заголовок>{ф['заголовок']}</div>"
        f"<div class=под>{ф['под']}</div>"
        f"<div class=телефон><div class=бровь></div>"
        f"<div class=канал><div class=ава><img src='{стиль.ЛОГО}'></div>"
        f"<div class=текст>Наш канал<span>{ф['канал']}</span></div></div>{посты}</div>"
        f"{кот('ukazyvaet', 540, рядом='телефон', left=1150, top=1180)}", доля, "тёмный")


ЗАМЕР = """document.fonts.ready.then(() => {
  const r = [];
  for (const el of document.querySelectorAll('.имя,.пояснение,.окно,.пилюля,.верх,.слово,.метка,.крупно,.заголовок,.под,.телефон,.кот,.знак')) {
    let b = el.getBoundingClientRect();
    if (!['окно','кот','знак','телефон'].includes(el.className)) {
      const д = document.createRange(); д.selectNodeContents(el); b = д.getBoundingClientRect();
    }
    r.push({кто: el.className, л: Math.round(b.left), п: Math.round(b.right), в: Math.round(b.top),
            н: Math.round(b.bottom), ширина: el.scrollWidth, видно: el.clientWidth});
  }
  const выход = r.filter(х => х.кто !== 'кот' && х.кто !== 'телефон' && (х.л < 90 || х.п > %d || х.ширина > х.видно + 2));
  const знак = r.find(х => х.кто === 'знак');
  const наезд = r.filter(х => !['знак','кот','телефон'].includes(х.кто) && х.н > знак.в - 20 && х.л < знак.п + 20);
  document.body.setAttribute("data-замер", JSON.stringify({
    шрифты: [...document.fonts].some(f => f.status === "loaded") && ![...document.fonts].some(f => f.status === "error" || f.status === "loading"),
    выход: выход.map(х => х.кто), наезд: наезд.map(х => х.кто), блоки: r,
    ...запас_кадра('.шапка,.окно,.пилюля,.верх,.слово,.метка,.крупно,.заголовок,.под,.телефон,.самолёт')}));
})""" % (W - 90)
ЗАМЕР = стиль.ЗАПАС_JS + ЗАМЕР


def main():
    global П
    файл = Path(sys.argv[1])
    П = json.loads(файл.read_text(encoding="utf-8"))
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    сайты = П["сайты"]
    всего = len(сайты) + 2
    кадры = [("01", обложка(1 / всего))]
    кадры += [(f"{н:02d}", сайт(с, н / всего)) for н, с in enumerate(сайты, 2)]
    кадры.append((f"{всего:02d}", финал(1.0)))
    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        снимок = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", flush=True)
            continue
        with Image.open(снимок) as к:
            к.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок)
        замер = браузер.замерить(html.replace("</body>", f"<script>{ЗАМЕР}</script></body>"), W, H)
        кратко = {к: в for к, в in (замер or {}).items() if к != "блоки"}
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", кратко, flush=True)
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
