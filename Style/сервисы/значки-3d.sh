#!/bin/zsh
# Пушистые 3D-значки для поста «бесплатные нейросети» (рерайт @nik_kukuytsev, 17.09.2026).
# Запуск: nohup ./значки-3d.sh > значки-3d.log 2>&1 &
set -u
cd "${0:A:h}"
П=/Users/xiix/4xSoft/yt-searcher/.venv/bin/python3
Р=/Users/xiix/4xSoft/postbot/Style/картинка.py
К=значки/3d; О=опоры-3d
mkdir -p $К

рисуй () {  # файл описание опора
  local файл=$1 описание=$2 опора=$3
  if [[ -s "$К/$файл" ]]; then echo "уже есть: $файл"; return; fi
  # Vertex отдаёт 429 после нескольких картинок подряд: ждём и пробуем снова.
  for попытка in 1 2 3 4 5; do
    echo "рисую: $файл (попытка $попытка)"
    if $П $Р "$К/$файл" "$описание" --форма 1:1 --размер 2K --буквы --опора $опора; then
      sleep 20; return
    fi
    sleep $((60 * попытка))
  done
  echo "не вышло: $файл"
}

ФОН="Single object centred, occupying about 60% of the frame, on a perfectly flat uniform solid background of colour #ECEFF6 (very light grey-blue), no gradient, no vignette, no floor, only a very soft faint contact shadow directly below. Nothing else in the frame. Match the reference image's object, material and lighting as closely as possible."
МЕХ="A soft 3D plush icon made entirely of fluffy realistic fur, like a furry toy, studio product render, soft light from the top-left."
рисуй gemini.png "$ФОН $МЕХ The Google Gemini four-pointed sparkle star logo, fur coloured in the Gemini rainbow gradient: red, yellow, green and blue." $О/gemini.jpg
рисуй firefly.png "$ФОН $МЕХ The Adobe Firefly app icon: a rounded square of deep red fur with a bold white fur letter-shape A (the Adobe A, without the crossbar) in the middle." $О/firefly.jpg
рисуй leonardo.png "$ФОН A round embroidered patch icon, like a thick stitched textile badge: the Leonardo AI logo, a stylised bearded face of Leonardo da Vinci with long hair in colourful yellow, orange, blue and purple threads, thin constellation lines around, dark navy base." $О/leonardo.jpg
рисуй pixai.png "$ФОН $МЕХ The PixAI app icon: a slightly tilted rounded square of black fur with a bold chunky white fur letter P in the middle." $О/pixai.jpg
рисуй magnific.png "$ФОН $МЕХ The Magnific AI icon: a round disc of black fur with a white fur letter M shape in the middle and the white word Magnific below it." $О/magnific.jpg
рисуй деньги.png "$ФОН Glossy 3D cartoon render icon: a hand in a blue sleeve holding a stack of green dollar banknotes, crossed out by a big red prohibition sign (red ring with a diagonal bar). Smooth clay-like plastic material, not fur." $О/деньги.jpg
echo "готово"
