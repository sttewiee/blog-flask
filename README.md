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

### GitHub Secrets

Настройте следующие секреты в вашем GitHub репозитории:

- `SECRET_KEY` - секретный ключ Flask
- `CLOUDSQL_KEY_JSON` - JSON ключ для Cloud SQL
- `GAR_EMAIL` - email для Artifact Registry

### Автоматическое развертывание

При пуше в ветку `main` автоматически:

1. Запускаются тесты
2. Собирается Docker образ
3. Образ пушится в Artifact Registry
4. Развертывается в GKE кластер
5. Настраивается Load Balancer

### Ручное развертывание

```bash
# Аутентификация в GCP
gcloud auth login

# Настройка проекта
gcloud config set project YOUR_PROJECT_ID

# Получение credentials для кластера
gcloud container clusters get-credentials blog-gke --zone europe-west4-b

# Применение манифестов
kubectl apply -f k8s/
```

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
