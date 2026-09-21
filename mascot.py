# -*- coding: utf-8 -*-
"""Рисует кота в новой позе под каждый пост.

Поза каждый раз своя, а кот — один и тот же: в модель уходит лист ракурсов
(assets/mascot/reference.png) как эталон персонажа. Без него получится
похожий кот, но другой, и канал развалится на десяток разных котов.

Фон нарочно синий, а не тёмный: кот сам почти чёрный, и вырезать его с
тёмного — значит съедать ему бока. Зелёный тоже не годится — у кота лаймовые
глаза и полосы, они бы ушли вместе с фоном.
"""

import base64
import os
import re
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageFilter

import config

API = "https://generativelanguage.googleapis.com/v1beta/models/{модель}:generateContent"
КЛЮЧ_ФОН = np.array([0, 71, 255], dtype=np.float32)      # #0047FF

ЭТАЛОН = """\
Generate the EXACT SAME character shown in the reference sheet — identical soft
matte clay-like material, identical rounded chunky proportions, identical big
glowing acid-lime (#C7E24B) eyes with a white catch-light, identical charcoal
near-black (#1B1E17) body, identical lime panel lines and glowing tail tip, NO
antenna on the head. The reference is the character bible: the copy must be as
accurate as possible.

CRITICAL BACKGROUND RULE: place the character on a PURE FLAT CHROMA-KEY BLUE
background, exact colour #0047FF, filling the entire frame edge to edge.
Absolutely uniform blue — no gradient, no vignette, no shadow on the background,
no floor, no reflection, no glow spilling onto the blue. The character must NOT
contain any blue anywhere.

Single character, full body, fully inside the frame with margin around it, soft
even lighting.

STRICTLY NO WRITING ANYWHERE IN THE IMAGE. No text, no letters, no numbers, no
watermark, no signage, no screens with interface, no labels, no charts with
axis names, no speech bubbles containing characters. If the pose mentions
pointing at something or explaining, the character points at EMPTY SPACE:
whatever it points at lives outside the frame. Even a few blurred letters ruin
the card, because the card already carries its own text.

POSE: """


def _канал() -> tuple[str, dict]:
    """Куда стучаться за картинкой: сперва Vertex, и только потом ключ AI Studio.

    Предоплата AI Studio у проекта кончилась («prepayment credits are depleted»),
    и все позы молча переставали рисоваться: `поза()` ловит исключение и отдаёт
    None, а карусель просто уходила с заготовкой из комплекта. Бесплатные кредиты
    Google Cloud списываются только через Vertex — тот же путь, которым уже ходит
    `Style/картинка.py`.
    """
    if os.getenv("КОТ_БЕЗ_VERTEX", "") == "":
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent / "Style"))
            import вертекс
            return вертекс.адрес(config.МОДЕЛЬ_КАРТИНОК), вертекс.заголовки()
        except Exception as п:                               # noqa: BLE001
            print(f"кот: Vertex недоступен ({п}), иду по ключу AI Studio")
    return (API.format(модель=config.МОДЕЛЬ_КАРТИНОК),
            {"x-goog-api-key": config.КЛЮЧ_GEMINI, "Content-Type": "application/json"})


