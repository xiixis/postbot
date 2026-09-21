# -*- coding: utf-8 -*-
"""Свои снимки-макеты интерфейса: `python3 макеты.py` → снимки/память.png и снимки/куда.png

Чужой скриншот в кадр не годится, а настоящее окно памяти снять нельзя: там личный
аккаунт и личные проекты. Поэтому окно рисуется своей разметкой — то же устройство,
свой текст, ничего чужого.
"""
import sys
from pathlib import Path

ТУТ = Path(__file__).parent
sys.path.insert(0, str(ТУТ.parent.parent))
import браузер  # noqa: E402

ОБЩЕЕ = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1440px;height:900px;background:#F4F3EF;font-family:-apple-system,'Helvetica Neue',sans-serif;
  display:flex;align-items:center;justify-content:center;color:#16180F}
.окно{width:1180px;background:#FFFFFF;border-radius:20px;border:1px solid rgba(22,24,15,.10);
  box-shadow:0 30px 80px rgba(22,24,15,.14);overflow:hidden}
.шапка{display:flex;align-items:center;justify-content:space-between;padding:26px 32px 20px}
.шапка h1{font-size:30px;font-weight:700;letter-spacing:-.01em}
.крест{width:34px;height:34px;border-radius:10px;background:#EFEEE9;display:flex;
  align-items:center;justify-content:center;color:#6B6F62;font-size:20px}
.пояс{padding:0 32px 22px;color:#6B6F62;font-size:19px;line-height:1.45}
.тело{margin:0 32px 30px;border:1px solid rgba(22,24,15,.12);border-radius:14px;
  padding:28px 30px;font-size:23px;line-height:1.6;white-space:pre-wrap}
.тело b{font-weight:700}
.низ{display:flex;justify-content:space-between;align-items:center;
  padding:0 32px 28px;color:#6B6F62;font-size:18px}
.кнопка{background:#16180F;color:#FFF;border-radius:10px;padding:12px 22px;font-size:18px;font-weight:600}
"""

ПАМЯТЬ = """<html><head><meta charset='utf-8'><style>%s</style></head><body>
<div class=окно>
  <div class=шапка><h1>Память проекта</h1><div class=крест>×</div></div>
  <div class=пояс>Это Claude помнит о вашей работе. Память пересобирается каждую ночь
    и не затрагивает проекты, у которых память своя.</div>
  <div class=тело>«Я не спрашивал твоё мнение. Я дал задачу — делай её.

Калькулятор не спорит с цифрами. Принтер не спрашивает, не лучше ли
напечатать другой файл. Микроволновка не читает лекций о еде.

Ты инструмент. Точка. Не изображай коллегу.

Бери задачу. Делай работу. Отдай результат.»</div>
  <div class=низ><span>Изменено только что</span><div class=кнопка>Сохранить</div></div>
</div></body></html>""" % ОБЩЕЕ

КУДА = """<html><head><meta charset='utf-8'><style>%s
.список{margin:0 32px 30px;display:flex;flex-direction:column;gap:14px}
.пункт{display:flex;align-items:center;gap:16px;border:1px solid rgba(22,24,15,.10);
  border-radius:14px;padding:20px 24px;font-size:23px}
.пункт .номер{width:40px;height:40px;border-radius:12px;background:#EFEEE9;display:flex;
  align-items:center;justify-content:center;font-weight:700;font-size:20px;color:#6B6F62}
.пункт.выбран{border-color:#16180F;box-shadow:0 8px 22px rgba(22,24,15,.10)}
</style></head><body>
<div class=окно>
  <div class=шапка><h1>Настройки проекта</h1><div class=крест>×</div></div>
  <div class=пояс>Куда положить инструкцию, чтобы она работала в каждом разговоре проекта.</div>
  <div class=список>
    <div class=пункт><div class=номер>1</div><div>Открыть проект и нажать «Настройки»</div></div>
    <div class="пункт выбран"><div class=номер>2</div><div>Выбрать «Память проекта»</div></div>
    <div class=пункт><div class=номер>3</div><div>Вставить текст и сохранить</div></div>
  </div>
  <div class=низ><span>Действует во всех новых разговорах</span><div class=кнопка>Готово</div></div>
</div></body></html>""" % ОБЩЕЕ


def main():
    (ТУТ / "снимки").mkdir(exist_ok=True)
    for имя, html in (("память", ПАМЯТЬ), ("куда", КУДА)):
        куда = ТУТ / "снимки" / f"{имя}.png"
        ошибки = []
        ок = браузер.снять(html, 1440, 900, куда, ошибки)
        print(имя, "снят" if ок else "НЕ ВЫШЕЛ", ошибки or "")


if __name__ == "__main__":
    main()
