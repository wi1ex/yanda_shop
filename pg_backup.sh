#!/bin/bash
set -e
source /root/app/yanda_shop/.env

BACKUP_DIR="/root/app/yanda_shop/backups/postgres"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +'%Y%m%d_%H%M')
FILENAME="${DB_NAME}_${TIMESTAMP}.dump"

PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h "$DB_HOST" \
  -U "$DB_USER" \
  -F c \
  -v \
  -f "$BACKUP_DIR/$FILENAME" \
  "$DB_NAME"

# Удаляем бэкапы старше 7 дней
find "$BACKUP_DIR" -type f -mtime +7 -name "*.dump" -delete

# Каждый день в 3:30 утра бэкап PostgreSQL
# 30 3 * * * /root/app/yanda_shop/scripts/pg_backup.sh >> /var/log/pg_backup.log 2>&1

# При каждой перезагрузке сервера сразу сделать бэкап «среза»
# @reboot /root/app/yanda_shop/scripts/pg_backup.sh >> /var/log/pg_backup.log 2>&1

# Тест восстановления
# PGPASSWORD="$DB_PASSWORD" pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" /root/app/yanda_shop/backups/postgres/yourfile.dump
