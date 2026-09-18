# -*- coding: utf-8 -*-
"""Холст согласования стиля «приложения»: python3 холст.py посты/<пост>.json

Стиль снят с разобранного референса (`референсы/maysoulme-Dcqzh6ICOvz/паспорт.md`):
тёплая кремовая бумага, шаблон повторяется от кадра к кадру с точностью до пикселя,
дорогой вид даёт пустота сверху, а чернила в кадр добирает снимок, уходящий за нижний
край. Приглушённого серого нет вовсе: иерархия держится кеглем и начертанием.

Что изменено против источника (раздел 11 паспорта): кегль заголовка поднят в 2,3–2,5
раза — источник сделан под пост, который открывают и читают, а наш кадр смотрят полторы
секунды на трети экрана; заведён свой акцент, которого у автора нет вовсе (весь цвет в
его кадрах приходит из чужих логотипов); обложка защищена тёмным грунтом, потому что
белый по фото давал у автора 4,4:1 при нашем пороге 8:1; кнопка-стрелка «листай» убрана —
это его подпись, а не приём.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402

КРЕМ, ЧЕРНИЛА = "#F8F4EF", "#12130E"          # тёплая бумага источника, не белый лист
АКЦЕНТ = "#2F3A07"                            # фирменная олива, затемнённая до 9,6:1 по крему
ТЁМНЫЙ, ЛАЙМ, СВЕТЛЫЙ = стиль.ТЁМНЫЙ, стиль.ЛАЙМ, стиль.СВЕТЛЫЙ
К = "font-family:Onest,'Arial Black',sans-serif;font-weight:800"
Т = "font-family:Golos,'Helvetica Neue',Arial,sans-serif"

ПОЛЕ = 60                                     # 5,6% ширины холста — единое для всех блоков


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;background:{КРЕМ};color:{ЧЕРНИЛА} }}
    .карточка {{ position:absolute;left:{ПОЛЕ}px;top:130px;background:#FFFFFF;border-radius:20px;
        padding:26px;box-shadow:0 14px 40px rgba(18,19,14,.08);display:flex;align-items:center }}
    .карточка img {{ width:112px;height:112px;object-fit:contain;display:block }}
    .номер {{ position:absolute;left:{ПОЛЕ}px;top:330px;{Т};font-weight:700;font-size:44px;
        letter-spacing:.12em;color:{АКЦЕНТ} }}
    .имя {{ position:absolute;left:{ПОЛЕ}px;top:390px;{К};line-height:.98;letter-spacing:-.04em }}
    .тело {{ position:absolute;left:{ПОЛЕ}px;top:610px;width:880px;{Т};font-size:44px;line-height:1.3 }}
    .тело p {{ margin:0 }}
    .тело .первая {{ font-weight:700 }}
    /* Снимок уходит за нижний край — приём источника: он добирает чернила без слов.
       Рамка задана обеими сторонами, а картинка вписана по верхнему краю: если задать одну
       ширину, высоту начинают решать пропорции снимка, и кадр рассыпается — обрезанный
       под cookie-плашку снимок 8:3 давал высоту 285 px и уползал в нижние 17% кадра. */
    /* Снимок по центру и на одной высоте во всех кадрах — так владелец поставил его руками
       на кадрах 2 и 3 (верх ≈ 820, ширина 590–720). Рамка и отступ заданы числом, а не краем:
       иначе положение снимка начинает зависеть от пропорций файла и кадры расходятся. */
    .снимок {{ position:absolute;left:50%;transform:translateX(-50%);top:790px;
        width:720px;height:374px;
        object-fit:cover;object-position:top center;border-radius:18px;
        box-shadow:0 26px 70px rgba(18,19,14,.18) }}
    .счёт {{ position:absolute;left:{ПОЛЕ}px;bottom:96px;{Т};font-weight:700;font-size:38px;color:{АКЦЕНТ} }}
    .кот {{ position:absolute;z-index:3 }}
    .знак {{ position:absolute;left:80px;bottom:205px;height:44px;z-index:4 }}
    .полоса {{ position:absolute;left:0;bottom:176px;height:6px;
        box-shadow:0 1px 0 rgba(18,19,14,.30);z-index:4 }}
  </style>\n</helmet>\n""")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def знак_и_полоса(доля: float, тёмный: bool = False) -> str:
    """Полоса — фирменный лайм на всех кадрах, светлых и тёмных: это знак бренда, и он
    должен быть одного цвета во всей карусели. На светлом лайм бледный сам по себе, поэтому
    под ним лежит тонкая тёмная линия — она держит край, не перекрашивая полосу."""
    подкраска = "" if тёмный else "filter:brightness(.45) saturate(1.4);"
    цвет = ЛАЙМ
    return (f'<img class=знак style="{подкраска}" src="logo.png">'
            f'<div class=полоса style="width:{доля * 100:.1f}%;background:{цвет}"></div>')


def кегль(слово: str, предел: int = 230) -> int:
    """Кегль под ширину строки: широкие прописные Onest 800 режутся, если считать по числу
    знаков грубее. Доля 0,63 замерена по снятым кадрам стиля «промпты»."""
    return min(предел, int((1080 - 2 * ПОЛЕ) / (0.63 * max(len(слово), 1))))


def кот(к: dict) -> str:
    где = {ключ: к[ключ] for ключ in ("left", "top", "right", "bottom") if ключ in к}
    return стиль.кот(к["поза"], к["высота"], класс="кот", **где)


