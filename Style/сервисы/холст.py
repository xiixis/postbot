# -*- coding: utf-8 -*-
"""Холст согласования стиля «подборка сервисов» из файла поста: python3 холст.py посты/<пост>.json

Кладёт в `холсты/<пост>/` кадры холста (`.dc.html`, 1080×1440, шрифты вшиты — снимок и экспорт
кнопкой не зависят от Google Fonts), картинки, `canvas.json` и готовую страницу `<пост>.html`.
Выложить её — один вызов Artifact; дальше владелец правит сам, выпуск — `../выпуск.py`.
Координаты кота в посте — в мерах холста.
"""
import base64, json, subprocess, sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from помощник_холста import помощник as найти_помощника     # noqa: E402
from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

КРЕМ, ОЛИВА, ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ = стиль.КРЕМ, стиль.ОЛИВА, стиль.ТЁМНЫЙ, стиль.ЛАЙМ, стиль.СВЕТЛЫЙ
ЧЕРНИЛА, МЯГКИЙ, ТИХИЙ = "#12130E", "#3A3E33", "#A3A69A"
К = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800"
Т = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif"


def голова(фейсы: str | None = None) -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            "</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + (фейсы or стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
                                    латиница=стиль.ЛАТИНИЦА + ",U+2192"))
            + f"\n    body {{ margin: 0; }}\n    a {{ color: {ОЛИВА}; }} a:hover {{ color: {ЧЕРНИЛА}; }}\n  </style>\n</helmet>\n")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    """Полоса — фирменный лайм на всех кадрах, светлых и тёмных: это знак бренда, и он
    один во всей карусели. На светлом лайм бледный, поэтому под ним волосяная тёмная
    линия — она держит край, не перекрашивая полосу."""
    return (f'<img src="logo.png" style="position: absolute; left: 80px; bottom: 205px; height: 44px;'
            f'{"" if тёмный else " filter: brightness(.45) saturate(1.4);"}">'
            f'<div style="position: absolute; left: 0; bottom: 176px; height: 6px; width: {доля * 100:.1f}%; '
            f'background: {ЛАЙМ}; box-shadow: 0 1px 0 rgba(18,19,14,.30);"></div>')


def кот(к: dict) -> str:
    где = "; ".join(f"{ключ}: {к[ключ]}px" for ключ in ("left", "top", "right", "bottom") if ключ in к)
    return f'<img src="kot-{латиницей(к["поза"])}.webp" style="position: absolute; height: {к["высота"]}px; {где};">'


