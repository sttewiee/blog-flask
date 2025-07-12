# Flask Blog Application

Простое веб-приложение блога на Flask с аутентификацией пользователей и CRUD операциями для постов.

## Функциональность

- Регистрация и авторизация пользователей
- Создание, редактирование и удаление постов
- Просмотр всех постов на главной странице
- Защита маршрутов (только авторизованные пользователи могут создавать/редактировать посты)

## Технологии

- **Backend**: Flask 3.0.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Быстрый старт

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd blog-flask
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
# Скопируйте пример файла
cp env.example .env

# Отредактируйте .env файл под ваши нужды
# Особенно важно изменить SECRET_KEY на уникальное значение
```

5. Инициализируйте базу данных:
```bash
python init_db.py
```

6. Запустите приложение:
```bash
python -m flask run
```

### С использованием Docker

1. Запустите приложение с базой данных:
```bash
docker-compose up --build
```

2. Приложение будет доступно по адресу: http://localhost:5000

## Структура проекта

```
blog-flask/
├── app.py                 # Основной файл приложения
├── requirements.txt       # Зависимости Python
├── Dockerfile            # Конфигурация Docker
├── docker-compose.yml    # Docker Compose конфигурация
├── test_app.py           # Тесты приложения
├── .github/workflows/    # GitHub Actions workflows
├── templates/            # HTML шаблоны
│   ├── index.html        # Главная страница
│   ├── login.html        # Страница входа
│   ├── register.html     # Страница регистрации
│   ├── create.html       # Создание поста
│   └── edit.html         # Редактирование поста
└── instance/             # Локальные файлы (исключены из Git)
```

## Тестирование

Запустите тесты:
```bash
pytest test_app.py
```

## CI/CD Pipeline

Проект настроен с автоматическим CI/CD pipeline через GitHub Actions:

1. **Test Job**: Запускает тесты на каждом push и pull request
2. **Build Job**: Собирает Docker образ и пушит в Docker Hub (только для main ветки)
3. **Deploy Job**: Деплоит в продакшн (только для main ветки)

### Настройка секретов

Для работы CI/CD необходимо настроить следующие секреты в GitHub:

- `DOCKER_USERNAME`: Имя пользователя Docker Hub
- `DOCKER_PASSWORD`: Пароль Docker Hub

## Развертывание в продакшн

1. Убедитесь, что у вас настроены секреты в GitHub
2. Сделайте push в main ветку
3. GitHub Actions автоматически соберет и задеплоит приложение

## Переменные окружения

- `DATABASE_URL`: URL подключения к базе данных PostgreSQL
- `SECRET_KEY`: Секретный ключ для Flask сессий
- `FLASK_ENV`: Окружение (development/production)

## Лицензия

MIT License 