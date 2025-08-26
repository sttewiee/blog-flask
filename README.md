# Flask Blog - CI/CD Pipeline с Kubernetes

Полнофункциональный Flask блог с автоматизированным CI/CD pipeline для развертывания в Google Kubernetes Engine (GKE).

## Архитектура

### Компоненты:
- **Flask Application** с аутентификацией и SQLite
- **Docker** контейнеризация
- **Kubernetes (GKE)** оркестрация 
- **GitHub Actions** CI/CD автоматизация
- **Prometheus** метрики

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
✅ Force replace старых подов
✅ Wait for rollout (120s)
```

#### 3. Deploy PROD (ветка `main`) 
```yaml
✅ Stop DEV environment (освобождение ресурсов)
✅ Deploy в blog-prod namespace
✅ Force replace старых подов
✅ Wait for rollout (200s)
```

#### 4. Test & Notify
```yaml
✅ Health check приложения
✅ HTTP тесты
✅ Telegram уведомления
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
└── Specs: e2-standard-2, 2-4 nodes, autoscaling
```


```bash
# Просмотр всех ресурсов
kubectl get all -n blog-dev    # DEV
kubectl get all -n blog-prod   # PROD

# Логи приложения
kubectl logs -n blog-prod deployment/flask-blog --tail=50 --follow

# Статус подов
kubectl get pods -n blog-prod -o wide

# Внешние IP сервисов
kubectl get services -n blog-prod

#### Подключение к кластеру
```bash
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4
```

#### Полная команда для всех URL
```bash
echo "=== PRODUCTION URLs ===" && \
FLASK_IP=$(kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
PROMETHEUS_IP=$(kubectl get service prometheus-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
GRAFANA_IP=$(kubectl get service grafana-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
echo "Flask App: http://$FLASK_IP/" && \
echo "Prometheus: http://$PROMETHEUS_IP:9090/" && \
echo "Grafana: http://$GRAFANA_IP:3000/ (admin/admin123)" && \
echo "Metrics: http://$FLASK_IP/metrics"
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

### Отладка мониторинга

```bash
# Статус подов мониторинга
kubectl get pods -n blog-prod | grep -E "(prometheus|grafana)"

# Детальная информация о сервисах
kubectl describe service prometheus-simple-service -n blog-prod
kubectl describe service grafana-simple-service -n blog-prod

# Логи мониторинга
kubectl logs -n blog-prod deployment/prometheus-simple
kubectl logs -n blog-prod deployment/grafana-simple
```

