# Время слов для субтитров: python tools/words.py voice/<ролик>.json <голос>
#
# Распознавание речи снимает с каждой записанной фразы время каждого слова, к нему
# прибавляется начало фразы в ролике. Слова пишутся как в сценарии: распознавание нужно только
# ради времени, а не ради текста. Заодно считается громкость голоса по кадрам для живой волны.
# Итог: src/series/words/<rN>.json и src/series/words/<rN>-wave.json, их ролик берёт при сборке.
# Запускать питоном 4xTube: ~/4xSoft/yt-searcher/.venv/bin/python3 tools/words.py voice/r6.json А-рассказчик
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

ТУТ = Path(__file__).resolve().parent.parent
FPS = 30


def слова_текста(текст: str) -> list[str]:
    return [с for с in re.split(r"\s+", текст.strip()) if re.search(r"[a-zа-яё0-9]", с, re.I)]


def main():
    сценарий = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    голос = sys.argv[2]
    папка = ТУТ / "out" / "voice" / сценарий["ролик"] / голос
    отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))
    короткое = сценарий["ролик"].split("-")[0]

    from faster_whisper import WhisperModel

    ухо = WhisperModel("small", device="cpu", compute_type="int8")
    итог = []
    for з in отчёт:
        файл = папка / f"{з['строка']:02d}.wav"
        части, _ = ухо.transcribe(str(файл), language="ru", beam_size=3, word_timestamps=True)
        услышано = [(w.start, w.end) for ч in части for w in (ч.words or [])]
        свои = слова_текста(з["текст"])
        # число слов совпало: берём времена как есть; не совпало: делим отрезки речи поровну по буквам
        if len(услышано) == len(свои):
            времена = услышано
        else:
            всего = sum(len(с) for с in свои)
            от, до = (услышано[0][0], услышано[-1][1]) if услышано else (0.0, з["по"] - з["с"])
            времена, т = [], от
            for с in свои:
                ш = (до - от) * len(с) / всего
                времена.append((т, т + ш))
                т += ш
            print(f"  строка {з['строка']}: услышано {len(услышано)} слов из {len(свои)}, время поделено по буквам")
        for с, (а, б) in zip(свои, времена):
            итог.append({"w": с, "s": round(з["с"] + а, 3), "e": round(з["с"] + б, 3), "line": з["строка"]})

    (ТУТ / "src" / "series" / "words" / f"{короткое}.json").write_text(json.dumps(итог, ensure_ascii=False), encoding="utf-8")

    with wave.open(str(папка / "голос.wav")) as в:
        частота = в.getframerate()
        с = np.frombuffer(в.readframes(в.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    шаг = частота // FPS
    кадров = len(с) // шаг
    сила = np.sqrt((с[: кадров * шаг].reshape(кадров, шаг) ** 2).mean(axis=1))
    сила = np.clip(сила / max(1e-9, np.percentile(сила[сила > 0.005], 95)), 0, 1) if (сила > 0.005).any() else сила
    (ТУТ / "src" / "series" / "words" / f"{короткое}-wave.json").write_text(json.dumps([round(float(x), 3) for x in сила]), encoding="utf-8")
    print(f"{короткое}: слов {len(итог)}, кадров волны {кадров}")


if __name__ == "__main__":
    main()
