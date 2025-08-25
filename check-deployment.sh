#!/bin/bash

echo "🔍 Проверка статуса деплоя Flask Blog"
echo "======================================"

PROJECT_ID="sonic-harbor-465608-v1"
REGION="europe-west4"
CLUSTER_NAME="blog-cluster"

echo "📊 Статус кластера:"
gcloud container clusters describe $CLUSTER_NAME --region=$REGION --format="table(
    name,
    status,
    currentNodeCount,
    currentMasterVersion
)" 2>/dev/null || echo "❌ Ошибка получения статуса кластера"

echo ""
echo "🖥️ Ноды кластера:"
gcloud compute instances list --filter="name:gke-$CLUSTER_NAME*" --format="table(
    name,
    zone,
    machineType,
    status,
    externalIP
)" 2>/dev/null || echo "❌ Ошибка получения списка нод"

echo ""
echo "🌐 LoadBalancer статус:"
gcloud compute forwarding-rules list --format="table(
    name,
    IPAddress,
    target
)" 2>/dev/null

echo ""
echo "📦 Docker образы в Artifact Registry:"
gcloud artifacts docker images list europe-west4-docker.pkg.dev/$PROJECT_ID/blog-flask/blog-flask --limit=3 --format="table(
    package,
    version,
    createTime
)" 2>/dev/null || echo "❌ Ошибка получения списка образов"

echo ""
echo "🎯 Возможные способы доступа к приложению:"
echo "1. Через LoadBalancer IP (может занять несколько минут)"
echo "2. Через kubectl port-forward (для тестирования)"
echo "3. Через Ingress (если настроен)"

echo ""
echo "📝 Команды для проверки:"
echo "kubectl get services -n blog-dev"
echo "kubectl get pods -n blog-dev"
echo "kubectl logs -f deployment/flask-blog -n blog-dev"

echo ""
echo "✅ Деплой завершен успешно!"
echo "📱 Мониторинг: kubectl get services -n blog-dev -w"
