# -*- coding: utf-8 -*-
"""Ширины знаков наших шрифтов, снятые в Chrome: python3 ширины_знаков.py → ширины_знаков.json

Оценка строк по средней ширине буквы врала в обе стороны: «Вставляешь текст —» в Onest 96 px
лезла в 940 при оценке «не лезет», а «за ИИ — $0» не лезла в 500 при оценке «лезет» (24.09.2026).
Здесь ширина каждого знака в долях кегля, измеренная `measureText` тем же Chrome, что снимает
доски, на тех же файлах шрифтов. Кернинг не учитывается — ошибка в доли процента.

Перегенерировать, когда меняются шрифты в `assets/fonts` или добавляется гарнитура.
"""
import json
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent
sys.path.insert(0, str(ТУТ))
import стиль  # noqa: E402

ГАРНИТУРЫ = [("Onest", "onest-800", 800), ("Golos", "golos-400", 400), ("Golos", "golos-700", 700),
             ("Oswald", "oswald-600", 600), ("JetBrains", "jetbrains-400", 400),
             ("JetBrains", "jetbrains-700", 700)]
ЗНАКИ = ("абвгдеёжзийклмнопрстуфхцчшщъыьэюя" "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
         "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "0123456789"
         " .,:;!?-–—«»\"'()/$%+=&@#№→←↓*·…")
ФАЙЛ = ТУТ / "ширины_знаков.json"


def снять() -> dict:
    sys.path.insert(0, str(стиль.ПОСТБОТ))
    import браузер
    css = стиль.фейсы(*ГАРНИТУРЫ)
    скрипт = """
Promise.all(%(ГАРН)s.map(([с, ф, в]) => document.fonts.load(`${в} 100px ${с}`, %(ЗНАКИ)s))).then(() => {
  const х = document.createElement('canvas').getContext('2d'), итог = {};
  for (const [с, ф, в] of %(ГАРН)s) {
    х.font = `${в} 100px ${с}`;
    const т = {};
    for (const з of %(ЗНАКИ)s) т[з] = +(х.measureText(з).width / 100).toFixed(4);
    итог[`${с} ${в}`] = т;
  }
  document.body.setAttribute('data-замер', JSON.stringify(итог));
});""" % {"ГАРН": json.dumps(ГАРНИТУРЫ, ensure_ascii=False), "ЗНАКИ": json.dumps(ЗНАКИ, ensure_ascii=False)}
    страница = f"<html><head><style>{css}</style></head><body><script>{скрипт}</script></body></html>"
    итог = браузер.замерить(страница, 400, 300)
    if not итог:
        raise SystemExit("Chrome не ответил: ширины не сняты")
    return итог


def main():
    ФАЙЛ.write_text(json.dumps(снять(), ensure_ascii=False, indent=0), encoding="utf-8")
    print(ФАЙЛ)


if __name__ == "__main__":
    main()
