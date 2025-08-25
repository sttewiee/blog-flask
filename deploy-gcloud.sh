#!/bin/bash

echo "🚀 Деплой через gcloud..."

# Аутентификация
gcloud auth activate-service-account --key-file=key.json
gcloud config set project sonic-harbor-465608-v1

# Создание кластера
echo "📦 Создание кластера..."
gcloud container clusters create blog-cluster \
  --region=europe-west4 \
  --num-nodes=1 \
  --machine-type=e2-micro \
  --disk-size=20 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=2 \
  --quiet

# Получение credentials
echo "🔑 Получение credentials..."
gcloud container clusters get-credentials blog-cluster --region=europe-west4

# Создание namespace через gcloud
echo "📋 Создание namespace..."
gcloud container clusters get-credentials blog-cluster --region=europe-west4
kubectl create namespace blog-dev --dry-run=client -o yaml | kubectl apply -f - --validate=false

# Деплой через gcloud
echo "🗄️ Деплой PostgreSQL..."
kubectl apply -f k8s/postgres.yaml --validate=false

echo "📱 Деплой приложения..."
kubectl apply -f k8s/deployment.yaml --validate=false

echo "🌐 Деплой сервиса..."
kubectl apply -f k8s/service.yaml --validate=false

echo "✅ Деплой завершен!"
echo "🌐 Получение внешнего IP..."
kubectl get service flask-blog-service -n blog-dev --validate=false
