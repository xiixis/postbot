# Звуковая дорожка ролика одним файлом: python tools/sound.py voice/<ролик>.json <голос>
#
# Для роликов, где голос ведёт (tools/layout.py). Голос, музыка под ним и звуки переходов
# сводятся в один файл, и его кладёт в ролик сам движок: Remotion тегом <Audio>, HyperFrames
# тегом <audio>. Так три исполнения одного ролика звучат одинаково, а пересчитывать кадры
# ради звука не нужно.
# Музыка опускается под каждой фразой по её времени из отчёта, как в tools/voice-mix.py.
# В сценарии: "музыка" — трек, он зацикливается; "переходы" — иды сцен, на входе в которые
# звучит public/sfx/whoosh.wav. Итог: public/<папка>/sound.m4a, папка из поля "звук".
import json
import subprocess
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent.parent
МУЗЫКА = 0.5             # громкость музыки в паузах
ПОД_РЕЧЬЮ = 0.78         # на сколько музыка убирается под фразой
ГОЛОС = 1.35
ПЕРЕХОД = 0.3


def окно(с: float, по: float, вниз: float = 0.2, вверх: float = 0.3) -> str:
    return f"clip(min((t-{с - вниз - 0.05:.3f})/{вниз},({по + вверх:.3f}-t)/{вверх}),0,1)"


def main():
    сценарий = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    папка = ТУТ / "out" / "voice" / сценарий["ролик"] / sys.argv[2]
    отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))
    время = json.loads((ТУТ / "src" / сценарий["ролик"] / "timeline.json").read_text(encoding="utf-8"))
    длина = время["length"]
    вниз = "0"
    for з in отчёт:
        вниз = f"max({вниз},{ПОД_РЕЧЬЮ}*{окно(з['с'], з['по'])})"
    конец = f"clip(({длина:.2f}-t)/1.2,0,1)"
    граф = [f"[0:a]atrim=0:{длина:.2f},volume='{МУЗЫКА}*(1-{вниз})*{конец}':eval=frame[m]",
            f"[1:a]aresample=48000,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=3,volume={ГОЛОС},aformat=channel_layouts=stereo[say]"]
    входы = ["-stream_loop", "-1", "-i", str(ТУТ / сценарий["музыка"]), "-i", str(папка / "голос.wav")]
    метки = ["[m]", "[say]"]
    for н, ид in enumerate(сценарий.get("переходы", [])):
        мс = max(0, round((время["scenes"][ид]["s"] - 0.12) * 1000))
        входы += ["-i", str(ТУТ / "public" / "sfx" / "whoosh.wav")]
        граф.append(f"[{н + 2}:a]volume={ПЕРЕХОД},adelay={мс}|{мс},aformat=channel_layouts=stereo[w{н}]")
        метки.append(f"[w{н}]")
    граф.append(f"{''.join(метки)}amix=inputs={len(метки)}:duration=longest:normalize=0,volume=1.15,alimiter=limit=0.74:level=disabled[a]")
    итог = ТУТ / "public" / сценарий["звук"] / "sound.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *входы, "-filter_complex", ";".join(граф), "-map", "[a]",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{длина:.2f}", str(итог)], check=True)
    вывод = subprocess.run(["ffmpeg", "-v", "info", "-i", str(итог), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    пик = [с.split("max_volume:")[1].strip() for с in вывод.splitlines() if "max_volume" in с][0]
    средняя = [с.split("mean_volume:")[1].strip() for с in вывод.splitlines() if "mean_volume" in с][0]
    print(f"{итог.relative_to(ТУТ)}: {длина:.2f} с, пик {пик}, средняя {средняя}")


if __name__ == "__main__":
    main()
