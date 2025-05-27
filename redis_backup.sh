#!/bin/bash
set -e
source /root/app/yanda_shop/.env

BACKUP_DIR="/root/app/yanda_shop/backups/redis"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +'%Y%m%d_%H%M')
FILENAME="redis_dump_${TIMESTAMP}.rdb"

# форсируем сохранение
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" BGSAVE

# ждём, пока появится новый RDB (можно паузу)
sleep 5

# копируем файл из тома
cp /var/lib/docker/volumes/$(docker volume ls -qf name=redis_data)/_data/dump.rdb "$BACKUP_DIR/$FILENAME"

# чистим старше 7 дней
find "$BACKUP_DIR" -type f -mtime +7 -name "redis_dump_*.rdb" -delete

# Ежедневный бэкап Redis в 4:00
# 0 4 * * * /root/app/telegram_test/scripts/redis_backup.sh >> /var/log/redis_backup.log 2>&1

# При перезагрузке
# @reboot /root/app/telegram_test/scripts/redis_backup.sh >> /var/log/redis_backup.log 2>&1
