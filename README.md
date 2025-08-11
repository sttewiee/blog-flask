Стек
Python 3.11, Flask

SQLAlchemy, Flask-Migrate (Alembic)

PostgreSQL

Docker

(CI/CD) GitHub Actions → Artifact Registry → GKE

Быстрый старт (чистая Ubuntu ВМ)
Понадобится JSON-ключ сервисного аккаунта с ролью Cloud SQL Client.
Файл назовите cloudsql-key.json и положите рядом с репозиторием. Не коммитить!

1) Установка Git и Docker
bash
Копировать
Редактировать
sudo apt-get update
sudo apt-get install -y git ca-certificates curl gnupg lsb-release

# репозиторий Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# чтобы работать без sudo
sudo usermod -aG docker $USER
newgrp docker
2) Клонирование репозитория
bash
Копировать
Редактировать
git clone https://github.com/sttewiee/blog-flask.git
# или по SSH: git clone git@github.com:sttewiee/blog-flask.git
cd blog-flask
3) Подготовка ключа для Cloud SQL
Положите сюда же cloudsql-key.json (из GCP → Service Accounts → Keys).
Проверьте:

bash
Копировать
Редактировать
ls -l cloudsql-key.json
4) Сеть Docker и Cloud SQL Proxy v2
bash
Копировать
Редактировать
docker network create blog-net || true

docker rm -f cloud-sql-proxy 2>/dev/null || true
docker run -d --name cloud-sql-proxy --restart unless-stopped --network blog-net \
  -v "$PWD/cloudsql-key.json":/secrets/key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json \
  gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.11.4 \
  --address 0.0.0.0 --port 5432 \
  sonic-harbor-465608-v1:europe-west4:blog-db
5) Сборка и запуск приложения
bash
Копировать
Редактировать
docker build -t flask-blog:local .

# сгенерируем секрет
SECRET=$(openssl rand -hex 32)

docker rm -f flask-blog 2>/dev/null || true
docker run -d --name flask-blog --restart unless-stopped --network blog-net -p 80:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY="$SECRET" \
  -e DATABASE_URL="postgresql://bloguser:blogpassword@cloud-sql-proxy:5432/blogdb" \
  flask-blog:local
6) Миграции БД
Миграции уже в репозитории. Просто примените:

bash
Копировать
Редактировать
docker exec -it flask-blog flask db upgrade
7) Проверка
bash
Копировать
Редактировать
curl -I http://localhost
# Должно быть: HTTP/1.1 200 OK
Если нужен доступ снаружи, откройте TCP/80 для ВМ в firewall’е облака.

Конфигурация
Переменные окружения
DATABASE_URL — строка подключения SQLAlchemy, пример:
postgresql://bloguser:blogpassword@cloud-sql-proxy:5432/blogdb

SECRET_KEY — любая случайная строка (для сессий).

FLASK_ENV — production | development | testing.

Cloud SQL Proxy
Мы используем v2-контейнер и слушаем 0.0.0.0:5432 внутри docker-сети blog-net.
Имя подключения (Connection name) инстанса:
sonic-harbor-465608-v1:europe-west4:blog-db.

Миграции: частые команды
bash
Копировать
Редактировать
# применить миграции
docker exec -it flask-blog flask db upgrade

# создать новую миграцию после изменения моделей
docker exec -it flask-blog flask db migrate -m "your change"

# посмотреть текущую ревизию
docker exec -it flask-blog flask db current

# если БД уже создана вручную и нужно просто «подписать» ревизию:
docker exec -it flask-blog flask db stamp head
Никогда не коммитьте cloudsql-key.json. Добавьте в .gitignore:

pgsql
Копировать
Редактировать
cloudsql-key.json
*.service-account.json
.env
Тесты локально
По умолчанию тесты запускаются на SQLite in-memory.

bash
Копировать
Редактировать
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///:memory:" SECRET_KEY="test" FLASK_ENV="testing"
pytest -v
CI/CD (что делает GitHub Actions)
test: ставит Python 3.11, зависимости, гоняет pytest на SQLite, выгружает coverage в Codecov. (Сейчас тесты не блокируют пайплайн — стоит || true.)

build-and-push: собирает Docker-образ и пушит в Artifact Registry:
us-docker.pkg.dev/sonic-harbor-465608-v1/flask-blog/flask-blog:${GITHUB_SHA}
Аутентификация — Workload Identity Federation (без JSON-ключей).

deploy (только ветка main): логинится в GKE, обновляет образ в деплойменте
kubectl -n blog-dev set image deployment/flask-blog flask-blog=$IMAGE и ждёт rollout.

Миграции в CI/CD не выполняются — их применяет контейнер при запуске командой flask db upgrade вручную, либо можно добавить это в entrypoint/отдельный Job (в будущем).