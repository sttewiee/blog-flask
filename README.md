# 🚀 Flask Blog - CI/CD Pipeline с Kubernetes

Полнофункциональный Flask блог с автоматизированным CI/CD pipeline для развертывания в Google Kubernetes Engine (GKE).

## 📋 Архитектура

### Компоненты:
- **Flask Application** с аутентификацией и SQLite
- **Docker** контейнеризация
- **Kubernetes (GKE)** оркестрация 
- **GitHub Actions** CI/CD автоматизация
- **Prometheus** метрики

### CI/CD Flow:
```
dev branch → Build → Test → Deploy DEV → Notify
main branch → Build → Test → Deploy PROD → Notify
```

## 🚀 Быстрый старт

### 1. Клонирование и запуск

```bash
# Клонируем репозиторий
git clone https://github.com/sttewiee/blog-flask.git
cd blog-flask

# Запускаем локально
docker compose up --build

# Открываем: http://localhost:5000
```

### 2. Структура проекта

```
blog-flask/
├── .github/workflows/cicd-pipeline.yml  # CI/CD
├── k8s/                                 # Kubernetes манифесты
├── app.py                               # Flask приложение
├── requirements.txt                     # Зависимости
├── Dockerfile                          # Docker образ
├── docker-compose.yml                  # Локальная разработка
└── test_app.py                         # Тесты
```

## 💻 Локальная разработка

### Docker Compose (рекомендуется)

```bash
# Запуск
docker compose up --build

# Тесты
docker compose exec web python -m pytest -v

# Остановка
docker compose down
```

### Python напрямую

```bash
# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Зависимости
pip install -r requirements.txt

# Запуск
python run.py
```

## 🌳 Работа с Git

### Структура веток
- **`main`** - Production (автодеплой в PROD)
- **`dev`** - Development (автодеплой в DEV)
- **`feature/*`** - Новые функции

### Workflow разработки

#### 1. Создание новой функции
```bash
# Переключаемся на dev
git checkout dev
git pull origin dev

# Создаем feature ветку
git checkout -b feature/new-posts

# Работаем с кодом
# ... редактируем файлы ...

# Коммитим изменения
git add .
git commit -m "✨ Add new posts functionality"
git push origin feature/new-posts
```

#### 2. Тестирование в DEV
```bash
# Мержим в dev
git checkout dev
git merge feature/new-posts
git push origin dev

# 🚀 Автоматически запускается DEV pipeline
# Проверяем: https://github.com/sttewiee/blog-flask/actions
```

#### 3. Деплой в Production
```bash
# Мержим в main
git checkout main
git pull origin main
git merge dev
git push origin main

# 🚀 Автоматически запускается PROD pipeline
```

### Полезные команды Git

```bash
# Просмотр веток
git branch -a

# История коммитов
git log --oneline --graph

# Статус изменений
git status
git diff

# Переключение веток
git checkout dev
git checkout main
```

## 🔄 CI/CD Pipeline

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
✅ Wait for rollout (300s)
```

#### 3. Deploy PROD (ветка `main`) 
```yaml
✅ Stop DEV environment (освобождение ресурсов)
✅ Deploy в blog-prod namespace
✅ Force replace старых подов
✅ Wait for rollout (300s)
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

## ☸️ Kubernetes

### Архитектура GKE
```
Cluster: blog-cluster-shared (europe-west4)
├── DEV: blog-dev namespace
├── PROD: blog-prod namespace  
└── Specs: e2-standard-2, 2-4 nodes, autoscaling
```

### Подключение к кластеру

```bash
# Установка gcloud CLI
curl https://sdk.cloud.google.com | bash

# Авторизация
gcloud auth login
gcloud config set project sonic-harbor-465608-v1

# Подключение к кластеру
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4

# Проверка
kubectl cluster-info
```

### Управление приложением

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

# Health check
kubectl exec -n blog-prod deployment/flask-blog -- curl http://localhost:5000/health
```

### Масштабирование

```bash
# Увеличение реплик
kubectl scale deployment flask-blog --replicas=3 -n blog-prod

# Автомасштабирование  
kubectl autoscale deployment flask-blog --cpu-percent=50 --min=1 --max=5 -n blog-prod
```

## 🔧 Устранение неполадок

### Частые проблемы

#### 1. Pipeline падает с таймаутом
```bash
# Проверяем ресурсы
kubectl top nodes
kubectl describe nodes

