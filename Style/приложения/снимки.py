# -*- coding: utf-8 -*-
"""Окна приложения для кадров стиля «приложения»: python3 снимки.py

Кладёт PNG в `../подборка-сайтов/сайты/` — оттуда их берёт `холст.py` по полю `снимок`.
Рисуется окно с полем ввода и панелью диктовки: это пост про голосовой ввод, а снимка чужого
сайта у нас нет и быть не должно — показываем то, что человек увидит у себя на экране.

Ширина 1200 под обрезку кадра: `холст.py` режет снимок по верхней части.
Имена — латиницей: помощник холста кириллицу в именах картинок не принимает.
"""
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent))
import стиль  # noqa: E402
sys.path.insert(0, str(стиль.ПОСТБОТ))
import браузер  # noqa: E402

ЦЕЛЬ = ТУТ.parent / "подборка-сайтов" / "сайты"
# Окно рисуется ровно в пропорции рамки кадра (820×500): иначе `object-fit:cover`
# режет его по бокам и первая буква каждой строки уходит за край.
Ш, В = 1230, 750

КАДРЫ = {
    "wispr-speed": ("Письмо клиенту", "", "Добрый день! Отправляю смету на сентябрь: "
                       "работы по разделу «монтаж» уложились в срок, остальное переносим на октябрь."),
    "wispr-anywhere": ("Почта · Чаты · Заметки · Терминал", "", "Любое окно, где есть курсор: "
                    "текст появляется прямо там, где стоит каретка."),
    "wispr-clean": ("Чат с коллегой", "эээ, ну как бы, давай встретимся завтра", "Давай встретимся завтра."),
    "wispr-fix": ("Заметки", "встретимся в пять… нет, в шесть", "Встретимся в 18:00."),
    "wispr-words": ("Задача в трекере", "", "Согласовать смету с Ириной из «Северстали» "
                    "и выслать её в Notion до пятницы."),
    "wispr-prompt": ("Запрос к ИИ", "ну напиши мне это, ну как бы для поста, покороче",
                     "Сократи текст до 600 знаков, оставь смысл и добавь призыв в конце."),
}

СТРАНИЦА = """<!doctype html><meta charset=utf-8><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{Ш}px;height:{В}px;background:#EFEDE7;
  font-family:-apple-system,"Helvetica Neue",Arial}}
.окно{{position:absolute;inset:28px;border-radius:26px;overflow:hidden;background:#FFFFFF;
  box-shadow:0 18px 50px rgba(30,28,24,.18)}}
.верх{{display:flex;align-items:center;gap:14px;height:84px;padding:0 30px;background:#F7F6F2;
  box-shadow:inset 0 -1px 0 rgba(0,0,0,.08)}}
.точка{{width:18px;height:18px;border-radius:50%}}
.имя{{margin-left:14px;font-size:42px;color:#4A4842;font-weight:600}}
.тело{{padding:44px 44px}}
.сказано{{font-size:50px;line-height:1.35;color:#8C8A82;margin-bottom:26px}}
.сказано b{{color:#B4B1A6;font-weight:600}}
.готово{{font-size:62px;line-height:1.4;color:#1F1E1A}}
.поле{{position:absolute;left:44px;right:44px;bottom:40px;height:150px;border-radius:26px;
  background:#F2F1EC;box-shadow:inset 0 0 0 2px rgba(0,0,0,.06);display:flex;align-items:center;
  gap:26px;padding:0 30px}}
.микро{{flex:none;width:86px;height:86px;border-radius:50%;background:{ЛАЙМ};display:flex;
  align-items:center;justify-content:center;font-size:44px;box-shadow:0 0 0 12px rgba(199,226,75,.20)}}
.волна{{flex:1;display:flex;align-items:center;gap:6px;height:60px}}
.волна span{{flex:1;border-radius:4px;background:#9AA37F}}
</style><body><div class=окно>
<div class=верх><span class=точка style="background:#FF5F57"></span>
<span class=точка style="background:#FEBC2E"></span>
<span class=точка style="background:#28C840"></span><span class=имя>{имя}</span></div>
<div class=тело>{сказано}<div class=готово>{готово}</div></div>
<div class=поле><div class=микро>🎙</div><div class=волна>{волна}</div></div>
</div></body>"""


def страница(имя: str, сказано: str, готово: str) -> str:
    import hashlib
    волна = "".join(
        f'<span style="height:{12 + int(hashlib.sha1(f"{имя}{i}".encode()).hexdigest()[:4], 16) % 46}px"></span>'
        for i in range(38))
    блок = f'<div class=сказано><b>сказано:</b> {сказано}</div>' if сказано else ""
    return СТРАНИЦА.format(Ш=Ш, В=В, ЛАЙМ=стиль.ЛАЙМ, имя=имя, сказано=блок, готово=готово, волна=волна)


def main():
    ЦЕЛЬ.mkdir(parents=True, exist_ok=True)
    for ключ, (имя, сказано, готово) in КАДРЫ.items():
        путь = ЦЕЛЬ / f"{ключ}.png"
        if not браузер.снять(страница(имя, сказано, готово), Ш, В, путь):
            raise SystemExit(f"снимок не вышел: {ключ}")
        print(путь.name, f"{путь.stat().st_size // 1024} КБ", flush=True)


if __name__ == "__main__":
    main()
