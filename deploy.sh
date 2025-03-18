#!/bin/bash
# Прерывать выполнение при ошибках
set -e

# Переход в директорию проекта
cd /root/app/telegram_test

# Обновление кода из репозитория
git fetch --all
git reset --hard origin/main

# Остановка контейнеров и освобождение портов
docker-compose down
docker system prune -af

# Обновление SSL-сертификатов (только если нужно)
certbot renew --noninteractive --standalone --agree-tos

# Пересборка и запуск контейнеров
docker-compose build --no-cache
docker-compose up -d

# Очистка старых образов
docker image prune -f

# Проверка статуса
docker-compose ps
