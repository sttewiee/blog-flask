#!/bin/bash

echo "🧪 Тестирование подключения к GCP..."

# Проверяем наличие key.json
if [ ! -f "key.json" ]; then
    echo "❌ Файл key.json не найден!"
    exit 1
fi

# Аутентификация в GCP
echo "🔑 Аутентификация в GCP..."
gcloud auth activate-service-account --key-file=key.json

# Проверяем проект
echo "📋 Проверка проекта..."
gcloud config set project sonic-harbor-465608-v1

# Проверяем доступ к GKE
echo "🐳 Проверка доступа к GKE..."
gcloud container clusters list --region=europe-west4

echo "✅ Подключение к GCP успешно!"
