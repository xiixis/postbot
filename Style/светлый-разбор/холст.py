# -*- coding: utf-8 -*-
"""Стиль «светлый разбор»: python3 холст.py посты/<пост>.json

Снят с кадров 2–8 карусели Instagram `Dc_JBG4D3Oq` (разбор — `_style.json`, кадры — `референс/`).
Кадры повторяются один в один по слову владельца 18.09.2026; своя у нас только обложка и финал
(у автора там его фото и воронка «напиши ТОКЕН» — это его почерк).

Устройство кадра: номер «N/8» вверху слева, чёрный жирный заголовок по центру, серая подводка,
сетка белых пилюль (ряд, 2×2 или вертикальный список с цветной полосой и таймлайном),
снимок окна файла, серебристая плашка-вывод, тонкая стрелка «→» в правом нижнем углу.

Доски холста 1080×1440; дальше как у «сервисов»: Artifact → «готово» → `../выпуск.py`.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
sys.path.insert(0, str(ТУТ.parent / "до-после"))
import стиль  # noqa: E402

ФОН, ЧЕРНИЛА, МЯГКИЙ = "#F2F1EF", "#2B2A28", "#4A4A48"
# Фирменные цвета вместо авторских оранжевого и сиреневого (слово владельца 18.09.2026).
# Олива — для текста и точек: лайм по светлому фону даёт 1,7:1 и не читается. Лайм — заливками
# и полосами, графит — третьим цветом, чтобы RULES / INDEX / MAP различались.
ОЛИВА, ЛАЙМ, ГРАФИТ = стиль.ОЛИВА, стиль.ЛАЙМ, "#3A3E33"
# Цвета трёх файлов — авторские (слово владельца 18.09.2026: «там где RULES INDEX MAP верни как
# было»). Это не палитра канала, а метки: у каждого файла свой цвет, и он один на всех кадрах —
# в списке, в цепочке, на обложке и в подсветке заголовка.
ФАЙЛЫ = {"RULES": "#F2542D", "INDEX": "#F89B4B", "MAP": "#A85CF9"}
НОЧЬ = "#0B0B0A"
К = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800; letter-spacing: -0.02em"
Т = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif"
# Тень в два слоя: ближняя очерчивает форму, дальняя даёт высоту; светлая кромка сверху —
# как на контролах iOS. Плоская тень в один слой выглядит наклейкой.
ТЕНЬ_ПИЛЮЛИ = ("box-shadow: 0 1px 2px rgba(23,22,20,.06), 0 10px 24px rgba(23,22,20,.10),"
               " inset 0 1px 0 rgba(255,255,255,.9)")
# Зерно — адрес без кавычек: двойные кавычки внутри style рвут атрибут, и разметка вываливается
# текстом в кадр (поймано отрисовкой 18.09).
ЗЕРНО = ("background-image: url(data:image/svg+xml;utf8,"
         "%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%27200%27%20height%3D%27200%27%3E"
         "%3Cfilter%20id%3D%27n%27%3E%3CfeTurbulence%20type%3D%27fractalNoise%27%20baseFrequency%3D%27.85%27"
         "%20numOctaves%3D%272%27/%3E%3C/filter%3E%3Crect%20width%3D%27200%27%20height%3D%27200%27"
         "%20filter%3D%27url%28%23n%29%27/%3E%3C/svg%3E);"
         " opacity: .05; mix-blend-mode: multiply;")
ПОДЛОЖКА = (f'<div style="position: absolute; inset: 0; background:'
            f' radial-gradient(120% 60% at 50% -10%, #FFFFFF 0%, rgba(255,255,255,0) 60%),'
            f' radial-gradient(90% 50% at 10% 110%, rgba(86,105,12,.08) 0%, rgba(86,105,12,0) 70%),'
            f' linear-gradient(180deg, #F6F5F3 0%, #EDECE8 100%);"></div>'
            f'<div style="position: absolute; inset: 0; {ЗЕРНО}"></div>')
СЕРЕБРО = ("background: linear-gradient(118deg, #F0F0EE 0%, #C9C9C6 22%, #9F9F9C 48%, #D7D7D4 72%, #ABABA8 100%);"
           " box-shadow: 0 2px 4px rgba(23,22,20,.12), 0 16px 34px rgba(23,22,20,.22),"
           " inset 0 1px 0 rgba(255,255,255,.85), inset 0 -1px 0 rgba(0,0,0,.10);")
# position и overflow задаёт сама плашка: в палитре они перебивали её position: absolute,
# и плашка уезжала за кадр (поймано отрисовкой 18.09).
БЛИК = ('<span style="position: absolute; left: -20%; top: -60%; width: 60%; height: 220%;'
        ' background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.55) 50%,'
        ' rgba(255,255,255,0) 100%); transform: rotate(8deg); pointer-events: none;"></span>')


def _дп():
    import importlib.util
    спека = importlib.util.spec_from_file_location("холст_до_после", ТУТ.parent / "до-после" / "холст.py")
    м = importlib.util.module_from_spec(спека)
    sys.modules["холст_до_после"] = м
    спека.loader.exec_module(м)
    return м


def голова(тёмный: bool = False) -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            "</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))
            + f"\n    body {{ margin: 0; background: {НОЧЬ if тёмный else ФОН}; }}\n  </style>\n</helmet>\n")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"
СТРЕЛКА = ("<svg viewBox='0 0 120 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round'"
           " style='width:120px;height:24px'><path d='M2 12h112M104 4l12 8-12 8'/></svg>")


def служебное(номер: int, всего: int, тёмный: bool = False) -> str:
    цвет = "#EDEFE6" if тёмный else ЧЕРНИЛА
    низ = ("" if тёмный else
           f'<div style="position: absolute; right: 70px; bottom: 60px; color: {МЯГКИЙ};">{СТРЕЛКА}</div>')
    лого = ("" if тёмный else
            f'<img src="logo.png" style="position: absolute; left: 80px; bottom: 56px; height: 34px;'
            f' filter: brightness(.45) saturate(1.4);">')
    точка = (f'<span style="width: 10px; height: 10px; border-radius: 50%; background: {ОЛИВА};'
             f' box-shadow: 0 0 0 5px rgba(86,105,12,.16);"></span>')
    плашка_номера = ("background: rgba(255,255,255,.75); box-shadow: inset 0 0 0 1px rgba(23,22,20,.08),"
                     " 0 4px 12px rgba(23,22,20,.06);" if not тёмный else
                     "background: rgba(255,255,255,.08); box-shadow: inset 0 0 0 1px rgba(255,255,255,.14);")
    return (f'  <div style="position: absolute; left: 80px; top: 58px; display: flex; align-items: center; gap: 12px;'
            f' padding: 10px 20px; border-radius: 999px; {плашка_номера} {Т}; font-weight: 700; font-size: 30px;'
            f' letter-spacing: .06em; color: {цвет};">{точка}{номер}/{всего}</div>\n  {низ}\n  {лого}')


def призрак(номер: int) -> str:
    """Гигантская цифра кадра фоном: ориентир в ленте, виден даже в превью."""
    return (f'  <div style="position: absolute; right: -40px; top: 120px; {К}; font-size: 420px; line-height: .8;'
            f' color: rgba(43,42,40,.05); pointer-events: none;">{номер:02d}</div>')


def подсветить(строка: str) -> str:
    """Ключевые слова — оранжевым: заголовок перестаёт быть сплошной чёрной плитой."""
    for слово, цвет in list(ФАЙЛЫ.items()) + [("токенов", ОЛИВА), ("токены", ОЛИВА)]:
        строка = строка.replace(слово, f'<span style="color: {цвет};">{слово}</span>')
    return строка


def заголовок(строки: list[str], верх: int = 150, кегль: int = 64, цвет: str = ЧЕРНИЛА) -> str:
    текст = "<br>".join(подсветить(с) for с in строки)
    return (f'  <div style="position: absolute; left: 80px; right: 80px; top: {верх}px; {К}; font-size: {кегль}px;'
            f' line-height: 1.12; text-align: center; color: {цвет};">{текст}</div>')


def подводка(строки: list[str], верх: int) -> str:
    текст = "<br>".join(строки)
    return (f'  <div style="position: absolute; left: 90px; right: 90px; top: {верх}px; {Т}; font-size: 34px;'
            f' line-height: 1.35; text-align: center; color: {МЯГКИЙ};">{текст}</div>')


def пилюля(п: dict) -> str:
    """Белая пилюля: либо оранжевый номер сверху, либо оранжевая точка слева."""
    if п.get("номер"):
        нутро = (f'<div style="{Т}; font-weight: 700; font-size: 26px; color: {ОЛИВА};">{п["номер"]}</div>'
                 f'<div style="{Т}; font-weight: 700; font-size: 30px; line-height: 1.2; margin-top: 6px;">{п["текст"]}</div>')
        выключка = ""
    else:
        нутро = (f'<span style="flex: none; width: 24px; height: 24px; border-radius: 50%; background: {ОЛИВА};'
                 f' box-shadow: 0 0 0 8px rgba(86,105,12,.18);"></span>'
                 f'<span style="{Т}; font-weight: 700; font-size: 30px; line-height: 1.2;">{п["текст"]}</span>')
        выключка = "display: flex; align-items: center; gap: 20px;"
    return (f'      <div style="position: relative; overflow: hidden; background: linear-gradient(180deg,#FFFFFF,#FBFAF8);'
            f' border-radius: 20px; padding: 22px 26px 22px 34px; {ТЕНЬ_ПИЛЮЛИ}; color: {ЧЕРНИЛА}; {выключка}">'
            f'<span style="position: absolute; left: 0; top: 0; bottom: 0; width: 8px;'
            f' background: linear-gradient(180deg, {ОЛИВА}, {ЛАЙМ});"></span>{нутро}</div>')


def сетка(пилюли: list[dict], верх: int, колонок: int) -> str:
    ячейки = "\n".join(пилюля(п) for п in пилюли)
    return (f'  <div style="position: absolute; left: 80px; right: 80px; top: {верх}px; display: grid;'
            f' grid-template-columns: repeat({колонок}, 1fr); gap: 24px;">\n{ячейки}\n  </div>')


def список_файлов(строки: list[dict], верх: int) -> str:
    """Вертикальные карточки с цветной полосой и таймлайном 1·2·3 слева — кадр «три файла»."""
    карточки = ""
    for н, с in enumerate(строки):
        цвет = ФАЙЛЫ.get(с["имя"], ОЛИВА)
        карточки += (f'    <div style="position: relative; background: #FFFFFF; border-radius: 24px;'
                     f' padding: 30px 34px 30px 44px; {ТЕНЬ_ПИЛЮЛИ};">'
                     f'<span style="position: absolute; left: 22px; top: 26px; bottom: 26px; width: 10px;'
                     f' border-radius: 6px; background: linear-gradient(180deg, {цвет}, {цвет}AA);"></span>'
                     f'<div style="{К}; font-size: 46px; color: {ЧЕРНИЛА};">{с["имя"]}</div>'
                     f'<div style="{Т}; font-size: 30px; color: {МЯГКИЙ}; margin-top: 8px;">{с["что"]}</div></div>')
    кружки = "".join(
        f'<div style="width: 46px; height: 46px; border-radius: 50%; background: #FFFFFF; border: 3px solid {ФАЙЛЫ['RULES']};'
        f' display: flex; align-items: center; justify-content: center; {Т}; font-weight: 700; font-size: 24px;'
        f' color: {ФАЙЛЫ['RULES']}; box-shadow: 0 0 0 6px rgba(242,84,45,.10), 0 6px 14px rgba(23,22,20,.10);">'
        f'{н + 1}</div>' for н in range(len(строки)))
    return (f'  <div style="position: absolute; left: 80px; right: 80px; top: {верх}px; display: flex; gap: 26px;">'
            f'<div style="position: relative; display: flex; flex-direction: column; justify-content: space-around;'
            f' align-items: center; width: 46px;">'
            f'<span style="position: absolute; top: 24px; bottom: 24px; width: 4px; background: rgba(242,84,45,.35);"></span>'
            f'{кружки}</div>'
            f'<div style="flex: 1; display: flex; flex-direction: column; gap: 26px;">{карточки}</div></div>')


def цепочка(звенья: list[dict], верх: int) -> str:
    """Три карточки в ряд со стрелками между ними — кадр «агент понимает»."""
    куски = []
    for н, з in enumerate(звенья):
        цвет = ФАЙЛЫ.get(з["имя"], ОЛИВА)
        куски.append(f'<div style="flex: 1; background: #FFFFFF; border-radius: 22px; padding: 26px 18px 30px;'
                     f' text-align: center; {ТЕНЬ_ПИЛЮЛИ};">'
                     f'<div style="height: 8px; border-radius: 4px; background: linear-gradient(90deg, {цвет}, {цвет}55); margin: 0 14px 22px;"></div>'
                     f'<div style="{К}; font-size: 40px; color: {ЧЕРНИЛА};">{з["имя"]}</div>'
                     f'<div style="{Т}; font-size: 26px; color: {МЯГКИЙ}; margin-top: 12px;">{з["что"]}</div></div>')
    между = f'<div style="{К}; font-size: 44px; color: {ОЛИВА}; align-self: center;">→</div>'
    тело = между.join(куски)
    return (f'  <div style="position: absolute; left: 80px; right: 80px; top: {верх}px; display: flex; gap: 16px;">'
            f'{тело}</div>')


def снимок(имя: str, верх: int, высота: int) -> str:
    """Окно стоит ровно: наклон с отражением («летающее окно») владелец забраковал 18.09.2026.
    Глубину держат волосяная рамка и двухслойная тень."""
    return (f'  <img src="{имя}.jpg" style="position: absolute; left: 80px; top: {верх}px; width: 920px;'
            f' height: {высота}px; object-fit: cover; object-position: top center; border-radius: 16px;'
            f' box-shadow: 0 2px 4px rgba(23,22,20,.10), 0 18px 44px rgba(23,22,20,.16),'
            f' 0 0 0 1px rgba(23,22,20,.06);">')


def плашка(строки: list[str], низ: int = 150, кегль: int = 36) -> str:
    текст = "<br>".join(строки)
    return (f'  <div style="position: absolute; overflow: hidden; left: 80px; right: 80px; bottom: {низ}px;'
            f' border-radius: 18px; padding: 30px 36px; {СЕРЕБРО} {Т}; font-weight: 700; font-size: {кегль}px; line-height: 1.3;'
            f' text-align: center; color: {ЧЕРНИЛА};">{БЛИК}<span style="position: relative;">{текст}</span></div>')


def кадр(к: dict, номер: int, всего: int) -> str:
    части = [служебное(номер, всего), призрак(номер),
             заголовок(к["заголовок"], к.get("верх", 150), к.get("кегль", 64))]
    if к.get("подводка"):
        части.append(подводка(к["подводка"], к.get("подводка_верх", 330)))
    if к.get("пилюли"):
        части.append(сетка(к["пилюли"], к.get("пилюли_верх", 430), к.get("колонок", 3)))
    if к.get("файлы"):
        части.append(список_файлов(к["файлы"], к.get("файлы_верх", 380)))
    if к.get("цепочка"):
        части.append(цепочка(к["цепочка"], к.get("цепочка_верх", 430)))
    if к.get("снимок"):
        части.append(снимок(к["снимок"], к.get("снимок_верх", 700), к.get("снимок_высота", 380)))
    if к.get("вывод"):
        части.append(плашка(к["вывод"], к.get("вывод_низ", 150)))
    тело = "\n".join(части)
    return голова() + (f'<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden;'
                       f' background: {ФОН}; color: {ЧЕРНИЛА};">\n  {ПОДЛОЖКА}\n{тело}\n</div>') + ХВОСТ


def обложка(о: dict, всего: int) -> str:
    """А — сцена: кот с ноутбуком, заголовок, серебристая плашка с обещанием."""
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ФОН}; color: {ЧЕРНИЛА};">
  {ПОДЛОЖКА}
{служебное(1, всего)}
{заголовок(о['заголовок'], 190, 78)}
{подводка(о['под'], 470)}
  <img src="kot.webp" style="position: absolute; left: 300px; top: 600px; width: 480px;">
{плашка(о['плашка'], 150, 38)}
</div>""" + ХВОСТ


