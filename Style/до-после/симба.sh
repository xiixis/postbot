#!/bin/zsh
# Обложка-4: кот на стуле поднимает плитку ChatGPT над головой, как Рафики Симбу.
set -u
cd "${0:A:h}"
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
for попытка in 1 2 3 4 5; do
  [[ -s картинки/обложка-симба.png ]] && break
  echo "рисую: обложка-симба (попытка $попытка)"
  $П $Р картинки/обложка-симба.png "Photorealistic premium 3D advertising photo, portrait. Recreate the scene of the first image exactly: a wooden mid-century armchair on top of a green grassy hill with small white daisies, deep clear blue sky, soft white clouds low at the sides. NEW: the black robot cat character from the second image — EXACTLY the same character: matte clay-like charcoal body, big glowing acid-lime eyes, lime panel lines, glowing lime tail tip, no antenna — stands proudly on the seat of the chair and lifts the dark charcoal rounded square tile with the white ChatGPT knot logo high above its head with both front paws stretched straight up, presenting it to the world like the famous heroic cliff-top presentation pose from a classic animated film. Warm golden sunbeams break through the sky and light the raised tile. The upper 38% of the frame is empty blue sky with nothing in it; the raised tile reaches no higher than 42% from the top. No other text or letters." --форма 3:4 --размер 2K --буквы --опора картинки/обложка.png --опора /Users/xiix/4xSoft/postbot/assets/mascot/reference.png && break
  sleep $((60 * попытка))
done
echo "готово"
