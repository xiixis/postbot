# -*- coding: utf-8 -*-
"""Фото-Карусель, стиль «подборка GitHub» (терминал с $): кадры 1620×2160 одним прогретым Chrome.

Что рисовать, лежит в файле поста: `python3 github.py посты/<пост>.json [01 05]`.
С номерами перерисовываются только они; без номеров кадры ещё и уезжают JPG
1080×1440 на стол, в папку из поля «папка», вместе с подписью.

Шрифты и картинки встроены в страницу данными: по file:// Chrome их молча
не рисует. Картинки проектов лежат в repo/.
"""
import base64, json, sys, time
from io import BytesIO
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402  фирменное общее: лайм, шрифты, знак с полосой, кот, запас
from стиль import W, H, СТОЛ, данные  # noqa: E402
import браузер  # noqa: E402  один живой Chrome постбота
from PIL import Image  # noqa: E402


def фейсы() -> str:
    return стиль.фейсы(("JB", "jetbrains-400", 400), ("JB", "jetbrains-700", 700),
                       латиница=стиль.ЛАТИНИЦА + ",U+2713,U+2605")


def фейсы_обложки() -> str:
    """Узкий Oswald под огромную цифру и широкий Manrope под заголовок — только обложке «цифра»."""
    return стиль.фейсы(("Os", "oswald-600", 600), ("Mn", "manrope-800", 800), ("Mn", "manrope-400", 400))


def звёзды(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


# Фон: призрачный вывод терминала, огромный «$», пунктир по краям, зерно и
# затемнение к углам. Строки терминала настоящие команды git, не выдумка.
ТЕРМИНАЛ_ОБЛОЖКИ = """$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

$ git fetch trending
remote: Enumerating objects: 10, done.
remote: Counting objects: 10, done.
remote: Compressing objects: 100% (10/10)
remote: Total 10 (delta 0), reused 10 (delta 0)
✓ 10 repositories loaded

$ _"""

ТЕРМИНАЛ_КАРТОЧКИ = """$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

$ git log --oneline -3
a1b2c3d update readme
6f7e8d9 add examples
3c4d5e6 initial commit

$ _"""

ЗЕРНО = ("data:image/svg+xml;base64," + base64.b64encode(
    b"<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'>"
    b"<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' "
    b"stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .55 0'/>"
    b"</filter><rect width='100%' height='100%' filter='url(#n)'/></svg>").decode())

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden}
body{background:%(ТЁМНЫЙ)s;color:%(СВЕТЛЫЙ)s;font-family:JB,monospace;position:relative;
  -webkit-font-smoothing:antialiased}
