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

# Высоты кадра одним местом: текст сразу под именем, заметка начинается там, где он кончается.
# Рамка заметки выросла с 720×374: пустоту между именем и текстом отдали ей, чтобы содержимое
# окна читалось с телефона, а не сжималось в серую полоску.
ТЕЛО = 560
# Потолок кегля имени: при 230 короткое «НА ХОДУ» опускалось до 565 и садилось
# на текст. 180 держит низ имени на 516 — те самые 40 px запаса до текста.
ИМЯ_ПРЕДЕЛ = 180
СНИМОК = 740
РАМКА_Ш, РАМКА_В = 820, 500


def голова() -> str:
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n"
            "  <script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
            + стиль.фейсы(("Onest", "onest-800", 800), ("Golos", "golos-400", 400),
                          ("Golos", "golos-700", 700))
            + f"""
    body {{ margin:0 }}
    .кадр {{ position:relative;width:1080px;height:1440px;overflow:hidden;background:{КРЕМ};color:{ЧЕРНИЛА} }}
    .карточка {{ position:absolute;left:{ПОЛЕ}px;top:104px;background:#FFFFFF;border-radius:20px;
        padding:26px;box-shadow:0 14px 40px rgba(18,19,14,.08);display:flex;align-items:center }}
    .карточка img {{ width:112px;height:112px;object-fit:contain;display:block }}
    .номер {{ position:absolute;left:{ПОЛЕ}px;top:280px;{Т};font-weight:700;font-size:44px;
        letter-spacing:.12em;color:{АКЦЕНТ} }}
    .имя {{ position:absolute;left:{ПОЛЕ}px;top:340px;{К};line-height:.98;letter-spacing:-.04em }}
    /* Текст идёт сразу за именем: прежние 610 оставляли между ними пустую полосу в 130 px,
       из-за которой заметка внизу сжималась до нечитаемой (слово владельца 18.09). */
    .тело {{ position:absolute;left:{ПОЛЕ}px;top:{ТЕЛО}px;width:880px;{Т};font-size:44px;line-height:1.3 }}
    .тело p {{ margin:0 }}
    .тело .первая {{ font-weight:700 }}
    /* Снимок уходит за нижний край — приём источника: он добирает чернила без слов.
       Рамка задана обеими сторонами, а картинка вписана по верхнему краю: если задать одну
       ширину, высоту начинают решать пропорции снимка, и кадр рассыпается — обрезанный
       под cookie-плашку снимок 8:3 давал высоту 285 px и уползал в нижние 17% кадра. */
    /* Снимок по центру и на одной высоте во всех кадрах — так владелец поставил его руками
       на кадрах 2 и 3 (верх ≈ 820, ширина 590–720). Рамка и отступ заданы числом, а не краем:
       иначе положение снимка начинает зависеть от пропорций файла и кадры расходятся. */
    .снимок {{ position:absolute;left:50%;transform:translateX(-50%);top:{СНИМОК}px;
        width:{РАМКА_Ш}px;height:{РАМКА_В}px;
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
    return стиль.кот_файлом(к)


def обложка(о: dict, доля: float) -> str:
    """Цвет заголовка берётся из поста: владелец 18.09 перекрасил его на холсте в лайм, и с тех
    пор это не случайная правка одной доски, а свойство обложки."""
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:250px">
    <div style="{К};font-size:{кегль('монтировать', 190)}px;line-height:1.0;letter-spacing:-.04em;
        text-wrap:balance;color:{о.get('цвет_заголовка', СВЕТЛЫЙ)}">{о['заголовок']}</div>
    <div style="{Т};font-size:48px;line-height:1.3;margin-top:44px;max-width:620px;
        color:{СВЕТЛЫЙ};text-wrap:pretty">{о['под']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def плашка(текст: str, кегль_: int, фон: str, цвет: str, обводка: str = "") -> str:
    """Строка заголовка на своей подложке. Подложка облегает строку (`display:inline-block`),
    а не тянется во всю ширину: тогда ступенчатый край сам собой держит ритм, как у наклеек.
    Отступ снизу отрицательный — иначе между строками появляется щель в высоту тени."""
    рамка = f";box-shadow:inset 0 0 0 3px {обводка}" if обводка else ""
    return (f'<span style="display:inline-block;background:{фон};color:{цвет};'
            f'padding:10px 26px 16px;border-radius:22px;font-size:{кегль_}px;line-height:1.0;'
            f'margin-bottom:12px{рамка}">{текст}</span>')


def кегль_плашки(строки: list[str], предел: int = 140) -> int:
    """Кегль, при котором самая длинная строка вместе с полями подложки влезает в кадр.
    52 px — поля плашки слева и справа. 0,64 кегля на знак: у Onest 800 узкие «не печатаю» идут
    по 0,60, а строка с пробелом и широкими буквами («Первый месяц») — по 0,63, и при мерке 0,60
    такая строка переносилась внутри плашки, растягивая её во всю ширину (проверено 18.09)."""
    длинная = max(len(с) for с in строки)
    return min(предел, int((1080 - 2 * ПОЛЕ - 52) / (0.64 * длинная)))


def обложка_плашки(о: dict, доля: float) -> str:
    """А+ — тот же текст, что у «сцены», но каждая строка заголовка лежит на своей подложке,
    а последняя — на лайме. Так главная мысль читается сразу: глаз цепляется за цветной блок
    раньше, чем начинает читать. Подзаголовок — в карточке с лаймовой чертой слева, метка
    сверху — контурная пилюля: три разных «носителя» текста вместо трёх кеглей."""
    строки = о.get("строки") or [о["заголовок"]]
    к = кегль_плашки(строки)
    блоки = "".join(
        плашка(с, к, ЛАЙМ if i == len(строки) - 1 else "rgba(255,255,255,.10)",
               "#141A05" if i == len(строки) - 1 else СВЕТЛЫЙ,
               "" if i == len(строки) - 1 else "rgba(255,255,255,.14)") + "<br>"
        for i, с in enumerate(строки))
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:190px">
    <div style="display:inline-block;{Т};font-weight:700;font-size:30px;letter-spacing:.16em;
        padding:14px 28px;border-radius:999px;box-shadow:inset 0 0 0 3px {ЛАЙМ};color:{ЛАЙМ}">
      🎙 {о['над']}</div>
    <div style="{К};letter-spacing:-.035em;margin-top:44px">{блоки}</div>
    <div style="position:relative;max-width:640px;margin-top:34px;padding:28px 30px 28px 34px;
        border-radius:26px;background:rgba(255,255,255,.06);
        box-shadow:inset 0 0 0 2px rgba(255,255,255,.10)">
      <span style="position:absolute;left:0;top:22px;bottom:22px;width:6px;border-radius:3px;
          background:{ЛАЙМ}"></span>
      <span style="{Т};font-size:42px;line-height:1.28">{о['под']}</span>
    </div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def обложка_окно(о: dict, доля: float) -> str:
    """А++ — тот же текст в «окне приложения»: светлая карточка с шапкой и точками, внутри
    заголовок и строка-кнопка. Приём взят из самих кадров карусели, где герой — окно на экране;
    на обложке он обещает то же, что показано внутри."""
    строки = о.get("строки") or [о["заголовок"]]
    к = min(126, кегль_плашки(строки, 126))
    # Ударная строка цветом — слово владельца 18.09: «Я больше» чёрным, «не печатаю» красным.
    # Цвет живёт в посте: это решение про конкретный заголовок, а не про весь стиль.
    удар = о.get("цвет_ударной")
    заголовок = "<br>".join(
        f'<span style="color:{удар}">{с}</span>' if удар and i == len(строки) - 1 else с
        for i, с in enumerate(строки))
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:200px;border-radius:34px;
      overflow:hidden;background:{КРЕМ};color:{ЧЕРНИЛА};box-shadow:0 30px 80px rgba(0,0,0,.45)">
    <div style="display:flex;align-items:center;gap:14px;padding:26px 30px;
        background:#EFEAE2;box-shadow:inset 0 -2px 0 rgba(18,19,14,.10)">
      <span style="width:18px;height:18px;border-radius:50%;background:#D9D3C8"></span>
      <span style="width:18px;height:18px;border-radius:50%;background:#D9D3C8"></span>
      <span style="width:18px;height:18px;border-radius:50%;background:#D9D3C8"></span>
      <span style="{Т};font-weight:700;font-size:28px;color:#6E6A60;margin-left:12px">{о['над']}</span>
    </div>
    <div style="padding:44px 40px 46px">
      <div style="{К};font-size:{к}px;line-height:1.02;letter-spacing:-.035em">{заголовок}</div>
      <div style="{Т};font-size:40px;line-height:1.28;margin-top:30px;color:#3C3A33">{о['под']}</div>
      <div style="display:inline-flex;align-items:center;gap:18px;margin-top:38px;padding:22px 34px;
          border-radius:999px;background:{АКЦЕНТ};color:{КРЕМ};{Т};font-weight:700;font-size:38px">
        🎙 говорю — оно печатает</div>
    </div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def обложка_число(о: dict, доля: float) -> str:
    """Б — число: гигант лаймом на тёмном, строка под ним."""
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:230px">
    <div style="{К};font-size:360px;line-height:.9;letter-spacing:-.05em;color:{ЛАЙМ}">{о['число']}</div>
    <div style="{К};font-size:84px;line-height:1.04;margin-top:30px">{о['строка']}</div>
    <div style="{Т};font-size:44px;margin-top:26px;color:{СВЕТЛЫЙ};opacity:.75">{о['под']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def обложка_допосле(о: dict, доля: float) -> str:
    """В — до/после: строка старая зачёркнута, новая на лаймовой плашке."""
    строка = "font-size:50px;line-height:1.3;padding:24px 30px;border-radius:26px"
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:250px">
    <div style="{К};font-size:96px;line-height:1.02;letter-spacing:-.03em">{о['заголовок']}</div>
    <div style="{Т};{строка};margin-top:60px;background:rgba(255,255,255,.08);
        color:#B8BAB0;text-decoration:line-through">{о['было']}</div>
    <div style="{Т};{строка};margin-top:26px;background:{ЛАЙМ};color:#1A2006;font-weight:700">{о['стало']}</div>
  </div>
  {кот(о['кот'])}
  {знак_и_полоса(доля, тёмный=True)}
</div>""" + ХВОСТ


