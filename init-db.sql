-- Инициализация базы данных для Flask Blog
-- Этот скрипт выполняется автоматически при первом запуске PostgreSQL контейнера

-- Создаем базу данных blogdb если её нет
SELECT 'CREATE DATABASE blogdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'blogdb')\gexec

-- Подключаемся к базе blogdb
\c blogdb;

-- Создаем пользователя bloguser если его нет
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'bloguser') THEN
        CREATE USER bloguser WITH PASSWORD 'blogpassword';
    END IF;
END
$$;

-- Даем права пользователю
GRANT ALL PRIVILEGES ON DATABASE blogdb TO bloguser;
GRANT ALL PRIVILEGES ON SCHEMA public TO bloguser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bloguser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bloguser;

-- Устанавливаем права по умолчанию для будущих таблиц
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bloguser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bloguser;

-- Возвращаемся к postgres для совместимости
\c postgres;
