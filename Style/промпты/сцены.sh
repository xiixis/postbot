#!/bin/zsh
# Сцены кадров стиля «промпты» — по одной за раз: две отрисовки разом машина не тянет.
# Запуск: nohup ./сцены.sh > /tmp/сцены.log 2>&1 &
set -u
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
К=/Users/xiix/4xSoft/postbot/Style/промпты/картинки

ОБЩЕЕ="Photorealistic editorial 3D product still life. Warm cream paper background (#EAE4DE) filling the whole frame. The whole scene is almost monochrome, desaturated to warm greys and beiges, EXCEPT one single crimson-red object that is the only colour in the picture. Soft daylight from the upper left, gentle long shadows, premium advertising render, shallow depth of field. The top 45% of the frame is empty cream background with nothing in it, the objects sit in the lower half."

рисуй () {
  if [[ -s "$К/$1" ]]; then echo "уже есть: $1"; return; fi
  echo "рисую: $1"
  $П $Р "$К/$1" "$ОБЩЕЕ $2" --форма 4:5 --размер 2K || echo "не вышло: $1"
}

рисуй 01-конкурент.png "Scene: two open paper folders lying side by side on a desk, a few chess pieces standing on them, and a single thin crimson-red thread stretched between the two folders like a connection line."
рисуй 02-цена.png "Scene: one matte black sneaker standing on the cream surface, a smartphone lying flat beside it, and a thin crimson-red laser line sweeping across the sneaker."
рисуй 03-резюме.png "Scene: an old typewriter with a sheet of paper in it, a neat stack of documents beside it, and a single crimson-red ribbon bookmark lying across the stack."
рисуй 04-долги.png "Scene: a heavy iron chain lying across the surface with one link glowing hot crimson-red, and a pair of bolt cutters resting next to it."
рисуй 05-поездка.png "Scene: an open vintage suitcase seen from above with a folded paper map and a passport inside, and one crimson-red luggage ribbon tied to the handle."
рисуй 06-договор.png "Scene: a formal paper contract lying flat with a crimson-red wax seal pressed on it, and a fountain pen resting beside the page."
рисуй 07-состав.png "Scene: a cosmetic dropper bottle standing on a stone block, a magnifying glass leaning against it, and a thin crimson-red laser line crossing the bottle label area."
echo "готово"
