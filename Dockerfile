# Образ бота. Контейнер — это ВМЕСТО мака, а не рядом с ним: бот живёт на одной
# машине за раз (хозяин.py), см. README, раздел «Сервер в контейнере».
#
# Кроме питона внутри нужны:
#   • Claude Code (Node.js + npm) — им бот сочиняет; без него config.проверить()
#     возвращает беду и бот выходит с кодом 1, контейнер крутится в перезапусках;
#   • Chromium — карточки и кадры рисуются вёрсткой и снимаются безголовым браузером;
#   • шрифты с кириллицей и эмодзи — фирменные лежат в assets/fonts, но всё, чего
#     в них нет (эмодзи, редкие знаки), браузер берёт из системы;
#   • tzdata — расписание идёт по POSTBOT_TZ.
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        fonts-noto-core \
        fonts-noto-color-emoji \
        fonts-dejavu-core \
        tzdata \
        tini \
        ca-certificates \
        curl \
        gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && npm cache clean --force \
    && rm -rf /var/lib/apt/lists/*

# POSTBOT_DATA — том: база (если не Supabase), карточки, сессия аккаунта Telegram.
# CLAUDE_CONFIG_DIR — вход Claude Code тоже в томе: /login переживает обновление образа.
# HF_HOME — модель whisper для голосовых заметок качается один раз, в том же томе.
# DISABLE_AUTOUPDATER — Claude Code не обновляет сам себя внутри образа: версию
# меняет пересборка.
ENV CHROME_PATH=/usr/bin/chromium \
    POSTBOT_DATA=/data \
    CLAUDE_CONFIG_DIR=/data/claude \
    HF_HOME=/data/hf \
    DISABLE_AUTOUPDATER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Сессия аккаунта Telegram (userbot.py ищет её в deploy/ключи) живёт в томе, а не
# в образе: .dockerignore её не пускает, а папка становится ссылкой в /data.
RUN rm -rf deploy/ключи && ln -s /data/ключи deploy/ключи && mkdir -p /data
VOLUME ["/data"]

EXPOSE 8137
# tini — первым процессом: собирает осиротевшие процессы Chromium и Claude Code
# и передаёт боту SIGTERM, на который он штатно снимает отметку хозяина.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "mkdir -p \"$POSTBOT_DATA/ключи\" \"$CLAUDE_CONFIG_DIR\" \"$HF_HOME\" && exec python -u bot.py"]