def обложка(о: dict, доля: float) -> str:
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {КРЕМ}; color: {ЧЕРНИЛА};">
  <div style="position: absolute; left: 80px; right: 80px; top: 170px; display: flex; flex-direction: column; align-items: flex-start; gap: 36px;">
    <div style="{Т}; font-weight: 700; font-size: 34px; letter-spacing: 0.12em; text-transform: uppercase; color: {ОЛИВА};">{о['над']}</div>
    <div style="{К}; font-size: 104px; line-height: 1.02; letter-spacing: -0.03em; text-wrap: balance;">{о['заголовок']}</div>
    <div style="{Т}; font-size: 46px; line-height: 1.3; color: {МЯГКИЙ}; text-wrap: pretty; max-width: 760px;">{о['под']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def обложка_число(о: dict, доля: float) -> str:
    """Б — число: гигант оливой, под ним строка и кот. Обложек в холсте всегда три."""
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {КРЕМ}; color: {ЧЕРНИЛА};">
  <div style="position: absolute; left: 70px; right: 70px; top: 180px; text-align: center; {К}; font-size: 380px; line-height: .88; color: {ОЛИВА};">{о['число']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 640px; text-align: center; {К}; font-size: 88px; line-height: 1.04;">{о['строка']}</div>
  <div style="position: absolute; left: 90px; right: 90px; top: 830px; text-align: center; {Т}; font-size: 44px; color: {МЯГКИЙ};">{о['под']}</div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: зачёркнутая строка и лаймовая плашка со второй."""
    строка = f"{Т}; font-size: 52px; line-height: 1.3; padding: 26px 32px; border-radius: 28px;"
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {КРЕМ}; color: {ЧЕРНИЛА};">
  <div style="position: absolute; left: 80px; right: 80px; top: 200px; {К}; font-size: 92px; line-height: 1.04;">{о['заголовок']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 520px; display: flex; flex-direction: column; gap: 28px;">
    <div style="{строка} background: #FFFFFF; color: {МЯГКИЙ}; text-decoration: line-through; box-shadow: 0 10px 26px rgba(18,19,14,.07);">{о['было']}</div>
    <div style="{строка} background: {ЛАЙМ}; color: #1A2006; font-weight: 700; box-shadow: 0 10px 26px rgba(18,19,14,.10);">{о['стало']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def кегль_текста(строки: list[str]) -> int:
    """Кегль карточки под объём текста. Без этого длинный текст либо вылезает из карточки,
    либо упирается в служебную зону; подбор по числу знаков держит карточку в своих
    границах, не трогая остальные блоки."""
    знаков = sum(len(с) for с in строки)
    return 45 if знаков <= 120 else 41 if знаков <= 170 else 37


def кадр(номер: int, к: dict, доля: float) -> str:
    """Блоки стоят на сетке, а не центрируются: раньше кадр со снимком вместо ряда значков
    уезжал вверх на 158 px, потому что flex-центрирование поднимало всё содержимое разом.
    Теперь объём блока меняет только его собственную высоту, а соседи не двигаются."""
    # Кадр может показывать не ряд значков, а снимок самого сервиса: «покажем картинкой
    # сам сайт». Снимок и ряд значков живут в одной зоне и взаимозаменяемы.
    if к.get("снимок"):
        медиа = (f'<img src="{к["снимок"]}.jpg" style="width: 880px; height: 260px; '
                 f'object-fit: cover; object-position: top center; border-radius: 28px; '
                 f'box-shadow: 0 16px 50px rgba(18,19,14,0.12);">')
    else:
        медиа = "\n".join(
            f'      <div style="width: 184px; height: 184px; border-radius: 50%; background: #FFFFFF; display: flex; '
            f'align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(18,19,14,0.10);">'
            f'<img src="{значок_файл(с["значок"])}" style="width: 118px; height: 118px; object-fit: contain;"></div>'
            for с in к["сервисы"])
    подпись = к.get("подпись") or ", ".join(с["имя"] for с in к.get("сервисы", []))
    текст = "\n".join(f'      <p style="margin: 0;">{а}</p>' for а in к["текст"])
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {КРЕМ}; color: {ЧЕРНИЛА};">
  <div style="position: absolute; left: 0; right: 0; top: 130px; text-align: center;">
    <span style="{К}; display: inline-block; font-size: 44px; color: {КРЕМ}; background: {ОЛИВА}; border-radius: 44px; padding: 8px 34px;">{номер:02d}</span>
  </div>
  <div style="position: absolute; left: 80px; right: 80px; top: 230px; height: 190px; {К}; font-size: 88px; line-height: 1.05; letter-spacing: -0.03em; text-align: center; text-wrap: balance;">{к['заголовок']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 450px; height: 280px; display: flex; gap: 30px; align-items: center; justify-content: center;">
{медиа}
  </div>
  <div style="position: absolute; left: 80px; right: 80px; top: 752px; {Т}; font-weight: 700; font-size: 40px; color: {МЯГКИЙ}; text-align: center;">{подпись}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 830px; bottom: 276px; {Т}; font-size: {кегль_текста(к['текст'])}px; line-height: 1.3; background: #FFFFFF; border-radius: 44px; padding: 46px 56px; display: flex; flex-direction: column; justify-content: center; gap: 24px; text-align: center; text-wrap: pretty; box-shadow: 0 16px 50px rgba(18,19,14,0.07);">
{текст}
  </div>
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ТЁМНЫЙ}; color: {СВЕТЛЫЙ};">
  <div style="position: absolute; left: 80px; right: 80px; top: 230px; display: flex; flex-direction: column; align-items: flex-start; gap: 40px;">
    <div style="{К}; font-size: 112px; line-height: 1.0; letter-spacing: -0.03em; color: {ЛАЙМ}; text-wrap: balance;">{ф['крупно']}</div>
    <div style="{Т}; font-weight: 700; font-size: 54px; line-height: 1.25; text-wrap: balance; max-width: 820px;">{ф['текст']}</div>
    <div style="{Т}; font-size: 42px; color: {ТИХИЙ};">{ф['под']}</div>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def значок_файл(имя: str) -> str:
    return f"{имя}.svg" if (ТУТ / "значки" / f"{имя}.svg").exists() else f"{имя}.png"


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Картинки холста: значки до 256 px, коты webp, логотип. Каждая заметно меньше 70 КБ."""
    файлы = []
    имена = {с["значок"] for к in пост["кадры"] for с in к.get("сервисы", [])}
    for имя in sorted(имена):
        исходник = ТУТ / "значки" / значок_файл(имя)
        цель = папка / исходник.name
        if исходник.suffix == ".svg":
            цель.write_bytes(исходник.read_bytes())
        else:
            with Image.open(исходник) as и:
                и = и.convert("RGBA"); и.thumbnail((256, 256), Image.LANCZOS); и.save(цель, optimize=True)
        файлы.append(цель)
    for к in пост["кадры"]:
        if not к.get("снимок"):
            continue
        цель = папка / f'{к["снимок"]}.jpg'
        with Image.open(ТУТ.parent / "подборка-сайтов/сайты" / f'{к["снимок"]}.png') as и:
            и = и.convert("RGB")
            ширина, высота = и.size
            и = и.crop((0, 0, ширина, min(высота, int(ширина / (880 / 300)))))
            и.thumbnail((1100, 1100), Image.LANCZOS)
            и.save(цель, quality=78, optimize=True)
        файлы.append(цель)
    for к in (пост["обложка"]["кот"], пост["финал"]["кот"]):
        цель = папка / f"kot-{латиницей(к['поза'])}.webp"
        with Image.open(стиль.ПОЗЫ / f"{к['поза']}.png") as и:
            и = и.convert("RGBA"); и.thumbnail((1000, round(к["высота"] * 1.5)), Image.LANCZOS); и.save(цель, quality=86)
        файлы.append(цель)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA"); и.thumbnail((240, 88), Image.LANCZOS); и.save(папка / "logo.png", optimize=True)
    return sorted(set(файлы)) + [папка / "logo.png"]


ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


def помощник() -> Path:
    """Помощник холста из распакованного скила design; путь меняется с версией Claude Code."""
    return найти_помощника()


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    всего = len(пост["кадры"]) + 2
    if пост.get("вид") == "один":                 # вариация «один сервис на кадр» — один.py
        import один
        шапка = голова(один.фейсы(стиль))
        доски = [(имя, подпись, шапка + тело + ХВОСТ) for имя, подпись, тело in один.доски(пост)]
    elif пост.get("вид") == "список":             # вариация «раздел списком со значками» — список.py
        import список
        доски = список.доски(пост)
    else:
        # ⛔️ Три обложки обязательны: холст без них не выкладывается.
        обложки = {"сцена": lambda: обложка(пост["обложка"], 1 / всего),
                   "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
                   "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
        главная = пост.get("главная", "сцена")
        запасные = [и for и in обложки if и != главная]
        доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
        for н, к in enumerate(пост["кадры"], 1):
            доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['заголовок']}", кадр(н, к, (н + 1) / всего)))
        доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
        for н, и in enumerate(запасные, 2):
            доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
        assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
            "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)
    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600, "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)], "launch": {"view": "canvas"}}
    if пост.get("заметка"):
        раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -560, "w": 900, "text": пост["заметка"]}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))
    п = помощник()
    страница = папка / f"{латиницей(файл.stem)}.html"     # помощник принимает имя только латиницей
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"), "--out", str(страница),
               "--title", пост.get("название") or пост["обложка"]["заголовок"][:60], "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    вид = пост.get("вид")
    for к in (один.картинки(пост, папка, стиль) if вид == "один"
              else список.картинки(пост, папка) if вид == "список" else картинки(пост, папка)):
        команда += ["--image", str(к)]
    р = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)], capture_output=True, text=True)
    print((р.stderr.strip() + "\n" if р.stderr.strip() else "") + проверка.stdout.strip()[:160])
    print("страница холста:", страница)


if __name__ == "__main__":
    main()
