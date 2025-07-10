#!/bin/sh
set -e

# 1. Ждем, пока база данных станет доступной
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL started"

# 2. Применяем миграции базы данных
echo "Applying database migrations..."
flask db upgrade

# 3. Запускаем Gunicorn
exec gunicorn wsgi:app -b 0.0.0.0:5000