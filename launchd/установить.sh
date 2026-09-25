#!/usr/bin/env bash
# Автозапуск бота на маке через launchd.
#
#   bash launchd/установить.sh          поставить (или переставить после правки шаблона)
#   bash launchd/установить.sh снять    остановить службу и убрать её
#
# Шаблон com.4xtube.postbot.plist лежит рядом: в нём __ROOT__ (папка 4xSoft) и
# __HOME__, которые подставляются здесь по месту этого скрипта и $HOME — у
# другой машины и другого пользователя пути свои.
#
# Бот живёт на одной машине за раз (хозяин.py): если он уже запущен руками,
# сперва погасите его, иначе служба будет раз в минуту упираться во второго.
set -euo pipefail

[ "$(uname -s)" = Darwin ] || { echo "launchd есть только на маке" >&2; exit 1; }

LABEL=com.4xtube.postbot
HERE="$(cd "$(dirname "$0")" && pwd)"
POSTBOT="$(dirname "$HERE")"
ROOT="$(dirname "$POSTBOT")"
PY="$ROOT/yt-searcher/.venv/bin/python3"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

if [ "${1:-}" = снять ]; then
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$DEST"
  echo "служба снята; бот остановлен"
  exit 0
fi

[ -x "$PY" ] || { echo "нет $PY — сперва заведите окружение yt-searcher/.venv" >&2; exit 1; }
"$PY" -c "import dotenv, telethon" 2>/dev/null \
  || { echo "в $PY нет зависимостей постбота: $PY -m pip install -r $POSTBOT/requirements.txt" >&2; exit 1; }

# Своя служба, если уже стоит, снимается: переустановка = перезапуск бота.
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
sleep 2
if pgrep -f '[ /]bot\.py( |$)' >/dev/null; then
  echo "бот уже запущен руками (PID: $(pgrep -f '[ /]bot\.py( |$)' | tr '\n' ' '))." >&2
  echo "Погасите его (kill <PID>) и повторите: два бота разом не живут." >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$POSTBOT/data"
# Подстановка питоном, а не sed: пути экранируются для XML, и знаки & | в них ничего не ломают.
"$PY" - "$HERE/$LABEL.plist" "$DEST" "$ROOT" "$HOME" <<'EOF'
import sys
from xml.sax.saxutils import escape
шаблон, куда, корень, дом = sys.argv[1:]
текст = open(шаблон, encoding="utf-8").read()
текст = текст.replace("__ROOT__", escape(корень)).replace("__HOME__", escape(дом))
open(куда, "w", encoding="utf-8").write(текст)
EOF
plutil -lint "$DEST" >/dev/null
launchctl bootstrap "$DOMAIN" "$DEST"

echo "поставлено: $DEST"
echo "питон:  $PY"
echo "папка:  $POSTBOT"
echo "логи:   tail -f \"$POSTBOT/data/бот.log\""
echo "снять:  bash \"$HERE/установить.sh\" снять"
