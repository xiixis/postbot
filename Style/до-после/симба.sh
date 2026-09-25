#!/usr/bin/env bash
# Обложка-4: кот на стуле поднимает плитку ChatGPT над головой, как Рафики Симбу.
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
for try_n in 1 2 3 4 5; do
  [[ -s картинки/обложка-симба.png ]] && break
  echo "рисую: обложка-симба (попытка $try_n)"
  "$PY" "$R" картинки/обложка-симба.png "Photorealistic premium 3D advertising photo, portrait. Recreate the scene of the first image exactly: a wooden mid-century armchair on top of a green grassy hill with small white daisies, deep clear blue sky, soft white clouds low at the sides. NEW: the black robot cat character from the second image — EXACTLY the same character: matte clay-like charcoal body, big glowing acid-lime eyes, lime panel lines, glowing lime tail tip, no antenna — stands proudly on the seat of the chair and lifts the dark charcoal rounded square tile with the white ChatGPT knot logo high above its head with both front paws stretched straight up, presenting it to the world like the famous heroic cliff-top presentation pose from a classic animated film. Warm golden sunbeams break through the sky and light the raised tile. The upper 38% of the frame is empty blue sky with nothing in it; the raised tile reaches no higher than 42% from the top. No other text or letters." --форма 3:4 --размер 2K --буквы --опора картинки/обложка.png --опора "$POSTBOT/assets/mascot/reference.png" && break
  sleep $((60 * try_n))
done
echo "готово"
