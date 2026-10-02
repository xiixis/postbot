# Звуковая дорожка ролика одним файлом: python tools/sound.py voice/<ролик>.json <голос>
#
# Для роликов, где голос ведёт (tools/layout.py). Голос, музыка и звуки сводятся в один файл,
# и его кладёт в ролик сам движок: Remotion тегом <Audio>, HyperFrames тегом <audio>. Так разные
# исполнения одного ролика звучат одинаково, а пересчитывать кадры ради звука не нужно.
#
# В сценарии:
#   "музыка"        трек, он зацикливается
#   "музыка ровно"  громкость музыки на весь ролик одним числом. Без этого поля музыка
#                   опускается под каждой фразой и возвращается в паузах, как в voice-mix.py.
#                   Владелец 02.10.2026: «чтобы она не прыгала, просто на фоне с одной громкостью».
#   "переходы"      иды сцен, на входе в которые звучит public/sfx/whoosh.wav
#   "звуки"         [файл из public/sfx, место, сдвиг в секундах, громкость]. Место: ид сцены
#                   (её начало) или "ид:номер" — миг, когда звучит слово фразы. Записи лежат в
#                   public/sfx/lib (Pixabay, лицензия в CREDITS.md): собранные кодом звуки
#                   владелец не принимает.
# Итог: public/<папка>/sound.m4a, папка из поля "звук". Печатается, на сколько голос громче музыки:
# меньше 10 дБ — речь тонет.
import json
import re
import subprocess
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent.parent
МУЗЫКА = 0.5             # громкость музыки в паузах
ПОД_РЕЧЬЮ = 0.78         # на сколько музыка убирается под фразой
ГОЛОС = 1.35
ПЕРЕХОД = 0.3
ЧИСТКА_ГОЛОСА = "aresample=48000,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=3"


def окно(с: float, по: float, вниз: float = 0.2, вверх: float = 0.3) -> str:
    return f"clip(min((t-{с - вниз - 0.05:.3f})/{вниз},({по + вверх:.3f}-t)/{вверх}),0,1)"


def громкость(доводы: list[str], что: str = "mean_volume") -> float:
    вывод = subprocess.run(["ffmpeg", "-v", "info", *доводы, "-vn", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(rf"{что}: (-?[\d.]+) dB", вывод).group(1))


def main():
    сценарий = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    папка = ТУТ / "out" / "voice" / сценарий["ролик"] / sys.argv[2]
    отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))
    время = json.loads((ТУТ / "src" / сценарий["ролик"] / "timeline.json").read_text(encoding="utf-8"))
    длина = время["length"]
    конец = f"clip(({длина:.2f}-t)/1.2,0,1)"
    ровно = сценарий.get("музыка ровно")
    if ровно:
        уровень = f"{ровно}*{конец}"
    else:
        вниз = "0"
        for з in отчёт:
            вниз = f"max({вниз},{ПОД_РЕЧЬЮ}*{окно(з['с'], з['по'])})"
        уровень = f"{МУЗЫКА}*(1-{вниз})*{конец}"
    музыка, голос = ТУТ / сценарий["музыка"], папка / "голос.wav"
    граф = [f"[0:a]atrim=0:{длина:.2f},volume='{уровень}':eval=frame[m]",
            f"[1:a]{ЧИСТКА_ГОЛОСА},volume={ГОЛОС},aformat=channel_layouts=stereo[say]"]
    входы = ["-stream_loop", "-1", "-i", str(музыка), "-i", str(голос)]
    метки = ["[m]", "[say]"]

    def звук(файл: Path, секунда: float, сила: float):
        н = len(метки)
        мс = max(0, round(секунда * 1000))
        входы.extend(["-i", str(файл)])
        граф.append(f"[{н}:a]volume={сила},adelay={мс}|{мс},aformat=channel_layouts=stereo[x{н}]")
        метки.append(f"[x{н}]")

    for ид in сценарий.get("переходы", []):
        звук(ТУТ / "public" / "sfx" / "whoosh.wav", время["scenes"][ид]["s"] - 0.12, ПЕРЕХОД)
    for файл, место, сдвиг, сила in сценарий.get("звуки", []):
        ид, _, слово = место.partition(":")
        секунда = время["w"][ид][int(слово)] if слово else время["scenes"][ид]["s"]
        звук(ТУТ / "public" / "sfx" / файл, секунда + сдвиг, сила)
    граф.append(f"{''.join(метки)}amix=inputs={len(метки)}:duration=longest:normalize=0,volume=1.15,alimiter=limit=0.74:level=disabled[a]")
    итог = ТУТ / "public" / сценарий["звук"] / "sound.m4a"
    итог.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *входы, "-filter_complex", ";".join(граф), "-map", "[a]",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{длина:.2f}", str(итог)], check=True)
    print(f"{итог.relative_to(ТУТ)}: {длина:.2f} с, пик {громкость(['-i', str(итог), '-af', 'volumedetect'], 'max_volume')} dB, "
          f"средняя {громкость(['-i', str(итог), '-af', 'volumedetect'])} dB, звуков {len(метки) - 2}")
    # Голос против музыки: речь меряется по первой фразе, музыка на том же отрезке.
    з = отчёт[0]
    речь = громкость(["-ss", str(з["с"]), "-t", str(з["по"] - з["с"]), "-i", str(голос), "-af", f"{ЧИСТКА_ГОЛОСА},volume={ГОЛОС},volumedetect"])
    фон_уровень = ровно if ровно else МУЗЫКА * (1 - ПОД_РЕЧЬЮ)
    фон = громкость(["-t", "20", "-i", str(музыка), "-af", f"volume={фон_уровень},volumedetect"])
    print(f"голос {речь:.1f} dB, музыка под ним {фон:.1f} dB: голос громче на {речь - фон:.1f} dB"
          + ("" if речь - фон >= 10 else "  ← МАЛО, речь тонет"))


if __name__ == "__main__":
    main()
