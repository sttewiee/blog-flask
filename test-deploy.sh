#!/bin/bash

set -e  # Выходить при ошибках

PROJECT_ID="sonic-harbor-465608-v1"
REGION="europe-west4"
CLUSTER_NAME="blog-cluster"

echo "🧪 Тестирование деплоя Flask Blog..."

# Проверяем аутентификацию
echo "🔐 Проверяем аутентификацию..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Не найдено активной аутентификации"
    echo "Выполните: gcloud auth activate-service-account --key-file=key.json"
    exit 1
fi

# Устанавливаем проект
echo "📝 Устанавливаем проект..."
gcloud config set project $PROJECT_ID

# Создаем Artifact Registry репозиторий
echo "📦 Создаем Artifact Registry..."
gcloud artifacts repositories create blog-flask \
    --repository-format=docker \
    --location=$REGION \
    --description="Flask Blog Docker Repository" || echo "✓ Репозиторий уже существует"

# Конфигурируем Docker
echo "🐳 Конфигурируем Docker..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Билдим и пушим образ
echo "🔨 Билдим Docker образ..."
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/blog-flask/blog-flask:${COMMIT_SHA}"
IMAGE_LATEST="${REGION}-docker.pkg.dev/${PROJECT_ID}/blog-flask/blog-flask:latest"

docker build -t $IMAGE_TAG .
docker build -t $IMAGE_LATEST .

echo "📤 Пушим образ в Artifact Registry..."
docker push $IMAGE_TAG
docker push $IMAGE_LATEST

# Создаем кластер
echo "🏗️ Создаем GKE кластер..."
gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=1 \
    --machine-type=e2-micro \
    --disk-size=15 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=2 \
    --quiet || echo "✓ Кластер уже существует"

# Получаем credentials
echo "🔑 Получаем credentials кластера..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION

# Обновляем образ в манифесте
echo "📝 Обновляем манифест с актуальным образом..."
cp k8s/deployment.yaml k8s/deployment.yaml.backup
sed "s|:latest|:${COMMIT_SHA}|g" k8s/deployment.yaml.backup > k8s/deployment.yaml

# Деплоим
echo "🚀 Деплоим приложение..."

# Создаем namespace
kubectl apply -f k8s/namespace.yaml

# Применяем PostgreSQL
kubectl apply -f k8s/postgres.yaml
echo "⏳ Ждем готовности PostgreSQL..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n blog-dev

# Применяем приложение
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Ждем готовности
echo "⏳ Ждем готовности приложения..."
kubectl rollout status deployment/flask-blog -n blog-dev --timeout=300s

# Восстанавливаем манифест
mv k8s/deployment.yaml.backup k8s/deployment.yaml

# Показываем статус
echo "📊 Статус деплоя:"
kubectl get pods -n blog-dev
echo ""
kubectl get services -n blog-dev

# Получаем внешний IP
echo ""
echo "🌐 Получение внешнего IP (может занять несколько минут)..."
kubectl get service flask-blog-service -n blog-dev -w &
WATCH_PID=$!

# Ждем LoadBalancer IP максимум 5 минут
for i in {1..30}; do
    EXTERNAL_IP=$(kubectl get service flask-blog-service -n blog-dev -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [[ -n "$EXTERNAL_IP" && "$EXTERNAL_IP" != "null" ]]; then
        kill $WATCH_PID 2>/dev/null || true
        echo ""
        echo "✅ Деплой успешен! Приложение доступно по адресу: http://$EXTERNAL_IP"
        echo "🧪 Тестируем приложение..."
        
        # Тестируем health endpoint
        if curl -s "http://$EXTERNAL_IP/health" | grep -q "ok"; then
            echo "✅ Health check прошел успешно"
        else
            echo "❌ Health check не прошел"
        fi
        
        break
    fi
    echo "⏳ Ждем внешний IP... ($i/30)"
    sleep 10
done

if [[ -z "$EXTERNAL_IP" || "$EXTERNAL_IP" == "null" ]]; then
    kill $WATCH_PID 2>/dev/null || true
    echo ""
    echo "⚠️ Внешний IP не получен за 5 минут. Проверьте LoadBalancer вручную:"
    echo "kubectl get service flask-blog-service -n blog-dev"
fi

echo ""
echo "🎉 Тестирование деплоя завершено!"
