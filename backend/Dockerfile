# Используем официальный минимальный Python-образ
FROM python:3.11-slim

# Переменная для невзаимодействующего режима (для prod)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . .

# Открываем порт
EXPOSE 8080

# Стартуем Gunicorn (продакшн-сервер для Flask)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
