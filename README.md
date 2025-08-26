# Flask Blog - CI/CD Pipeline с Kubernetes

Полнофункциональный Flask блог с автоматизированным CI/CD pipeline для развертывания в Google Kubernetes Engine (GKE).

## Архитектура

### Компоненты:
- **Flask Application** с аутентификацией и SQLite
- **Docker** контейнеризация
- **Kubernetes (GKE)** оркестрация 
- **GitHub Actions** CI/CD автоматизация
- **Prometheus + Grafana** общий мониторинг для DEV/PROD

## Быстрый старт

### Клонирование и запуск

```bash
# Клонируем репозиторий
git clone https://github.com/sttewiee/blog-flask.git
cd blog-flask

# Запускаем локально
docker compose up --build

# Открываем: http://localhost:5000
```

## Локальная разработка

### Docker Compose (рекомендуется)

```bash
# Запуск
docker compose up --build

# Тесты
docker compose exec web python -m pytest -v

# Остановка
docker compose down
```

## Работа с Git

### Структура веток
- **`main`** - Production (автодеплой в PROD)
- **`dev`** - Development (автодеплой в DEV)
- **`feature/*`** - Новые функции

## CI/CD Pipeline

### Автоматические триггеры
- **Push в `dev`** → Deploy в DEV environment
- **Push в `main`** → Deploy в PROD environment

### Стадии Pipeline

#### 1. Build & Push
```yaml
✅ Setup Python 3.11
✅ Install dependencies  
✅ Run pytest tests
✅ Build Docker image
✅ Push to Google Artifact Registry
```

#### 2. Deploy DEV (ветка `dev`)
```yaml
✅ Create/Update GKE cluster
✅ Deploy в blog-dev namespace
✅ Deploy общий мониторинг (monitoring namespace)
✅ Wait for rollout (120s)
```

#### 3. Deploy PROD (ветка `main`) 
```yaml
✅ Stop DEV environment (освобождение ресурсов)
✅ Deploy в blog-prod namespace
✅ Deploy общий мониторинг (monitoring namespace)
✅ Wait for rollout (200s)
```

#### 4. Test & Notify
```yaml
✅ Health check приложения
✅ HTTP тесты
✅ Telegram уведомления с URL мониторинга
```

### Просмотр статуса
```bash
# GitHub Actions
https://github.com/sttewiee/blog-flask/actions

# Логи в реальном времени
# Выбираем workflow → job → step
```

## Kubernetes

### Архитектура GKE
```
Cluster: blog-cluster-shared (europe-west4)
├── DEV: blog-dev namespace
├── PROD: blog-prod namespace  
├── Monitoring: monitoring namespace (общий)
└── Specs: e2-standard-2, 2-4 nodes, autoscaling
```

### Подключение к кластеру

```bash
# Установка gke-gcloud-auth-plugin (если не установлен)
sudo apt-get update && sudo apt-get install -y gnupg
sudo mkdir -p /usr/share/keyrings
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install -y google-cloud-sdk-gke-gcloud-auth-plugin

# Подключение к кластеру
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4
```

### Основные команды Kubernetes

```bash
# Просмотр всех ресурсов
kubectl get all -n blog-dev      # DEV
kubectl get all -n blog-prod     # PROD
kubectl get all -n monitoring    # Мониторинг

# Логи приложения
kubectl logs -n blog-prod deployment/flask-blog --tail=50 --follow

# Статус подов
kubectl get pods -n blog-prod -o wide

# Внешние IP сервисов
kubectl get services -n blog-prod
kubectl get services -n monitoring
```

### Получение внешних адресов

```bash
# Flask App (PROD)
kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Flask App (DEV)
kubectl get service flask-blog-service -n blog-dev -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Prometheus (общий)
kubectl get service prometheus-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Grafana (общий)
kubectl get service grafana-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Полная команда для всех URL

```bash
echo "=== PRODUCTION URLs ===" && \
FLASK_IP=$(kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
PROMETHEUS_IP=$(kubectl get service prometheus-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
GRAFANA_IP=$(kubectl get service grafana-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
echo "Flask App: http://$FLASK_IP/" && \
echo "Prometheus: http://$PROMETHEUS_IP:9090/" && \
echo "Grafana: http://$GRAFANA_IP:3000/ (admin/admin123)" && \
echo "Metrics: http://$FLASK_IP/metrics"
```

## Мониторинг

### Общий мониторинг для DEV/PROD

Система использует **один набор Prometheus + Grafana** в namespace `monitoring` для мониторинга обоих окружений:

- **Prometheus** автоматически обнаруживает сервисы в `blog-dev` и `blog-prod`
- **Grafana** показывает дашборды для обоих окружений
- **Экономия ресурсов** - вместо 4 LoadBalancer только 2

### Отладка мониторинга

```bash
# Статус подов мониторинга
kubectl get pods -n monitoring

# Детальная информация о сервисах
kubectl describe service prometheus-shared-service -n monitoring
kubectl describe service grafana-shared-service -n monitoring

# Логи мониторинга
kubectl logs -n monitoring deployment/prometheus-shared
kubectl logs -n monitoring deployment/grafana-shared

# Проверка targets в Prometheus
curl -s "http://$(kubectl get service prometheus-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):9090/api/v1/targets" | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, health: .health}'
```

### Локальная разработка

```bash
# Запуск
docker compose up -d

# Проверка метрик
curl http://localhost:5000/metrics

# Health check
curl http://localhost:5000/health
```

## Устранение неполадок

### Проблемы с gke-gcloud-auth-plugin

```bash
# Ошибка: "Request had insufficient authentication scopes"
# Решение: Установить плагин (см. раздел "Подключение к кластеру")

# Ошибка: "gke-gcloud-auth-plugin not found"
# Решение: Переустановить плагин
sudo apt-get remove google-cloud-sdk-gke-gcloud-auth-plugin
sudo apt-get install google-cloud-sdk-gke-gcloud-auth-plugin
```

### Проблемы с LoadBalancer IP

```bash
# Проверка квоты IP адресов
gcloud compute addresses list

# Если превышена квота - удалить неиспользуемые IP
gcloud compute addresses delete [IP_NAME] --region=europe-west4

# Проверка событий сервиса
kubectl describe service grafana-shared-service -n monitoring
```

### Проблемы с мониторингом

```bash
# Проверка конфигурации Prometheus
kubectl get configmap prometheus-config-shared -n monitoring -o yaml

# Проверка аннотаций сервисов
kubectl get service flask-blog-service -n blog-prod -o yaml | grep -A 5 annotations
```

