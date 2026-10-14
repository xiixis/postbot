#!/bin/sh
# Собрать, проверить и отрендерить ролик на HyperFrames: sh tools/hf-render.sh <ролик>
# Проверка идёт до рендера: с ошибками рендер не запускается. Время рендера пишется в
# out/<ролик>-time.txt, итог в out/<ролик>.mp4.
cd "$(dirname "$0")/.." || exit 1
R="$1"
[ -n "$R" ] || { echo "нужно имя ролика, например r11-plugins"; exit 2; }
export HYPERFRAMES_SKIP_SKILLS=1
HF="npx -y hyperframes@0.8.111"
mkdir -p out
node tools/hf-build.mjs "$R" || exit 1
cd "hf/$R" || exit 1
$HF check > "../../out/$R-check.log" 2>&1
grep -E "error\(s\)|Check " "../../out/$R-check.log"
grep -q "Check passed" "../../out/$R-check.log" || { grep "✗" "../../out/$R-check.log" | cut -c1-240; exit 1; }
s=$(date +%s)
$HF render --quality looks --fps 30 --output "../../out/$R.mp4" > "../../out/$R-render.log" 2>&1
echo "$(( $(date +%s) - s ))" > "../../out/$R-time.txt"
tail -3 "../../out/$R-render.log" | cut -c1-220
echo "рендер $R: $(cat "../../out/$R-time.txt") с"
