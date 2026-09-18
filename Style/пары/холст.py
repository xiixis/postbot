# -*- coding: utf-8 -*-
"""Холст согласования стиля «пары» на claude.ai: python3 холст.py посты/<пост>.json

Слово владельца 17.09.2026: прежде чем кадры уезжают на стол, пост показывается холстом, где
он сам двигает, правит и удаляет блоки. Вёрстка не дублируется: страницы кадров собирает
`фразы.py` (вариация «фразы»), здесь они перекладываются в доски 1080×1440 уменьшением `zoom`
с 1620 — тот же приём, что у `до-после/холст.py`. Шрифты вшиты в доску, картинки (коты, логотип)
уходят отдельными файлами webp до ~70 КБ: так велит редактор холста.
Дальше как у «сервисов»: «готово» → `Artifact read_file index.html` → `../выпуск.py пары/посты/<пост>.json <index.html>`.
"""
import base64
import hashlib
import json
import re
import subprocess
import sys
from io import BytesIO
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ))
sys.path.insert(0, str(ТУТ.parent / "до-после"))
import фразы as ф  # noqa: E402
import рисовать as р  # noqa: E402
from PIL import Image  # noqa: E402

_ДО_ПОСЛЕ = ТУТ.parent / "до-после" / "холст.py"


def _из_до_после():
    """`доска`, `латиницей`, `помощник` — общие с холстом «до-после», без копии кода."""
    import importlib.util
    спека = importlib.util.spec_from_file_location("холст_до_после", _ДО_ПОСЛЕ)
    модуль = importlib.util.module_from_spec(спека)
    sys.modules["холст_до_после"] = модуль
    спека.loader.exec_module(модуль)
    return модуль


def вынести_картинки(html: str, папка: Path, картинки: dict) -> str:
    """Картинки, вшитые данными в `src`, — в файлы webp рядом с досками (редактор холста не
    переносит многомегабайтные страницы: каждое сохранение перезаливает её целиком)."""
    def замена(м):
        сырьё = base64.b64decode(м.group(2))
        имя = "img-" + hashlib.sha1(сырьё).hexdigest()[:10] + ".webp"
        if имя not in картинки:
            with Image.open(BytesIO(сырьё)) as и:
                и = и.convert("RGBA")
                и.thumbnail((720, 720), Image.LANCZOS)
                качество = 84
                while True:
                    и.save(папка / имя, "WEBP", quality=качество, method=6)
                    if (папка / имя).stat().st_size < 70_000 or качество <= 40:
                        break
                    качество -= 8
            картинки[имя] = папка / имя
        return f'src="{имя}"'
    return re.sub(r"src=(['\"])data:image/(?:png|webp|jpeg);base64,([A-Za-z0-9+/=]+)\1", замена, html)


def main():
    дп = _из_до_после()
    файл = Path(sys.argv[1]).resolve()
    П = json.loads(файл.read_text())
    р.П = П
    папка = ТУТ / "холсты" / файл.stem
    папка.mkdir(parents=True, exist_ok=True)
    for старое in папка.glob("*"):
        старое.unlink()

    всего = len(П["шпаргалки"]) + 3
    обложки = {"кот": lambda: ф.обложка_кот(П["обложка"], 1 / всего),
               "маркер": lambda: ф.обложка_маркер(П["обложка_маркер"], 1 / всего),
               "сравнение": lambda: ф.обложка_сравнение(П["обложка_сравнение"], 1 / всего)}
    главная = П.get("главная", "кот")
    запасные = [и for и in ("кот", "маркер", "сравнение") if и != главная]
    доски = [("Main.dc.html", f"01 · Обложка · {главная}", обложки[главная]())]
    for н, к in enumerate(П["шпаргалки"], 2):
        доски.append((f"Kadr{н:02d}.dc.html", f"{н:02d} · {к['тонко']}", ф.шпаргалка(к, н / всего)))
    доски.append((f"Kadr{всего - 1:02d}.dc.html", f"{всего - 1:02d} · Почему", р.почему((всего - 1) / всего)))
    доски.append((f"Kadr{всего:02d}.dc.html", f"{всего:02d} · Финал", ф.финал(П["финал"])))
    for н, и in enumerate(запасные, 2):
        доски.append((f"Oblozhka{н}.dc.html", f"Обложка {н} · {и}", обложки[и]()))

    картинки: dict[str, Path] = {}
    for имя, _, html in доски:
        (папка / имя).write_text(дп.доска(вынести_картинки(html, папка, картинки)))

    раскладка = {"artboards": [], "launch": {"view": "canvas"}}
    кадров = обложек = 0
    for имя, заголовок, _ in доски:
        if имя.startswith("Oblozhka"):
            обложек += 1
            x, y = (обложек - 1) * 1180, 1700
        else:
            x, y = кадров * 1180, 0
            кадров += 1
        раскладка["artboards"].append({"file": имя, "title": заголовок, "x": x, "y": y, "w": 1080, "h": 1440})
    раскладка["annotations"] = [{"id": "brief", "x": 0, "y": -420, "w": 1400, "text":
        f"{П.get('название', 'Пост')}: {кадров} кадров карусели сверху, запасные обложки снизу. "
        "Двигайте, правьте текст и удаляйте блоки прямо здесь, потом Save и напишите «готово»."}]
    (папка / "canvas.json").write_text(json.dumps(раскладка, ensure_ascii=False, indent=1))

    п = дп.помощник()
    страница = папка / f"{дп.латиницей(файл.stem)}.html"
    команда = ["node", str(п), "--template", str(п.parent / "payload.template.html"), "--out", str(страница),
               "--title", П.get("название", файл.stem), "--canvas", str(папка / "canvas.json")]
    for имя, _, _ in доски:
        команда += ["--artboard", str(папка / имя)]
    for к in sorted(картинки.values()):
        команда += ["--image", str(к)]
    вывод = subprocess.run(команда, capture_output=True, text=True)
    проверка = subprocess.run(["node", str(п), "--check", str(страница)], capture_output=True, text=True)
    print((вывод.stderr.strip() + "\n") if вывод.stderr.strip() else "", end="")
    print(проверка.stdout.strip()[:300], проверка.stderr.strip()[:300])
    print("страница холста:", страница, f"{страница.stat().st_size // 1024} КБ")


if __name__ == "__main__":
    main()
