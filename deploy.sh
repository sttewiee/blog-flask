#!/bin/bash

if pgrep -x "certbot" > /dev/null; then
    echo "Certbot is already running, skipping certificate generation."
else
    
    echo "Certbot is not running, starting the certificate generation..."
    
    
    sudo docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d $DOMAIN --email $EMAIL --agree-tos --no-eff-email --non-interactive
fi


echo "Starting other services in production mode..."
sudo docker-compose -f docker-compose.prod.yml down --remove-orphans
sudo docker-compose -f docker-compose.prod.yml up -d


echo "вЏі Applying database migrations..."
sleep 20
sudo docker-compose -f docker-compose.prod.yml exec -T web flask db upgrade

echo "рџЋ‰ Deployment to production completed successfully!"
