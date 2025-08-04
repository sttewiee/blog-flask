FROM python:3.11-slim

# Рабочая директория в контейнере
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего исходного кода
COPY . .

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Открытие порта (если нужно для локальных запусков)
EXPOSE 5000

# Команда запуска: сначала применяет миграции, потом запускает приложение
CMD ["sh", "-c", "flask db upgrade && python run.py"]
