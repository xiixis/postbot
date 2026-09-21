# -*- coding: utf-8 -*-
"""Фирменный стиль Фото-Карусели одним файлом — общий для всех стилей в `Style/`.

Раньше каждый шаблон держал свою копию: лайм, знак с полосой, шрифты, кота. Копии
расходились (тихий текст #3A3E33 у одного, #A3A69A у другого), а знак и полосу при
новом шаблоне переносили руками. Здесь то, что у карусели должно быть одинаковым;
своя палитра и вёрстка стиля остаются в его рисовальщике.

Лайм и светлый текст берутся из `postbot/config.py`: цвет у карусели бота и у
шаблонов один и тот же. Запас между блоками — то же правило, что `card._впритык`.
"""
import base64
import sys
from io import BytesIO
from pathlib import Path

ПОСТБОТ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ПОСТБОТ))
import config  # noqa: E402
from PIL import Image  # noqa: E402

W, H = 1620, 2160                       # кадр; на стол уходит JPG 1080×1440
ШРИФТЫ = ПОСТБОТ / "assets/fonts"
ПОЗЫ = ПОСТБОТ / "assets/mascot/позы"
СТОЛ = Path.home() / "Desktop/Посты"

# Палитра бренда. Лайм — только из config, не цифрами здесь.
ЛАЙМ, ЛАЙМ_RGB = config.ЛАЙМ, config.ЛАЙМ_RGB
СВЕТЛЫЙ, ПРИГЛУШ = config.ТЕКСТ, config.ПРИГЛУШ
ТЁМНЫЙ = "#12130F"                      # тёмный грунт: GitHub-подборка, финал сайтов
КРЕМ, ОЛИВА = "#F1F2EA", "#56690C"      # светлый грунт и акцент по нему (подборка сайтов)

ЛАТИНИЦА = "U+0000-00FF,U+2000-206F,U+2190-21FF"
КИРИЛЛИЦА = "U+0400-04FF"


