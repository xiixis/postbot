# -*- coding: utf-8 -*-
"""Стиль «нативный экран»: промпт показан прямо в поле ввода ИИ, с клавиатурой телефона.

    python3 холст.py посты/<пост>.json

Снят с @promptdrill (в библиотеке `данные/promptdrill.json` (библиотека удалена 18.09, числа перенесены в паспорт),
7,9 млн показов, 8 кадров) — семейство «скриншот переписки с нейросетью»: медиана вовлечения
8,7% против 2,4% у аккуратно свёрстанных карточек. Приём в чистом виде: не рассказать про
промпт, а показать его ровно там, куда зритель его вставит; клавиатура в кадре — доказательство,
что это настоящий экран.

Что наше: чернил мало, содержимое в центральной трети, шапка — наш аккаунт (кот и @4xtube),
пилюля-подзаголовок белая, лаймовая полоса и знак внизу. Чужую «клавиатуру именно iOS» не
копируем попиксельно: рисуем свою раскладку тем же приёмом.

Доски холста 1080×1440; дальше как у «сервисов»: выложить Artifact → «готово» → `../выпуск.py`.
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

ГРУНТ, ТЕКСТ, СЕРЫЙ = "#0A0B09", "#F2F4EC", "#2A2D27"
ПОЛЕ, КЛАВИША = "#1E211B", "#6E7269"
К = "font-family: Onest, 'Arial Black', sans-serif; font-weight: 800"
Т = "font-family: Golos, 'Helvetica Neue', Arial, sans-serif"

# Клавиатура телефона целиком: русская раскладка, четыре ряда. Обрезанная нижним краем
# читалась как ошибка вёрстки (слово владельца 18.09.2026).
РЯДЫ = ["йцукенгшщзхъ", "фывапролджэ", "ячсмитьбю"]
КЛ_ПОЛЯ, КЛ_ЗАЗОР, КЛ_ВЫСОТА = 12, 10, 92
ПОД_КЛАВИАТУРОЙ = 4 * 92 + 3 * 12 + 42          # высота панели: полоса прогресса идёт над ней


def _дп():
    import importlib.util
    спека = importlib.util.spec_from_file_location("холст_до_после", ТУТ.parent / "до-после" / "холст.py")
    м = importlib.util.module_from_spec(спека)
    sys.modules["холст_до_после"] = м
    спека.loader.exec_module(м)
    return м


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            "</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700))
            + f"\n    body {{ margin: 0; background: {ГРУНТ}; }}\n  </style>\n</helmet>\n")


ХВОСТ = "\n</x-dc>\n</body>\n</html>\n"


def статус() -> str:
    """Строка состояния: время и значки. Кадр должен читаться как экран телефона, а не как карточка."""
    палки = "".join(f'<span style="display:inline-block;width:7px;height:{9 + i * 4}px;border-radius:2px;'
                    f'background:{ТЕКСТ};margin-left:3px;vertical-align:bottom"></span>' for i in range(4))
    return f"""  <div style="position: absolute; left: 60px; right: 60px; top: 52px; display: flex; align-items: center;
       justify-content: space-between; {Т}; font-weight: 700; font-size: 34px; color: {ТЕКСТ};">
    <div>9:41</div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <div>{палки}</div>
      <div style="width: 52px; height: 26px; border-radius: 8px; border: 3px solid {ТЕКСТ}; padding: 3px;">
        <div style="width: 70%; height: 100%; border-radius: 3px; background: {ТЕКСТ};"></div>
      </div>
    </div>
  </div>"""


def шапка() -> str:
    """Наш аккаунт сверху каждого кадра: пост читается как пересланный экран, а не как карточка."""
    return f"""  <div style="position: absolute; left: 90px; top: 150px; display: flex; align-items: center; gap: 24px;">
    <img src="ava.webp" style="width: 88px; height: 88px; border-radius: 50%; object-fit: cover; background: #14170F;">
    <div style="{Т}; line-height: 1.25;">
      <div style="font-weight: 700; font-size: 38px; color: {ТЕКСТ};">4xTube</div>
      <div style="font-size: 32px; color: #8D9186;">@4xtube</div>
    </div>
  </div>"""


def полоса(доля: float, светлый: bool = False, над_клавиатурой: bool = False) -> str:
    """Логотип — в шапке справа, а не внизу: низ кадра занят клавиатурой, и знак уходил под неё."""
    приглушить = " filter: brightness(.45) saturate(1.4);" if светлый else ""
    return (f'<img src="logo.png" style="position: absolute; right: 90px; top: 168px; height: 52px;{приглушить}">'
            f'<div style="position: absolute; left: 0; bottom: {ПОД_КЛАВИАТУРОЙ if над_клавиатурой else 0}px; height: 8px; width: {доля * 100:.1f}%; z-index: 4;'
            f' background: {стиль.ЛАЙМ};"></div>')


def _клавиша(знак: str, ширина: float, тёмная: bool = False) -> str:
    фон = "#3A3E36" if тёмная else КЛАВИША
    цвет = "#EDEFE6" if тёмная else "#10120D"
    return (f'<div style="flex: 0 0 {ширина:.1f}px; height: {КЛ_ВЫСОТА}px; border-radius: 12px; background: {фон};'
            f' box-shadow: 0 2px 0 rgba(0,0,0,.55); display: flex; align-items: center; justify-content: center;'
            f' {Т}; font-size: 40px; color: {цвет};">{знак}</div>')


def клавиатура() -> str:
    """Панель с четырьмя рядами: буквы, ряд с Shift и стиранием, нижний ряд с пробелом.

    Ширина клавиши считается по самому длинному ряду, чтобы столбцы стояли ровно, а Shift
    и стирание занимали остаток третьего ряда.
    """
    поле_ш = 1080 - 2 * КЛ_ПОЛЯ
    ширина = (поле_ш - (len(РЯДЫ[0]) - 1) * КЛ_ЗАЗОР) / len(РЯДЫ[0])
    ряды = []
    for н, ряд in enumerate(РЯДЫ):
        клавиши = "".join(_клавиша(з, ширина) for з in ряд)
        if н == 2:
            край = (поле_ш - (len(ряд) + 1) * КЛ_ЗАЗОР - len(ряд) * ширина) / 2
            клавиши = _клавиша("⇧", край, тёмная=True) + клавиши + _клавиша("⌫", край, тёмная=True)
        ряды.append(f'    <div style="display: flex; gap: {КЛ_ЗАЗОР}px; justify-content: center;'
                    f' margin-top: {0 if not н else КЛ_ЗАЗОР + 2}px;">{клавиши}</div>')
    пробел = поле_ш - 3 * КЛ_ЗАЗОР - 2 * (ширина * 1.7)
    низ = (_клавиша("123", ширина * 1.7, тёмная=True) + _клавиша("пробел", пробел)
           + _клавиша("ввод", ширина * 1.7, тёмная=True))
    ряды.append(f'    <div style="display: flex; gap: {КЛ_ЗАЗОР}px; justify-content: center;'
                f' margin-top: {КЛ_ЗАЗОР + 2}px;">{низ}</div>')
    тело = "\n".join(ряды)
    return (f'  <div style="position: absolute; left: 0; right: 0; bottom: 0; padding: {КЛ_ПОЛЯ}px {КЛ_ПОЛЯ}px 30px;'
            f' background: #16190F; box-shadow: 0 -20px 50px rgba(0,0,0,.5);">\n{тело}\n  </div>')


def диктовка(строка: str) -> str:
    """Панель диктовки вместо клавиатуры: кнопка микрофона и бегущая волна.

    Приём тот же, что с клавиатурой у @promptdrill: внизу кадра показано, чем человек вводит
    текст. Для поста про голосовой ввод клавиатура была бы враньём — там микрофон.
    """
    import hashlib
    столбики = ""
    for i in range(46):
        высота = 14 + (int(hashlib.sha1(f"в{i}".encode()).hexdigest()[:4], 16) % 62)
        столбики += (f'<span style="flex: 1; height: {высота}px; border-radius: 6px;'
                     f' background: {стиль.ЛАЙМ}; opacity: {.35 + (высота / 160):.2f};"></span>')
    return (f'  <div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 44px 60px 70px;'
            f' background: #16190F; box-shadow: 0 -20px 50px rgba(0,0,0,.5);">'
            f'<div style="display: flex; align-items: center; gap: 34px;">'
            f'<div style="flex: none; width: 132px; height: 132px; border-radius: 50%; background: {стиль.ЛАЙМ};'
            f' display: flex; align-items: center; justify-content: center; font-size: 66px;'
            f' box-shadow: 0 0 0 16px rgba(199,226,75,.16);">🎙</div>'
            f'<div style="flex: 1; display: flex; align-items: center; gap: 7px; height: 96px;">{столбики}</div>'
            f'</div>'
            f'<div style="margin-top: 28px; text-align: center; {Т}; font-size: 34px; color: #9DA291;">{строка}</div>'
            f'  </div>')


def поле(текст: str, курсор: bool = True, сказано: str = "") -> str:
    """Поле ввода: сам промпт, ряд кнопок и стрелка отправки — то, что человек видит перед вставкой.

    Кегль промпта — по его длине: длинный текст иначе вылезал из поля и уходил под клавиатуру.
    """
    кегль = 46 if len(текст) <= 150 else 40 if len(текст) <= 260 else 34
    кнопка = (f'display: flex; align-items: center; gap: 14px; height: 72px; padding: 0 28px; border-radius: 36px;'
              f' background: {СЕРЫЙ}; {Т}; font-size: 34px; color: #C9CCC2;')
    хвостик = f'<span style="color: {стиль.ЛАЙМ};">|</span>' if курсор else ""
    было = ("" if not сказано else
            f'<div style="{Т}; font-size: 36px; line-height: 1.3; color: #7E8278; margin-bottom: 22px;">'
            f'<span style="color: #5E6258;">сказано:</span> {сказано}</div>')
    return f"""  <div style="position: absolute; left: 60px; right: 60px; top: 430px; border-radius: 48px; background: {ПОЛЕ};
       padding: 40px 46px 30px; box-shadow: 0 30px 70px rgba(0,0,0,.45);">
    {было}<div style="{Т}; font-size: {кегль}px; line-height: 1.34; color: {ТЕКСТ};">{текст}{хвостик}</div>
    <div style="display: flex; align-items: center; gap: 18px; margin-top: 40px;">
      <div style="{кнопка} width: 72px; justify-content: center; padding: 0;">+</div>
      <div style="{кнопка}">Поиск</div>
      <div style="{кнопка}">Глубокий разбор</div>
      <div style="margin-left: auto; width: 76px; height: 76px; border-radius: 50%; background: {ТЕКСТ};
           display: flex; align-items: center; justify-content: center; font-size: 42px; color: #0A0B09;">↑</div>
    </div>
  </div>"""


# Вид белой плашки под текстом: «плоско» — как было, остальные добавляют глубину.
ПЛАШКИ = {
    "плоско": "background: #FFFFFF; border-radius: 22px;",
    "тень": ("background: linear-gradient(#FFFFFF, #E9EBE2); border-radius: 26px;"
             " box-shadow: 0 18px 40px rgba(0,0,0,.55), inset 0 2px 0 rgba(255,255,255,.9);"),
    "наклейка": ("background: #FFFFFF; border-radius: 10px; transform: rotate(-1.4deg);"
                 " box-shadow: 10px 12px 0 rgba(174,255,0,.85), 0 24px 46px rgba(0,0,0,.5);"),
    "лайм": ("background: #FFFFFF; border-radius: 26px;"
             " box-shadow: 0 0 0 4px rgba(174,255,0,.9), 0 20px 44px rgba(0,0,0,.5);"),
    # «Эппл»: матовое стекло поверх тёмного экрана — капсула, размытие с усилением цвета,
    # тонкая светлая кромка сверху и две мягкие тени: ближняя даёт форму, дальняя — высоту.
    "эппл": ("background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(238,241,233,.92));"
             " -webkit-backdrop-filter: blur(30px) saturate(180%); backdrop-filter: blur(30px) saturate(180%);"
             " border-radius: 999px;"
             " box-shadow: inset 0 2px 0 rgba(255,255,255,1), inset 0 -2px 6px rgba(0,0,0,.06),"
             " inset 0 0 0 1px rgba(255,255,255,.6), 0 3px 8px rgba(0,0,0,.4), 0 22px 60px rgba(0,0,0,.5);"),
}


def пилюля(текст: str, вид: str = "эппл") -> str:
    return (f'  <div style="position: absolute; left: 90px; right: 90px; top: 320px; text-align: center;">'
            f'<span style="display: inline-block; color: #0A0B09; padding: 16px 36px; {К}; font-size: 44px;'
            f' {ПЛАШКИ[вид]}">{текст}</span></div>')


def кадр(к: dict, доля: float, вид: str = "эппл") -> str:
    низ = диктовка(к["голос"]) if к.get("голос") else клавиатура()
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРУНТ}; color: {ТЕКСТ};">
{статус()}
{шапка()}
{пилюля(к['пилюля'], к.get('плашка', вид))}
{поле(к['промпт'], сказано=к.get('сказано', ''))}
{низ}
  {полоса(доля, над_клавиатурой=True)}
</div>""" + ХВОСТ


