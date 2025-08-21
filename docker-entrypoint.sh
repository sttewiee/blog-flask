#!/bin/bash
set -e

# Функция для ожидания готовности PostgreSQL
wait_for_postgres() {
    if [ "$DATABASE_URL" != "${DATABASE_URL#postgresql://}" ]; then
        echo "🔄 Ожидание готовности PostgreSQL..."
        
        # Извлекаем хост и порт из DATABASE_URL
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$DB_HOST" ]; then
            DB_HOST="localhost"
        fi
        if [ -z "$DB_PORT" ]; then
            DB_PORT="5432"
        fi
        
        until nc -z $DB_HOST $DB_PORT; do
            echo "⏳ PostgreSQL недоступен на $DB_HOST:$DB_PORT - ожидание..."
            sleep 2
        done
        
        echo "✅ PostgreSQL готов!"
    fi
}

# Функция для инициализации БД
init_database() {
    echo "🗄️ Инициализация базы данных..."
    
    # Пытаемся создать таблицы
    if python -c "
import os
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        # Проверяем, есть ли уже таблицы
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables or len(existing_tables) <= 1:  # Только alembic_version
            print('Создаем таблицы...')
            db.create_all()
            print('✅ Таблицы созданы успешно')
        else:
            print('✅ Таблицы уже существуют')
            
        # Проверяем, что таблицы user и post существуют
        tables = inspector.get_table_names()
        if 'user' in tables and 'post' in tables:
            print('✅ Основные таблицы user и post готовы')
        else:
            print('⚠️ Не все таблицы созданы')
            
    except Exception as e:
        print(f'❌ Ошибка инициализации БД: {e}')
        exit(1)
"; then
        echo "✅ База данных готова"
    else
        echo "❌ Ошибка инициализации БД"
        exit 1
    fi
}

# Функция для выполнения миграций
run_migrations() {
    echo "🔄 Проверка миграций..."
    
    if command -v flask >/dev/null 2>&1; then
        if flask db current >/dev/null 2>&1; then
            echo "🔄 Выполнение миграций..."
            flask db upgrade || echo "⚠️ Миграции не выполнены, но продолжаем"
        else
            echo "ℹ️ Миграции не настроены, пропускаем"
        fi
    else
        echo "ℹ️ Flask CLI недоступен, пропускаем миграции"
    fi
}

# Основная логика
echo "🚀 Запуск Flask Blog..."

# Ожидаем готовности БД
wait_for_postgres

# Инициализируем БД
init_database

# Выполняем миграции
run_migrations

echo "✅ Приложение готово к запуску!"

# Запускаем команду
exec "$@"
