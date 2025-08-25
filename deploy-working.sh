#!/bin/bash

echo "🚀 Деплой рабочего образа в продакшен"

# 1. Создаем рабочий образ
echo "📦 Создание рабочего образа..."
docker build -t blog-flask-working .

# 2. Тестируем образ
echo "🧪 Тестирование образа..."
docker run --rm -d -p 5001:5000 -e DATABASE_URL=sqlite:///:memory: -e SECRET_KEY=test --name test-container blog-flask-working python run.py
sleep 5

# Проверяем регистрацию
if curl -s -X POST -d "username=testuser&password=testpass" http://localhost:5001/register | grep -q "Redirecting"; then
    echo "✅ Образ работает корректно!"
else
    echo "❌ Образ не работает!"
    docker stop test-container
    exit 1
fi

docker stop test-container

# 3. Помечаем образ для продакшена
echo "🏷️  Помечаем образ для продакшена..."
docker tag blog-flask-working us-docker.pkg.dev/sonic-harbor-465608-v1/flask-blog/flask-blog:working-version

echo "✅ Рабочий образ готов!"
echo "📋 Следующие шаги:"
echo "1. Аутентифицируйтесь в Google Cloud: gcloud auth login"
echo "2. Отправьте образ: docker push us-docker.pkg.dev/sonic-harbor-465608-v1/flask-blog/flask-blog:working-version"
echo "3. Обновите deployment: kubectl set image deployment/flask-blog flask-blog=us-docker.pkg.dev/sonic-harbor-465608-v1/flask-blog/flask-blog:working-version -n blog-dev"
