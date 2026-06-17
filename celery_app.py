import os
from celery import Celery

# Забираем адрес Redis из .env (по умолчанию ставим localhost для тестов вне Докера)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Инициализируем приложение Celery
app = Celery(
    "flat_hunter",
    broker=redis_url,
    backend=redis_url,
    include=["parser.tasks"]  # Указываем, в каком файле искать задачи
)

# Настраиваем планировщик
app.conf.beat_schedule = {
    "parse-yandex-every-5-minutes": {
        "task": "parser.tasks.parse_flats_task",
        "schedule": 600.0,  \
    },
}
app.conf.timezone = "UTC"