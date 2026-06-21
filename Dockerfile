# Делаем стадию build для MultiStage
FROM python:3.11-slim as builder

# Настраиваем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Используем BuildKit для кэширования загрузок(--mount=type=cache - неявный указатель на то что нужен buildkit)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Вторая стадия - runner
FROM python:3.11-slim as runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Создаём непревилегированного пользователя
RUN addgroup --system appuser && adduser --system --group appuser

# Копируем готовые зависимости из этапа builder
COPY --from=builder /opt/venv /opt/venv

# Копируем код проекта
COPY . .

# Передаем права пользователю appuser на папку проекта
RUN chown -R appuser:appuser /app

# Переключаемся на безопасного пользователя
USER appuser

CMD ["python", "parser/main.py"]

