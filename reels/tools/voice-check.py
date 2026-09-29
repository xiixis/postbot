# Проверка готовых роликов с озвучкой: python tools/voice-check.py
# Ушей у модели нет, поэтому проверяется то, что можно измерить:
#   слова     что распознаёт whisper в готовом ролике поверх музыки и звуков;
#   громкость общая громкость ролика в LUFS;
#   музыка    на сколько децибел музыка тише под речью, чем в паузах, и на сколько речь громче её.
# Речь должна быть громче музыки под ней хотя бы на 10 дБ: на 3–7 дБ низкий голос в ней тонул.
# Запускать питоном 4xTube: ~/4xSoft/yt-searcher/.venv/bin/python3 tools/voice-check.py
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ТУТ = Path(__file__).resolve().parent.parent
ЧАСТОТА = 16000


def слова(текст: str) -> list[str]:
    текст = текст.lower().replace("ё", "е")
    замены = {"клот": "клод", "клоуд": "клод", "телеграмме": "телеграме", "enter": "энтер", "интер": "энтер"}
    return [замены.get(с, с) for с in re.findall(r"[a-zа-я0-9]+", текст)]


def звук(доводы: list[str]) -> np.ndarray:
    сырое = subprocess.run(["ffmpeg", "-v", "error", *доводы, "-ac", "1", "-ar", str(ЧАСТОТА), "-f", "s16le", "-"],
                           check=True, capture_output=True).stdout
    return np.frombuffer(сырое, dtype=np.int16).astype(np.float64) / 32768


def громкость(файл: Path) -> float:
    вывод = subprocess.run(["ffmpeg", "-v", "info", "-i", str(файл), "-af", "ebur128", "-vn", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", вывод)[-1])


def дб(с: np.ndarray) -> float:
    return 20 * np.log10(max(1e-9, float(np.sqrt(np.mean(с ** 2)))))


def main():
    from faster_whisper import WhisperModel

    ухо = WhisperModel("small", device="cpu", compute_type="int8")
    плохо = False
    for сценарий in sorted((ТУТ / "voice").glob("v*.json")):
        д = json.loads(сценарий.read_text(encoding="utf-8"))
        текст = " ".join(с["текст"] for с in д["строки"])
        for папка in sorted((ТУТ / "out" / "voice" / д["ролик"]).iterdir()):
            ролик = ТУТ / "out" / f"{д['ролик']}-{папка.name}.mp4"
            отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))
            части, _ = ухо.transcribe(str(ролик), language="ru", beam_size=3)
            слышно = " ".join(ч.text.strip() for ч in части)
            сходство = difflib.SequenceMatcher(None, слова(текст), слова(слышно)).ratio()

            # музыка и голос теми же фильтрами, что в сведении, но отдельными дорожками
            фильтры = json.loads((папка / "сведение.json").read_text(encoding="utf-8"))
            музыка = звук(["-i", str(ТУТ / д["музыка"]), "-af", фильтры["музыка"], "-t", "15"])
            голос = звук(["-i", str(папка / "голос.wav"), "-af", фильтры["голос"]])
            под = np.zeros(len(музыка), dtype=bool)
            for з in отчёт:
                под[int((з["с"] + 0.15) * ЧАСТОТА): int((з["по"] - 0.1) * ЧАСТОТА)] = True
            пауза = np.zeros(len(музыка), dtype=bool)
            край = [0.0] + [x for з in отчёт for x in (з["с"], з["по"])] + [15.0]
            for от, до in zip(край[0::2], край[1::2]):
                if до - от > 0.9:
                    пауза[int((от + 0.6) * ЧАСТОТА): int((до - 0.1) * ЧАСТОТА)] = True
            речь = голос[: len(под)][под[: len(голос)]]
            вниз = дб(музыка[пауза]) - дб(музыка[под]) if пауза.any() else float("nan")
            выше = дб(речь) - дб(музыка[под])
            годно = сходство >= 0.85 and выше >= 10
            плохо = плохо or not годно
            print(f"{ролик.name:32s} слова {сходство:.2f} | громкость {громкость(ролик):6.1f} LUFS | "
                  f"музыка под речью тише на {вниз:4.1f} дБ | речь громче музыки на {выше:4.1f} дБ | {'годно' if годно else 'ПЛОХО'}")
            print(f"    слышно: {слышно}")
            sys.stdout.flush()
    sys.exit(1 if плохо else 0)


if __name__ == "__main__":
    main()
