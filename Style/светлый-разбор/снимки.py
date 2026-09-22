# -*- coding: utf-8 -*-
"""Снимки-доказательства для стиля «светлый разбор»: python3 снимки.py

Кладёт PNG в `снимки/`. Два вида, оба взяты с кадров референса (`_style.json`):

* **окно файла** — три кружка, имя файла, моноширинный текст на белом; снизу текст обрезан
  краем окна, видно, что файл длиннее;
* **список файлов** — окно проводника со столбцами «Имя · Дата изменения · Размер · Тип».

Содержимое настоящее: файлы и папки постбота. Пост учит приёму RULES/INDEX/MAP, и показывать
в нём выдуманный проект нечестно.
"""
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
sys.path.insert(0, str(стиль.ПОСТБОТ))
import браузер  # noqa: E402

ЦЕЛЬ = ТУТ / "снимки"
Ш, В = 1380, 930             # 920×620 × 1,5: доска снимается в полуторном масштабе, и окно попадает один в один

ОКНА = {
    "rules": ("RULES.md", [
        "# Правила работы в проекте «постбот»",
        "",
        "Этот файл помощник читает первым и перечитывает в начале",
        "каждого разговора. Поэтому он короткий.",
        "",
        "## Порядок работы — обязателен",
        "",
        "1. Начинай с `INDEX.md`. Это каталог: какой вопрос — какой файл.",
        "2. Не нашёл в каталоге — открой `MAP.md`: там, где что лежит.",
        "3. Проект целиком не обходи. Не открывай папки подряд",
        "   «на всякий случай».",
        "",
        "## Как здесь принято работать",
        "",
        "— Прежде чем менять файлы — покажи план и дождись ответа.",
        "— «Готово» говори только после проверки. Назови, что проверил.",
        "— Не выдумывай факты, пути и ссылки. Не знаешь — говори «не знаю».",
        "— Кадры смотри листом, а не по одному.",
    ]),
    "index": ("INDEX.md", [
        "# INDEX — каталог проекта «постбот»",
        "",
        "Правила проекта — в `RULES.md`. Чтение начинать отсюда.",
        "",
        "## Куда смотреть",
        "",
        "| Вопрос | Файл |",
        "|---|---|",
        "| Как рисуется кадр карусели | card.py |",
        "| Откуда берётся план постов | конвейер.py |",
        "| Почему кадр забраковали | приёмка.py |",
        "| Где лежат посты и темы | db.py |",
        "",
        "## Кто за что отвечает",
        "",
        "| Роль | Что делает | Где описана |",
        "|---|---|---|",
        "| Рисовальщик | кадры и обложки | card.py |",
        "| Конвейер | план на неделю | конвейер.py |",
    ]),
    "map": ("MAP.md", [
        "# MAP — карта проекта «постбот»",
        "",
        "## Где что лежит",
        "",
        "postbot/            бот, рисовальщик, база",
        "├── webapp/         мини-приложение владельца",
        "├── assets/         шрифты, кот, логотип",
        "├── Style/          ДНК стилей из референсов",
        "├── docs/           спеки и планы",
        "└── tests/          525 тестов",
        "",
        "postbot/Style/",
        "├── Style/          стили каруселей и их холсты",
        "└── референсы/      чужие посты, по которым сняты стили",
        "",
        "## Чего здесь нет",
        "",
        "— Секретов и ключей: они в `.env`, в git не попадают.",
    ]),
}

ПАПКИ = [("01_Роли", "14 августа 2026 г. в 15:24", "--", "Папка"),
         ("02_Протоколы", "14 августа 2026 г. в 01:02", "--", "Папка"),
         ("03_Архитектура", "14 августа 2026 г. в 02:02", "--", "Папка"),
         ("04_Источники", "14 августа 2026 г. в 15:24", "--", "Папка"),
         ("05_Runtime", "14 августа 2026 г. в 15:26", "--", "Папка"),
         ("06_Рабочее_пространство", "16 августа 2026 г. в 15:29", "--", "Папка"),
         ("RULES.md", "Вчера в 15:38", "3 КБ", "Файл с…arkdown"),
         ("INDEX.md", "Вчера в 15:39", "28 КБ", "Файл с…arkdown"),
         ("MAP.md", "Вчера в 15:16", "3 КБ", "Файл с…arkdown"),
         ("CLAUDE.md", "6 августа 2026 г. в 08:05", "236 Б", "Файл с…arkdown"),
         ("AGENTS.md", "Вчера в 15:38", "11 КБ", "Файл с…arkdown"),
         ("GEMINI.md", "6 августа 2026 г. в 08:05", "236 Б", "Файл с…arkdown")]

