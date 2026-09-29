#!/usr/bin/env bash
# Свести ролик со звуком: tools/mix.sh <видео.mp4> <звуки.wav> <музыка.m4a> <итог.mp4> [с по]
# Видео берётся как есть, без пересчёта кадров. Звуки — отдельный рендер Remotion
# (`remotion render … out/sfx.wav`, около 10 секунд). Музыка приглушается на отрезке
# «с … по» в секундах: там, где должен быть слышен набор на клавиатуре.
set -euo pipefail

video="$1"; sfx="$2"; music="$3"; out="$4"
from="${5:-0}"; to="${6:-0}"

if [ "$to" = "0" ]; then
  duck="volume=0.92"
else
  # плавно вниз за 0,25 с до начала отрезка и плавно вверх за 0,35 с после него
  duck="volume='0.92-0.34*min(1,max(0,(t-($from-0.25))/0.25))+0.34*min(1,max(0,(t-$to)/0.35))':eval=frame"
fi

ffmpeg -v error -y -i "$video" -i "$music" -i "$sfx" \
  -filter_complex "[1:a]${duck}[m];[2:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=disabled[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 15 -movflags +faststart "$out"

ffmpeg -v info -i "$out" -af volumedetect -vn -f null - 2>&1 | grep -E "max_volume" | sed "s|.*max_volume|$(basename "$out"): пик|"
