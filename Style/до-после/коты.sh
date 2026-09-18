#!/bin/zsh
# Коты и сцена с котом по одной, с повтором на 429.
set -u
cd "${0:A:h}"
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
повтор () {
  for попытка in 1 2 3 4 5; do
    if "$@"; then sleep 20; return; fi
    sleep $((60 * попытка))
  done
  echo "не вышло: $*"
}
[[ -s коты/над-краем.png ]] || повтор $П кот.py над-краем
[[ -s коты/с-телефоном.png ]] || повтор $П кот.py с-телефоном
[[ -s картинки/сцена-с-котом.png ]] || повтор $П $Р картинки/сцена-с-котом.png "Photorealistic premium advertising photo, portrait. Recreate the scene of the second image: dark wet stone, cut lemons, lavender, warm sunbeams through leaves, the Bleu de Chanel bottle with its exact label. Composition: the upper 45% of the frame is empty soft blurred warm golden background with light rays, nothing there. The bottle stands in the lower half, slightly right of centre. On the stone to the left of the bottle sits the black robot cat character from the first image — EXACTLY the same character: matte clay-like charcoal body, big glowing acid-lime eyes, lime panel lines, glowing lime tail tip, no antenna — looking up at the bottle in amazement with its paws near its cheeks, lit by the same warm sunbeams, with a real contact shadow on the stone." --форма 3:4 --размер 2K --буквы --опора /Users/xiix/4xSoft/postbot/assets/mascot/reference.png --опора картинки/после-1.png
echo "готово"
