# Образ бота. Кроме питона внутри нужен браузер: карточки постов рисуются
# вёрсткой и снимаются безголовым Chromium, без него посты уйдут без картинок.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        fonts-noto-core \
        fonts-noto-color-emoji \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Шрифты карточки тянутся из Google Fonts при отрисовке, а вот эмодзи берутся
# системные: без fonts-noto-color-emoji вместо них были бы пустые квадраты.

ENV CHROME_PATH=/usr/bin/chromium \
    POSTBOT_DATA=/data \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Том для карточек и, если Supabase не подключён, для файловой базы
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8137
CMD ["python", "bot.py"]
