#!/bin/bash

set -e

# 1. Установим переменные
PROJECT_ID="sonic-harbor-465608-v1"
REGION="europe-west4"
REPO="flask-blog"
INSTANCE="blog-db"
NAMESPACE="blog-dev"
IMAGE="us-docker.pkg.dev/$PROJECT_ID/$REPO/flask-blog:latest"

echo "✅ Сборка Docker-образа..."
docker build -t $IMAGE .

echo "📤 Пуш в Artifact Registry..."
docker push $IMAGE

echo "🗝️ Обновление Docker-секрета в Kubernetes..."
kubectl delete secret regcred -n $NAMESPACE --ignore-not-found
kubectl create secret docker-registry regcred \
  --docker-server=us-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password="$(< credentials.json)" \
  --docker-email=any@example.com \
  -n $NAMESPACE

echo "🚀 Деплой в Kubernetes..."
kubectl apply -f k8s/flask-blog-deployment.yaml -n $NAMESPACE
kubectl apply -f k8s/flask-blog-service.yaml -n $NAMESPACE

echo "♻️ Перезапуск приложения..."
kubectl rollout restart deployment flask-blog -n $NAMESPACE

echo "✅ Готово! Проверь ingress и доступность по адресу."
