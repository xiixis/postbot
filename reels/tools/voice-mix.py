# Сведение роликов с озвучкой: python tools/voice-mix.py <папка с готовыми роликами> [ролик ...]
#
# В папке лежат v2-words.mp4, v3-keys.mp4, v4-desk.mp4: из них берётся только картинка, кадры
# заново не считаются. До сведения должны быть готовы дорожки:
#   out/voice/<ролик>/<голос>/голос.wav и отчёт.json   tools/voice.py
#   out/<v2|v3|v4>-sfx.wav                             рендер звуков с настройкой music: false
#
# Музыка уходит вниз под каждую фразу по её точному времени из отчёта и возвращается в паузах.
# Прижимать музыку самим голосом (sidechain) пробовали: под разными голосами она опускалась
# на 4–10 дБ, и низкий голос в ней тонул.
import json
import subprocess
import sys
from pathlib import Path

ТУТ = Path(__file__).resolve().parent.parent
МУЗЫКА = 0.92            # громкость музыки в паузах
ПОД_РЕЧЬЮ = 0.75         # на сколько музыка убирается под фразой: 0,75 это минус 12 дБ
ПОД_НАБОРОМ = 0.37       # и под набором на клавиатуре
ГОЛОС = 1.35


def окно(с: float, по: float, вниз: float = 0.2, вверх: float = 0.3) -> str:
    """Единица внутри отрезка, плавный край до и после него."""
    return f"clip(min((t-{с - вниз - 0.05:.3f})/{вниз},({по + вверх:.3f}-t)/{вверх}),0,1)"


def наибольшее(части: list[str]) -> str:
    итог = части[0]
    for ч in части[1:]:
        итог = f"max({итог},{ч})"
    return итог


def свести(видео: Path, сценарий: dict, папка: Path, итог: Path) -> str:
    отчёт = json.loads((папка / "отчёт.json").read_text(encoding="utf-8"))
    части = [f"{ПОД_РЕЧЬЮ}*{окно(з['с'], з['по'])}" for з in отчёт]
    if "набор" in сценарий:
        части.append(f"{ПОД_НАБОРОМ}*{окно(*сценарий['набор'], 0.25, 0.35)}")
    короткое = сценарий["ролик"].split("-")[0]
    музыка = f"volume='{МУЗЫКА}*(1-{наибольшее(части)})':eval=frame"
    голос = f"aresample=48000,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=3,volume={ГОЛОС}"
    граф = (f"[1:a]{музыка}[m];"
            f"[3:a]{голос},aformat=channel_layouts=stereo[say];"
            "[2:a][m][say]amix=inputs=3:duration=first:normalize=0,volume=1.2,alimiter=limit=0.74:level=disabled,afade=t=in:d=0.02[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(видео), "-i", str(ТУТ / сценарий["музыка"]),
                    "-i", str(ТУТ / "out" / f"{короткое}-sfx.wav"), "-i", str(папка / "голос.wav"),
                    "-filter_complex", граф, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(сценарий.get("длина", 15)), "-movflags", "+faststart", str(итог)], check=True)
    # теми же фильтрами проверка собирает музыку и голос отдельными дорожками
    (папка / "сведение.json").write_text(json.dumps({"музыка": музыка, "голос": голос}, ensure_ascii=False), encoding="utf-8")
    вывод = subprocess.run(["ffmpeg", "-v", "info", "-i", str(итог), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    return [с.split("max_volume:")[1].strip() for с in вывод.splitlines() if "max_volume" in с][0]


def main():
    if len(sys.argv) < 2:
        raise SystemExit("нужна папка с готовыми роликами")
    откуда, нужные = Path(sys.argv[1]), sys.argv[2:]
    for файл in sorted((ТУТ / "voice").glob("[rv]*.json")):
        сценарий = json.loads(файл.read_text(encoding="utf-8"))
        if нужные and сценарий["ролик"] not in нужные:
            continue
        if not (ТУТ / "out" / "voice" / сценарий["ролик"]).is_dir():
            continue
        for папка in sorted((ТУТ / "out" / "voice" / сценарий["ролик"]).iterdir()):
            итог = ТУТ / "out" / f"{сценарий['ролик']}-{папка.name}.mp4"
            print(f"{итог.name}: пик {свести(откуда / (сценарий['ролик'] + '.mp4'), сценарий, папка, итог)}")


if __name__ == "__main__":
    main()
