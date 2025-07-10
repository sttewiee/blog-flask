#!/bin/bash

# Убедимся, что Certbot не работает
if pgrep -x "certbot" > /dev/null; then
    echo "Certbot is already running, skipping certificate generation."
else
    # Если Certbot не запущен, продолжаем с его запуском
    echo "Certbot is not running, starting the certificate generation..."
    
    # Запуск Certbot для получения сертификата
    sudo docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d $DOMAIN --email $EMAIL --agree-tos --no-eff-email --non-interactive
fi

# Перезапуск всех остальных сервисов, независимо от того, что Certbot уже работает или нет
echo "Starting other services in production mode..."
sudo docker-compose -f docker-compose.prod.yml down --remove-orphans
sudo docker-compose -f docker-compose.prod.yml up -d

# Применение миграций базы данных
echo "⏳ Applying database migrations..."
sleep 20
sudo docker-compose -f docker-compose.prod.yml exec -T web flask db upgrade

echo "🎉 Deployment to production completed successfully!"
