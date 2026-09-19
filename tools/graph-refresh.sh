#!/bin/sh
# Догоняет граф Graphify после правок кода. Вызывается хуком PostToolUse
# фоном, поэтому обязан быть дешёвым и не мешать работе.
#
# Сам пересбор занимает около двенадцати секунд, и запускать его на КАЖДУЮ
# правку файла незачем: в одном подходе их бывает десятки. Поэтому здесь два
# ограничителя — замок (одновременно идёт не больше одной пересборки) и
# выдержка (не чаще раза в три минуты). Между ними граф отстаёт максимум на
# несколько правок, а машина не занята постоянным пересчётом.
#
# Имена переменных латиницей нарочно: /bin/sh не принимает кириллицу в
# идентификаторах и падает на первой же строке.
set -e

# Корень — по расположению самого скрипта (tools/ на один уровень ниже),
# а не жёстко зашитый путь: у каждого, кто клонирует репозиторий, он свой.
DEFAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="${GRAPH_ROOT:-$DEFAULT_ROOT}"
PY="${GRAPHIFY_PYTHON:-$HOME/.graphify-venv/bin/python}"
GRAPH="$ROOT/graphify-out/graph.json"
LOCK="$ROOT/graphify-out/.refreshing"
COOLDOWN=180

[ -x "$PY" ] || exit 0
[ -f "$GRAPH" ] || exit 0

# mtime в секундах. У BSD и GNU stat разные ключи — пробуем оба.
mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null; }

now=$(date +%s)
graph_at=$(mtime "$GRAPH")
[ -n "$graph_at" ] || exit 0

# Замок протухает через десять минут: упавшая пересборка не должна запереть
# обновление навсегда.
if [ -f "$LOCK" ]; then
  lock_at=$(mtime "$LOCK")
  [ -n "$lock_at" ] && [ $((now - lock_at)) -lt 600 ] && exit 0
  rm -f "$LOCK"
fi

# Свежий граф трогать незачем.
[ $((now - graph_at)) -lt "$COOLDOWN" ] && exit 0

# Есть ли что пересобирать: хоть один исходник новее графа.
changed=$(find "$ROOT" \
  \( -name .venv -o -name node_modules -o -name graphify-out -o -name .git -o -name __pycache__ \) -prune -o \
  \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) \
  -newer "$GRAPH" -print 2>/dev/null | head -1)
[ -n "$changed" ] || exit 0

touch "$LOCK"
cd "$ROOT" && "$PY" tools/graph-update.py . >"$ROOT/graphify-out/.refresh.log" 2>&1 || true
rm -f "$LOCK"
