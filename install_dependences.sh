#!/bin/bash

echo "Установка системных пакетов"
sudo apt-get update
sudo apt-get install -y python3-dev libpq-dev postgresql postgresql-contrib

echo "Обновление wheel и setuptools"
pip install --upgrade wheel setuptools

echo "Установка psycopg2"
pip install psycopg2

echo "Установка RPi.GPIO"
pip install RPi.GPIO

echo "Настройка PostgreSQL"
sudo service postgresql start

# Создание БД и пользователя
sudo -u postgres psql <<EOF
DO \$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'robot') THEN
        CREATE USER robot WITH PASSWORD 'Access_for_robot_12345';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'warehouse_db') THEN
        CREATE DATABASE warehouse_db;
    END IF;
END
\$$;
ALTER USER robot CREATEDB SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO robot;
\c warehouse_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO robot;
EOF

echo "Настройка завершена"