#!/bin/bash
set -e

echo "🧪 Запуск тестов в Docker контейнере..."

# Проверяем, что контейнер запущен
if ! docker compose ps | grep -q "blog-flask-web-1.*Up"; then
    echo "❌ Контейнер web не запущен. Запускаем..."
    docker compose up -d
    echo "⏳ Ожидание готовности контейнера..."
    sleep 10
fi

# Запускаем тесты с SQLite в памяти (не влияет на основную БД)
echo "🚀 Запуск тестов с SQLite в памяти..."
docker exec -e DATABASE_URL="sqlite:///:memory:" -e SECRET_KEY="test_secret_key" -e FLASK_ENV="testing" blog-flask-web-1 python -m pytest -v --cov=app --cov-report=term-missing

echo "✅ Тесты завершены!"
echo "💡 Тесты использовали SQLite в памяти и не повлияли на основную PostgreSQL базу"