def данные(путь: Path, тип: str | None = None) -> str:
    """Файл внутрь страницы: по file:// Chrome шрифты и картинки молча не рисует."""
    if тип is None:
        тип = {".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".woff2": "font/woff2"}.get(путь.suffix, "image/png")
    return f"data:{тип};base64," + base64.b64encode(путь.read_bytes()).decode()


def фейсы(*гарнитуры: tuple, латиница: str = ЛАТИНИЦА) -> str:
    """@font-face для гарнитур вида («семья», «файл без набора», вес) из assets/fonts."""
    css = []
    for семья, файл, вес in гарнитуры:
        for набор, диапазон in (("latin", латиница), ("cyrillic", КИРИЛЛИЦА)):
            css.append(f"@font-face{{font-family:{семья};font-weight:{вес};font-display:block;"
                       f"src:url({данные(ШРИФТЫ / f'{файл}-{набор}.woff2', 'font/woff2')}) "
                       f"format('woff2');unicode-range:{диапазон}}}")
    return "\n".join(css)


ЛОГО = данные(ПОСТБОТ / "assets/logo-dark.png")


def знак_и_полоса_css(светлый_грунт: bool = False, слой: int = 5) -> str:
    """Знак и полоса как в фирменных кадрах card.py (3к4) ×1,5; всё важное выше y≈1760.

    На светлом грунте знак приглушён, полоса оливковая; на тёмном — тень и лайм со свечением.
    `слой` — z-index: у GitHub-подборки кот (z 4) стоит поверх знака, поэтому там 3.
    """
    if светлый_грунт:
        знак, полоса = "filter:brightness(.45) saturate(1.4)", f"background:{ОЛИВА}"
    else:
        знак = "filter:drop-shadow(0 6px 20px rgba(0,0,0,.35))"
        полоса = f"background:{ЛАЙМ};box-shadow:0 0 39px rgba({ЛАЙМ_RGB},.45)"
    return (f".знак{{position:absolute;left:120px;bottom:308px;height:66px;z-index:{слой};{знак}}}\n"
            f".полоса{{position:absolute;left:0;bottom:264px;height:9px;z-index:{слой};{полоса}}}\n")


def знак_и_полоса(доля: float) -> str:
    return (f"<img class=знак data-блок src='{ЛОГО}'>"
            f"<div class=полоса style='width:{доля * 100:.1f}%'></div>")


def кот(поза: str, высота: int, класс: str = "кот", рядом: str = "", **где) -> str:
    """Поза, обрезанная по видимому коту: замер запаса мерит кота, а не прозрачные поля.

    `рядом` — классы блоков, к которым кот прижат нарочно (опирается на телефон):
    замер запаса эту пару не судит.
    """
    with Image.open(ПОЗЫ / (поза + ".png")) as и:
        и = и.convert("RGBA")
        и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
        буф = BytesIO()
        и.save(буф, "PNG")
    с = ";".join(f"{к}:{в}px" for к, в in где.items())
    рядом_ = f" data-рядом='{рядом}'" if рядом else ""
    return (f"<img class={класс} data-блок{рядом_} style='height:{высота}px;{с}' "
            f"src='data:image/png;base64,{base64.b64encode(буф.getvalue()).decode()}'>")


# ── Запас между важными блоками ──────────────────────────────────────────────
# Слово владельца 15.09.2026: «нельзя, чтобы что-то было впритык к другому».
# 40 px кадра — ≈10 точек на экране телефона, где кадр идёт в ширину ~400 точек.
ЗАПАС, КРАЙ = 40, 100

# JS: `запас_кадра('<селекторы>')` → {тесно: [...], край: [...]}; годен, когда оба пусты.
# Рамка видимой коробки (фон, рамка, тень, картинка, overflow:hidden) — она сама;
# у текста — сами буквы: по высоте от верха самой высокой до низа самого глубокого
# знака (canvas.measureText), а не метрики шрифта. У огромной цифры Oswald 520 px
# рамка строки на ~100 px выше и ниже букв, и срез «5% высоты» её не покрывал —
# «9» считалась налезающей на ник над ней. Вложенные блоки между собой не
# сравниваются. Кот может уходить за край кадра, текст — нет. Нарочное соседство
# (кот опирается на телефон) помечается у блока: data-рядом="<класс соседа>".
ЗАПАС_JS = """
function запас_кадра(селекторы) {
  const ЗАПАС = %(ЗАПАС)d, КРАЙ = %(КРАЙ)d, W = document.documentElement.clientWidth;
  const видимая = el => {
    if (el.tagName === 'IMG' || el.tagName === 'svg' || !el.textContent.trim()) return true;
    const с = getComputedStyle(el);
    const фон = с.backgroundColor !== 'rgba(0, 0, 0, 0)' && с.backgroundColor !== 'transparent';
    return фон || parseFloat(с.borderTopWidth) > 0 || с.boxShadow !== 'none'
        || с.backgroundImage !== 'none' || с.overflow === 'hidden';
  };
  const холст = document.createElement('canvas').getContext('2d');
  const буквы = (узел, п) => {
    const с = getComputedStyle(узел.parentElement);
    холст.font = `${с.fontStyle} ${с.fontWeight} ${с.fontSize} ${с.fontFamily}`;
    const текст = узел.textContent.trim();
    const м = холст.measureText(с.textTransform === 'uppercase' ? текст.toUpperCase() : текст);
    const шрифт = м.fontBoundingBoxAscent + м.fontBoundingBoxDescent;
    const база = п.top + (п.height - шрифт) / 2 + м.fontBoundingBoxAscent;
    return {в: база - м.actualBoundingBoxAscent, н: база + м.actualBoundingBoxDescent};
  };
  const рамки = el => {
    if (видимая(el)) {
      const б = el.getBoundingClientRect();
      return [{л: б.left, п: б.right, в: б.top, н: б.bottom}];
    }
    const к = [];
    const обход = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let т; (т = обход.nextNode());) {
      if (!т.textContent.trim()) continue;
      const д = document.createRange(); д.selectNodeContents(т);
      for (const п of д.getClientRects()) {
        if (п.width <= 1 || п.height <= 1) continue;
        const б = буквы(т, п);
        к.push({л: п.left, п: п.right, в: Math.max(п.top, б.в), н: Math.min(п.bottom, б.н)});
      }
    }
    for (const в of el.querySelectorAll('img,svg')) {
      const б = в.getBoundingClientRect();
      к.push({л: б.left, п: б.right, в: б.top, н: б.bottom});
    }
    return к;
  };
  const все = [...new Set(document.querySelectorAll(селекторы ? селекторы + ',[data-блок]' : '[data-блок]'))];
  const блоки = все.filter(el => !все.some(о => о !== el && о.contains(el)))
    .map(el => ({el, кто: String(el.className.baseVal ?? el.className).split(' ')[0]
                   + (el.textContent.trim() ? ':' + el.textContent.trim().slice(0, 14) : ''),
                 кот: el.classList.contains('кот'), р: рамки(el)}))
    .filter(б => б.р.length);
  const тесно = [];
  for (let i = 0; i < блоки.length; i++) for (let j = i + 1; j < блоки.length; j++) {
    const а = блоки[i], б = блоки[j];
    const рядом = (х, у) => (х.el.getAttribute('data-рядом') || '').split(' ').some(к => к && у.el.classList.contains(к));
    if (рядом(а, б) || рядом(б, а)) continue;
    let зазор = Infinity;
    for (const х of а.р) for (const у of б.р)
      зазор = Math.min(зазор, Math.max(у.л - х.п, х.л - у.п, у.в - х.н, х.в - у.н));
    if (зазор < ЗАПАС) тесно.push(а.кто + ' ↔ ' + б.кто + ' ' + Math.round(зазор));
  }
  const край = блоки.filter(б => !б.кот && б.р.some(х => х.л < КРАЙ - 1 || х.п > W - КРАЙ + 1))
    .map(б => б.кто + ' ' + Math.round(Math.min(...б.р.map(х => х.л))) + '–'
              + Math.round(Math.max(...б.р.map(х => х.п))));
  return {тесно, край};
}
""" % {"ЗАПАС": ЗАПАС, "КРАЙ": КРАЙ}


# ── Кот файлом, а не данными ────────────────────────────────────────────────
# Вшитая в страницу поза (`кот`) удобна для прямой отрисовки, но доска холста с ней
# перерастает предел помощника в 2 МБ и молча не собирается. Поэтому у холстов кот идёт
# отдельным webp, а имя файла — латиницей: кириллицу в именах картинок помощник не берёт.
_ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                 "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                 "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(_ЛАТ.get(б, б) for б in имя.lower())


def кот_файлом(к: dict, класс: str = "кот") -> str:
    """Разметка кота, ссылающаяся на файл `kot-<поза латиницей>.webp` рядом с доской."""
    где = ";".join(f"{ключ}:{к[ключ]}px" for ключ in ("left", "top", "right", "bottom") if ключ in к)
    return f'<img class={класс} src="kot-{латиницей(к["поза"])}.webp" style="height:{к["высота"]}px;{где}">'


def коты_в_файлы(пост: dict, папка: Path) -> list[Path]:
    """Сохраняет позы всех котов поста рядом с доской и возвращает пути."""
    места = [пост.get(ключ, {}) for ключ in ("обложка", "обложка_число", "обложка_допосле",
                                             "обложка_сцена", "обложка_маркер", "финал")]
    места += пост.get("кадры", [])
    файлы = []
    for к in (м["кот"] for м in места if isinstance(м, dict) and м.get("кот")):
        цель = папка / f'kot-{латиницей(к["поза"])}.webp'
        # Готовый файл не перерисовываем, но в список отдаём всегда: холст вшивает картинки
        # по этому списку, и при пересборке в уже заполненной папке коты пропадали из
        # опубликованной доски совсем — ссылка в разметке есть, картинки нет (18.09).
        if цель.exists():
            файлы.append(цель)
            continue
        with Image.open(ПОЗЫ / f'{к["поза"]}.png') as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((900, round(к["высота"] * 1.6)), Image.LANCZOS)
            и.save(цель, quality=84, method=6)
        файлы.append(цель)
    return файлы
