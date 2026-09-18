# -*- coding: utf-8 -*-
"""Вариация «сервисов»: раздел со списком сервисов (пост с `"вид": "список"`).

Рерайт @degtyareval «Ты слабо монтируешь», 17.09.2026: у автора белые страницы с засечками и
нумерованным списком «Сервис — что делает». По слову владельца вид наш кремовый, а подборка
сервисов — Фото-Карусель: у каждой строки значок самого сервиса. Номер-пилюля, заголовок раздела,
белая карточка, знак с полосой — как у основного вида; внутри карточки строки «значок · имя — что
делает». Значка нет или он мельче 120 px — круг с первой буквой в цвете значка сервиса.

Доски холста 1080×1440; зовётся из `холст.py`.
"""
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent
БОРДО = "#5C0A0A"
МЕЛКИЙ = 120                   # значок меньше этого на круге 84 px расплывается — ставим букву


def _х():
    import холст                # холст запущен как __main__; здесь берём его функции модулем
    return холст


def значок_есть(имя: str | None) -> bool:
    if not имя:
        return False
    х = _х()
    путь = ТУТ / "значки" / х.значок_файл(имя)
    if not путь.exists():
        return False
    if путь.suffix == ".svg":
        return True
    with Image.open(путь) as и:
        return min(и.size) >= МЕЛКИЙ


def цвет_значка(имя: str | None) -> str:
    """Самый частый насыщенный цвет мелкого favicon — фон буквы; нет значка — олива."""
    х = _х()
    путь = ТУТ / "значки" / f"{имя}.png" if имя else None
    if not путь or not путь.exists():
        return х.ОЛИВА
    with Image.open(путь) as и:
        и = и.convert("RGBA").resize((32, 32))
        цвета = [(r, g, b) for r, g, b, a in и.getdata() if a > 200 and max(r, g, b) - min(r, g, b) > 40]
    if not цвета:
        return х.ЧЕРНИЛА
    r, g, b = max(set(цвета), key=цвета.count)
    return f"#{r:02X}{g:02X}{b:02X}"


def кружок(с: dict, размер: int) -> str:
    х = _х()
    фон = с.get("фон", "#FFFFFF")
    if значок_есть(с.get("значок")):
        return (f'<div style="flex: none; width: {размер}px; height: {размер}px; border-radius: 50%; background: {фон};'
                f' display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 18px rgba(18,19,14,0.10);">'
                f'<img src="{х.значок_файл(с["значок"])}" style="width: {round(размер * 0.64)}px; height: {round(размер * 0.64)}px;'
                f' object-fit: contain;"></div>')
    return (f'<div style="flex: none; width: {размер}px; height: {размер}px; border-radius: 50%;'
            f' background: {цвет_значка(с.get("значок"))}; color: #FFFFFF; display: flex; align-items: center;'
            f' justify-content: center; {х.К}; font-size: {round(размер * 0.46)}px;">{с["имя"][0]}</div>')


def кадр(номер: int, к: dict, доля: float) -> str:
    """Кегль и значок по числу строк: девять строк должны влезть в карточку, четыре — не тонуть в ней."""
    х = _х()
    строк = len(к["сервисы"])
    кегль, значок, зазор = (35, 70, 12) if строк >= 8 else (39, 82, 22) if строк >= 6 else (48, 104, 40)
    строки = "\n".join(
        f'    <div style="display: flex; align-items: center; gap: 22px;">{кружок(с, значок)}'
        f'<div style="{х.Т}; font-size: {кегль}px; line-height: 1.2; text-wrap: pretty;">'
        f'<b style="font-weight: 700; color: {х.ЧЕРНИЛА};">{с["имя"]}</b>'
        f'<span style="color: {х.МЯГКИЙ};"> — {с["что"]}</span></div></div>'
        for с in к["сервисы"])
    return х.голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {х.КРЕМ}; color: {х.ЧЕРНИЛА};">
  <div style="position: absolute; left: 0; right: 0; top: 110px; text-align: center;">
    <span style="{х.К}; display: inline-block; font-size: 40px; color: {х.КРЕМ}; background: {х.ОЛИВА}; border-radius: 44px; padding: 6px 32px;">{номер:02d}</span>
  </div>
  <div style="position: absolute; left: 80px; right: 80px; top: 190px; {х.К}; font-size: 84px; line-height: 1.05; letter-spacing: -0.03em; text-align: center;">{к['заголовок']}</div>
  <div style="position: absolute; left: 40px; right: 40px; top: 310px; bottom: 262px; background: #FFFFFF; border-radius: 44px; padding: 30px 36px; display: flex; flex-direction: column; justify-content: center; gap: {зазор}px; box-shadow: 0 16px 50px rgba(18,19,14,0.07);">
{строки}
  </div>
  {х.знак_и_полоса(доля)}
