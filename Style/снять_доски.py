# -*- coding: utf-8 -*-
"""Снимки всех досок холста — рабочих кадров и запасных обложек — для приёмки и для глаз.

    python3 снять_доски.py <холст> [куда] [доска …]

`<холст>` — папка `холсты/<пост>` или её `project/`. Снимки 1620×2160 ложатся в
`<холст>/снимки/` как `NN-<доска>.png`, по раскладке холста строка за строкой.

Выпуск (`выпуск.py`) снимает только Main и кадры, а здесь — все доски, включая
`Oblozhka*`: брак запасной обложки надо поймать до того, как владелец её выберет.
Доска, чья страница не менялась с прошлого снимка, не переснимается: рядом со снимком
лежит `.хэш` страницы (правило экономии конвейера v2 — снимать только изменённое).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402

ТИПЫ = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "svg": "image/svg+xml", "woff2": "font/woff2"}


def проект(папка: Path) -> Path:
    """Папка с досками: холст Design держит их в `project/`, прежние холсты — в корне."""
    папка = Path(папка)
    return папка / "project" if (папка / "project" / "canvas.json").exists() else папка


def доски(папка: Path) -> list[dict]:
    """Доски холста сверху вниз и слева направо: `file`, `title`, `x`, `y`, `номер` с 1."""
    папка = проект(папка)
    индекс = json.loads((папка / "canvas.json").read_text(encoding="utf-8"))
    # Холст Design (с 23.09.2026) — `"boards": {файл: {x, y, …}}`; прежние — `"artboards": [...]`.
    if "boards" in индекс:
        все = [{"file": ф, **д} for ф, д in индекс["boards"].items()]
    else:
        все = индекс["artboards"]
    все = sorted((д for д in все if (папка / д["file"]).exists()), key=lambda д: (д["y"], д["x"]))
    return [{**д, "номер": н} for н, д in enumerate(все, 1)]


def страница(папка: Path, файл: str, скрипт: str = "") -> str:
    """Доска для Chrome с диска: без support.js холста, картинки и шрифты вшиты данными.

    По file:// Chrome картинки и шрифты по относительному имени молча не рисует. Коту
    (`kot-*.webp`) ставится `data-кот`: приёмка судит его по своим правилам — за край
    кадра ему можно, под кнопки TikTok нельзя. Сцена `kot-*.jpg` — фон, не кот.
    """
    папка = проект(папка)
    html = (папка / файл).read_text(encoding="utf-8").replace('<script src="./support.js"></script>', "")
    html = html.replace("<body>", "<body style='margin:0'>", 1)
    html = re.sub(r"""<img\b(?=[^>]*\bsrc=["']kot-[^"']+\.webp["'])""", "<img data-кот", html)
    # Кавычки любые: доски «пар» пишутся из вёрстки, где атрибуты в одинарных кавычках.
    html = re.sub(r"""src=(["'])([^"'/:]+\.(webp|png|jpe?g|svg))\1""", lambda м: 'src="%s"' % стиль.данные(
        папка / м.group(2), ТИПЫ[м.group(3)]), html)
    # Шрифты и фоны в CSS зовутся так же, по имени рядом с доской.
    html = re.sub(r"""url\((["']?)([^"'/:()]+\.(webp|png|jpe?g|svg|woff2))\1\)""", lambda м: "url(%s)" % стиль.данные(
        папка / м.group(2), ТИПЫ[м.group(3)]), html)
    if скрипт:
        html = html.replace("</body>", f"<script>{скрипт}</script></body>", 1)
    return html


def снять(папка: Path, куда: Path | None = None, только=()) -> list[Path]:
    """Снимки досок (все или `только` по имени без `.dc.html`); пути в порядке раскладки."""
    sys.path.insert(0, str(стиль.ПОСТБОТ))
    import браузер
    папка = проект(папка)
    куда = Path(куда) if куда else папка.parent / "снимки"
    куда.mkdir(parents=True, exist_ok=True)
    снимки = []
    for д in доски(папка):
        имя = д["file"].removesuffix(".dc.html")
        if только and имя not in только:
            continue
        html = страница(папка, д["file"])
        путь = куда / f"{д['номер']:02d}-{имя}.png"
        метка = путь.with_suffix(".хэш")
        хэш = hashlib.sha1(html.encode()).hexdigest()
        if not (путь.exists() and метка.exists() and метка.read_text() == хэш):
            if not браузер.снять(html, 1080, 1440, путь):
                raise SystemExit(f"снимок не вышел: {д['file']}")
            метка.write_text(хэш)
        снимки.append(путь)
    if not только:
        # Доски переименовали или убрали — старые снимки не должны попасть в лист.
        for лишний in set(куда.glob("*.png")) - set(снимки):
            лишний.unlink()
            лишний.with_suffix(".хэш").unlink(missing_ok=True)
    return снимки


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    куда = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    for путь in снять(Path(sys.argv[1]), куда, tuple(sys.argv[3:])):
        print(путь)


if __name__ == "__main__":
    main()
