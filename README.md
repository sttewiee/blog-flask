# Flask Blog — Deployment Guide

## Стек
- Python 3.11, Flask
- SQLAlchemy, Flask-Migrate (Alembic)
- PostgreSQL
- Docker
- CI/CD: GitHub Actions → Artifact Registry → GKE

---

## Быстрый старт (чистая Ubuntu VM)

**Требуется**: JSON-ключ сервисного аккаунта с ролью **Cloud SQL Client**.  
Файл назвать `cloudsql-key.json` и положить **рядом с репозиторием** (`~/blog-flask`).  
**Никогда не коммитить!**

---

### 1. Установка Git и Docker

```bash
sudo apt-get update
sudo apt-get install -y git ca-certificates curl gnupg lsb-release
```

Репозиторий Docker:
```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Чтобы работать без `sudo`:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### 2. Клонирование репозитория
```bash
git clone https://github.com/sttewiee/blog-flask.git
cd blog-flask
```
или по SSH:
```bash
git clone git@github.com:sttewiee/blog-flask.git
cd blog-flask
```

---

### 3. Подготовка ключа для Cloud SQL

1. В GCP → Service Accounts → Keys → **Create key** (JSON) → скачать.
2. Переименовать в `cloudsql-key.json`.
3. Положить в каталог проекта:
```bash
mv ~/Downloads/cloudsql-key.json ~/blog-flask/
```
4. Дать права для чтения непривилегированным контейнерам:
```bash
chmod 0644 cloudsql-key.json
```
5. Проверить, что файл валидный JSON:
```bash
python3 -m json.tool cloudsql-key.json
```

---

### 4. Сеть Docker и Cloud SQL Proxy v2

```bash
docker network create blog-net || true

docker rm -f cloud-sql-proxy 2>/dev/null || true

docker run -d   --name cloud-sql-proxy   --restart unless-stopped   --network blog-net   --network-alias cloud-sql-proxy   -v "$PWD/cloudsql-key.json":/secrets/key.json:ro   -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json   gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.11.4   --address 0.0.0.0 --port 5432   sonic-harbor-465608-v1:europe-west4:blog-db
```

Проверка:
```bash
docker inspect -f '{{.State.Status}}' cloud-sql-proxy
docker inspect -f '{{.NetworkSettings.Networks.blog-net.IPAddress}}' cloud-sql-proxy
docker logs --tail=50 cloud-sql-proxy
```
Статус должен быть `running`, без ошибок.

---

### 5. Сборка и запуск приложения

```bash
docker build -t flask-blog:local .

SECRET=$(openssl rand -hex 32)

docker rm -f flask-blog 2>/dev/null || true

docker run -d   --name flask-blog   --restart unless-stopped   --network blog-net   -p 80:5000   -e FLASK_ENV=production   -e SECRET_KEY="$SECRET"   -e DATABASE_URL="postgresql://bloguser:blogpassword@cloud-sql-proxy:5432/blogdb"   flask-blog:local
```

---

### 6. Миграции БД

```bash
docker exec -it flask-blog flask db upgrade
```

---

### 7. Проверка

```bash
curl -I http://localhost
```
Ожидаемый ответ: `HTTP/1.1 200 OK`.

Для доступа извне откройте TCP/80 в firewall облака.

---

## Конфигурация переменных окружения

- `DATABASE_URL` — строка подключения SQLAlchemy, пример:
  ```
  postgresql://bloguser:blogpassword@cloud-sql-proxy:5432/blogdb
  ```
- `SECRET_KEY` — случайная строка для сессий.
- `FLASK_ENV` — `production` | `development` | `testing`.

---

## Частые команды миграций

Применить:
```bash
docker exec -it flask-blog flask db upgrade
```
Создать новую:
```bash
docker exec -it flask-blog flask db migrate -m "your change"
```
Посмотреть текущую ревизию:
```bash
docker exec -it flask-blog flask db current
```
Подписать ревизию без изменений:
```bash
docker exec -it flask-blog flask db stamp head
```

---

## Тесты локально
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///:memory:" SECRET_KEY="test" FLASK_ENV="testing"
pytest -v
```

---

## CI/CD (GitHub Actions)
- **test**: Python 3.11, зависимости, pytest на SQLite, coverage в Codecov.
- **build-and-push**: Docker build → Artifact Registry.
- **deploy**: Обновление образа в GKE (только `main`).

---

## Типичные ошибки и отладка

1. **`invalid character ...` при старте прокси** — ключ невалидный JSON.
2. **`is a directory`** — `cloudsql-key.json` оказался папкой, а не файлом.
3. **`permission denied`** — у файла слишком строгие права. Исправить:
   ```bash
   chmod 0644 cloudsql-key.json
   ```
4. **`could not translate host name "cloud-sql-proxy"`** — прокси не запущен или не в сети `blog-net`.
5. Проверить статус и IP прокси:
   ```bash
   docker inspect -f '{{.State.Status}}' cloud-sql-proxy
   docker inspect -f '{{.NetworkSettings.Networks.blog-net.IPAddress}}' cloud-sql-proxy
   ```
6. Проверить DNS из приложения:
   ```bash
   docker exec -it flask-blog getent hosts cloud-sql-proxy
   ```

---

SSH ключ для Git 
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
---

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```
---
Содержимое 
```bash
cat ~/.ssh/id_ed25519.pub
```
Переключить Git на ssh
```bash
 git remote set-url origin git@github.com:user/repo.git
```

Установить gcloud, auth-плагин и kubectl
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg

# Репозиторий Google Cloud SDK
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
 | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
 | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

sudo apt-get update
sudo apt-get install -y google-cloud-cli google-cloud-sdk-gke-gcloud-auth-plugin kubectl
```
Залогиниться
```bash
gcloud auth login --no-launch-browser
```
Выбрать проект
```bash
gcloud config set project sonic-harbor-465608-v1
```
kubeconfig для GKE
```bash
gcloud container clusters get-credentials blog-gke --region europe-west4 --project sonic-harbor-465608-v1
```
Проверь доступ
```bash
kubectl -n blog-dev get deploy flask-blog
kubectl -n blog-dev get pods -l app=flask-blog
kubectl -n blog-dev logs <имя-пода>
kubectl -n blog-dev get svc
kubectl -n blog-dev get ingress
```