def носитель(к: dict) -> str:
    """Имя файла визуала кадра: снимок сайта или нарисованная сцена."""
    return f'{к["снимок"]}-shot.jpg' if к.get("снимок") else f'{латиницей(к["сцена"])}.jpg'


def низ_текста(абзацы: list[str], ширина: int = 880, кегль: int = 44) -> int:
    """Где кончается текст кадра. У Golos знак занимает около половины кегля — отсюда строк.

    Снимок стоит на жёсткой высоте 790: у этого стиля шаблон повторяется кадр в кадр, и
    плавающий снимок прыгает по ленте и залезает под лаймовую полосу (проверено 18.09).
    Поэтому не снимок опускается под текст, а текст обязан влезать — это и сторожит `сервис`.
    """
    # 0,58 кегля на знак — снято с отрисованных кадров: в 880 px влезает 34 знака, не 44.
    в_строке = max(1, int(ширина / (кегль * 0.58)))
    строк = sum(max(1, -(-len(а) // в_строке)) for а in абзацы)
    # Отступа между абзацами нет (`.тело p {{ margin:0 }}`), считаем только строки.
    return ТЕЛО + int(строк * кегль * 1.3)


ПОД_ТЕКСТ = СНИМОК     # низ текстового блока: ровно там начинается заметка


def сервис(номер: int, всего: int, к: dict, доля: float) -> str:
    низ = низ_текста(к["текст"])
    if низ > ПОД_ТЕКСТ:
        лишних = -(-(низ - ПОД_ТЕКСТ) // 57)      # строка текста — 57 px
        raise SystemExit(f"кадр «{к['имя']}»: текст длиннее рамки на {лишних} стр. — сократить "
                         f"(сейчас {sum(len(а) for а in к['текст'])} знаков, влезает около 190)")
    строки = "\n".join(
        f'    <p class="{"первая" if i == 0 and к.get("жирная_первая") else ""}">{с}</p>'
        for i, с in enumerate(к["текст"]))
    return голова() + f"""<div class=кадр>
  {f'<div class=карточка><img src="{к["значок"]}.png"></div>' if к.get("значок") else ""}
  <div class=номер>{к['номер']}</div>
  <div class=имя style="font-size:{кегль(к['имя'], ИМЯ_ПРЕДЕЛ)}px">{к['имя']}</div>
  <div class=тело>
{строки}
  </div>
  <img class=снимок style="object-position:{к.get('положение', 'top center')}" src="{носитель(к)}">
  <div class=счёт>{номер}/{всего}</div>
  {знак_и_полоса(доля)}
</div>""" + ХВОСТ


САМОЛЁТИК = ('<svg viewBox="0 0 24 24" style="width:52px;height:52px;flex:none" fill="currentColor">'
             '<path d="M9.04 15.8 8.7 20.54c.48 0 .69-.21.94-.45l2.25-2.15 4.66 3.41c.86.47 '
             '1.46.22 1.69-.79l3.06-14.34c.27-1.26-.46-1.75-1.29-1.44L2.2 10.29c-1.23.48-1.21 '
             '1.17-.21 1.48l4.77 1.49L17.84 6.5c.52-.33 1-.15.6.18z"/></svg>')


def финал(ф: dict) -> str:
    """Финал — не объявление, а кнопка. Выгода лежит на лаймовой наклейке (её видно раньше,
    чем прочитан текст), переход — в настоящей кнопке со значком Telegram и стрелкой в круге:
    такую форму глаз узнаёт как нажимаемую и тянется к ней. Ниже — строка-подсказка, где
    искать ссылку, чтобы после нажатия человек не искал её по каналу."""
    строки = ф.get("строки") or [ф["крупно"]]
    к = кегль_плашки(строки, 132)
    наклейки = "".join(плашка(с, к, ЛАЙМ, "#141A05") + "<br>" for с in строки)
    return голова() + f"""<div class=кадр style="background:{ТЁМНЫЙ};color:{СВЕТЛЫЙ}">
  <div style="position:absolute;left:{ПОЛЕ}px;right:{ПОЛЕ}px;top:180px">
    <div style="display:inline-block;{Т};font-weight:700;font-size:30px;letter-spacing:.16em;
        padding:14px 28px;border-radius:999px;box-shadow:inset 0 0 0 3px rgba(255,255,255,.22);
        color:#C9CCC0">{ф.get('метка', 'ЧТО ДАЛЬШЕ')}</div>
    <div style="{К};letter-spacing:-.035em;margin-top:38px">{наклейки}</div>
    <div style="{Т};font-weight:700;font-size:42px;line-height:1.26;margin-top:28px;
        max-width:640px">{ф['текст']}</div>
    <div style="display:flex;align-items:center;gap:24px;width:620px;margin-top:44px;
        padding:28px 34px;border-radius:34px;background:{СВЕТЛЫЙ};color:{ТЁМНЫЙ};
        box-shadow:0 22px 50px rgba(0,0,0,.45)">
      <span style="display:flex;align-items:center;justify-content:center;width:78px;height:78px;
          border-radius:24px;background:{ЛАЙМ};color:#141A05">{САМОЛЁТИК}</span>
      <span style="flex:1;{Т};font-weight:700;font-size:40px;line-height:1.1">{ф.get('кнопка', 'Открыть канал')}
        <span style="display:block;font-weight:400;font-size:30px;color:#4A4C43;margin-top:8px">{ф['под']}</span></span>
      <span style="display:flex;align-items:center;justify-content:center;width:72px;height:72px;
          border-radius:50%;background:{ТЁМНЫЙ};color:{ЛАЙМ};font-size:40px;font-weight:700">→</span>
    </div>
  </div>
  {кот(ф['кот'])}
  {знак_и_полоса(1.0, тёмный=True)}
</div>""" + ХВОСТ


def картинки(пост: dict, папка: Path) -> list[Path]:
    файлы_котов = стиль.коты_в_файлы(пост, папка)
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
            # Свои окна нарисованы под рамку целиком, поэтому по умолчанию берём их
            # полностью; у чужого сайта поле «верх» отрезает cookie-плашку и подвал.
            # Если после этого снимок всё ещё выше рамки, режем до её пропорции.
            нужная = min(int(высота * к.get("верх", 1.0)), int(ширина / (РАМКА_Ш / РАМКА_В)))
            и = и.crop((0, 0, ширина, нужная))
            и.thumbnail((1000, 1000), Image.LANCZOS)
            и.save(снимок, quality=76, optimize=True)
        файлы.append(снимок)
    with Image.open(стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((240, 88), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    return файлы + файлы_котов + [папка / "logo.png"]


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
    # ⛔️ Три обложки обязательны: холст без них не выкладывается.
    обложки = {"сцена": lambda: рисовать_обложку(пост["обложка"], 1 / всего),
               "плашки": lambda: обложка_плашки(пост["обложка"], 1 / всего),
               "окно": lambda: обложка_окно(пост["обложка"], 1 / всего),
               "число": lambda: обложка_число(пост["обложка_число"], 1 / всего),
               "до-после": lambda: обложка_допосле(пост["обложка_допосле"], 1 / всего)}
    # Какие три обложки идут в холст. По умолчанию — три разных подхода; когда владелец
    # выбрал один текст и просит вариации на него, список задаётся в посте.
    набор = пост.get("обложки", ["сцена", "число", "до-после"])
    обложки = {и: обложки[и] for и in набор}
    главная = пост.get("главная", набор[0])
    запасные = [и for и in обложки if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(пост["кадры"], 1):
        доски.append((f"Kadr{н + 1:02d}.dc.html", f"{н + 1:02d} · {к['имя']}",
                      сервис(н + 1, всего, к, (н + 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", финал(пост["финал"])))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))
    assert len([д for д in доски if д[0].startswith(("Main", "Oblozhka"))]) == 3, \
        "холст без трёх обложек не выкладывается"
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
    for к in dict.fromkeys(картинки(пост, папка)):   # один значок на шесть кадров — без повторов
        команда += ["--image", str(к)]
    р = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)],
                              capture_output=True, text=True)
    print((р.stderr.strip() + "\n" if р.stderr.strip() else "") + проверка.stdout.strip()[:200])
    print("страница холста:", страница)


if __name__ == "__main__":
    main()