.терм{position:absolute;left:%(терм_x)dpx;top:%(терм_y)dpx;white-space:pre;
  font-size:%(терм_к)dpx;line-height:1.55;color:#D8DDCB;opacity:.17}
.доллар{position:absolute;right:40px;top:120px;font-size:880px;font-weight:700;
  line-height:1;color:%(ЛАЙМ)s;opacity:.05;filter:blur(1.5px)}
.пунктир{position:absolute;top:0;bottom:0;width:14px;opacity:.28;
  background-image:radial-gradient(circle,#7C8270 2.2px,transparent 2.6px);
  background-size:14px 26px}
.пунктир.л{left:52px;-webkit-mask:linear-gradient(transparent 26%%,#000 28%% 38%%,transparent 40%% 72%%,#000 74%% 90%%,transparent 92%%)}
.пунктир.п{right:52px;-webkit-mask:linear-gradient(transparent 22%%,#000 24%% 34%%,transparent 36%% 80%%,#000 82%% 88%%,transparent 90%%)}
.виньетка{position:absolute;inset:0;
  background:radial-gradient(ellipse 80%% 70%% at 50%% 45%%,transparent 45%%,rgba(0,0,0,.62) 100%%)}
.зерно{position:absolute;inset:0;opacity:.07;background:url(%(ЗЕРНО)s);mix-blend-mode:screen}
.слой{position:absolute;inset:0;z-index:2}
/* Знак и полоса — общие, из стиль.py; слой 3: кот (z 4) поверх знака. */
%(ЗНАК_И_ПОЛОСА)s
/* Обложка и финал */
.окно{position:absolute;left:50%%;transform:translateX(-50%%);top:%(окно_y)dpx;
  width:1060px;padding:62px 88px;border:2px solid rgba(%(ЛАЙМ_RGB)s,.38);border-radius:30px;
  background:rgba(18,19,15,.78);box-shadow:0 0 0 1px rgba(255,255,255,.05),0 30px 80px rgba(0,0,0,.6)}
.окно div{font-size:58px;line-height:1.7;white-space:nowrap;color:%(СВЕТЛЫЙ)s}
.окно .ок{color:#B9BEAC}
.лайм{color:%(ЛАЙМ)s}
/* Колонка под окном: блоки идут потоком и не могут налезть друг на друга. */
.колонка{position:absolute;left:0;right:0;display:flex;flex-direction:column;
  align-items:center;text-align:center}
/* Узкий моноширинный заголовок, как у образца: JetBrains, сжатый по горизонтали. */
h1{font-weight:700;white-space:nowrap;letter-spacing:-.01em;line-height:1.1;color:%(СВЕТЛЫЙ)s;
  transform:scaleX(.84);text-shadow:0 0 22px rgba(255,255,255,.12)}
.под{margin-top:28px;font-size:%(под_к)dpx;line-height:1.2;color:#B9BEAC;
  white-space:nowrap;letter-spacing:.01em}
.ник{position:absolute;left:0;right:0;bottom:300px;text-align:center;font-size:56px;
  color:#B9BEAC}

/* Карточка проекта */
.картинка{position:absolute;left:150px;right:150px;top:%(кар_y)dpx;height:%(кар_h)dpx;
  border-radius:40px;overflow:hidden;background:#FFF;
  box-shadow:0 0 70px 10px rgba(241,243,234,.22),0 0 160px 30px rgba(%(ЛАЙМ_RGB)s,.10)}
.картинка img{width:100%%;height:100%%;object-fit:cover;object-position:top center;display:block}
.звёзды{position:absolute;right:170px;font-size:54px;color:#B9BEAC;letter-spacing:.02em}
.звёзды b{color:%(ЛАЙМ)s;font-weight:400;margin-right:22px}
.ссылка{position:absolute;left:150px;right:120px;font-size:%(ссылка_к)dpx;color:%(ЛАЙМ)s;
  white-space:nowrap;letter-spacing:-.01em}
.текст{position:absolute;left:150px;right:150px;font-size:%(текст_к)dpx;line-height:1.5;
  color:%(СВЕТЛЫЙ)s;text-wrap:balance}
.текст p{margin:0}

/* Карточка «замена»: под ссылкой поток — что заменяет, что делает, нюанс */
.поток{position:absolute;left:150px;right:150px;display:flex;flex-direction:column;gap:36px}
.замена{font-size:62px;font-weight:700;line-height:1.2;color:%(СВЕТЛЫЙ)s}
.замена b{color:%(ЛАЙМ)s;font-weight:700}
.дело{font-size:48px;line-height:1.45;color:%(СВЕТЛЫЙ)s;text-wrap:pretty}
.нюанс{font-size:44px;line-height:1.4;color:#B9BEAC;text-wrap:pretty}
.кот{position:absolute;z-index:4;filter:drop-shadow(0 30px 40px rgba(0,0,0,.55))}

/* Обложка «цифра» */
.цифра-сцена .доллар,.цифра-сцена ~ .пунктир{display:none}
.н-ник{position:absolute;left:120px;top:150px;font-size:46px;color:#B9BEAC}
.н-цифра{position:absolute;left:104px;top:196px;font-family:Os;font-weight:600;font-size:520px;
  line-height:1;color:%(ЛАЙМ)s;text-shadow:0 0 60px rgba(%(ЛАЙМ_RGB)s,.35)}
.н-загл{position:absolute;left:440px;top:268px;font-family:Mn;line-height:1.02;color:%(СВЕТЛЫЙ)s;
  text-transform:uppercase;white-space:nowrap}
.н-загл .жир{font-weight:800;font-size:168px;letter-spacing:-.02em}
.н-загл .тон{font-weight:400;font-size:124px;letter-spacing:-.01em}
.н-черта{position:absolute;left:120px;top:738px;width:200px;height:6px;background:%(ЛАЙМ)s;
  box-shadow:0 0 24px rgba(%(ЛАЙМ_RGB)s,.5)}
.н-под{position:absolute;left:120px;top:790px;font-family:Mn;font-weight:400;font-size:84px;
  line-height:1.14;color:%(СВЕТЛЫЙ)s;text-transform:uppercase;white-space:nowrap}
.н-под b{color:%(ЛАЙМ)s;font-weight:400}
.н-свет{position:absolute;left:640px;top:760px;width:1100px;height:1100px;border-radius:50%%;
  background:radial-gradient(circle,rgba(%(ЛАЙМ_RGB)s,.20),rgba(%(ЛАЙМ_RGB)s,.06) 45%%,transparent 70%%)}
.н-крышка{position:absolute;left:800px;top:1560px;width:760px;height:90px;
  background:linear-gradient(#34382C,#1B1D16);transform:skewX(-24deg);transform-origin:bottom left}
.н-перед{position:absolute;left:760px;top:1650px;width:800px;height:320px;
  background:linear-gradient(#191B14,#0B0C09 80%%);border-top:6px solid %(ЛАЙМ)s;
  box-shadow:0 -8px 50px rgba(%(ЛАЙМ_RGB)s,.40)}
.н-точки{position:absolute;left:120px;top:1450px;width:200px;height:110px;opacity:.55;
  background-image:radial-gradient(circle,#B9BEAC 4px,transparent 4.6px);background-size:36px 36px}
.н-листай{position:absolute;left:120px;top:1640px;display:flex;align-items:center;gap:28px;
  font-family:Mn;font-weight:800;font-size:44px;letter-spacing:.02em;color:%(СВЕТЛЫЙ)s}
.н-листай i{display:grid;place-items:center;width:78px;height:78px;background:%(ЛАЙМ)s;color:%(ТЁМНЫЙ)s;
  font-style:normal;font-family:JB;font-weight:700;font-size:48px}
"""


def страница(тело: str, терм: str, доля: float = 1.0, **пар) -> str:
    п = dict(W=W, H=H, ЗЕРНО=ЗЕРНО, ЛАЙМ=стиль.ЛАЙМ, ЛАЙМ_RGB=стиль.ЛАЙМ_RGB, ТЁМНЫЙ=стиль.ТЁМНЫЙ,
             СВЕТЛЫЙ=стиль.СВЕТЛЫЙ, ЗНАК_И_ПОЛОСА=стиль.знак_и_полоса_css(слой=3), терм_x=190, терм_y=170, терм_к=31, окно_y=850,
             под_к=112, кар_y=250, кар_h=880, ссылка_к=64, текст_к=52)
    п.update(пар)
    лишние = фейсы_обложки() if "цифра-сцена" in тело else ""
    return (f"<!doctype html><meta charset=utf-8><style>{фейсы()}{лишние}{CSS % п}</style>"
            f"<body><div class=терм>{терм}</div><div class=доллар>$</div>"
            f"<div class='пунктир л'></div><div class='пунктир п'></div>"
            f"<div class=виньетка></div><div class=зерно></div>"
            f"<div class=слой>{тело}</div>{стиль.знак_и_полоса(доля)}</body>")


# У JetBrains Mono каждый знак ровно 0,6 кегля: ширину строки считаем заранее,
# а не ловим переполнение после снимка.
ЗНАК = 0.6


def кегль(строка: str, ширина: float, потолок: int, сжатие: float = 1.0) -> int:
    return min(потолок, int(ширина / (len(строка) * ЗНАК * сжатие)))


def лаймом(строка: str) -> str:
    """Приглашение «$» и галочка «✓» фирменным лаймом."""
    for знак in ("$", "✓"):
        if строка.startswith(знак):
            return f"<span class=лайм>{знак}</span>{строка[1:]}"
    return строка


def кот(поза: str, высота: int, left: int, top: int) -> str:
    return стиль.кот(поза, высота, left=left, top=top)


def обложка_цифра(о: dict, доля: float) -> str:
    под = "<br>".join(о["под"]) + "<br>" + "<br>".join(f"<b>{с}</b>" for с in о["под_лайм"])
    к = о.get("кот", {"поза": "noutbuk", "высота": 760, "left": 820, "top": 830})
    return страница(
        f"<div class=цифра-сцена><style>.доллар,.пунктир{{display:none}}</style>"
        f"<div class=н-свет></div>"
        f"<div class=н-ник>{лаймом(о['ник'])}</div>"
        f"<div class=н-цифра>{о['цифра']}</div>"
        f"<div class=н-загл><div class=жир>{о['верх']}</div><div class=тон>{о['низ']}</div></div>"
        f"<div class=н-черта></div><div class=н-под>{под}</div>"
        f"<div class=н-точки></div><div class=н-листай>{о['листай']}<i>→</i></div>"
        f"<div class=н-крышка></div><div class=н-перед></div>"
        f"{кот(к['поза'], к['высота'], к['left'], к['top'])}</div>",
        "", доля)


def обложка(о: dict, строки_заголовка: list, колонка_y=1250, потолок_под=104,
            доля: float = 1.0, потолок_заг: int = 176, окно_y: int = 850, хвост: str = "") -> str:
    к_заг = min(кегль(с, 1380, потолок_заг, .84 * .99) for с in строки_заголовка)
    к_под = min(кегль(с, 1300, потолок_под) for с in о["подзаголовок"])
    заголовок = "".join(f"<h1 style='font-size:{к_заг}px'>{с}</h1>" for с in строки_заголовка)
    под = "<br>".join(о["подзаголовок"])
    ник = f"<div class=ник>{о['ник']}</div>" if о.get("ник") else ""
    return страница(
        f"<div class=окно><div>{лаймом(о['команда'])}</div><div class=ок>{лаймом(о['ответ'])}</div></div>"
        f"<div class=колонка style='top:{колонка_y}px'>{заголовок}"
        f"<div class=под style='font-size:{к_под}px'>{под}</div></div>{ник}{хвост}",
        ТЕРМИНАЛ_ОБЛОЖКИ, доля, окно_y=окно_y)


def снимок(п: dict) -> tuple[str, float]:
    """Картинка проекта: первый кадр GIF, обрезка по полю «обрезка», JPEG шириной 1400."""
    with Image.open(ТУТ / "repo" / п["картинка"]) as и:
        и.seek(0)
        и = и.convert("RGB")
        if п.get("обрезка"):
            и = и.crop(tuple(п["обрезка"]))
        и = и.resize((1400, round(и.height * 1400 / и.width)), Image.LANCZOS)
        буф = BytesIO()
        и.save(буф, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(буф.getvalue()).decode(), и.width / и.height


def карточка_замена(п: dict, доля: float) -> str:
    src, пропорция = снимок(п)
    кар_h = max(620, min(700, round(1320 / пропорция)))
    кар_y = 180
    низ = кар_y + кар_h
    дело = " ".join(п["текст"]).replace("-", chr(0x2011))
    нюанс = п["нюанс"].replace("-", chr(0x2011))
    к_ссылки = кегль("github.com/" + п["repo"], 1330, 64, .99)
    return страница(
        f"<div class=картинка style='top:{кар_y}px;height:{кар_h}px'><img src='{src}'></div>"
        f"<div class=звёзды style='top:{низ + 60}px'><b>★</b>{звёзды(п['звёзды'])}</div>"
        f"<div class=ссылка style='top:{низ + 165}px;font-size:{к_ссылки}px'>github.com/{п['repo']}</div>"
        f"<div class=поток style='top:{низ + 295}px'>"
        f"<div class=замена><span class=лайм>→</span> заменяет <b>{п['заменяет']}</b></div>"
        f"<div class=дело>{дело}</div>"
        f"<div class=нюанс><span class=лайм>#</span> нюанс: {нюанс}</div></div>",
        ТЕРМИНАЛ_КАРТОЧКИ, доля, терм_x=110, терм_y=90, терм_к=34)


def карточка(п: dict, доля: float) -> str:
    if п.get("заменяет"):
        return карточка_замена(п, доля)
    img = ТУТ / "repo" / п["картинка"]
    тип = "image/png" if img.suffix == ".png" else "image/jpeg"
    # Окно под картинку повторяет её пропорции: превью GitHub вдвое шире, чем
    # высоко, и в окне 3:2 у него срезались края с названием проекта.
    with Image.open(img) as к:
        пропорция = к.width / к.height
    кар_h = max(600, min(780, round(1320 / пропорция)))
    кар_y = 210 + (780 - кар_h) // 3
    низ = кар_y + кар_h
    абзацы = "".join(f"<p>{с.replace('-', chr(0x2011))}</p>" for с in п["текст"])
    к_ссылки = кегль("github.com/" + п["repo"], 1330, 64, .99)
    return страница(
        f"<div class=картинка style='top:{кар_y}px;height:{кар_h}px'><img src='{данные(img, тип)}'></div>"
        f"<div class=звёзды style='top:{низ + 70}px'><b>★</b>{звёзды(п['звёзды'])}</div>"
        f"<div class=ссылка style='top:{низ + 175}px;font-size:{к_ссылки}px'>"
        f"github.com/{п['repo']}</div>"
        f"<div class=текст style='top:{низ + 300}px'>{абзацы}</div>",
        ТЕРМИНАЛ_КАРТОЧКИ, доля, терм_x=110, терм_y=90, терм_к=34)


ЗАМЕР = """document.fonts.ready.then(() => {
  const r = [];
  for (const el of document.querySelectorAll('.ссылка,.текст,.окно,.звёзды,.колонка,.ник,.знак,.поток,.н-загл,.н-под,.н-листай')) {
    const b = el.getBoundingClientRect();
    r.push({кто: el.className || el.tagName, л: Math.round(b.left), п: Math.round(b.right),
            в: Math.round(b.top), н: Math.round(b.bottom), ширина: el.scrollWidth,
            видно: el.clientWidth});
  }
  const знак = r.find(х => х.кто === 'знак');
  const наезд = r.filter(х => !['знак','ник'].includes(х.кто) && х.н > знак.в - 40).map(х => 'на знак: ' + х.кто);
  const выход = наезд.concat(r.filter(х => (!['колонка','ник'].includes(х.кто) && (х.л < 100 || х.п > %d)) || х.н > %d || х.ширина > х.видно + 2));
  document.body.setAttribute("data-замер", JSON.stringify({шрифты: document.fonts.check("40px JB") , выход,
    ...запас_кадра('.окно,.колонка,.ник,.картинка,.звёзды,.ссылка,.текст,.поток,.н-ник,.н-цифра,.н-загл,.н-черта,.н-под,.н-листай')}));
})""" % (W - 100, H - 120)
ЗАМЕР = стиль.ЗАПАС_JS + ЗАМЕР


def main():
    файл = Path(sys.argv[1])
    Г = json.loads(файл.read_text(encoding="utf-8"))
    выход = ТУТ / "кадры" / файл.stem
    выход.mkdir(parents=True, exist_ok=True)
    всего = len(Г["проекты"]) + 2
    о = Г["обложка"]
    if о.get("сцена") == "цифра":
        кадры = [("01", обложка_цифра(о, 1 / всего))]
    else:
        # Заголовок под окном команды с запасом 40 px: при 1180 окно садилось на буквы.
        кадры = [("01", обложка(о, [о["заголовок"]], колонка_y=1230, доля=1 / всего))]
    for н, п in enumerate(Г["проекты"], 2):
        кадры.append((f"{н:02d}", карточка(п, н / всего)))
    ф = Г["финал"]
    хвост = кот(**ф["кот"]) if ф.get("кот") else ""
    кадры.append((f"{len(кадры) + 1:02d}", обложка(
        ф, ф["строки_заголовка"], колонка_y=ф.get("колонка_y", 1225), потолок_под=ф.get("потолок_под", 70),
        потолок_заг=ф.get("потолок_заг", 150), окно_y=ф.get("окно_y", 850), хвост=хвост)))
    только = set(sys.argv[2:])
    for имя, html in кадры:
        if только and имя not in только:
            continue
        старт = time.time()
        снимок_ = выход / f"{имя}.png"
        ошибки = []
        if not браузер.снять(html, W, H, снимок_, ошибки):
            print(имя, "СНИМОК НЕ ВЫШЕЛ", flush=True)
            continue
        with Image.open(снимок_) as к:
            к.convert("RGB").resize((W, H), Image.LANCZOS).save(снимок_)
        # Замер: не вылезает ли текст за поле и загрузились ли шрифты.
        сверка = html.replace("</body>", f"<script>{ЗАМЕР}</script></body>")
        замер = браузер.замерить(сверка, W, H)
        print(имя, f"{time.time() - старт:.1f} с", ошибки or "", замер or "", flush=True)
    if только or not Г.get("папка"):
        return
    стол = СТОЛ / Г["папка"]
    стол.mkdir(parents=True, exist_ok=True)
    for имя, _ in кадры:
        with Image.open(выход / f"{имя}.png") as к:
            к.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{имя}.jpg", quality=92)
    (стол / "подпись.txt").write_text(Г["подпись"], encoding="utf-8")
    print("на столе:", стол, flush=True)


if __name__ == "__main__":
    main()
