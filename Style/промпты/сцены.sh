#!/usr/bin/env bash
# Сцены кадров стиля «промпты» — по одной за раз: две отрисовки разом машина не тянет.
# Запуск: nohup ./сцены.sh > /tmp/сцены.log 2>&1 &
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
K="$POSTBOT/Style/промпты/картинки"

COMMON="Photorealistic editorial 3D product still life. Warm cream paper background (#EAE4DE) filling the whole frame. The whole scene is almost monochrome, desaturated to warm greys and beiges, EXCEPT one single crimson-red object that is the only colour in the picture. Soft daylight from the upper left, gentle long shadows, premium advertising render, shallow depth of field. The top 45% of the frame is empty cream background with nothing in it, the objects sit in the lower half."

draw () {
  if [[ -s "$K/$1" ]]; then echo "уже есть: $1"; return; fi
  echo "рисую: $1"
  "$PY" "$R" "$K/$1" "$COMMON $2" --форма 4:5 --размер 2K || echo "не вышло: $1"
}

draw 01-конкурент.png "Scene: two open paper folders lying side by side on a desk, a few chess pieces standing on them, and a single thin crimson-red thread stretched between the two folders like a connection line."
draw 02-цена.png "Scene: one matte black sneaker standing on the cream surface, a smartphone lying flat beside it, and a thin crimson-red laser line sweeping across the sneaker."
draw 03-резюме.png "Scene: an old typewriter with a sheet of paper in it, a neat stack of documents beside it, and a single crimson-red ribbon bookmark lying across the stack."
draw 04-долги.png "Scene: a heavy iron chain lying across the surface with one link glowing hot crimson-red, and a pair of bolt cutters resting next to it."
draw 05-поездка.png "Scene: an open vintage suitcase seen from above with a folded paper map and a passport inside, and one crimson-red luggage ribbon tied to the handle."
draw 06-договор.png "Scene: a formal paper contract lying flat with a crimson-red wax seal pressed on it, and a fountain pen resting beside the page."
draw 07-состав.png "Scene: a cosmetic dropper bottle standing on a stone block, a magnifying glass leaning against it, and a thin crimson-red laser line crossing the bottle label area."
echo "готово"
