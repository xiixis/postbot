# -*- coding: utf-8 -*-
"""Собирает папку для выкладки на Vercel.

Туда попадает только то, что нужно облачной функции: работа с базой, разметка,
публикация и проверка подписи. Всё тяжёлое (агент, Pillow, numpy, браузер)
остаётся на маке, иначе функция не соберётся и будет стоить денег.

    python3 tools_vercel.py
"""

import json
import shutil
from pathlib import Path

import config

КОРЕНЬ = Path(__file__).resolve().parent
ЦЕЛЬ = КОРЕНЬ / "vercel"

# Модули, которые нужны функции. Список закрытый нарочно: любой лишний тянет
# за собой зависимости, а вместе с ними время сборки и размер.
МОДУЛИ = ["access.py", "api.py", "card.py", "channels.py", "config.py", "консоль.py", "content.py",
          "crosspost.py", "db.py", "facts.py", "icons.py", "ideas.py", "jobs.py", "markup.py", "publish.py", "repeats.py",
          "storage.py", "stream.py", "telegram.py", "threads.py", "tiktok.py",
          "times.py", "варианты.py", "x.py", "замер.py", "конвейер.py", "площадки.py",
          "подпись.py", "приёмка.py",
          "уборка.py"]

ТРЕБОВАНИЯ = """\
requests>=2.31
python-dotenv>=1.0
psycopg[binary]>=3.1
# Часовой пояс в функции: без базы zoneinfo время постов уезжает при переводе часов.
tzdata
"""

# Vercel заводит функцию по имени файла, то есть на /api/index. Все наши
# адреса вида /api/state он переписывает туда же и сам путь теряет, поэтому
# передаём его параметром: иначе функция не знает, о чём её просят.
# regions это не украшение. База живёт в Ирландии, и функция, поднятая по
# умолчанию в Вашингтоне, ходила к ней через океан на каждый запрос. Дублин
# стоит рядом с базой, и то же самое приложение открывается заметно быстрее.
# Заголовки безопасности берутся из config, а не пишутся здесь: приложение
# отдают два входа, облако и сам мак, и защита у них обязана быть одна. Что
# именно каждое правило закрывает — рассказано там же, рядом с ними.
# ignoreCommand сравнивает папку с последней успешной выкаткой, а не с
# предыдущим коммитом. Прежнее правило в кабинете смотрело только HEAD^..HEAD:
# 05.10.2026 ушла пачка из 20 коммитов, правка vercel/ была в одном из ранних,
# последний папку не трогал, и Vercel дважды отменил сборку. Нет прежней
# выкатки или её коммита в клоне — команда падает, и сборка идёт.
НАСТРОЙКИ = json.dumps({
    "ignoreCommand": '[ -n "$VERCEL_GIT_PREVIOUS_SHA" ] && '
                     'git diff --quiet "$VERCEL_GIT_PREVIOUS_SHA" HEAD -- .',
    "regions": ["dub1"],
    "rewrites": [
        {"source": "/api/:route*", "destination": "/api/index?route=:route*"},
    ],
    "headers": [
        {"source": "/(.*)",
         "headers": [{"key": имя, "value": значение}
                     for имя, значение in config.ЗАЩИТА.items()]},
    ],
}, ensure_ascii=False, indent=2) + "\n"


def собрать() -> None:
    (ЦЕЛЬ / "public").mkdir(parents=True, exist_ok=True)
    (ЦЕЛЬ / "api").mkdir(parents=True, exist_ok=True)

    for имя in МОДУЛИ:
        shutil.copy2(КОРЕНЬ / имя, ЦЕЛЬ / имя)

    # Всё из webapp уезжает в public как есть. Раньше копировались только
    # страница и логотип, и любой добавленный туда файл, вроде подтверждения
    # владения доменом для TikTok, терялся при первой же пересборке.
    for файл in sorted((КОРЕНЬ / "webapp").iterdir()):
        if файл.is_file() and not файл.name.startswith("_"):
            shutil.copy2(файл, ЦЕЛЬ / "public" / файл.name)

    (ЦЕЛЬ / "requirements.txt").write_text(ТРЕБОВАНИЯ, encoding="utf-8")
    (ЦЕЛЬ / "vercel.json").write_text(НАСТРОЙКИ, encoding="utf-8")
    (ЦЕЛЬ / ".vercelignore").write_text("*.session\n.env\n", encoding="utf-8")

    print(f"собрано в {ЦЕЛЬ}")
    страниц = len(list((ЦЕЛЬ / "public").iterdir()))
    print("модулей:", len(МОДУЛИ), "| файлов на странице:", страниц)


if __name__ == "__main__":
    собрать()