</div>""" + х.ХВОСТ


def зачин(з: dict, доля: float) -> str:
    """Второй кадр: мысль крупно и пояснение — «Всё потому, что ты не используешь ИИ»."""
    х = _х()
    return х.голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {х.КРЕМ}; color: {х.ЧЕРНИЛА};">
  <div style="position: absolute; left: 80px; right: 80px; top: 360px; display: flex; flex-direction: column; gap: 48px;">
    <div style="{х.К}; font-size: 112px; line-height: 1.02; letter-spacing: -0.035em; text-wrap: balance;">{з['крупно']}</div>
    <div style="{х.Т}; font-size: 52px; line-height: 1.3; color: {х.МЯГКИЙ}; text-wrap: pretty; max-width: 820px;">{з['под']}</div>
  </div>
  {х.знак_и_полоса(доля)}
</div>""" + х.ХВОСТ


def обложка_автора(о: dict, доля: float) -> str:
    """А — как у автора: бордовый кадр, узкие белые прописные, курсив с засечками ниже."""
    х = _х()
    фейсы = х.стиль.фейсы(("Oswald", "oswald-600", 600), ("Playfair", "playfair-700-italic", 700))
    return х.голова(фейсы + "\n" + х.стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                                                 ("Golos", "golos-700", 700))) + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {БОРДО}; color: #FFFFFF;">
  <div style="position: absolute; left: 60px; right: 60px; top: 420px; display: flex; flex-direction: column; align-items: center; text-align: center;">
    <div style="font-family: Oswald, sans-serif; font-weight: 600; font-size: 190px; line-height: 1.02; text-transform: uppercase; transform: scaleX(0.86);">{о['строки'][0]}<br>{о['строки'][1]}</div>
    <div style="margin-top: 36px; font-family: Playfair, serif; font-style: italic; font-weight: 700; font-size: 72px;">{о['под']}</div>
  </div>
  {х.знак_и_полоса(доля, тёмный=True)}
</div>""" + х.ХВОСТ


def обложка_сцена(о: dict, доля: float) -> str:
    """Б — сцена: число и тема крупно, кот-монтажёр за ноутбуком."""
    х = _х()
    return х.голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {х.КРЕМ}; color: {х.ЧЕРНИЛА};">
  <div style="position: absolute; left: 80px; right: 80px; top: 150px; display: flex; flex-direction: column; gap: 26px;">
    <div style="{х.Т}; font-weight: 700; font-size: 34px; letter-spacing: 0.12em; text-transform: uppercase; color: {х.ОЛИВА};">{о['над']}</div>
    <div style="{х.К}; font-size: 128px; line-height: 1.0; letter-spacing: -0.035em; text-wrap: balance;">{о['заголовок']}</div>
  </div>
  {х.кот(о['кот'])}
  {х.знак_и_полоса(доля)}
</div>""" + х.ХВОСТ


