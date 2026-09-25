#!/usr/bin/env bash
# Коты и сцена с котом по одной, с повтором на 429.
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
retry () {
  for try_n in 1 2 3 4 5; do
    if "$@"; then sleep 20; return; fi
    sleep $((60 * try_n))
  done
  echo "не вышло: $*"
}
[[ -s коты/над-краем.png ]] || retry "$PY" кот.py над-краем
[[ -s коты/с-телефоном.png ]] || retry "$PY" кот.py с-телефоном
[[ -s картинки/сцена-с-котом.png ]] || retry "$PY" "$R" картинки/сцена-с-котом.png "Photorealistic premium advertising photo, portrait. Recreate the scene of the second image: dark wet stone, cut lemons, lavender, warm sunbeams through leaves, the Bleu de Chanel bottle with its exact label. Composition: the upper 45% of the frame is empty soft blurred warm golden background with light rays, nothing there. The bottle stands in the lower half, slightly right of centre. On the stone to the left of the bottle sits the black robot cat character from the first image — EXACTLY the same character: matte clay-like charcoal body, big glowing acid-lime eyes, lime panel lines, glowing lime tail tip, no antenna — looking up at the bottle in amazement with its paws near its cheeks, lit by the same warm sunbeams, with a real contact shadow on the stone." --форма 3:4 --размер 2K --буквы --опора "$POSTBOT/assets/mascot/reference.png" --опора картинки/после-1.png
echo "готово"
