# Flask Blog - CI/CD Pipeline

Flask блог с автоматизированным CI/CD для GKE.

## Быстрый старт

```bash
git clone https://github.com/sttewiee/blog-flask.git
cd blog-flask
docker compose up --build
# http://localhost:5000
```

## Деплой

```bash
# Dev
git checkout dev
git push origin dev

# Prod  
git checkout main
git push origin main
```

## Локальная разработка

```bash
docker compose up --build
docker compose exec web python -m pytest -v
curl http://localhost:5000/health
```

## Пересборка подов

```bash
# Быстрая
kubectl rollout restart deployment/flask-blog -n blog-dev

# Полная
docker build -t europe-west4-docker.pkg.dev/sonic-harbor-465608-v1/blog-flask/blog-flask:latest .
docker push europe-west4-docker.pkg.dev/sonic-harbor-465608-v1/blog-flask/blog-flask:latest
kubectl set image deployment/flask-blog flask-blog=europe-west4-docker.pkg.dev/sonic-harbor-465608-v1/blog-flask/blog-flask:latest -n blog-dev
```

## Kubernetes

```bash
# Подключение
gcloud container clusters get-credentials blog-cluster-shared --region europe-west4

# Статус
kubectl get all -n blog-dev
kubectl get all -n blog-prod

# Логи
kubectl logs -n blog-prod deployment/flask-blog --tail=50 --follow

# IP адреса
kubectl get service flask-blog-service -n blog-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
kubectl get service flask-blog-service -n blog-dev -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Мониторинг

```bash
# Prometheus
kubectl get service prometheus-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Grafana  
kubectl get service grafana-shared-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Архитектура

- **DEV/PROD**: SQLite в K8s
- **Локально**: PostgreSQL в Docker
- **CI/CD**: GitHub Actions → GKE
- **Мониторинг**: Prometheus + Grafana

## Версии

- Flask: 3.0.0
- Python: 3.11  
- App: 2.7.0-dev
