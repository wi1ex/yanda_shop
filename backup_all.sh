#!/usr/bin/env bash
# --------------------------------------------
# backup_all.sh — комплексный бэкап Postgres, Redis и MinIO
# --------------------------------------------
set -euo pipefail

# 0) Load env
source /root/app/yanda_shop/.env

# 1) Dirs & timestamp
BACKUP_ROOT="/root/app/yanda_shop/backups"
PG_DIR="$BACKUP_ROOT/postgres"
REDIS_DIR="$BACKUP_ROOT/redis"
MINIO_DIR="$BACKUP_ROOT/minio"
TIMESTAMP=$(date +'%Y%m%d_%H%M')

mkdir -p "$PG_DIR" "$REDIS_DIR" "$MINIO_DIR"

# 2) PostgreSQL
echo "[1/3] PostgreSQL: $DB_NAME → $PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"
export PGPASSWORD="$DB_PASSWORD"
pg_dump -h "$DB_HOST" -U "$DB_USER" -F c -v -f "$PG_DIR/${DB_NAME}_${TIMESTAMP}.dump" "$DB_NAME"
echo "Done."

# 3) Redis
echo "[2/3] Redis RDB backup..."
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" BGSAVE
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" INFO persistence | grep -q 'rdb_bgsave_in_progress:0'; do
  sleep 1
done

# Найдём docker‐volume
REDIS_VOL=$(docker volume ls -qf "name=redis_data$")
VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")
cp "$VOL_PATH/dump.rdb" "$REDIS_DIR/redis_${TIMESTAMP}.rdb"
echo "Done → $REDIS_DIR/redis_${TIMESTAMP}.rdb"

# 4) MinIO
echo "[3/3] MinIO bucket backup..."
MC_ALIAS="shopminio"
mc alias set "$MC_ALIAS" "http://${MINIO_HOST}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4

TARGET="$MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}"
mc mirror --overwrite "$MC_ALIAS/$MINIO_BUCKET" "$TARGET"

tar czf "$MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}.tar.gz" -C "$MINIO_DIR" "${MINIO_BUCKET}_${TIMESTAMP}"
rm -rf "$TARGET"
echo "Done → $MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}.tar.gz"

# 5) Ротация >7 дней
echo "Cleaning backups older than 7 days..."
find "$BACKUP_ROOT" -type f -mtime +7 -delete

echo "All backups completed successfully."

# Установка и планирование
#
# Поместите этот скрипт, например, в ~/app/yanda_shop/backup_all.sh и сделайте его исполняемым:
# chmod +x ~/app/yanda_shop/backup_all.sh
#
# Установите MinIO Client (mc), если ещё не установлен:
# curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc
#
# Один раз настроьте alias для mc:
# mc alias set shopminio http://${MINIO_HOST} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY} --api S3v4
#
# Добавьте в crontab (ежедневно в 2:00):
# 0 2 * * * /root/app/yanda_shop/backup_all.sh >> /var/log/backup_all.log 2>&1
