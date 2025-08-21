# 🚀 Flask Blog — Полное руководство

## ✨ Возможности

### 🔧 **Автоматическая инициализация БД**
- **Entrypoint скрипт** автоматически создает таблицы при запуске
- **Ожидание готовности PostgreSQL** перед запуском приложения
- **Автоматические миграции** через Flask-Migrate

### 🏥 **Health Checks**
- **Docker health checks** для web и db сервисов
- **Автоматический мониторинг** состояния контейнеров
- **Graceful startup** с проверкой зависимостей

### 🐳 **Улучшенный Docker**
- **Multi-stage build** с оптимизацией
- **Безопасность**: непривилегированный пользователь
- **Автоматическая установка зависимостей**

## 🚀 Быстрый старт

### 1. Клонирование и настройка
```bash
git clone <your-repo>
cd blog-flask
chmod +x run_tests_docker.sh restart_final.sh
```

### 2. Запуск в Docker (рекомендуется)
```bash
# Полный запуск с финальной конфигурацией
./restart_final.sh

# Или пошагово:
docker compose up -d --build
```

### 3. Проверка статуса
```bash
docker compose ps
docker logs blog-flask-web-1
```

### 4. Тестирование
```bash
# Тесты в контейнере (безопасно для основной БД)
./run_tests_docker.sh

# Или напрямую
docker exec blog-flask-web-1 python -m pytest -v
```

## 🏗️ Архитектура

### **Сервисы**
- **web**: Flask приложение с автоматической инициализацией БД
- **db**: PostgreSQL 15 с health checks и автоматической настройкой

### **Entrypoint скрипт**
```bash
# Автоматически выполняет:
1. Ожидание готовности PostgreSQL
2. Создание таблиц БД
3. Выполнение миграций
4. Запуск приложения
```

### **Health Checks**
- **Web**: HTTP GET / (curl)
- **DB**: pg_isready
- **Интервалы**: 30s для web, 10s для db

## 🔍 Мониторинг

### **Логи контейнеров**
```bash
# Web сервис
docker logs blog-flask-web-1 -f

# База данных
docker logs blog-flask-db-1 -f

# Все сервисы
docker compose logs -f
```

### **Статус сервисов**
```bash
docker compose ps
docker compose exec web curl -f http://localhost:5000/
docker compose exec db pg_isready -U postgres
```

## 🧪 Тестирование

### **Безопасные тесты в контейнере**
```bash
# Тесты используют SQLite в памяти и не влияют на основную БД
./run_tests_docker.sh
```

### **Локальные тесты**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v
```

## 🚀 Продакшен деплой

### **CI/CD Pipeline (GitHub Actions)**
- **Test Stage**: Автоматические тесты при каждом push
- **Build & Push Stage**: Сборка Docker образа и загрузка в Google Artifact Registry
- **Deploy Stage**: Автоматический деплой в GKE кластер

### **Инфраструктура (Terraform)**
- **GKE кластер** с автоскейлингом
- **Cloud SQL** (PostgreSQL) для продакшена
- **Load Balancer** и **Ingress** для внешнего доступа
- **Workload Identity Federation** для безопасной аутентификации

### **Kubernetes манифесты**
- **Deployment** с health checks (liveness/readiness probes)
- **Service** и **Ingress** для маршрутизации
- **ConfigMap** и **Secrets** для конфигурации
- **HorizontalPodAutoscaler** для автоматического масштабирования

## 🔧 Устранение неполадок

### **Проблемы с Docker**
```bash
# Проверить права
sudo usermod -aG docker $USER && newgrp docker

# Перезапуск с новой конфигурацией
./restart_final.sh
```

### **Проблемы с базой данных**
```bash
# Проверить статус контейнеров
docker compose ps

# Проверить таблицы БД
docker exec blog-flask-db-1 psql -U postgres -d postgres -c "\dt"

# Инициализировать БД если нужно
docker exec blog-flask-web-1 python init_db.py
```

### **Проблемы с приложением**
```bash
# Проверить логи
docker logs blog-flask-web-1 -f

# Проверить доступность
curl -I http://localhost:5000
```

## 📁 Структура проекта

```
blog-flask/
├── app.py                 # Основное Flask приложение
├── requirements.txt       # Python зависимости
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Локальная разработка
├── docker-entrypoint.sh  # Скрипт запуска контейнера
├── init_db.py            # Инициализация БД
├── run_tests_docker.sh   # Безопасные тесты в контейнере
├── restart_final.sh      # Полный перезапуск
├── k8s/                  # Kubernetes манифесты
├── blog-infra/           # Terraform конфигурация
└── .github/workflows/    # CI/CD pipeline
```

## 💡 Полезные команды

```bash
# Полный перезапуск
./restart_final.sh

# Тесты
./run_tests_docker.sh

# Статус
docker compose ps

# Логи
docker logs blog-flask-web-1 -f

# Доступ к БД
docker exec -it blog-flask-db-1 psql -U postgres -d postgres
```
