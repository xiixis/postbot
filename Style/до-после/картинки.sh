#!/usr/bin/env bash
# Картинки поста «до-после» по одной: рисует Gemini, кадры референса идут опорой.
# Запуск: nohup ./картинки.sh > картинки.log 2>&1 &
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
K=картинки; O=опоры

draw () {  # файл форма описание [опоры...]
  local file=$1 form=$2 desc=$3; shift 3
  if [[ -s "$K/$file" ]]; then echo "уже есть: $file"; return; fi
  local refs=(); for r in "$@"; do refs+=(--опора "$r"); done
  # Vertex отдаёт 429 после нескольких картинок подряд: ждём и пробуем снова, до пяти раз.
  for try_n in 1 2 3 4 5; do
    echo "рисую: $file (попытка $try_n)"
    if "$PY" "$R" "$K/$file" "$desc" --форма $form --размер 2K --буквы ${refs[@]+"${refs[@]}"}; then
      sleep 20; return
    fi
    sleep $((60 * try_n))
  done
  echo "не вышло: $file"
}

BEFORE="Clean e-commerce packshot photo, product centred on a pure white seamless background, soft even studio light, gentle contact shadow, nothing else in the frame. Recreate the same product as in the reference image, with its real label text exactly as on the reference."
draw до-1.png 1:1 "$BEFORE Product: Bleu de Chanel eau de parfum bottle, deep navy blue square glass bottle with black cap." $O/до-1.jpg
draw до-2.png 1:1 "$BEFORE Product: orange iPhone 17 Pro seen from the back, triple camera plateau, Apple logo." $O/до-2.jpg
draw до-3.png 1:1 "$BEFORE Product: KitKat 4-finger chocolate bar in its red wrapper with the white KitKat logo, lying flat." $O/до-3.jpg
draw до-4.png 1:1 "$BEFORE Product: Coco Noir Chanel eau de parfum, black glass bottle with gold-framed label, with a faint mirror reflection below." $O/до-4.jpg
draw до-5.png 1:1 "Realistic photo: a white wireless gaming mouse on a dark grey desk mousepad with a thin glowing cyan-white LED edge, dim moody desk light, three-quarter top view. Recreate the reference." $O/до-5.jpg

AFTER="Photorealistic premium advertising product photo. Keep the product from the first image exactly the same: shape, colour, label text and logo unchanged. Match the composition, light and mood of the second reference image as closely as possible."
draw после-1.png 1:1 "$AFTER Task: place the product in a scene with realistic beams of sunlight, warm highlights, natural shadows, and a premium atmospheric look. Bottle on a dark wet stone, cut lemons and lavender around, sunbeams through leaves behind." $K/до-1.png $O/после-1.jpg
draw после-2.png 3:2 "$AFTER Task: take the uploaded product and place it in a realistic showroom or store display designed to attract customers. The phone stands on an illuminated acrylic stand in a bright Apple Store, glowing glass sign beside it." $K/до-2.png $O/после-2.jpg
draw после-3.png 4:3 "$AFTER Task: make the product appear to float or fly in the scene, rather than simply sitting on a surface. The bar hangs tilted in mid-air, broken wafer fingers and chocolate crumbs fly around, warm blurred red background." $K/до-3.png $O/после-3.jpg
draw после-4.png 1:1 "$AFTER Task: keep the main product prominent and surround it with realistic water effects to create a fresh, refreshing, premium look. Water splash crown around the base, droplets on the glass, dark background with golden bokeh and a white flower." $K/до-4.png $O/после-4.jpg
draw после-5.png 1:1 "$AFTER Task: the main object should generally stay intact while the background is creatively replaced. The mouse on a dark desk, a potted plant, warm lamp glow, a monitor and a keyboard with purple backlight behind, blurred." $K/до-5.png $O/после-5.jpg

draw обложка.png 3:4 "Recreate the reference image as a clean photo WITHOUT any text, letters, logos or watermarks except the icon on the tile: a wooden mid-century armchair standing on top of a green grassy hill with small white daisies, deep clear blue sky with a few soft white clouds low at the sides. On the chair seat rests a dark charcoal rounded square tile with the white ChatGPT knot logo. The upper 45% of the frame is empty sky." $O/обложка.jpg
echo "готово"
