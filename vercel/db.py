# -*- coding: utf-8 -*-
"""База постов. SQLite на ноутбуке, Postgres в Supabase на сервере.

Почему две. SQLite не требует ничего: скачал, запустил, работает. Но живёт он
файлом рядом с кодом, а в контейнере файл исчезает при каждом обновлении, и
вместе с ним расписание, история и настройки. Postgres в Supabase этим не
страдает, зато его надо завести и прописать адрес.

Поэтому выбор по переменной DATABASE_URL: пусто, значит файл; postgres://,
значит Supabase. Запросы написаны так, чтобы работать в обоих, а различия
диалектов собраны в этом файле и больше нигде не всплывают.

Главное, ради чего база вообще нужна, это помнить, о чём уже писали. Без этого
через неделю бот начнёт по третьему разу сочинять «пять бесплатных нейросетей»,
и канал сам себя обесценит.
"""

import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

import config

АДРЕС = os.getenv("DATABASE_URL", "").strip()
ПОСТГРЕС = АДРЕС.startswith(("postgres://", "postgresql://"))

# Отличается ровно одна строка схемы: как выдаются номера постов.
_КЛЮЧ = "SERIAL PRIMARY KEY" if ПОСТГРЕС else "INTEGER PRIMARY KEY AUTOINCREMENT"

