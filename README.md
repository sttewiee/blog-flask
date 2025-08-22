# Flask Blog Application

Простое Flask приложение для блога с PostgreSQL базой данных, Docker и Kubernetes развертыванием.

## Технологии

- **Backend**: Python + Flask
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker + Docker Compose
- **Оркестрация**: Kubernetes (GKE)
- **CI/CD**: GitHub Actions
- **Балансировка нагрузки**: GCP Load Balancer

## Локальная разработка

### Предварительные требования

- Docker
- Docker Compose

### Запуск

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd blog-flask
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
# Отредактируйте .env файл при необходимости
```

3. Запустите приложение:
```bash
docker-compose up --build
```

4. Откройте браузер: http://localhost:5000

### Структура проекта

```
blog-flask/
├── app.py                 # Основное Flask приложение
├── run.py                 # Скрипт запуска
├── init_db.py            # Инициализация БД
├── requirements.txt       # Python зависимости
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Локальная разработка
├── docker-entrypoint.sh  # Docker entrypoint
├── k8s/                  # Kubernetes манифесты
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── clusterissuer-letsencrypt.yaml
└── .github/workflows/    # GitHub Actions
    └── deploy.yml
```

## Продакшн развертывание

### Предварительные требования

1. **GCP проект** с включенными API:
   - Container Registry API
   - Kubernetes Engine API 
   - Artifact Registry API

2. **Workload Identity настроен** для GitHub Actions (см. детали ниже)

3. **GitHub Secrets** в репозитории:
   - `SECRET_KEY` - секретный ключ Flask
   - `GAR_EMAIL` - email для Artifact Registry

### Быстрое развертывание

1. **Форкните репозиторий**
2. **Обновите PROJECT_ID** в `.github/workflows/deploy.yml`
3. **Добавьте GitHub Secrets**
4. **Push в main ветку** - все остальное происходит автоматически!

### Настройка Workload Identity (один раз)

```bash
# 1. Создайте Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="YOUR-PROJECT-ID" \
  --location="global"

# 2. Создайте Provider  
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="YOUR-PROJECT-ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Создайте Service Account
gcloud iam service-accounts create github-actions-deployer \
  --project="YOUR-PROJECT-ID"

# 4. Назначьте роли
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-deployer@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"
```

### Что происходит автоматически

GitHub Actions workflow:

1. ✅ **Тестирование** - запуск pytest
2. ✅ **Инфраструктура** - создание GKE кластера (если нет)
3. ✅ **Сборка** - Docker образ в Artifact Registry
4. ✅ **База данных** - PostgreSQL в кластере
5. ✅ **Приложение** - Flask с health checks
6. ✅ **Сеть** - Load Balancer + Ingress

### Health Check Endpoints

- `/health` - статус приложения
- `/health/db` - проверка подключения к БД

## API Endpoints

- `GET /` - главная страница со списком постов
- `GET /register` - страница регистрации
- `POST /register` - регистрация пользователя
- `GET /login` - страница входа
- `POST /login` - вход пользователя
- `GET /logout` - выход пользователя
- `GET /create` - страница создания поста
- `POST /create` - создание поста
- `GET /edit/<id>` - редактирование поста
- `POST /edit/<id>` - обновление поста
- `POST /delete/<id>` - удаление поста

## Разработка

### Добавление новых зависимостей

```bash
pip install <package>
pip freeze > requirements.txt
```

### Запуск тестов

```bash
python -m pytest
```

### Миграции базы данных

```bash
flask db init
flask db migrate -m "Description"
flask db upgrade
```

## Лицензия

MIT