def обложка(о: dict, доля: float, вид: str = "эппл") -> str:
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРУНТ}; color: {ТЕКСТ};">
{статус()}
{шапка()}
  <img src="kot.webp" style="position: absolute; left: 330px; top: 300px; width: 420px;">
  <div style="position: absolute; left: 90px; right: 90px; top: 880px; text-align: center;">
    <span style="display: inline-block; color: #0A0B09; {К}; font-size: 64px; line-height: 1.18;
          padding: 24px 36px; {ПЛАШКИ[вид].replace('border-radius: 999px', 'border-radius: 40px')}">{о['заголовок']}</span>
  </div>
  <div style="position: absolute; left: 90px; right: 90px; top: 1090px; text-align: center; {Т}; font-size: 34px; color: #8D9186;">[{о['мелко']}]</div>
  {полоса(доля)}
</div>""" + ХВОСТ


def обложка_число(о: dict, доля: float) -> str:
    """Б — число: гигантская цифра лаймом и строка под ней."""
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРУНТ}; color: {ТЕКСТ};">
{статус()}
{шапка()}
  <div style="position: absolute; left: 70px; right: 70px; top: 330px; text-align: center; {К}; font-size: 400px;
       line-height: .9; color: {стиль.ЛАЙМ};">{о['число']}</div>
  <div style="position: absolute; left: 90px; right: 90px; top: 790px; text-align: center; {К}; font-size: 76px;
       line-height: 1.08;">{о['строка']}</div>
  <div style="position: absolute; left: 90px; right: 90px; top: 990px; text-align: center; {Т}; font-size: 40px;
       color: #8D9186;">{о['под']}</div>
{диктовка(о['голос'])}
  {полоса(доля, над_клавиатурой=True)}
</div>""" + ХВОСТ


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: зачёркнутая клавиатура сверху, голос снизу."""
    строка = ("display: flex; align-items: center; gap: 26px; border-radius: 30px; padding: 30px 34px;"
              f" {Т}; font-size: 44px;")
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {ГРУНТ}; color: {ТЕКСТ};">
{статус()}
{шапка()}
  <div style="position: absolute; left: 80px; right: 80px; top: 330px; {К}; font-size: 84px; line-height: 1.06;">{о['заголовок']}</div>
  <div style="position: absolute; left: 80px; right: 80px; top: 620px; display: flex; flex-direction: column; gap: 26px;">
    <div style="{строка} background: rgba(255,255,255,.06); color: #8D9186; text-decoration: line-through;">⌨️ {о['было']}</div>
    <div style="{строка} background: rgba(199,226,75,.14); color: {ТЕКСТ}; box-shadow: inset 0 0 0 3px rgba(199,226,75,.5);">🎙 {о['стало']}</div>
  </div>
{диктовка(о['голос'])}
  {полоса(доля, над_клавиатурой=True)}
</div>""" + ХВОСТ