def обложка_число(о: dict, всего: int) -> str:
    """Б — число: гигантская «3» оранжевым, три цветные карточки файлов, маркер снизу."""
    карточки = "".join(
        f'<div style="flex: 1; background: #FFFFFF; border-radius: 22px; padding: 26px 14px; text-align: center;'
        f' {ТЕНЬ_ПИЛЮЛИ}; position: relative; overflow: hidden;">'
        f'<div style="position: absolute; left: 0; right: 0; top: 0; height: 12px; background: {ц};"></div>'
        f'<div style="{К}; font-size: 40px; margin-top: 10px;">{и}</div></div>'
        for и, ц in ((и, ФАЙЛЫ.get(и, ОЛИВА)) for и in о["файлы"]))
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ФОН}; color: {ЧЕРНИЛА};">
  {ПОДЛОЖКА}
{служебное(1, всего)}
  <div style="position: absolute; left: 80px; top: 150px; {К}; font-size: 540px; line-height: .82; color: {ОЛИВА};">{о['число']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 640px; {К}; font-size: 86px; line-height: 1.06;">{'<br>'.join(о['строки'])}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 900px; display: flex; gap: 20px;">{карточки}</div>
{плашка(о['плашка'], 170, 38)}
</div>""" + ХВОСТ


def обложка_экран(о: dict, всего: int) -> str:
    """В — доказательство: снимок списка файлов во весь кадр, заголовок плашкой поверх."""
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {НОЧЬ}; color: #EDEFE6;">
  <img src="{о['снимок']}.jpg" style="position: absolute; left: 50%; top: 120px; width: 1180px; transform: translateX(-50%) rotateZ(-2deg); opacity: .5; border-radius: 18px;">
  <div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(11,11,10,.35) 0%, rgba(11,11,10,.92) 62%);"></div>
{служебное(1, всего, тёмный=True)}
  <div style="position: absolute; left: 80px; right: 80px; top: 720px; {К}; font-size: 82px; line-height: 1.06; color: #FFFFFF;">{'<br>'.join(о['строки'])}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 1010px; {Т}; font-size: 40px; line-height: 1.3; color: #B9BCB2;">{о['под']}</div>
  <img src="logo.png" style="position: absolute; left: 80px; bottom: 60px; height: 34px;">
</div>""" + ХВОСТ


def финал(ф: dict, всего: int) -> str:
    """Наш: тёмный кадр, призыв в канал вместо воронки автора."""
    пункты = "".join(f'<li style="margin-bottom: 14px;">{п}</li>' for п in ф["пункты"])
    return голова(тёмный=True) + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {НОЧЬ}; color: #EDEFE6;">
{служебное(всего, всего, тёмный=True)}
{заголовок(ф['заголовок'], 250, 72, '#EDEFE6')}
  <ul style="position: absolute; left: 180px; right: 120px; top: 500px; {Т}; font-size: 38px; line-height: 1.35;">{пункты}</ul>
  <img src="kot-final.webp" style="position: absolute; right: 60px; bottom: 300px; height: 420px;">
{плашка(ф['плашка'], 170, 36)}
  <img src="logo.png" style="position: absolute; left: 80px; bottom: 60px; height: 34px;">
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    файлы = []
    имена = {к["снимок"] for к in пост["кадры"] if к.get("снимок")} | {пост["обложка_экран"]["снимок"]}
    for имя in sorted(имена):
        цель = папка / f"{имя}.jpg"
        with Image.open(ТУТ / "снимки" / f"{имя}.png") as и:
            и = и.convert("RGB")
            и.thumbnail((1380, 1380), Image.LANCZOS)  # окна нарисованы под полуторный масштаб доски
            качество = 78
            while True:
                и.save(цель, quality=качество, optimize=True)
                if цель.stat().st_size < 110_000 or качество <= 40:
                    break
                качество -= 8
        файлы.append(цель)
    for ключ, имя in (("обложка", "kot.webp"), ("финал", "kot-final.webp")):
        поза = пост[ключ]["кот"]
        with Image.open(стиль.ПОЗЫ / f"{поза}.png") as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((900, 900), Image.LANCZOS)
            и.save(папка / имя, quality=84, method=6)
        файлы.append(папка / имя)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + [папка / "logo.png"]


def main():
    дп = _дп()
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text(encoding="utf-8"))
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    всего = len(пост["кадры"]) + 2
    # ⛔️ Три обложки обязательны: правило владельца, холст без них не выкладывается.
    обложки = {"сцена": lambda: обложка(пост["обложка"], всего),
               "число": lambda: обложка_число(пост["обложка_число"], всего),
               "экран": lambda: обложка_экран(пост["обложка_экран"], всего)}
    главная = пост.get("главная", "сцена")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {' '.join(к['заголовок'])[:28]}", кадр(к, н, всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"], всего)))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    если_мало = [д for д in доски if д[0].startswith(("Main", "Oblozhka"))]
    assert len(если_мало) == 3, "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html, encoding="utf-8")

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600, "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)], "launch": {"view": "canvas"}}
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{пост['название']}: кадры повторяют referенс один в один, обложка и финал наши. "
        "Двигайте и правьте прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1), encoding="utf-8")

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    картинки(пост, папка)          # картинки и коты рядом с досками
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
