# Flask Blog Application

Flask блог с PostgreSQL, Docker и Kubernetes.

## Локальная разработка

### Запуск

```bash
git clone <your-repo-url>
cd blog-flask
docker-compose up --build
```

Откройте: http://localhost:5000

### Структура

```
blog-flask/
├── app.py
├── k8s/
│   ├── postgres.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── monitoring.yaml
└── .github/workflows/
    └── deploy.yml
```

## Продакшн

Push в main ветку - все происходит автоматически!

### Endpoints

- `/health` - статус приложения
- `/health/db` - проверка БД
- `/` - главная страница
- `/register`, `/login`, `/logout` - авторизация
- `/create`, `/edit/<id>`, `/delete/<id>` - управление постами


