# Озвучка ролика через Fish Audio: python tools/voice.py voice/<ролик>.json [голос ...]
#
# Каждая строка текста озвучивается отдельно и ставится в своё окно «с … до» в секундах:
# окна стоят на состояниях ролика, поэтому голос не уезжает от картинки. Строка длиннее окна
# озвучивается заново быстрее. Что получилось, проверяет распознавание речи: ушей у модели нет.
#
# Ключ Fish берётся из окружения (FISH_API_KEY) или из облака команды 4xTube тем же способом,
# что и в приложении. Он живёт только в памяти процесса: на диск и в вывод не попадает.
# Запускать питоном 4xTube, там стоят requests и faster-whisper:
#   ~/4xSoft/yt-searcher/.venv/bin/python3 tools/voice.py voice/v2-words.json
import difflib
import io
import json
import os
import re
import sys
import time
import wave
from pathlib import Path

import numpy as np
import requests

ТУТ = Path(__file__).resolve().parent.parent
ТЬЮБ = Path.home() / "4xSoft" / "yt-searcher"
АДРЕС = "https://api.fish.audio/v1/tts"
ЧАСТОТА = 44100
ДЛИНА = 15.0
БЫСТРЕЕ_НЕЛЬЗЯ = 1.2                 # быстрее речь мнётся: на 1,17 распознавание уже теряло слова
ДУБЛЕЙ = 4                           # озвучка каждый раз немного разная, неудачный дубль переснимается
ПОХОЖЕ = 0.85                        # доля слов текста, которую обязано услышать распознавание
ГРОМКОСТЬ = 0.11                     # средняя громкость строки, одна на все голоса


def ключ() -> str:
    свой = os.getenv("FISH_API_KEY", "").strip()
    if свой:
        return свой
    sys.path.insert(0, str(ТЬЮБ))
    from app import cloud

    if not cloud.configured() or not cloud.token():
        raise SystemExit("ключа Fish нет: FISH_API_KEY не задан, в облако 4xTube вход не сделан")
    строки = [с for с in cloud.team_keys() if с.get("service") == "fish" and с.get("value")]
    if not строки:
        raise SystemExit("в ключах команды 4xTube нет записи fish")
    return строки[0]["value"]


def озвучить(текст: str, голос: str, модель: str, скорость: float, секрет: str) -> bytes:
    тело = {"text": текст, "reference_id": голос, "format": "wav", "sample_rate": ЧАСТОТА,
            "latency": "normal", "chunk_length": 300, "prosody": {"speed": round(скорость, 2)}}
    шапка = {"Authorization": f"Bearer {секрет}", "Content-Type": "application/json", "model": модель}
    причина = ""
    for попытка in range(1, 5):
        try:
            о = requests.post(АДРЕС, headers=шапка, json=тело, timeout=300)
        except requests.exceptions.RequestException as e:
            причина = type(e).__name__
            time.sleep(3 * попытка)
            continue
        if о.status_code == 200 and о.content:
            return о.content
        причина = f"{о.status_code} {о.text[:160]}"
        if о.status_code in (401, 402, 403):
            raise SystemExit(f"Fish отказал: {причина}")
        time.sleep(3 * попытка)
    raise SystemExit(f"Fish не ответил: {причина}")


