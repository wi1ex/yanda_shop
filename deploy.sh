#!/usr/bin/env bash
set -euo pipefail

# Обновляем код
cd /root/app/yanda_shop
git fetch --all
git reset --hard origin/main

# Останавливаем прежние контейнеры и чистим ненужное
docker-compose down
docker image prune -f
# docker-compose down --rmi all --volumes --remove-orphans
# docker system prune --all --volumes --force

# Обновление SSL-сертификатов (только если нужно)
certbot renew --noninteractive --standalone --agree-tos

# Пересобираем образы
docker-compose build --no-cache

# Поднимаем БД, Redis и MinIO
docker-compose up -d db redis minio

# Ждём, пока Postgres начнёт отвечать
echo "⏳ Ждём Postgres…"
until docker-compose exec -T db pg_isready -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 1
done
echo "✅ Postgres готов"

# Ждём, пока Redis выйдет на связь
echo "⏳ Ждём Redis…"
until docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" ping | grep -q PONG; do
  sleep 1
done
echo "✅ Redis готов"

# Применяем миграции в свежесобранном образе
echo "🚀 Применяем миграции"
docker-compose run --rm backend flask db upgrade

# Теперь поднимаем остальные сервисы
docker-compose up -d backend bot frontend proxy

# Финальная проверка и логи
docker-compose ps
docker-compose logs -f
