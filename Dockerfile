# 1. Используем официальный образ Python
FROM python:3.11-slim

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем зависимости
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем всё приложение
COPY . .

# 6. Экспортируем порт (по умолчанию Flask — 5000)
EXPOSE 5000

# 7. Указываем переменные окружения для Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# 8. Запуск приложения
CMD ["flask", "run"]