def _запросить(описание: str) -> bytes:
    эталон = config.МАСКОТ / "reference.png"
    части = [{"text": ЭТАЛОН + описание}]
    if эталон.exists():
        части.append({"inlineData": {
            "mimeType": "image/png",
            "data": base64.b64encode(эталон.read_bytes()).decode()}})

    тело = {"contents": [{"role": "user", "parts": части}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": "1:1"}}}
    адрес, заголовки = _канал()
    r = requests.post(адрес, headers=заголовки, json=тело, timeout=180)
    r.raise_for_status()
    for ч in r.json()["candidates"][0]["content"]["parts"]:
        д = ч.get("inlineData") or ч.get("inline_data")
        if д and д.get("data"):
            return base64.b64decode(д["data"])
    raise RuntimeError("модель не вернула картинку")


def _снять_фон(сырое: Path) -> Path:
    """Хромакей. Три шага, и каждый нужен.

    Порог по расстоянию до ключа убирает основной фон. Отсечение по «синий выше
    красного и зелёного» добивает ореол на границе — у персонажа синего нет, так
    что режем смело. Сжатие маски на пиксель снимает кайму, которая иначе видна
    тонкой синей полоской по контуру.
    """
    im = Image.open(сырое).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

    альфа = np.clip((np.linalg.norm(a - КЛЮЧ_ФОН, axis=2) - 95) / 45, 0, 1)
    альфа[(b - np.maximum(r, g)) > 28] = 0

    маска = (Image.fromarray((альфа * 255).astype(np.uint8))
             .filter(ImageFilter.MinFilter(5))
             .filter(ImageFilter.GaussianBlur(0.7)))

    # деспилл: синий не может быть ярче максимума из двух других каналов
    цвет = np.dstack([r, g, np.minimum(b, np.maximum(r, g))])
    слой = Image.fromarray(np.clip(цвет, 0, 255).astype(np.uint8))
    слой.putalpha(маска)
    слой = слой.crop(слой.getbbox())

    готово = сырое.with_name(сырое.stem + "_cut.png")
    слой.save(готово)
    сырое.unlink(missing_ok=True)
    return готово


def _фон_чистый(сырое: Path) -> bool:
    """Углы должны быть тем самым синим.

    Модель иногда игнорирует требование фона и рисует кота на своей подложке.
    Хромакей такую подложку не снимает: остаётся мутный прямоугольник вокруг
    кота, и карточка выглядит браком. Дешевле проверить четыре угла и
    перерисовать, чем отдавать это в канал.
    """
    a = np.asarray(Image.open(сырое).convert("RGB")).astype(np.float32)
    углы = [a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]]
    return all(float(np.linalg.norm(у - КЛЮЧ_ФОН)) < 70 for у in углы)


def поза(описание: str, попыток: int = 3) -> Path | None:
    """Новая поза под конкретный пост. None, если не вышло."""
    if not config.КЛЮЧ_GEMINI:
        return None
    config.ВЫВОД.mkdir(parents=True, exist_ok=True)
    for попытка in range(попыток):
        сырое = config.ВЫВОД / f"pose_{int(time.time())}_{попытка}.png"
        try:
            сырое.write_bytes(_запросить(описание))
            if not _фон_чистый(сырое):
                сырое.unlink(missing_ok=True)
                continue
            return _снять_фон(сырое)
        except Exception:                                    # noqa: BLE001
            сырое.unlink(missing_ok=True)
    return None


def пополнить(описание: str, ключ: str = "") -> Path | None:
    """Рисует новую позу и кладёт её в библиотеку насовсем.

    До сих пор библиотека была закрытой: тридцать одна поза, и карусели
    брали только их. Свежая поза жила один пост и стиралась вместе с
    временной папкой — то есть деньги за генерацию тратились на один слайд.
    Складывая её на полку, мы платим один раз, а пользуемся всегда.

    В библиотеку идёт только целая поза: обрезанный край на слайде выглядит
    сломанным, сколько его ни двигай, и такую лучше выбросить сразу.
    """
    свежая = поза(описание)
    if not свежая or not целая(свежая):
        return None
    СКЛАД.mkdir(parents=True, exist_ok=True)
    имя = re.sub(r"[^a-z0-9]+", "_", (ключ or "sam").lower()).strip("_") or "sam"
    цель = СКЛАД / f"{имя}_{int(time.time())}.png"
    shutil.copyfile(свежая, цель)
    return цель


ЗАПАС = {"privet": "b1_privet_cut.png", "ukazyvaet": "b2_ukazyvaet_cut.png",
         "dumaet": "b3_dumaet_cut.png", "moneta": "b4_moneta_cut.png"}

# Библиотека готовых поз. Рисовать кота заново под каждый пост это деньги,
# минута ожидания и риск, что он выйдет непохожим на себя. Библиотека решает
# всё сразу: берём подходящую по смыслу и ставим мгновенно.
СКЛАД = config.АССЕТЫ / "mascot" / "позы"


def целая(путь, порог: float = 0.25) -> bool:
    """Не обрезан ли персонаж рамкой самой картинки.

    Фон снимается по силуэту, поэтому силуэт касается краёв у всех поз, и
    проверять касание бесполезно. Обрезанный бюст выдаёт другое: у него нижний
    край заполнен сплошной прямой линией. У стоящего кота внизу только лапы,
    это единицы процентов, у обрезанного портрета семьдесят.
    """
    try:
        from PIL import Image
        i = Image.open(путь).convert("RGBA")
    except Exception:                                        # noqa: BLE001
        return True
    ш, в = i.size
    a = i.getchannel("A")
    края = ((0, в - 2, ш, в), (0, 0, ш, 2), (0, 0, 2, в), (ш - 2, 0, ш, в))
    for край in края:
        кусок = a.crop(край)
        всего = max(1, кусок.width * кусок.height)
        доля = sum(1 for з in кусок.get_flattened_data() if з > 20) / всего
        if доля > порог:
            return False
    return True


БРАК = "плохие_позы"


def бракованные() -> set:
    """Позы, которые владелец отверг вручную.

    Автоматика ловит обрезанных котов, но не пятилапых: с точки зрения
    пикселей такая картинка безупречна. Решает это глаз, и его решение
    должно оставаться навсегда — иначе та же поза вернётся через слайд.
    """
    import db
    return set(db.настройка(БРАК, []) or [])


def забраковать(ключ: str) -> set:
    """Больше эту позу не берём."""
    import db
    if not ключ:
        return бракованные()
    плохие = бракованные() | {ключ}
    db.запомнить(БРАК, sorted(плохие))
    return плохие


def библиотека(только_целые: bool = True) -> dict:
    """{ключ: путь} по тому, что реально лежит на диске.

    По умолчанию отдаёт только те позы, которые не обрезаны краем картинки:
    остальные на слайде выглядят сломанными, сколько их ни двигай.
    """
    if not СКЛАД.exists():
        return {}
    всё = {п.stem: п for п in sorted(СКЛАД.glob("*.png"))}
    плохие = бракованные()
    if плохие:
        всё = {к: п for к, п in всё.items() if к not in плохие} or всё
    if not только_целые:
        return всё
    return {к: п for к, п in всё.items() if целая(п)} or всё


def взять(ключ: str = "") -> Path | None:
    """Поза из библиотеки. Незнакомый ключ отдаёт приветствие, а не пустоту."""
    склад = библиотека()
    if ключ in склад:
        return склад[ключ]
    if "privet" in склад:
        return склад["privet"]
    return запасная("privet")


def запасная(ключ: str = "privet") -> Path | None:
    """Готовая поза из комплекта — на случай, если генерация не удалась.

    Пост без кота лучше, чем пост без поста: если сеть моргнула, берём
    заготовку и идём дальше.
    """
    ф = config.МАСКОТ / ЗАПАС.get(ключ, ЗАПАС["privet"])
    return ф if ф.exists() else None
