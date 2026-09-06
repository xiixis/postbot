#!/usr/bin/env bash
# Поднимает бота на чистой машине с Ubuntu или Debian.
#
#   sudo bash deploy/установка.sh
#
# Ставит docker, собирает образ, поднимает бота вместе с Caddy. Дальше машина
# сама переживает перезагрузки: контейнеры помечены restart: always.
set -euo pipefail

корень="$(cd "$(dirname "$0")/.." && pwd)"
cd "$корень"

if [ ! -f .env ]; then
	echo "Нет файла .env. Скопируйте .env.example, заполните и повторите."
	exit 1
fi

echo "== пакеты =="
apt-get update -qq
apt-get install -y -qq ca-certificates curl ufw

if ! command -v docker >/dev/null; then
	echo "== docker =="
	curl -fsSL https://get.docker.com | sh
fi

echo "== порты =="
# Наружу нужны только 80 и 443: сам бот слушает внутри сети docker,
# и выставлять его порт в интернет незачем.
ufw allow OpenSSH >/dev/null 2>&1 || true
ufw allow 80/tcp  >/dev/null 2>&1 || true
ufw allow 443/tcp >/dev/null 2>&1 || true
ufw --force enable >/dev/null 2>&1 || true

echo "== сборка и запуск =="
docker compose up -d --build

echo
echo "Готово. Что дальше:"
echo "  логи:        docker compose logs -f bot"
echo "  перезапуск:  docker compose restart bot"
echo "  обновление:  git pull && docker compose up -d --build"
