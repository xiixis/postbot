#!/usr/bin/env bash
# Пушистые 3D-значки для поста «бесплатные нейросети» (рерайт @nik_kukuytsev, 17.09.2026).
# Запуск: nohup ./значки-3d.sh > значки-3d.log 2>&1 &
set -u
# Переносимо: мак и ПК (Git Bash). Корень считается от места скрипта, питон —
# общее окружение yt-searcher/.venv (или PB_PYTHON, если задан).
cd "$(dirname "$0")" || exit 1
POSTBOT="$(cd ../.. && pwd)"
ROOT="$(dirname "$POSTBOT")"
PY="${PB_PYTHON:-}"
for p in "$ROOT/yt-searcher/.venv/bin/python3" "$ROOT/yt-searcher/.venv/Scripts/python.exe"; do
  [ -z "$PY" ] && [ -x "$p" ] && PY="$p"
done
[ -n "$PY" ] || { echo "нет питона yt-searcher/.venv в $ROOT — задай PB_PYTHON" >&2; exit 2; }
export PYTHONUTF8=1
R="$POSTBOT/Style/картинка.py"
K=значки/3d; O=опоры-3d
mkdir -p $K

draw () {  # файл описание опора
  local file=$1 desc=$2 ref=$3
  if [[ -s "$K/$file" ]]; then echo "уже есть: $file"; return; fi
  # Vertex отдаёт 429 после нескольких картинок подряд: ждём и пробуем снова.
  for try_n in 1 2 3 4 5; do
    echo "рисую: $file (попытка $try_n)"
    if "$PY" "$R" "$K/$file" "$desc" --форма 1:1 --размер 2K --буквы --опора $ref; then
      sleep 20; return
    fi
    sleep $((60 * try_n))
  done
  echo "не вышло: $file"
}

BG="Single object centred, occupying about 60% of the frame, on a perfectly flat uniform solid background of colour #ECEFF6 (very light grey-blue), no gradient, no vignette, no floor, only a very soft faint contact shadow directly below. Nothing else in the frame. Match the reference image's object, material and lighting as closely as possible."
FUR="A soft 3D plush icon made entirely of fluffy realistic fur, like a furry toy, studio product render, soft light from the top-left."
draw gemini.png "$BG $FUR The Google Gemini four-pointed sparkle star logo, fur coloured in the Gemini rainbow gradient: red, yellow, green and blue." $O/gemini.jpg
draw firefly.png "$BG $FUR The Adobe Firefly app icon: a rounded square of deep red fur with a bold white fur letter-shape A (the Adobe A, without the crossbar) in the middle." $O/firefly.jpg
draw leonardo.png "$BG A round embroidered patch icon, like a thick stitched textile badge: the Leonardo AI logo, a stylised bearded face of Leonardo da Vinci with long hair in colourful yellow, orange, blue and purple threads, thin constellation lines around, dark navy base." $O/leonardo.jpg
draw pixai.png "$BG $FUR The PixAI app icon: a slightly tilted rounded square of black fur with a bold chunky white fur letter P in the middle." $O/pixai.jpg
draw magnific.png "$BG $FUR The Magnific AI icon: a round disc of black fur with a white fur letter M shape in the middle and the white word Magnific below it." $O/magnific.jpg
draw деньги.png "$BG Glossy 3D cartoon render icon: a hand in a blue sleeve holding a stack of green dollar banknotes, crossed out by a big red prohibition sign (red ring with a diagonal bar). Smooth clay-like plastic material, not fur." $O/деньги.jpg
echo "готово"
