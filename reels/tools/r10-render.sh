#!/bin/sh
# Ролик «5 бесплатных плагинов» тремя способами подряд: sh tools/r10-render.sh
# По одному процессу за раз: на 16 ГБ два рендера разом не помещаются.
# Время каждого пишется в out/times.txt, итоги лежат в out/r10-*.mp4.
cd "$(dirname "$0")/.." || exit 1
export HYPERFRAMES_SKIP_SKILLS=1
HF="npx -y hyperframes@0.8.111"
REM="--props=out/props-sound.json --codec=h264 --crf=17 --pixel-format=yuv420p --concurrency=2"
mkdir -p out
echo '{"sound": true}' > out/props-sound.json
: > out/times.txt
rm -f out/render-done
t() { echo "$1: $(( $(date +%s) - $2 )) с" >> out/times.txt; }

node tools/hf-build.mjs r10-plugins && node tools/hf-build.mjs r10-plugins --scenes || exit 1

s=$(date +%s)
(cd hf/r10-plugins && $HF render --quality looks --fps 30 --output ../../out/r10-hyperframes.mp4) > out/hf-render.log 2>&1
t "HyperFrames" "$s"

s=$(date +%s)
npx remotion render src/index.ts Plugins out/r10-remotion.mp4 $REM > out/rem-render.log 2>&1
t "Remotion" "$s"

s=$(date +%s)
(cd hf/r10-plugins-scenes && $HF render --quality looks --fps 30 --output ../../public/plugins/hf-scenes.mp4) > out/hfs-render.log 2>&1
t "гибрид, сцены в HyperFrames" "$s"

s=$(date +%s)
npx remotion render src/index.ts PluginsHybrid out/r10-hybrid.mp4 $REM > out/hyb-render.log 2>&1
t "гибрид, сборка в Remotion" "$s"

echo done > out/render-done
