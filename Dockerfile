FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директорий
RUN mkdir -p frontend/static/css frontend/static/js frontend/templates

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8000

# Команда запуска (только веб-сервер, бот запускается отдельно)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