def обложка(о: dict, доля: float) -> str:
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:250px">
    <div style="{К};font-size:{кегль('монтировать', 190)}px;line-height:1.0;letter-spacing:-.04em;
        text-wrap:balance">{о['заголовок']}</div>
    <div style="{Т};font-size:48px;line-height:1.3;margin-top:44px;max-width:620px;
        color:{СВЕТЛЫЙ};text-wrap:pretty">{о['под']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def носитель(к: dict) -> str:
    """Имя файла визуала кадра: снимок сайта или нарисованная сцена."""
    return f'{к["снимок"]}-shot.jpg' if к.get("снимок") else f'{латиницей(к["сцена"])}.jpg'


def сервис(номер: int, всего: int, к: dict, доля: float) -> str:
    строки = "\n".join(
        f'    <p class="{"первая" if i == 0 and к.get("жирная_первая") else ""}">{с}</p>'
        for i, с in enumerate(к["текст"]))
    return голова() + f"""<div class=кадр>
  {f'<div class=карточка><img src="{к["значок"]}.png"></div>' if к.get("значок") else ""}
  <div class=номер>{к['номер']}</div>
  <div class=имя style="font-size:{кегль(к['имя'])}px">{к['имя']}</div>
  <div class=тело>
{строки}
  </div>
  <img class=снимок style="object-position:{к.get('положение', 'top center')}" src="{носитель(к)}">
  <div class=счёт>{номер}/{всего}</div>
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


def финал(ф: dict) -> str:
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:230px">
    <div style="{К};font-size:{кегль(ф['крупно'])}px;line-height:1.0;letter-spacing:-.04em;
        color:{ЛАЙМ}">{ф['крупно']}</div>
    <div style="{Т};font-weight:700;font-size:52px;line-height:1.26;margin-top:40px;
        max-width:820px">{ф['текст']}</div>
    <div style="{Т};font-size:40px;margin-top:22px">{ф['под']}</div>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Значки сервисов и снимки их страниц. Снимок обрезается по верхней части: ниже первого
    экрана начинается текст сайта, который в кадре всё равно не прочесть."""
    файлы = []
    for к in пост["кадры"]:
        if к.get("значок"):
            значок = папка / f"{к['значок']}.png"
            with Image.open(ТУТ.parent / "сервисы/значки" / f"{к['значок']}.png") as и:
                и = и.convert("RGBA")
                и.thumbnail((256, 256), Image.LANCZOS)
                и.save(значок, optimize=True)
            файлы.append(значок)
        if к.get("сцена"):
            цель = папка / f"{латиницей(к['сцена'])}.jpg"
            with Image.open(ТУТ.parent / "промпты/картинки" / f"{к['сцена']}.png") as и:
                и = и.convert("RGB")
                ширина, высота = и.size
                и = и.crop((0, int(высота * 0.25), ширина, высота))
                и.thumbnail((1000, 1000), Image.LANCZOS)
                и.save(цель, quality=76, optimize=True)
            файлы.append(цель)
            continue
        снимок = папка / f"{к['снимок']}-shot.jpg"
        with Image.open(ТУТ.parent / "подборка-сайтов/сайты" / f"{к['снимок']}.png") as и:
            и = и.convert("RGB")
            ширина, высота = и.size
            # Верхние 80% первого экрана: ниже живут cookie-плашки и начало подвала.
            # Если после этого снимок всё ещё выше рамки, режем до её пропорции.
            нужная = min(int(высота * к.get("верх", 0.8)), int(ширина / (720 / 380)))
            и = и.crop((0, 0, ширина, нужная))
            и.thumbnail((1000, 1000), Image.LANCZOS)
            и.save(снимок, quality=76, optimize=True)
        файлы.append(снимок)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
                "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
                "yu", "ya"]))


def латиницей(имя: str) -> str:
    return "".join(ЛАТ.get(б, б) for б in имя.lower())


def чужая_обложка(имя: str):
    """Обложку можно взять у другого стиля: владелец выбрал кадры отсюда, а обложку —
    из «промптов». Генератор зовётся по пути, потому что модули везде названы «холст»."""
    import importlib.util
    путь = ТУТ.parent / имя / "холст.py"
    спец = importlib.util.spec_from_file_location(f"холст_{имя}", путь)
    модуль = importlib.util.module_from_spec(спец)
    спец.loader.exec_module(модуль)
    return модуль.обложка


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)

    всего = len(пост["кадры"]) + 2
    рисовать_обложку = чужая_обложка(пост["обложка_из"]) if пост.get("обложка_из") else обложка
    доски = [("Main.dc.html", "01 · Обложка", рисовать_обложку(пост["обложка"], 1 / всего))]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['имя']}",
                      сервис(н + 1, всего, к, (н + 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600,
                                "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)],
                 "launch": {"view": "canvas"}}
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = sorted(Path("/private/tmp/claude-501/bundled-skills").glob("*/*/design/seed-canvas.mjs"),
               key=lambda п: п.stat().st_mtime)[-1]
    страница = папка / f"{латиницей(файл.stem)}.html"   # имя страницы — по имени поста
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"),
               "--out", str(страница), "--title", пост.get("название", "Холст"),
               "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    for к in картинки(пост, папка):
        команда += ["--image", str(к)]
    р = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)],
                              capture_output=True, text=True)
    print((р.stderr.strip() + "\n" if р.stderr.strip() else "") + проверка.stdout.strip()[:200])
    print("страница холста:", страница)


if __name__ == "__main__":
    main()
