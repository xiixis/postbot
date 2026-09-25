# -*- coding: utf-8 -*-
"""Значок сервиса для кадра: python3 значок.py <папка> <имя>=<сайт>[@<запрос App Store>] …

Лестница, от дешёвого к надёжному:
1. favicon 256 от Google — годен, если не меньше 128 px;
2. иконка с самого сайта: svg, apple-touch-icon, крупный favicon, в конце og:image;
3. App Store — только если задан запрос, и только приложение, в названии или у продавца
   которого есть имя сервиса. 24.09.2026 первым по «Lumen5» стоял «Lumen AI» — чужое
   приложение; такое печатается как «проверить», а не сохраняется молча.

Печатает строку на значок: имя, откуда, размер. Сохраняет `<папка>/<имя>.png` (или `.svg`).
Раньше эти три скрипта жили в черновиках сессии и терялись вместе с ней.
"""
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"}
НАИМЕНЬШИЙ = 128


def _взять(адрес: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(адрес, headers=UA), timeout=30).read()


def иконки_сайта(html: str, база: str) -> list[str]:
    """Адреса иконок страницы: svg, потом по убыванию `sizes`, og:image последним."""
    кандидаты = []
    for тег in re.findall(r"<link\b[^>]*>", html, re.I):
        рел = re.search(r'rel=["\']([^"\']+)["\']', тег, re.I)
        адрес = re.search(r'href=["\']([^"\']+)["\']', тег, re.I)
        if not (рел and адрес and "icon" in рел.group(1).lower()):
            continue
        размер = re.search(r'sizes=["\'](\d+)x\d+', тег, re.I)
        svg = адрес.group(1).lower().split("?")[0].endswith(".svg") or "svg" in тег.lower()
        вес = 10_000 if svg else int(размер.group(1)) if размер else (
            180 if "apple" in рел.group(1).lower() else 16)
        кандидаты.append((вес, urllib.parse.urljoin(база, адрес.group(1))))
    адреса = [а for _, а in sorted(кандидаты, key=lambda к: -к[0])]
    og = re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    return адреса + [urllib.parse.urljoin(база, og[0])] if og else адреса


def приложение(результаты: list[dict], имя: str) -> tuple[dict | None, list[str]]:
    """Приложение App Store, в названии или у продавца которого есть имя; и строки кандидатов."""
    строки = [f"{р.get('trackName')} | {р.get('sellerName')}" for р in результаты]
    ключ = re.sub(r"\W", "", имя.lower())
    for р in результаты:
        if ключ in re.sub(r"\W", "", f"{р.get('trackName', '')} {р.get('sellerName', '')}".lower()):
            return р, строки
    return None, строки


def _сохранить_растр(данные: bytes, путь: Path) -> int:
    и = Image.open(io.BytesIO(данные)).convert("RGBA")
    и.save(путь, optimize=True)
    return min(и.size)


def достать(папка: Path, имя: str, сайт: str, запрос: str = "") -> str:
    """Один значок по лестнице; строка отчёта."""
    мелкий = 0                   # лучший из мелких: он остаётся в папке запасным
    try:
        размер = _сохранить_растр(_взять(
            "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL"
            f"&url=https://{сайт}&size=256"), папка / f"{имя}.png")
        if размер >= НАИМЕНЬШИЙ:
            return f"{имя}: favicon {размер} px"
        мелкий = размер
    except Exception:                                          # noqa: BLE001
        pass
    try:
        страница = _взять(f"https://{сайт}").decode("utf-8", "ignore")
        for адрес in иконки_сайта(страница, f"https://{сайт}/"):
            try:
                данные = _взять(адрес)
            except Exception:                                  # noqa: BLE001
                continue
            if адрес.lower().split("?")[0].endswith(".svg"):
                (папка / f"{имя}.svg").write_bytes(данные)
                (папка / f"{имя}.png").unlink(missing_ok=True)
                return f"{имя}: svg с сайта {адрес}"
            try:
                и = Image.open(io.BytesIO(данные))
            except Exception:                                  # noqa: BLE001
                continue
            if min(и.size) >= НАИМЕНЬШИЙ:
                return f"{имя}: с сайта {_сохранить_растр(данные, папка / f'{имя}.png')} px {адрес}"
            if min(и.size) > мелкий:
                мелкий = _сохранить_растр(данные, папка / f"{имя}.png")
    except Exception:                                          # noqa: BLE001
        pass
    запас = f" (в папке мелкий {мелкий} px)" if мелкий else ""
    if запрос:
        о = json.loads(_взять("https://itunes.apple.com/search?entity=software&limit=5&term="
                              + urllib.parse.quote(запрос)))
        выбор, строки = приложение(о.get("results", []), имя)
        if выбор:
            размер = _сохранить_растр(_взять(выбор["artworkUrl512"]), папка / f"{имя}.png")
            return f"{имя}: App Store «{выбор['trackName']}» ({выбор.get('sellerName')}) {размер} px"
        return f"{имя}: ПРОВЕРИТЬ{запас} — в App Store нет приложения с этим именем: " + "; ".join(строки)
    return f"{имя}: НЕТ крупного значка{запас} — дать запрос App Store"


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    папка = Path(sys.argv[1])
    папка.mkdir(parents=True, exist_ok=True)
    for арг in sys.argv[2:]:
        имя, _, остальное = арг.partition("=")
        сайт, _, запрос = остальное.partition("@")
        print(достать(папка, имя, сайт, запрос), flush=True)


if __name__ == "__main__":
    # Windows без PYTHONUTF8: консоль cp1251, print кириллицы и значков падает.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import консоль
    консоль.в_utf8()
    main()
