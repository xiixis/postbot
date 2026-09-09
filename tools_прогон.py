# -*- coding: utf-8 -*-
"""Живой прогон приложения: открывает каждый раздел и ловит падения.

Зачем отдельно от разбора. `node --check` говорит только, что файл не сломан.
Обращение к несуществующей переменной он пропускает молча, а лист от этого не
открывается вовсе — в постботе так уже было: `alt="Слайд ${н+1}"` с неверным
именем уронил лист поста целиком, и ни один пост не открывался нигде.

Прогон грузит каждый раздел в настоящем браузере, вешает обработчик на ошибки
страницы и вдобавок открывает лист поста — самый ходовой и самый дорогой,
если он падает.

    python3 tools_прогон.py
"""

import http.server
import json
import re
import socket
import subprocess
import sys
import threading

import config
from tools_снимок import КОРЕНЬ, ОКНО_В, ОКНО_Ш, Ручка, _порт

# Раздел плюс, через «+», что там ещё сделать. «пост» — открыть лист поста.
ПРОГОН = ["today", "plan", "out", "out-числа", "stock",
          "out+пост", "today+пост"]


def прогнать(шаги=None) -> int:
    шаги = шаги or ПРОГОН
    хром = config.хром()
    if not хром:
        raise SystemExit("Chrome не найден: поставьте CHROME_PATH")
    порт = _порт()
    сервер = http.server.ThreadingHTTPServer(("127.0.0.1", порт), Ручка)
    threading.Thread(target=сервер.serve_forever, daemon=True).start()
    всего_бед = 0
    try:
        for шаг in шаги:
            итог = subprocess.run(
                [хром, "--headless", "--disable-gpu", "--no-sandbox",
                 "--disable-dev-shm-usage", "--disable-background-networking",
                 "--no-first-run", "--disable-extensions", "--disable-sync",
                 "--disable-default-apps", "--mute-audio",
                 "--virtual-time-budget=6000", "--dump-dom",
                 f"--window-size={ОКНО_Ш},{ОКНО_В}",
                 f"http://127.0.0.1:{порт}/_рамка.html#{шаг}"],
                capture_output=True, text=True, timeout=120)
            найдено = re.search(r"БЕДЫ: (\[.*?\])</pre>", итог.stdout, re.S)
            if not найдено:
                print(f"  {шаг}: страница не отчиталась вовсе")
                всего_бед += 1
                continue
            беды = json.loads(найдено.group(1))
            if беды:
                всего_бед += len(беды)
                print(f"  {шаг}: {len(беды)}")
                for б in беды:
                    print(f"      {б}")
            else:
                print(f"  {шаг}: чисто")
    finally:
        сервер.shutdown()
    print("итого бед:", всего_бед)
    return всего_бед


if __name__ == "__main__":
    sys.exit(1 if прогнать(sys.argv[1:] or None) else 0)
