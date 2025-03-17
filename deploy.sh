#!/bin/bash

# Переход в директорию проекта (если скрипт запускается из другой папки)
cd /root/app/telegram_test  # Укажите полный путь к папке с docker-compose.yml

# Обновление кода из репозитория
git pull origin main

# Пересборка контейнеров
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Опционально: очистка старых образов
docker image prune -f

curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${ADMIN_ID}&text=Deploy+successful"