def финал(ф: dict, доля: float) -> str:
    """Единственный светлый кадр карусели: восемь тёмных подряд сливаются в сетке профиля."""
    return голова() + f"""<div style="position: relative; width: 1080px; height: 1440px; overflow: hidden; background: {стиль.КРЕМ}; color: #12130E;">
  <div style="position: absolute; left: 90px; top: 150px; display: flex; align-items: center; gap: 24px;">
    <img src="ava.webp" style="width: 88px; height: 88px; border-radius: 50%; object-fit: cover; background: #E3E5DA;">
    <div style="{Т}; line-height: 1.25;">
      <div style="font-weight: 700; font-size: 38px;">4xTube</div>
      <div style="font-size: 32px; color: #6E7269;">@4xtube</div>
    </div>
  </div>
  <!-- Крупное слово чернилами, а не оливой: олива по крему даёт 5,4:1 при нашем пороге 8:1.
       Лайм остаётся акцентом — плашкой под словом. -->
  <div style="position: absolute; left: 90px; top: 420px; {К}; font-size: 120px; line-height: 1.02; color: #12130E;">
    <!-- Подсветка строкой-градиентом, а не отдельным слоем: слой с z-index -1 уходил под фон кадра. -->
    <span style="display: inline-block; background: linear-gradient(transparent 74%, {стиль.ЛАЙМ} 74%, {стиль.ЛАЙМ} 92%, transparent 92%); padding: 0 6px;">{ф['крупно']}</span>
  </div>
  <div style="position: absolute; left: 90px; right: 90px; top: 640px; {Т}; font-size: 48px; line-height: 1.3;">{ф['текст']}</div>
  <div style="position: absolute; left: 90px; right: 90px; top: 800px; {Т}; font-size: 36px; color: #6E7269;">{ф['под']}</div>
  <img src="kot-final.webp" style="position: absolute; right: 60px; bottom: 220px; height: 520px;">
  {полоса(доля, светлый=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    """Аватар (морда кота кружком), кот обложки и финала, логотип — файлами до 70 КБ."""
    файлы = []
    позы = {"ava.webp": (пост["аватар"], 200), "kot.webp": (пост["обложка"]["кот"], 900),
            "kot-final.webp": (пост["финал"]["кот"], 800)}
    for имя, (поза, сторона) in позы.items():
        with Image.open(стиль.ПОЗЫ / f"{поза}.png") as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            if имя == "ava.webp":                       # аватар — квадрат по верхней части кота
                ш, в = и.size
                и = и.crop((0, 0, ш, min(в, ш)))
            и.thumbnail((сторона, сторона), Image.LANCZOS)
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
    пост = json.loads(файл.read_text())
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    всего = len(пост["кадры"]) + 2
    вид = пост.get("плашка", "эппл")
    # ⛔️ Три обложки обязательны (правило владельца): холст без них не выкладывается.
    обложки = {"экран": lambda: обложка(пост["обложка"], 1 / всего, вид),
               "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
               "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
    главная = пост.get("главная", "экран")
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['пилюля']}", кадр(к, н / всего, вид)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"], 1.0)))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
    for имя, _, html in доски:
        (папка / имя).write_text(html)

    раскладка = {"artboards": [{"file": имя, "title": з, "x": i % 5 * 1180, "y": i // 5 * 1600, "w": 1080, "h": 1440}
                               for i, (имя, з, _) in enumerate(доски)], "launch": {"view": "canvas"}}
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{пост['название']}: промпт показан прямо в поле ввода. Двигайте и правьте прямо здесь, "
        "потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    картинки(пост, папка)          # картинки и коты рядом с досками
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
