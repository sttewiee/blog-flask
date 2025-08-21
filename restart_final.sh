#!/bin/bash
set -e

echo "🚀 Финальный перезапуск с исправленной конфигурацией..."

# Останавливаем и удаляем старые контейнеры
echo "🛑 Остановка старых контейнеров..."
docker compose down

# Удаляем старые образы
echo "🗑️ Удаление старых образов..."
docker rmi blog-flask-web:latest 2>/dev/null || true

# Собираем новый образ
echo "🏗️ Сборка нового образа..."
docker compose build --no-cache

# Запускаем с новой конфигурацией
echo "🚀 Запуск с новой конфигурацией..."
docker compose up -d

# Ждем готовности
echo "⏳ Ожидание готовности сервисов..."
sleep 15

# Проверяем статус
echo "📊 Статус сервисов:"
docker compose ps

# Проверяем health checks
echo "🏥 Проверка health checks:"
docker compose exec web curl -f http://localhost:5000/ || echo "⚠️ Web сервис еще не готов"
docker compose exec db pg_isready -U postgres -d postgres || echo "⚠️ DB сервис еще не готов"

# Проверяем таблицы БД
echo "🗄️ Проверка таблиц БД:"
docker exec blog-flask-db-1 psql -U postgres -d postgres -c "\dt" || echo "⚠️ Не удалось проверить таблицы"

# Тестируем приложение
echo "🧪 Тестирование приложения..."
curl -I http://localhost:5000 || echo "⚠️ Приложение недоступно"

echo "✅ Финальный перезапуск завершен!"
echo "🌐 Приложение доступно по адресу: http://localhost:5000"
echo "📊 Статус: docker compose ps"
echo "📝 Логи: docker logs blog-flask-web-1 -f"
