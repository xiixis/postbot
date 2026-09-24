# -*- coding: utf-8 -*-
"""Холст согласования «до-после» на claude.ai: python3 холст.py посты/<пост>.json

Вёрстка не дублируется: страницы кадров собирает `рисовать.py`, здесь они перекладываются в
доски холста 1080×1440 (`.dc.html`) — уменьшением `zoom` с 1620. Шрифты вшиты в каждую доску,
картинки уходят отдельными файлами webp до ~70 КБ: так велит редактор холста, иначе страница
раздувается при каждом сохранении. Порядок после — как у «сервисов» (`сервисы/ДИЗАЙН.md`).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ))
import рисовать as р  # noqa: E402
from PIL import Image  # noqa: E402

ЛАТ = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s",
                "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


def латиницей(имя: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", "".join(ЛАТ.get(б, б) for б in имя.lower())).strip("-")



def доска(html: str) -> str:
    """Страница кадра → доска холста: стили в helmet, тело в рамку 1080×1440 с zoom 2/3."""
    стиль = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    класс = re.search(r"<body class='([^']*)'>", html).group(1)
    тело = re.search(r"<body class='[^']*'>(.*)</body>", html, re.S).group(1)
    стиль = стиль.replace("html,body{", ".кадр{").replace("body{", ".кадр{")
    return ("<!doctype html>\n<html>\n<head>\n  <meta charset=\"utf-8\">\n  <script src=\"./support.js\"></script>\n"
            f"</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n{стиль}\n    body {{ margin: 0; }}\n  </style>\n</helmet>\n"
            "<div style=\"position: relative; width: 1080px; height: 1440px; overflow: hidden;\">"
            f"<div class=\"кадр {класс}\" style=\"zoom: 0.66667; position: relative; width: 1620px; height: 2160px; "
            f"overflow: hidden;\">{тело}</div></div>\n</x-dc>\n</body>\n</html>\n")


def main():
    файл = Path(sys.argv[1]).resolve()
    р.П = json.loads(файл.read_text())
    р.ТОН = р.ТОНЫ[р.П.get("тон", "референс")]
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    картинки: dict[str, Path] = {}

    def картинка(путь: str, ширина: int = 760) -> str:
        """Вместо данных внутри страницы — файл холста webp, ужатый под показ в доске."""
        исходник = (ТУТ / путь) if not Path(путь).is_absolute() else Path(путь)
        имя = латиницей(исходник.stem) + ".webp"
        if имя not in картинки:
            with Image.open(исходник) as и:
                и = и.convert("RGBA" if исходник.suffix == ".png" and "кот" in str(исходник.parent) else "RGB")
                и.thumbnail((ширина, ширина * 2), Image.LANCZOS)
                качество = 80
                while True:
                    и.save(папка / имя, quality=качество, method=6)
                    if (папка / имя).stat().st_size < 70_000 or качество <= 40:
                        break
                    качество -= 7
            картинки[имя] = папка / имя
        return имя

    def свой_кот(имя: str, высота: int, класс: str = "кот", рядом: str = "", **где) -> str:
        with Image.open(ТУТ / "коты" / f"{имя}.png") as и:
            и = и.convert("RGBA")
            и = и.crop(и.getchannel("A").point(lambda а: 255 if а > 24 else 0).getbbox())
            и.thumbnail((высота, высота), Image.LANCZOS)
            файл_кота = f"kot-{латиницей(имя)}.webp"
            и.save(папка / файл_кота, quality=82, method=6)
            картинки[файл_кота] = папка / файл_кота
        с = ";".join(f"{к}:{в}px" for к, в in где.items())
        return f"<img class='{класс}' style='height:{высота}px;{с}' src='{файл_кота}'>"

    р.картинка = картинка
    р.свой_кот = свой_кот
    with Image.open(р.стиль.ПОСТБОТ / "assets/logo-dark.png") as и:
        и = и.convert("RGBA")
        и.thumbnail((200, 200), Image.LANCZOS)
        и.save(папка / "logo.png", optimize=True)
    лого = р.стиль.ЛОГО

    доски = [("Main.dc.html", "01 · Обложка", р.обложка)]
    for н, п in enumerate(р.П["приёмы"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {п['имя']}", lambda п=п: р.приём(п)))
    н = len(р.П["приёмы"]) + 2
    доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · Финал", р.финал))
    if р.П.get("обложка_цифра"):
        доски.append(("Oblozhka2.dc.html", "Обложка 2 · цифра", р.обложка_цифра))
    if р.П.get("обложка_сцена"):
        доски.append(("Oblozhka3.dc.html", "Обложка 3 · сцена", р.обложка_сцена))
    if р.П.get("обложка_симба"):
        доски.append(("Oblozhka4.dc.html", "Обложка 4 · симба", lambda: р.обложка(р.П["обложка_симба"])))

    for имя, _, собрать in доски:
        html = собрать().replace(лого, "logo.png")
        (папка / имя).write_text(доска(html))

    # Карусель одной строкой, обложки — второй строкой под первым кадром.
    раскладка = {"artboards": [], "launch": {"view": "canvas"}}
    кадров = len(р.П["приёмы"]) + 2
    обложек = 0
    for имя, заголовок, _ in доски:
        if имя.startswith("Oblozhka"):
            обложек += 1
            x, y = (обложек - 1) * 1180, 1700
        else:
            i = len([а for а in раскладка["artboards"] if not а["file"].startswith("Oblozhka")])
            x, y = i * 1180, 0
        раскладка["artboards"].append({"file": имя, "title": заголовок, "x": x, "y": y, "w": 1080, "h": 1440})
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"«{р.П['обложка']['рука']} {' '.join(р.П['обложка']['заголовок'])}» — {кадров} кадров карусели "
        "сверху, варианты обложки снизу. Правьте текст и картинки прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    # Сборка страницы помощником холста (seed-canvas) убрана 24.09.2026: он не распаковывается с
    # 21.09, а холст собирается своими руками (`.claude/ПУБЛИКАЦИЯ.md`, шаг 5).
    print("доски холста:", папка, "— выкладка: ПУБЛИКАЦИЯ.md, шаг 5")


if __name__ == "__main__":
    main()