ОБЩЕЕ = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%dpx;height:%dpx;background:#F2F1EF;font-family:-apple-system,"Helvetica Neue",Arial}
.окно{position:absolute;inset:0;border-radius:24px;overflow:hidden;background:#FFFFFF;
  box-shadow:0 12px 34px rgba(0,0,0,.14)}
.шапка{display:flex;align-items:center;gap:18px;height:93px;padding:0 36px;background:#F7F7F5;
  box-shadow:inset 0 -1px 0 rgba(0,0,0,.08)}
.точка{width:24px;height:24px;border-radius:50%%}
.имя{margin-left:18px;font-size:36px;color:#4A4A48;font-weight:600}
""" % (Ш, В)

ФАЙЛ = ОБЩЕЕ + """
.код{padding:30px 39px;font-family:"SF Mono",Menlo,monospace;font-size:33px;line-height:1.45;color:#15150F;
  white-space:pre-wrap}
"""

СПИСОК = ОБЩЕЕ + """
.строка{display:flex;align-items:center;height:78px;padding:0 36px;font-size:34px;color:#15150F}
.строка:nth-child(even){background:#F6F6F4}
.шапка-таблицы{font-size:30px;color:#66665F;font-weight:600;height:69px}
.имя-ф{flex:1;min-width:0;display:flex;align-items:center;gap:14px;white-space:nowrap}
.дата{width:420px;color:#3A3A38}.размер{width:110px;text-align:right;color:#3A3A38}
.тип{width:250px;text-align:right;color:#3A3A38}
.значок{width:39px;height:33px;border-radius:4px;background:#39C46B}
.значок.файл{background:#DCDCD8}
"""


def окно_файла(имя: str, строки: list[str]) -> str:
    текст = "\n".join(строки)
    return (f"<!doctype html><meta charset=utf-8><style>{ФАЙЛ}</style><body><div class=окно>"
            f"<div class=шапка><span class=точка style='background:#FF5F57'></span>"
            f"<span class=точка style='background:#FEBC2E'></span>"
            f"<span class=точка style='background:#28C840'></span><span class=имя>{имя}</span></div>"
            f"<div class=код>{текст}</div></div></body>")


def окно_списка() -> str:
    ряды = ("<div class='строка шапка-таблицы'><div class=имя-ф style='padding-left:40px'>Имя</div>"
            "<div class=дата>Дата изменения</div><div class=размер>Размер</div><div class=тип>Тип</div></div>")
    for имя, дата, размер, тип in ПАПКИ:
        папка = "" if имя.endswith(".md") else ""
        ряды += (f"<div class=строка><div class=имя-ф><span class='значок{' файл' if имя.endswith('.md') else папка}'></span>{имя}</div>"
                 f"<div class=дата>{дата}</div><div class=размер>{размер}</div><div class=тип>{тип}</div></div>")
    return (f"<!doctype html><meta charset=utf-8><style>{СПИСОК}</style><body><div class=окно>"
            f"<div class=шапка><span class=точка style='background:#FF5F57'></span>"
            f"<span class=точка style='background:#FEBC2E'></span>"
            f"<span class=точка style='background:#28C840'></span><span class=имя>постбот</span></div>"
            f"{ряды}</div></body>")


def main():
    ЦЕЛЬ.mkdir(exist_ok=True)
    задачи = [(f"{ключ}.png", окно_файла(имя, строки)) for ключ, (имя, строки) in ОКНА.items()]
    задачи.append(("papki.png", окно_списка()))   # только латиница: помощник холста кириллицу в именах не берёт
    for имя, html in задачи:
        путь = ЦЕЛЬ / имя
        if not браузер.снять(html, Ш, В, путь):
            raise SystemExit(f"снимок не вышел: {имя}")
        print(путь, f"{путь.stat().st_size // 1024} КБ", flush=True)


if __name__ == "__main__":
    main()