# Пересоздаем deployment
kubectl delete deployment flask-blog -n blog-prod
kubectl apply -f k8s/deployment.yaml -n blog-prod
```

#### 2. Приложение недоступно
```bash
# Проверяем сервис
kubectl get services -n blog-prod
kubectl describe service flask-blog-service -n blog-prod

# Проверяем endpoints
kubectl get endpoints -n blog-prod

# Тест внутри кластера
kubectl exec -n blog-prod deployment/flask-blog -- curl http://localhost:5000/health
```

#### 3. Ошибки аутентификации GCP
```bash
# Переавторизация
gcloud auth login
gcloud config set project sonic-harbor-465608-v1
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4
```

### Полезные команды отладки

```bash
# События кластера
kubectl get events --sort-by=.metadata.creationTimestamp

# Подробная информация о ресурсе
kubectl describe pod <pod-name> -n blog-prod
kubectl describe node <node-name>

# Вход в контейнер
kubectl exec -it -n blog-prod deployment/flask-blog -- /bin/bash

# Port-forwarding для локального доступа
kubectl port-forward -n blog-prod service/flask-blog-service 8080:80
# Затем: http://localhost:8080
```

## 📊 Мониторинг

Полностью автоматизированная система мониторинга с Prometheus и Grafana.

### 🌐 Production URLs

```
🚀 Flask App:    http://34.91.2.135/
📊 Prometheus:   http://34.12.110.197:9090/
📈 Grafana:      http://34.12.240.66:3000/ (admin/admin123)
📋 Metrics:      http://34.91.2.135/metrics
```

### 🔍 Получение IP адресов мониторинга

#### Подключение к кластеру
```bash
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4
```

#### Команды для получения IP
```bash
# Все сервисы
kubectl get services -n blog-prod

# Отдельные IP адреса
kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
kubectl get service prometheus-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
kubectl get service grafana-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

#### Полная команда для всех URL
```bash
echo "=== 🌐 PRODUCTION URLs ===" && \
FLASK_IP=$(kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
PROMETHEUS_IP=$(kubectl get service prometheus-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
GRAFANA_IP=$(kubectl get service grafana-simple-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}') && \
echo "🚀 Flask App: http://$FLASK_IP/" && \
echo "📊 Prometheus: http://$PROMETHEUS_IP:9090/" && \
echo "📈 Grafana: http://$GRAFANA_IP:3000/ (admin/admin123)" && \
echo "📋 Metrics: http://$FLASK_IP/metrics"
```

### 🏥 Health Checks

```bash
# Базовый health check
curl http://34.91.2.135/health
# Ответ: {"status":"ok","version":"2.7.0-dev"}

# Проверка БД
curl http://34.91.2.135/health/db

# Debug информация
curl http://34.91.2.135/debug
```

### 📈 Локальная разработка

```bash
# Запуск
docker compose up -d

# Проверка метрик
curl http://localhost:5000/metrics

# Health check
curl http://localhost:5000/health
```

### 🔧 Отладка мониторинга

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

### 📊 Конфигурация

- **Prometheus**: Scrape interval 30s, targets Flask app
- **Grafana**: Version 10.2.0, admin/admin123
- **Retention**: 7 дней для Prometheus
- **Автодеплой**: Через CI/CD pipeline

## 🎯 Текущие URLs

- **🚀 PROD App**: http://34.91.2.135/
- **📊 Prometheus**: http://34.12.110.197:9090/
- **📈 Grafana**: http://34.12.240.66:3000/ (admin/admin123)
- **📋 Metrics**: http://34.91.2.135/metrics
- **🔧 GitHub Actions**: https://github.com/sttewiee/blog-flask/actions
- **☁️ GCP Console**: https://console.cloud.google.com/kubernetes/workload

---

## 📞 Поддержка

- **GitHub Issues**: [Создать issue](https://github.com/sttewiee/blog-flask/issues)
- **Documentation**: [Flask](https://flask.palletsprojects.com/) | [Kubernetes](https://kubernetes.io/docs/) | [GKE](https://cloud.google.com/kubernetes-engine/docs)

---

**🎉 Готово! У вас есть полнофункциональный CI/CD pipeline с автоматическим развертыванием в Kubernetes!**