def звук(данные: bytes) -> np.ndarray:
    with wave.open(io.BytesIO(данные)) as в:
        каналов, частота = в.getnchannels(), в.getframerate()
        с = np.frombuffer(в.readframes(в.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    if каналов > 1:
        с = с.reshape(-1, каналов).mean(axis=1)
    if частота != ЧАСТОТА:
        raise SystemExit(f"Fish вернул частоту {частота}, ждали {ЧАСТОТА}")
    return с


def обрезать(с: np.ndarray) -> np.ndarray:
    """Тишина до и после речи убирается, остаётся по 20 мс с плавным краем."""
    окно = int(ЧАСТОТА * 0.02)
    сила = np.sqrt(np.convolve(с ** 2, np.ones(окно) / окно, mode="same"))
    где = np.where(сила > 0.04 * сила.max())[0]
    if not len(где):
        return с
    с = с[max(0, где[0] - окно): где[-1] + окно].copy()
    край = int(ЧАСТОТА * 0.008)
    с[:край] *= np.linspace(0, 1, край)
    с[-край:] *= np.linspace(1, 0, край)
    return с


def выровнять(с: np.ndarray) -> np.ndarray:
    """Одна средняя громкость на все строки и голоса, пик не выше 0,95."""
    шаг = int(ЧАСТОТА * 0.05)
    куски = [np.sqrt(np.mean(с[н:н + шаг] ** 2)) for н in range(0, len(с) - шаг, шаг)]
    речь = [к for к in куски if к > 0.2 * max(куски)]
    с = с * (ГРОМКОСТЬ / float(np.mean(речь)))
    пик = np.abs(с).max()
    return с * (0.95 / пик) if пик > 0.95 else с


def слова(текст: str) -> list[str]:
    текст = текст.lower().replace("ё", "е")
    замены = {"клот": "клод", "клоуд": "клод", "телеграмме": "телеграме", "enter": "энтер", "интер": "энтер",
              "скиллы": "скилы", "скилла": "скила", "промбт": "промпт", "3": "три", "11": "одиннадцать", "12": "двенадцать"}
    return [замены.get(с, с) for с in re.findall(r"[a-zа-я0-9]+", текст)]


def записать(файл: Path, с: np.ndarray) -> None:
    файл.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(файл), "wb") as в:
        в.setnchannels(1)
        в.setsampwidth(2)
        в.setframerate(ЧАСТОТА)
        в.writeframes((np.clip(с, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    доводы = sys.argv[1:]
    if not доводы:
        raise SystemExit(__doc__ or "нужен файл сценария")
    сценарий = json.loads(Path(доводы[0]).read_text(encoding="utf-8"))
    набор = json.loads((ТУТ / "voice" / "голоса.json").read_text(encoding="utf-8"))
    имена = доводы[1:] or list(набор["голоса"])
    секрет = ключ()

    from faster_whisper import WhisperModel

    ухо = WhisperModel("small", device="cpu", compute_type="int8")
    плохо = False
    for имя in имена:
        голос = набор["голоса"][имя]["id"]
        папка = ТУТ / "out" / "voice" / сценарий["ролик"] / имя
        дорожка = np.zeros(int(сценарий.get("длина", ДЛИНА) * ЧАСТОТА))
        отчёт = []
        прежний = {}
        if (папка / "отчёт.json").exists():
            прежний = {з["строка"]: з for з in json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))}
        for н, строка in enumerate(сценарий["строки"], 1):
            # у строки может быть свой голос: так в одном ролике фразу читают три голоса подряд
            голос = набор["голоса"][строка.get("голос", имя)]["id"]
            начало = строка.get("с", строка.get("не раньше", 0.0))
            окно = строка["до"] - начало
            файл = папка / f"{н:02d}.wav"
            скорость, лучший = 1.0, None
            # Удачный дубль не переснимается: текст тот же, распознан, в новое окно влезает без ускорения.
            было = прежний.get(н, {})
            if файл.exists() and было.get("текст") == строка["текст"] and было.get("сходство", 0) >= ПОХОЖЕ:
                с = звук(файл.read_bytes())
                if len(с) / ЧАСТОТА <= окно + 0.02 and было.get("скорость", 9) <= 1.0:
                    лучший = ((True, было["сходство"]), с, было["слышно"], было["скорость"])
            for дубль in range(0 if лучший else ДУБЛЕЙ):
                с = выровнять(обрезать(звук(озвучить(f"{набор['манера']} {строка['текст']}", голос, набор["модель"], скорость, секрет))))
                длина = len(с) / ЧАСТОТА
                записать(файл, с)
                части, _ = ухо.transcribe(str(файл), language="ru", beam_size=3)
                слышно = " ".join(ч.text.strip() for ч in части)
                сходство = difflib.SequenceMatcher(None, слова(строка["текст"]), слова(слышно)).ratio()
                оценка = (длина <= окно + 0.02, сходство)
                if лучший is None or оценка > лучший[0]:
                    лучший = (оценка, с, слышно, скорость)
                if длина <= окно + 0.02 and сходство >= ПОХОЖЕ:
                    break
                if длина > окно + 0.02:
                    скорость = min(БЫСТРЕЕ_НЕЛЬЗЯ, max(скорость + 0.05, скорость * длина / окно * 1.03))
            (_, сходство), с, слышно, скорость = лучший
            длина = len(с) / ЧАСТОТА
            записать(файл, с)
            старт = строка["до"] - длина if строка.get("к концу") else начало
            влезла = длина <= окно + 0.02 and старт >= начало - 0.02
            от = int(старт * ЧАСТОТА)
            дорожка[от:от + len(с)] += с[: len(дорожка) - от]
            плохо = плохо or not влезла or сходство < ПОХОЖЕ
            отчёт.append({"строка": н, "текст": строка["текст"], "с": round(старт, 2), "по": round(старт + длина, 2),
                          "окно до": строка["до"], "скорость": round(скорость, 2), "слышно": слышно, "сходство": round(сходство, 2)})
            print(f"{сценарий['ролик']} {имя} {н:02d}: {старт:5.2f}–{старт + длина:5.2f} с (окно до {строка['до']:5.2f}) "
                  f"скорость {скорость:.2f} {'' if влезла else 'НЕ ВЛЕЗЛА '}| сходство {сходство:.2f} | {слышно}")
            sys.stdout.flush()
        записать(папка / "голос.wav", дорожка)
        (папка / "отчёт.json").write_text(json.dumps(отчёт, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(1 if плохо else 0)


if __name__ == "__main__":
    main()
