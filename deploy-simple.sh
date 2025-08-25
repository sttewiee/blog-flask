#!/bin/bash

echo "🚀 Простой деплой в GCP..."

# Аутентификация
gcloud auth activate-service-account --key-file=key.json
gcloud config set project sonic-harbor-465608-v1

# Создание кластера с минимальными ресурсами
echo "📦 Создание кластера..."
gcloud container clusters create blog-cluster \
  --region=europe-west4 \
  --num-nodes=1 \
  --machine-type=e2-micro \
  --disk-size=20 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=2 \
  --enable-legacy-authorization \
  --quiet

# Получение credentials
echo "🔑 Получение credentials..."
gcloud container clusters get-credentials blog-cluster --region=europe-west4

# Создание namespace
echo "📋 Создание namespace..."
kubectl create namespace blog-dev --dry-run=client -o yaml | kubectl apply -f -

# Деплой PostgreSQL
echo "🗄️ Деплой PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

# Деплой приложения
echo "📱 Деплой приложения..."
kubectl apply -f k8s/deployment.yaml

# Деплой сервиса
echo "🌐 Деплой сервиса..."
kubectl apply -f k8s/service.yaml

echo "✅ Деплой завершен!"
echo "🌐 Получение внешнего IP..."
kubectl get service flask-blog-service -n blog-dev
