# Раскладка ролика по голосу: python tools/layout.py voice/<ролик>.json <голос>
#
# Обычно окна фраз стоят на состояниях ролика (tools/voice.py). Здесь наоборот: голос ведёт.
# Записанные фразы ставятся подряд с паузами, с каждой снимается время слов, и из этого
# получается время сцен. Итог читают все движки ролика (Remotion, HyperFrames, гибрид):
#   src/<ролик>/timeline.json   длина, фразы, слова, громкость по кадрам
#   out/voice/<ролик>/<голос>/голос.wav и отчёт.json   дорожка и времена для сведения
# В сценарии у фразы: "пауза" после неё в секундах и "не короче": сколько держится её сцена.
# Запускать питоном 4xTube, после tools/voice.py.
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

ТУТ = Path(__file__).resolve().parent.parent
FPS = 30
ЧАСТОТА = 44100
НАЧАЛО = 0.25
ПАУЗА = 0.32
ХВОСТ = 1.6
ОПЕРЕЖЕНИЕ = 0.2


def слова_текста(текст: str) -> list[str]:
    return [с for с in re.split(r"\s+", текст.strip()) if re.search(r"[a-zа-яё0-9]", с, re.I)]


def звук(файл: Path) -> np.ndarray:
    with wave.open(str(файл)) as в:
        return np.frombuffer(в.readframes(в.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def main():
    сценарий = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    голос = sys.argv[2]
    папка = ТУТ / "out" / "voice" / сценарий["ролик"] / голос
    отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))

    from faster_whisper import WhisperModel

    ухо = WhisperModel("small", device="cpu", compute_type="int8")
    т, фразы, слова, куски = НАЧАЛО, [], [], []
    for з, строка in zip(отчёт, сценарий["строки"]):
        файл = папка / f"{з['строка']:02d}.wav"
        с = звук(файл)
        длина = len(с) / ЧАСТОТА
        части, _ = ухо.transcribe(str(файл), language="ru", beam_size=3, word_timestamps=True)
        услышано = [(w.start, w.end) for ч in части for w in (ч.words or [])]
        свои = слова_текста(показ := строка.get("на экране", строка["текст"]))
        if len(услышано) == len(свои):
            времена = услышано
        else:
            всего = sum(len(x) for x in свои)
            от, до = (услышано[0][0], услышано[-1][1]) if услышано else (0.0, длина)
            времена, ш = [], от
            for x in свои:
                д = (до - от) * len(x) / всего
                времена.append((ш, ш + д))
                ш += д
            print(f"  фраза {з['строка']}: услышано {len(услышано)} слов из {len(свои)}, время поделено по буквам")
        for x, (а, б) in zip(свои, времена):
            слова.append({"w": x, "s": round(т + а, 3), "e": round(т + min(б, длина), 3), "line": з["строка"]})
        конец = т + длина
        фразы.append({"n": з["строка"], "s": round(т, 3), "e": round(конец, 3), "text": показ})
        куски.append((т, с))
        з.update({"с": round(т, 2), "по": round(конец, 2)})
        т = max(конец + строка.get("пауза", ПАУЗА), т + строка.get("не короче", 0))

    длина = round((фразы[-1]["e"] + ХВОСТ) * FPS) / FPS
    дорожка = np.zeros(int(длина * ЧАСТОТА))
    for старт, с in куски:
        от = int(старт * ЧАСТОТА)
        дорожка[от:от + len(с)] += с[: len(дорожка) - от]
    with wave.open(str(папка / "голос.wav"), "wb") as в:
        в.setnchannels(1)
        в.setsampwidth(2)
        в.setframerate(ЧАСТОТА)
        в.writeframes((np.clip(дорожка, -1, 1) * 32767).astype(np.int16).tobytes())
    (папка / "отчёт.json").write_text(json.dumps(отчёт, ensure_ascii=False, indent=1), encoding="utf-8")

    шаг = ЧАСТОТА // FPS
    кадров = len(дорожка) // шаг
    сила = np.sqrt((дорожка[: кадров * шаг].reshape(кадров, шаг) ** 2).mean(axis=1))
    сила = np.clip(сила / max(1e-9, np.percentile(сила[сила > 0.005], 95)), 0, 1)
    # Сцена на фразу: начинается чуть раньше голоса, чтобы картинка успела встать.
    границы = [0.0] + [round(ф["s"] - ОПЕРЕЖЕНИЕ, 3) for ф in фразы[1:]] + [длина]
    иды = [с.get("ид", str(н)) for н, с in enumerate(сценарий["строки"], 1)]
    сцены = {иды[н]: {"s": границы[н], "e": границы[н + 1]} for н in range(len(фразы))}
    # Метки: имя → [ид фразы, номер слова с нуля]. Это миг, когда слово звучит.
    по_фразам = {}
    for с in слова:
        по_фразам.setdefault(иды[с["line"] - 1], []).append(с)
    метки = {имя: по_фразам[ф][н]["s"] for имя, (ф, н) in сценарий.get("метки", {}).items()}
    итог = {"fps": FPS, "length": длина, "frames": round(длина * FPS), "scenes": сцены, "cues": метки,
            "w": {ид: [с["s"] for с in сс] for ид, сс in по_фразам.items()},
            "lines": фразы, "words": слова, "wave": [round(float(x), 2) for x in сила]}
    цель = ТУТ / "src" / сценарий["ролик"] / "timeline.json"
    цель.parent.mkdir(parents=True, exist_ok=True)
    цель.write_text(json.dumps(итог, ensure_ascii=False), encoding="utf-8")
    for ф in фразы:
        print(f"{ф['n']:02d} {ф['s']:6.2f}–{ф['e']:6.2f}  {ф['text']}")
    print(f"длина {длина:.2f} с, кадров {итог['frames']}, слов {len(слова)}")


if __name__ == "__main__":
    main()