def обложка_маркер(о: dict, значки: list[dict], доля: float) -> str:
    """В — маркер: гигантское число оливой, строка темы, лаймовый маркер и ряд значков."""
    х = _х()
    ряд = "\n".join(f"      {кружок(с, 104)}" for с in значки)
    return х.голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {х.КРЕМ}; color: {х.ЧЕРНИЛА};">
  <div style="position: absolute; left: 50px; top: 90px; {х.К}; font-size: 560px; line-height: 1; letter-spacing: -0.06em; color: {х.ОЛИВА};">{о['число']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 690px; {х.К}; font-size: 110px; line-height: 1.0; letter-spacing: -0.035em;">{о['строка']}</div>
  <div style="position: absolute; left: 80px; top: 830px; {х.К}; font-size: 72px; letter-spacing: -0.03em; background: {х.ЛАЙМ}; padding: 4px 22px; border-radius: 10px; transform: rotate(-2deg);">{о['маркер']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 990px; display: flex; gap: 20px; flex-wrap: wrap;">
{ряд}
  </div>
  {х.знак_и_полоса(доля)}
</div>""" + х.ХВОСТ


def доски(пост: dict) -> list[tuple[str, str, str]]:
    х = _х()
    всего = len(пост["кадры"]) + 3
    д = [("Main.dc.html", "01 · Обложка А · как у автора", обложка_автора(пост["обложка"], 1 / всего)),
         ("Kadr02.dc.html", "02 · Зачин", зачин(пост["зачин"], 2 / всего))]
    for н, к in enumerate(пост["кадры"], 1):
        д.append((f"Kadr{н + 2:02d}.dc.html", f"{н + 2:02d} · {к['заголовок']}", кадр(н, к, (н + 2) / всего)))
    д.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", х.финал(пост["финал"])))
    д.append(("Oblozhka2.dc.html", "Обложка Б · сцена", обложка_сцена(пост["обложка_сцена"], 1 / всего)))
    по_имени = {с["имя"]: с for к in пост["кадры"] for с in к["сервисы"]}   # Topaz у автора дважды — в ряд один раз
    значки = [по_имени[имя] for имя in пост["обложка_маркер"]["значки"]]
    д.append(("Oblozhka3.dc.html", "Обложка В · маркер", обложка_маркер(пост["обложка_маркер"], значки, 1 / всего)))
    return д


def исходник_кота(поза: str) -> Path:
    """Поза бота или кот, нарисованный под пост в `до-после/коты/` (имя там кириллицей, в посте — латиницей)."""
    х = _х()
    if (х.стиль.ПОЗЫ / f"{поза}.png").exists():
        return х.стиль.ПОЗЫ / f"{поза}.png"
    for путь in (ТУТ.parent / "до-после/коты").glob("*.png"):
        if х.латиницей(путь.stem) == поза:
            return путь
    raise SystemExit(f"нет позы кота: {поза}")


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Картинки холста: настоящие значки до 256 px, коты webp, логотип — каждая меньше 70 КБ."""
    х = _х()
    файлы = []
    имена = {с["значок"] for к in пост["кадры"] for с in к["сервисы"] if значок_есть(с.get("значок"))}
    for имя in sorted(имена):
        исходник = ТУТ / "значки" / х.значок_файл(имя)
        цель = папка / исходник.name
        if исходник.suffix == ".svg":
            цель.write_bytes(исходник.read_bytes())
        else:
            with Image.open(исходник) as и:
                и = и.convert("RGBA")
                и.thumbnail((256, 256), Image.LANCZOS)
                и.save(цель, optimize=True)
        файлы.append(цель)
    for к in (пост["обложка_сцена"]["кот"], пост["финал"]["кот"]):
        цель = папка / f"kot-{к['поза']}.webp"
        with Image.open(исходник_кота(к["поза"])) as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((1000, round(к["высота"] * 1.5)), Image.LANCZOS)
            и.save(цель, quality=86)
        файлы.append(цель)
    with Image.open(х.стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]
