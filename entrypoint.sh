# На твоей локальной машине
nano entrypoint.sh
```Вставь в него следующий код. Этот скрипт — новая точка входа в твой контейнер.
```bash
#!/bin/sh
set -e

# 1. Ждем, пока база данных не станет доступной
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

# 2. Применяем миграции базы данных
echo "Applying database migrations..."
flask db upgrade

# 3. Запускаем основную команду (gunicorn)
exec "$@"