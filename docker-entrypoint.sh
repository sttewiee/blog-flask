#!/bin/bash
set -e

echo "🚀 Запуск Flask Blog..."

# Ожидание PostgreSQL
if [[ "$DATABASE_URL" == postgresql://* ]]; then
    echo "🔄 Ожидание готовности PostgreSQL..."
    
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    until nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
        echo "⏳ Ожидание PostgreSQL..."
        sleep 2
    done
    echo "✅ PostgreSQL готов!"
fi

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Таблицы готовы')
"

echo "✅ Приложение готово к запуску!"
exec "$@"
