# Flask Blog - CI/CD Pipeline с Kubernetes

Полнофункциональный Flask блог с автоматизированным CI/CD pipeline для развертывания в Google Kubernetes Engine (GKE).

## Архитектура

### Компоненты:
- Flask Application с аутентификацией и SQLite
- Docker контейнеризация
- Kubernetes (GKE) оркестрация 
- GitHub Actions CI/CD автоматизация
- Prometheus + Grafana общий мониторинг для DEV/PROD

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

### Развертывание в GCP

#### Рекомендуемый процесс разработки:

**Этап 1: Разработка**
```bash
git checkout dev
# Разрабатываем новую функциональность
git add .
git commit -m "Add user authentication"
git push origin dev
# → Автоматический деплой в dev окружение
```

**Этап 2: Тестирование**
- Проверяем dev окружение: `http://34.12.188.35`
- Тестируем функциональность
- Исправляем баги если нужно

**Этап 3: Релиз**
```bash
git checkout main
git merge dev --no-ff -m "Release: user authentication feature"
git push origin main
# → Автоматический деплой в prod окружение
```

#### Быстрое развертывание:
```bash
# Запушить в dev ветку для тестирования
git checkout -b dev
git push origin dev

# После успешного тестирования - в main для продакшена
git checkout main
git push origin main
```

## Локальная разработка

```bash
# Запуск
docker compose up --build

# Тесты
docker compose exec web python -m pytest -v

# Остановка
docker compose down

# Проверка метрик
curl http://localhost:5000/metrics

# Health check
curl http://localhost:5000/health
```

## CI/CD Pipeline

### Автоматические триггеры
- Push в dev → Deploy в DEV environment
- Push в main → Deploy в PROD environment

### Стадии Pipeline

#### 1. Build & Push
- Setup Python 3.11
- Install dependencies  
- Run pytest tests
- Build Docker image
- Push to Google Artifact Registry

#### 2. Deploy DEV (ветка dev)
- Create/Update GKE cluster
- Deploy в blog-dev namespace
- Deploy общий мониторинг (monitoring namespace)
- Wait for rollout (120s)

#### 3. Deploy PROD (ветка main) 
- Stop DEV environment (освобождение ресурсов)
- Deploy в blog-prod namespace
- Deploy общий мониторинг (monitoring namespace)
- Wait for rollout (200s)

#### 4. Test & Notify
- Health check приложения
- HTTP тесты
- Telegram уведомления с URL мониторинга

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

## Мониторинг

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
```

## Git Workflow

### Когда мержить в prod:

#### ✅ Мержить когда:
- Функциональность протестирована в dev
- Нет критических багов
- Код прошел ревью
- Готов к продакшну

#### ❌ НЕ мержить когда:
- Есть неисправленные баги
- Функциональность не протестирована
- Код не готов к продакшну

### Создание новой функциональности:
```bash
git checkout dev
git pull origin dev
git checkout -b feature/user-dashboard
# Разрабатываем...
git add .
git commit -m "Add user dashboard"
git push origin feature/user-dashboard
# Создаем PR в dev
```

### Готовый релиз:
```bash
git checkout main
git pull origin main
git merge dev --no-ff -m "Release v1.3.0: user dashboard"
git tag v1.3.0
git push origin main
git push origin v1.3.0
```
