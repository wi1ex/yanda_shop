#!/usr/bin/env bash
set -euo pipefail

# Обновляем код
cd /root/app/yanda_shop
git fetch --all
git reset --hard origin/main

# Останавливаем прежние контейнеры и чистим ненужное
docker-compose down
docker builder prune --filter "until=72h" --force
docker image prune --filter "until=72h" --force

# Для полной очистки
# docker-compose down --rmi all --volumes --remove-orphans
# docker system prune --all --volumes --force

# Обновление SSL-сертификатов (только если нужно)
certbot renew --noninteractive --standalone --agree-tos

# Пересобираем образы
docker-compose build --no-cache

# Поднимаем образы
docker-compose up -d

# Применяем миграции в свежесобранном образе
docker-compose run --rm backend flask db upgrade

# Финальная проверка и логи
docker-compose ps
docker-compose logs -f
