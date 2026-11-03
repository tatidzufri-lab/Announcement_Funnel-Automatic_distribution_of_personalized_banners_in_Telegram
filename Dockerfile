FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CHROME_BIN=/usr/bin/chromium

# Chromium рендерит HTML-шаблоны в PNG (html2image).
# Шрифты с кириллицей обязательны: шаблоны тянут Google Fonts из сети,
# но при недоступности CDN нужен локальный запасной набор, иначе текст станет квадратами.
#
# fonts-noto-color-emoji нужен отдельно: обычные наборы эмодзи не содержат,
# а шаблоны ими пользуются (росток, алмаз, щит и прочие). Без него такие
# символы выходят пустыми квадратами — на Mac шрифт есть в системе, поэтому
# локально дефект незаметен.
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        fonts-liberation \
        fonts-dejavu-core \
        fonts-noto-core \
        fonts-noto-color-emoji \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py utils.py bot_funnel.py test_basic.py ./
COPY templates/ ./templates/
COPY profiles/ ./profiles/
COPY assets/ ./assets/

# UID должен совпадать с владельцем примонтированного ./output на хосте,
# иначе контейнер не сможет сохранить сгенерированные баннеры. На сервере это 1000.
ARG APP_UID=1000
RUN useradd --create-home --uid ${APP_UID} app \
    && mkdir -p /app/output \
    && chown -R app:app /app
USER app

# Безопасное поведение по умолчанию: только генерация PNG, без рассылки.
# Реальная отправка — явной командой с флагом --send.
CMD ["python3", "bot_funnel.py", "--test", "--brand", "wellness"]
