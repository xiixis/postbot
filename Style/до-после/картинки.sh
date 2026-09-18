#!/bin/zsh
# Картинки поста «до-после» по одной: рисует Gemini, кадры референса идут опорой.
# Запуск: nohup ./картинки.sh > картинки.log 2>&1 &
set -u
cd "${0:A:h}"
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
К=картинки; О=опоры

рисуй () {  # файл форма описание [опоры...]
  local файл=$1 форма=$2 описание=$3; shift 3
  if [[ -s "$К/$файл" ]]; then echo "уже есть: $файл"; return; fi
  local оп=(); for о in "$@"; do оп+=(--опора "$о"); done
  # Vertex отдаёт 429 после нескольких картинок подряд: ждём и пробуем снова, до пяти раз.
  for попытка in 1 2 3 4 5; do
    echo "рисую: $файл (попытка $попытка)"
    if $П $Р "$К/$файл" "$описание" --форма $форма --размер 2K --буквы "${оп[@]}"; then
      sleep 20; return
    fi
    sleep $((60 * попытка))
  done
  echo "не вышло: $файл"
}

ДО="Clean e-commerce packshot photo, product centred on a pure white seamless background, soft even studio light, gentle contact shadow, nothing else in the frame. Recreate the same product as in the reference image, with its real label text exactly as on the reference."
рисуй до-1.png 1:1 "$ДО Product: Bleu de Chanel eau de parfum bottle, deep navy blue square glass bottle with black cap." $О/до-1.jpg
рисуй до-2.png 1:1 "$ДО Product: orange iPhone 17 Pro seen from the back, triple camera plateau, Apple logo." $О/до-2.jpg
рисуй до-3.png 1:1 "$ДО Product: KitKat 4-finger chocolate bar in its red wrapper with the white KitKat logo, lying flat." $О/до-3.jpg
рисуй до-4.png 1:1 "$ДО Product: Coco Noir Chanel eau de parfum, black glass bottle with gold-framed label, with a faint mirror reflection below." $О/до-4.jpg
рисуй до-5.png 1:1 "Realistic photo: a white wireless gaming mouse on a dark grey desk mousepad with a thin glowing cyan-white LED edge, dim moody desk light, three-quarter top view. Recreate the reference." $О/до-5.jpg

ПОСЛЕ="Photorealistic premium advertising product photo. Keep the product from the first image exactly the same: shape, colour, label text and logo unchanged. Match the composition, light and mood of the second reference image as closely as possible."
рисуй после-1.png 1:1 "$ПОСЛЕ Task: place the product in a scene with realistic beams of sunlight, warm highlights, natural shadows, and a premium atmospheric look. Bottle on a dark wet stone, cut lemons and lavender around, sunbeams through leaves behind." $К/до-1.png $О/после-1.jpg
рисуй после-2.png 3:2 "$ПОСЛЕ Task: take the uploaded product and place it in a realistic showroom or store display designed to attract customers. The phone stands on an illuminated acrylic stand in a bright Apple Store, glowing glass sign beside it." $К/до-2.png $О/после-2.jpg
рисуй после-3.png 4:3 "$ПОСЛЕ Task: make the product appear to float or fly in the scene, rather than simply sitting on a surface. The bar hangs tilted in mid-air, broken wafer fingers and chocolate crumbs fly around, warm blurred red background." $К/до-3.png $О/после-3.jpg
рисуй после-4.png 1:1 "$ПОСЛЕ Task: keep the main product prominent and surround it with realistic water effects to create a fresh, refreshing, premium look. Water splash crown around the base, droplets on the glass, dark background with golden bokeh and a white flower." $К/до-4.png $О/после-4.jpg
рисуй после-5.png 1:1 "$ПОСЛЕ Task: the main object should generally stay intact while the background is creatively replaced. The mouse on a dark desk, a potted plant, warm lamp glow, a monitor and a keyboard with purple backlight behind, blurred." $К/до-5.png $О/после-5.jpg

рисуй обложка.png 3:4 "Recreate the reference image as a clean photo WITHOUT any text, letters, logos or watermarks except the icon on the tile: a wooden mid-century armchair standing on top of a green grassy hill with small white daisies, deep clear blue sky with a few soft white clouds low at the sides. On the chair seat rests a dark charcoal rounded square tile with the white ChatGPT knot logo. The upper 45% of the frame is empty sky." $О/обложка.jpg
echo "готово"
