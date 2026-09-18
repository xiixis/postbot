# -*- coding: utf-8 -*-
"""Выпуск карусели с холста согласования — без проверок и просмотров (слово владельца 15.09.2026).

    python3 выпуск.py <стиль>/посты/<пост>.json [сохранённый холст.html]

Сохранённый холст — файл из `Artifact read_file` (`path: index.html`): он кладётся молча.
Без него снимаются рабочие кадры из `<стиль>/холсты/<пост>/`. Итог — JPG 1080×1440 и подпись
на столе, в папке из поля «папка». Печатает одну строку.
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402


def помощник() -> Path:
    найдено = sorted(Path("/private/tmp/claude-501/bundled-skills").glob("*/*/design/seed-canvas.mjs"),
                     key=lambda п: п.stat().st_mtime)
    if not найдено:
        raise SystemExit("нет помощника холста: в сессии Claude Code вызвать /design, он распакуется")
    return найдено[-1]


def снять(папка: Path, куда: Path) -> None:
    """Снимки досок 1620×2160 рисовальщиком постбота, по раскладке холста строка за строкой.

    Раньше снимал `снять-холст.mjs` через playwright-core из ~/4xSoft/html-instagram-carousel;
    17.09.2026 той папки не стало, и выпуск падал. Доска открывается как есть, без support.js
    холста, а картинки вшиваются данными: по file:// Chrome их молча не рисует.
    """
    import base64, re
    sys.path.insert(0, str(стиль.ПОСТБОТ))
    import браузер
    куда.mkdir(parents=True, exist_ok=True)
    доски = [а for а in json.loads((папка / "canvas.json").read_text())["artboards"] if (папка / а["file"]).exists()]
    for н, а in enumerate(sorted(доски, key=lambda а: (а["y"], а["x"])), 1):
        html = (папка / а["file"]).read_text().replace('<script src="./support.js"></script>', "")
        html = html.replace("<body>", "<body style='margin:0'>", 1)
        # Кавычки любые: доски «пар» пишутся из вёрстки, где атрибуты в одинарных кавычках.
        html = re.sub(r"""src=(["'])([^"'/:]+\.(webp|png|jpe?g|svg))\1""", lambda м: 'src="%s"' % стиль.данные(папка / м.group(2), {
            "webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml"}[м.group(3)]), html)
        if not браузер.снять(html, 1080, 1440, куда / f"{н:02d}.png"):
            raise SystemExit(f"снимок не вышел: {а['file']}")


# Хештеги в подписи обязательны всегда (слово владельца 17.09.2026: «Хештеги!!! Они всегда
# должны быть»). Пределы те же, что у придирок бота: `postbot/придирки.ХЕШТЕГОВ`.
ХЕШТЕГОВ = (5, 8)


def хештеги(подпись: str) -> None:
    метки = re.findall(r"#\w+", подпись)
    мало, много = ХЕШТЕГОВ
    if not мало <= len(метки) <= много:
        raise SystemExit(f"в подписи хештегов {len(метки)}, нужно от {мало} до {много} — допиши в поле «подпись»")


def main():
    файл = Path(sys.argv[1]).resolve()
    пост = json.loads(файл.read_text())
    хештеги(пост["подпись"])               # до съёмки: без хештегов пост на стол не уходит
    рабочие = файл.parent.parent / "холсты" / файл.stem
    with tempfile.TemporaryDirectory() as врем:
        if len(sys.argv) > 2:
            кадры_холста = Path(врем) / "холст"
            р = subprocess.run(["node", str(помощник()), "--extract", sys.argv[2], "--to", str(кадры_холста)],
                               capture_output=True, text=True)
            if р.returncode:
                raise SystemExit("холст не распаковался: " + р.stderr.strip()[-300:])
        else:
            кадры_холста = рабочие
        снимки = Path(врем) / "снимки"
        снять(кадры_холста, снимки)
        стол = стиль.СТОЛ / пост["папка"]
        if стол.exists():
            shutil.rmtree(стол)
        стол.mkdir(parents=True)
        for png in sorted(снимки.glob("*.png")):
            with Image.open(png) as и:
                и.convert("RGB").resize((1080, 1440), Image.LANCZOS).save(стол / f"{png.stem}.jpg", quality=92)
        (стол / "подпись.txt").write_text(пост["подпись"])
    print(f"на столе: {стол} — {len(list(стол.glob('*.jpg')))} кадров")


if __name__ == "__main__":
    main()
