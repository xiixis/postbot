#!/bin/zsh
# Сцена финала: как обложка «сцена», но вместо флакона 3D-логотип Telegram и его цвет.
set -u
cd "${0:A:h}"
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
for попытка in 1 2 3 4 5; do
  [[ -s картинки/финал-телеграм.png ]] && break
  echo "рисую: финал-телеграм (попытка $попытка)"
  $П $Р картинки/финал-телеграм.png "Photorealistic premium 3D advertising photo, portrait. Use the composition, camera, depth of field and wet dark stone surface of the first image, but restyle the whole mood into Telegram brand colour: cool sky-blue and cyan light (#229ED9, #2AABEE), soft blue light rays from the upper left, blue-tinted bokeh, the leaves and lemons replaced by soft blurred blue glass shapes. Where the perfume bottle stood, there is a large glossy 3D Telegram logo — a sky-blue circle with a white paper plane — standing upright on the stone, slightly right of centre, with a real reflection on the wet stone. On the stone to the left of the logo sits the black robot cat character from the second image — EXACTLY the same character: matte clay-like charcoal body, big glowing acid-lime eyes, lime panel lines, glowing lime tail tip, no antenna — happily pointing up at the logo with one paw, lit by the blue light, with a real contact shadow. The upper 45% of the frame is empty soft blurred blue light background, nothing there." --форма 3:4 --размер 2K --опора картинки/сцена-с-котом.png --опора /Users/xiix/4xSoft/postbot/assets/mascot/reference.png && break
  sleep $((60 * попытка))
done
echo "готово"
