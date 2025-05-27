#!/bin/bash
# Прерывать выполнение при ошибках
set -e

# Переход в директорию проекта
cd /root/app/yanda_shop

# Обновление кода из репозитория
git fetch --all
git reset --hard origin/main

# Остановка контейнеров и освобождение портов
docker-compose down
docker system prune -af

# ХАРД ОЧИСТКА
# docker-compose down --rmi all --volumes --remove-orphans
# docker system prune --all --volumes --force
# docker builder prune --all --force

# Обновление SSL-сертификатов (только если нужно)
certbot renew --noninteractive --standalone --agree-tos

# Пересборка и запуск контейнеров
docker-compose build --no-cache
docker-compose up -d

# Очистка старых образов
docker image prune -f
# docker image prune --force

# Проверка статуса
docker-compose ps
