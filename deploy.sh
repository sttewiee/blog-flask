#!/bin/bash

# Простой деплой в GCP
PROJECT_ID=${1:-"sonic-harbor-465608-v1"}
REGION=${2:-"europe-west4"}
CLUSTER_NAME=${3:-"blog-cluster"}

echo "🚀 Деплой в GCP..."

# 1. Создаем кластер (если не существует)
echo "📦 Создание кластера..."
gcloud container clusters create $CLUSTER_NAME \
  --region=$REGION \
  --num-nodes=1 \
  --machine-type=e2-micro \
  --disk-size=15 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=2

# 2. Получаем credentials
echo "🔑 Получение credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# 3. Деплоим приложение
echo "📋 Деплой приложения..."
kubectl apply -f k8s/namespace.yaml --validate=false
kubectl apply -f k8s/postgres.yaml --validate=false
kubectl apply -f k8s/deployment.yaml --validate=false
kubectl apply -f k8s/service.yaml --validate=false

# 4. Ждем готовности
echo "⏳ Ожидание готовности..."
kubectl rollout status deployment/flask-blog -n blog-dev --validate=false

# 5. Получаем внешний IP
echo "🌐 Получение внешнего IP..."
kubectl get service flask-blog-service -n blog-dev --validate=false

echo "✅ Деплой завершен!"