СХЕМА = [
    f"""CREATE TABLE IF NOT EXISTS posts (
        id           {_КЛЮЧ},
        rubric       TEXT    NOT NULL,
        title        TEXT    NOT NULL,
        body         TEXT    NOT NULL,
        image_path   TEXT,
        status       TEXT    NOT NULL DEFAULT 'draft',
        created_at   TEXT    NOT NULL,
        published_at TEXT,
        tg_message_id INTEGER,
        shape        TEXT,
        scheduled_at TEXT,
        card         TEXT,
        channel      TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)",
    """CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )""",
]

# Колонки, добавленные после первого выпуска. База у владельца уже живёт,
# ронять её ради новой возможности нельзя.
ДОБАВКИ = [("shape", "TEXT"), ("scheduled_at", "TEXT"),
           ("card", "TEXT"), ("channel", "TEXT"), ("tg_sched_id", "INTEGER"),
           ("views", "INTEGER"), ("reactions", "INTEGER"), ("seen_at", "TEXT"),
           ("images", "TEXT"),
           # Адрес поста на площадке, куда его выложили руками. Через API
           # это не узнать: приложение работает ключом песочницы, а прав на
           # «список моих видео» у него нет вовсе — только публикация.
           ("link", "TEXT")]


class _Связь:
    """Тонкая обёртка: прячет разницу между «?» и «%s» в подстановках.

    Она же держит соединение открытым между запросами и переоткрывает его,
    если пулер успел его закрыть, пока приложение молчало.
    """

    def __init__(self, соединение):
        self._с = соединение
        self.первый = True          # ни один запрос в этом блоке ещё не прошёл

    def мертво(self) -> bool:
        return bool(getattr(self._с, "closed", False))

    def откатить(self) -> None:
        try:
            self._с.rollback()
        except Exception:                                    # noqa: BLE001
            self.close()

    def execute(self, запрос: str, значения=()):
        if ПОСТГРЕС:
            запрос = запрос.replace("?", "%s")
        try:
            итог = self._выполнить(запрос, значения)
        except _разрыв():
            # Пулер закрывает соединение, которое долго молчало. Если в этом
            # блоке мы ещё ничего не сделали, переоткрыть безопасно: терять
            # нечего. Если уже сделали, молча повторять нельзя.
            if not self.первый:
                raise
            try:
                self._с.close()
            except Exception:                                # noqa: BLE001
                pass
            self._с = _открыть()
            итог = self._выполнить(запрос, значения)
        self.первый = False
        return итог

    def _выполнить(self, запрос: str, значения):
        # Без подстановок параметры не передаём вовсе: иначе psycopg
        # разбирает запрос на плейсхолдеры и спотыкается о литеральный
        # процент, например в LIKE 'http%'.
        if ПОСТГРЕС and not значения:
            return self._с.execute(запрос)
        return self._с.execute(запрос, значения)

    def commit(self):
        self._с.commit()

    def close(self):
        self._с.close()


def _открыть():
    if ПОСТГРЕС:
        import psycopg
        from psycopg.rows import dict_row
        # prepare_threshold=None обязателен для пулера Supabase: psycopg сам
        # начинает готовить повторяющиеся запросы, а PgBouncer в режиме
        # транзакций про них не знает и отвечает ошибкой на ровном месте.
        return psycopg.connect(АДРЕС, row_factory=dict_row, connect_timeout=20,
                               prepare_threshold=None)
    config.БАЗА.parent.mkdir(parents=True, exist_ok=True)
    сырое = sqlite3.connect(config.БАЗА)
    сырое.row_factory = sqlite3.Row
    return сырое


def _разрыв() -> tuple:
    """Ошибки, после которых соединение годится только выбросить."""
    if not ПОСТГРЕС:
        return (sqlite3.ProgrammingError,)
    import psycopg
    return (psycopg.OperationalError, psycopg.InterfaceError)


# Соединение живёт, пока живёт нить, и переиспользуется всеми запросами.
# Раньше каждый вызов открывал своё, и один экран приложения стоил восемнадцати
# рукопожатий через океан: база в Ирландии, и на каждое уходило больше секунды.
_СВОЁ = threading.local()


@contextmanager
def соединение():
    conn = getattr(_СВОЁ, "связь", None)
    if conn is None or conn.мертво():
        conn = _Связь(_открыть())
        _СВОЁ.связь = conn
    conn.первый = True
    try:
        yield conn
        conn.commit()
    except Exception:
        # Постгрес после неудачного запроса блокирует всю транзакцию, и без
        # отката следующий вызов получил бы «transaction is aborted» на ровном
        # месте, хотя виноват был прошлый.
        conn.откатить()
        raise


def закрыть() -> None:
    """Отпускает соединение этой нити. Нужно только при остановке."""
    conn = getattr(_СВОЁ, "связь", None)
    if conn is not None:
        conn.close()
        _СВОЁ.связь = None


def _колонки(c) -> set:
    if ПОСТГРЕС:
        ряды = c.execute("SELECT column_name FROM information_schema.columns"
                         " WHERE table_name='posts'").fetchall()
        return {р["column_name"] for р in ряды}
    return {р[1] for р in c.execute("PRAGMA table_info(posts)").fetchall()}


_ПОДГОТОВЛЕНО = False


def подготовить() -> None:
    """Создаёт таблицы и добирает новые колонки. Одного раза на запуск хватает.

    Раньше это делалось на каждый запрос, и на Vercel, где функция живёт от
    вызова к вызову, схема проверялась перед каждым нажатием кнопки. Это
    десяток обращений к базе там, где нужно ноль.
    """
    global _ПОДГОТОВЛЕНО
    if _ПОДГОТОВЛЕНО:
        return
    with соединение() as c:
        for запрос in СХЕМА:
            c.execute(запрос)
        есть = _колонки(c)
        for имя, тип in ДОБАВКИ:
            if имя not in есть:
                c.execute(f"ALTER TABLE posts ADD COLUMN {имя} {тип}")
    _ПОДГОТОВЛЕНО = True


def _сейчас() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def добавить(рубрика: str, заголовок: str, текст: str, картинка: str | None,
             форма: str | None = None, карточка: dict | None = None,
             картинки: list[str] | None = None) -> int:
    """Кладёт черновик. `картинки` это карусель: несколько снимков под один текст.

    Первая из них дублируется в image_path, чтобы всё, что умеет показывать
    одну картинку (список черновиков, предпросмотр, старые экраны), работало
    с каруселью без переделки.
    """
    if картинки:
        картинка = картинка or картинки[0]
    with соединение() as c:
        ряд = c.execute(
            "INSERT INTO posts (rubric, title, body, image_path, status, created_at,"
            " shape, card, images) VALUES (?,?,?,?,'draft',?,?,?,?) RETURNING id",
            (рубрика, заголовок, текст, картинка, _сейчас(), форма,
             json.dumps(карточка, ensure_ascii=False) if карточка else None,
             json.dumps(картинки, ensure_ascii=False) if картинки else None)
        ).fetchone()
        ид = int(ряд["id"] if ПОСТГРЕС else ряд[0])
    _сказать_о_черновике(ид, заголовок, len(картинки or []))
    return ид


# Пока True, о новых черновиках не пишем. Ставится на время работы «рабочего»:
# он о готовом докладывает сам и подробнее, а два сообщения об одном посте
# читаются как сбой.
_МОЛЧА = False


@contextmanager
def тихо():
    """Внутри этого блока о новых черновиках владельцу не пишут."""
    global _МОЛЧА
    было, _МОЛЧА = _МОЛЧА, True
    try:
        yield
    finally:
        _МОЛЧА = было


def _сказать_о_черновике(ид: int, заголовок: str, слайдов: int) -> None:
    """Одна строка владельцу: появился черновик.

    Раньше о готовом посте узнавали только те пути, что идут через «рабочего».
    Конвейер собирает карусели сам, ночью, и они молча ложились в очередь:
    владелец видел их, когда сам туда заглядывал, то есть через день.
    """
    if _МОЛЧА:
        return
    try:
        import config
        import telegram as tg
        if not config.АДМИН:
            return
        хвост = f" · {слайдов} слайдов" if слайдов else ""
        tg.написать(config.АДМИН,
                    f"📝 Новый черновик: {заголовок}{хвост}\n\nЖдёт в очереди.",
                    разметка="")
    except Exception:                                        # noqa: BLE001
        pass          # не написали — черновик от этого не пропал


def правка(ид: int, **поля) -> None:
    """Меняет отдельные поля поста. Пустой вызов ничего не делает."""
    можно = {"title", "body", "image_path", "card", "rubric", "images"}
    поля = {к: з for к, з in поля.items() if к in можно and з is not None}
    if not поля:
        return
    набор = ", ".join(f"{к}=?" for к in поля)
    with соединение() as c:
        c.execute(f"UPDATE posts SET {набор} WHERE id=?", (*поля.values(), ид))


def карточка(ряд) -> dict:
    """Поля карточки поста. Пусто у старых постов, снятых до появления правки."""
    try:
        return json.loads(ряд["card"]) if ряд["card"] else {}
    except (TypeError, ValueError):
        return {}


def картинки(ряд) -> list[str]:
    """Слайды карусели. У обычного поста пусто, и это не ошибка."""
    try:
        зн = ряд["images"] if "images" in ряд.keys() else None
    except (TypeError, AttributeError):
        зн = None
    try:
        return json.loads(зн) if зн else []
    except (TypeError, ValueError):
        return []


def взять(ид: int):
    with соединение() as c:
        return c.execute("SELECT * FROM posts WHERE id=?", (ид,)).fetchone()


def отметить_опубликованным(ид: int, message_id: int, канал: str = "") -> None:
    with соединение() as c:
        c.execute("UPDATE posts SET status='published', published_at=?,"
                  " tg_message_id=?, channel=? WHERE id=?",
                  (_сейчас(), message_id, канал, ид))


def отметить_пропущенным(ид: int) -> None:
    with соединение() as c:
        c.execute("UPDATE posts SET status='skipped' WHERE id=?", (ид,))


def отметить_выложенным(ид: int, ссылка: str = "", канал: str = "") -> None:
    """Владелец выложил пост руками — бот об этом иначе не узнает.

    В TikTok мы не публикуем через API: ключ песочный, и оттуда пост виден
    только владельцу. Значит выкладывает человек, из приложения на телефоне, а
    в базе пост так и остаётся черновиком: он снова попадает в «чего не
    хватает», конвейер добирает лишнее, и в сводке всё враньё.

    `tg_message_id` не трогаем: он про телеграм, а здесь его нет. Отличить
    такую публикацию от нашей можно по нему — он останется пустым.
    """
    with соединение() as c:
        c.execute("UPDATE posts SET status='published', published_at=?,"
                  " link=?, channel=? WHERE id=?",
                  (_сейчас(), (ссылка or "").strip() or None, канал, ид))


def запомнить_ссылку(ид: int, ссылка: str) -> None:
    """Ссылка приходит вторым шагом: сперва отметка, потом адрес.

    Отдельно, потому что торопящийся владелец жмёт «выложил» и уходит, а
    ссылку присылает следующим сообщением — или не присылает вовсе.
    """
    with соединение() as c:
        c.execute("UPDATE posts SET link=? WHERE id=?",
                  ((ссылка or "").strip() or None, ид))


def запланировать(ид: int, когда_utc: str, у_телеграма: int | None = None) -> None:
    """`у_телеграма` это номер поста в отложенных Telegram, если отдали ему."""
    with соединение() as c:
        c.execute("UPDATE posts SET status='scheduled', scheduled_at=?,"
                  " tg_sched_id=? WHERE id=?", (когда_utc, у_телеграма, ид))


def снять_с_плана(ид: int) -> None:
    """Обратно в черновики. Пост остаётся, уходит только время.

    Уже опубликованный пост не трогаем ни при каких обстоятельствах. Иначе
    достаточно одной неудачи на второй площадке, чтобы вышедший в канал пост
    снова стал черновиком и ушёл в канал второй раз.
    """
    with соединение() as c:
        c.execute("UPDATE posts SET status='draft', scheduled_at=NULL,"
                  " tg_sched_id=NULL WHERE id=? AND status<>'published'", (ид,))


def созревшие(сейчас_utc: str) -> list:
    """Что пора публиковать. Проверяется на каждом круге опроса."""
    with соединение() as c:
        # Посты, отданные телеграму, он публикует сам: трогать их нельзя.
        return c.execute(
            "SELECT * FROM posts WHERE status='scheduled' AND scheduled_at<=?"
            " AND tg_sched_id IS NULL ORDER BY scheduled_at", (сейчас_utc,)).fetchall()


def расписание() -> list:
    """Всё, что ещё выйдет. Самое близкое сверху."""
    with соединение() as c:
        return c.execute(
            "SELECT * FROM posts WHERE status='scheduled' ORDER BY scheduled_at"
        ).fetchall()


def черновики() -> list:
    with соединение() as c:
        return c.execute(
            "SELECT * FROM posts WHERE status='draft' ORDER BY id DESC LIMIT 20"
        ).fetchall()


def для_экрана(канал: str | None, черновиков: int = 20,
               истории: int = 15) -> tuple[list, list, list]:
    """План, черновики и история одним обращением к базе.

    Три отдельных запроса стоили трёх походов через океан: база в Ирландии, и
    каждый поход это доли секунды. Смысл один и тот же, время втрое меньше.
    """
    условие = " AND channel=?" if канал else ""
    значения = ([черновиков, канал, истории] if канал else [черновиков, истории])
    with соединение() as c:
        ряды = c.execute(
            "SELECT * FROM (SELECT * FROM posts WHERE status='scheduled') AS п"
            " UNION ALL SELECT * FROM (SELECT * FROM posts WHERE status='draft'"
            "   ORDER BY id DESC LIMIT ?) AS ч"
            f" UNION ALL SELECT * FROM (SELECT * FROM posts WHERE status='published'{условие}"
            "   ORDER BY id DESC LIMIT ?) AS и", значения).fetchall()
    # Порядок внутри веток UNION не обещан, поэтому раскладываем сами.
    план = sorted((р for р in ряды if р["status"] == "scheduled"),
                  key=lambda р: р["scheduled_at"] or "")
    черн = sorted((р for р in ряды if р["status"] == "draft"),
                  key=lambda р: -int(р["id"]))
    ист = sorted((р for р in ряды if р["status"] == "published"),
                 key=lambda р: -int(р["id"]))
    return план, черн, ист


def последние_формы(сколько: int = 3) -> list[str]:
    """Формы прошлых постов. Нужны, чтобы лента не собиралась по одному рецепту."""
    with соединение() as c:
        строки = c.execute(
            "SELECT shape FROM posts WHERE shape IS NOT NULL"
            " AND rubric <> 'стрим' ORDER BY id DESC LIMIT ?", (сколько,)).fetchall()
    return [с["shape"] for с in строки]


def уже_писали(сколько: int = 40) -> list[str]:
    """Заголовки прошлых постов, уходят в промпт как список запретов.

    Берём все четыре состояния, и каждое по своей причине: опубликованное
    повторять незачем, отклонённое забраковали, а запланированное и черновик
    ещё выйдут. Без последних двух бот, набивая расписание на неделю, писал бы
    одну и ту же тему пять раз подряд: она ведь ещё нигде не вышла.
    """
    with соединение() as c:
        строки = c.execute(
            "SELECT title FROM posts WHERE rubric <> 'стрим'"
            " ORDER BY id DESC LIMIT ?", (сколько,)).fetchall()
    return [с["title"] for с in строки]


# Настроек мало, а спрашивают их часто: за один экран приложения набегало
# девять отдельных обращений к базе. Поэтому таблица читается целиком и живёт
# несколько секунд. Срок короткий намеренно: канал и звук переключают с
# телефона, и приложение на маке должно узнать об этом почти сразу.
_НАСТРОЙКИ_СРОК = 5
_настройки: dict | None = None
_настройки_до = 0.0


def _все_настройки() -> dict:
    global _настройки, _настройки_до
    if _настройки is not None and time.time() < _настройки_до:
        return _настройки
    with соединение() as c:
        ряды = c.execute("SELECT key, value FROM settings").fetchall()
    свод = {}
    for р in ряды:
        try:
            свод[р["key"]] = json.loads(р["value"])
        except ValueError:
            pass
    _настройки, _настройки_до = свод, time.time() + _НАСТРОЙКИ_СРОК
    return свод


def забыть_кэш() -> None:
    """Сбрасывает запомненные настройки. Зовётся после любой записи."""
    global _настройки
    _настройки = None


def настройка(ключ: str, по_умолчанию=None):
    свод = _все_настройки()
    return свод[ключ] if ключ in свод else по_умолчанию


def запомнить(ключ: str, значение) -> None:
    """Настройка переживает перезапуск: правки владельца не должны теряться."""
    with соединение() as c:
        c.execute("INSERT INTO settings (key, value) VALUES (?,?)"
                  " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                  (ключ, json.dumps(значение, ensure_ascii=False)))
    забыть_кэш()


def записать_охват(ид: int, просмотры: int, реакции: int) -> None:
    with соединение() as c:
        c.execute("UPDATE posts SET views=?, reactions=?, seen_at=? WHERE id=?",
                  (просмотры, реакции, _сейчас(), ид))


def свежие_публикации(дней: int = 30, канал: str | None = None) -> list:
    """Опубликованное, у чего есть смысл спрашивать охват."""
    from datetime import timedelta
    порог = (datetime.now(timezone.utc) - timedelta(days=дней)).isoformat(timespec="seconds")
    условие = " AND channel=?" if канал else ""
    значения = (порог, канал) if канал else (порог,)
    with соединение() as c:
        return c.execute(
            "SELECT * FROM posts WHERE status='published' AND tg_message_id IS NOT NULL"
            f" AND published_at >= ?{условие} ORDER BY id DESC", значения).fetchall()


def охват_по_рубрикам(канал: str | None = None) -> list:
    """Средние просмотры по рубрикам и формам: что читают, а что листают."""
    условие = " AND channel=?" if канал else ""
    with соединение() as c:
        return c.execute(
            "SELECT rubric, shape, COUNT(*) AS штук, AVG(views) AS среднее"
            f" FROM posts WHERE views IS NOT NULL AND views > 0{условие}"
            " GROUP BY rubric, shape ORDER BY среднее DESC",
            (канал,) if канал else ()).fetchall()


def о_чём_писали(сколько: int = 40) -> list[str]:
    """Прошлые темы по существу, а не по заголовкам.

    Заголовок это упаковка, и по нему повтор не виден: «5 ошибок ИИ-канала» и
    «Почему канал глохнет» с виду разные, а мысль одна. Модель, глядя на
    список заголовков, честно придумывала «новую» тему и приносила ту же.

    Поэтому вместе с заголовком отдаём суть, если она записана. У постов,
    сочинённых до этого правила, её нет — они идут заголовком, как раньше.
    """
    with соединение() as c:
        строки = c.execute(
            "SELECT title, card FROM posts WHERE rubric <> 'стрим'"
            " ORDER BY id DESC LIMIT ?", (сколько,)).fetchall()
    итог = []
    for с in строки:
        суть = ""
        try:
            суть = (json.loads(с["card"] or "{}") or {}).get("суть") or ""
        except (ValueError, TypeError):
            суть = ""
        итог.append(f"{с['title']} — {суть}" if суть.strip() else с["title"])
    return итог


def что_зашло(сколько: int = 6, канал: str | None = None) -> dict:
    """Лучшие и худшие посты по охвату. Для промпта, а не для отчёта.

    Числа мы собираем давно, но до сих пор они только показывались человеку.
    Модель писала сотый пост ровно так же, как первый: заголовок, который
    прочитали втрое чаще остальных, ничему её не учил.

    Отдаём именно заголовки с рубрикой и охватом, а не средние по рубрикам:
    средние говорят, куда идти, а заголовок показывает, как именно. Сравнивать
    есть смысл только внутри одного канала: у тестового и основного разные
    порядки чисел.
    """
    условие = " AND channel=?" if канал else ""
    значения = (канал,) if канал else ()
    with соединение() as c:
        ряды = c.execute(
            "SELECT title, rubric, shape, views, reactions FROM posts"
            " WHERE status='published' AND views IS NOT NULL AND views > 0"
            # Анонсы выходят по расписанию каждую неделю одним и тем же
            # текстом: их числа говорят о дне и часе, а не о том, как написано.
            f" AND rubric <> 'стрим'{условие}"
            " ORDER BY views DESC", значения).fetchall()
    все = [{"заголовок": р["title"], "рубрика": р["rubric"], "форма": р["shape"],
            "просмотры": int(р["views"] or 0), "отклики": int(р["reactions"] or 0)}
           for р in ряды]
    пусто = {"лучшие": [], "худшие": [], "средний": 0}
    # Меньше пяти замеров это ещё не наблюдение: один удачный час публикации
    # даст перекос, который модель примет за правило.
    if len(все) < 5:
        return пусто
    верх, низ = все[0]["просмотры"], все[-1]["просмотры"]
    # И числа должны отличаться. На канале в два десятка читателей разница
    # между двумя просмотрами и тремя это не «вдвое лучше», а один человек,
    # который в тот вечер листал ленту. Учить на таком нельзя.
    if верх < 30 or верх < низ * 2:
        return пусто
    середина = round(sum(п["просмотры"] for п in все) / len(все))
    return {"лучшие": все[:сколько], "худшие": все[-сколько:][::-1],
            "средний": середина}


def сводка(канал: str | None = None) -> dict:
    """Черновики и план общие, а «опубликовано» считается по каналу.

    Пост становится принадлежащим каналу только когда вышел, поэтому
    фильтровать раньше нечего и незачем.
    """
    from datetime import timedelta
    условие = " FILTER (WHERE status='published' AND channel=?)" if канал \
        else " FILTER (WHERE status='published')"
    # Неделя считается тем же запросом, а не вторым: сводку показывает главный
    # экран бота, он перерисовывается на каждое нажатие, а база за океаном.
    порог = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(
        timespec="seconds")
    значения = (канал, порог) if канал else (порог,)
    with соединение() as c:
        ряд = c.execute(
            "SELECT COUNT(*) AS всего,"
            f" COUNT(*){условие} AS опубликовано,"
            " COUNT(*) FILTER (WHERE status='published' AND published_at >= ?)"
            "   AS за_неделю,"
            " COUNT(*) FILTER (WHERE status='draft') AS черновики,"
            " COUNT(*) FILTER (WHERE status='scheduled') AS запланировано"
            " FROM posts", значения).fetchone()
    return {k: (ряд[k] or 0)
            for k in ("всего", "опубликовано", "за_неделю", "черновики",
                      "запланировано")}


def последние(сколько: int = 10, канал: str | None = None) -> list:
    условие = " AND channel=?" if канал else ""
    значения = (канал, сколько) if канал else (сколько,)
    with соединение() as c:
        return c.execute(
            f"SELECT * FROM posts WHERE status='published'{условие}"
            " ORDER BY id DESC LIMIT ?", значения).fetchall()
