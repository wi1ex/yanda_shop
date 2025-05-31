#!/usr/bin/env bash
# --------------------------------------------
# backup_all.sh — комплексный бэкап Postgres, Redis и MinIO
# --------------------------------------------
set -euo pipefail

# 0) Подгружаем переменные окружения (файл .env лежит в /root/app/yanda_shop/.env)
source /root/app/yanda_shop/.env

# 1) Определяем директории и timestamp
BACKUP_ROOT="/root/app/yanda_shop/backups"
PG_DIR="$BACKUP_ROOT/postgres"
REDIS_DIR="$BACKUP_ROOT/redis"
MINIO_DIR="$BACKUP_ROOT/minio"
TIMESTAMP=$(date +'%Y%m%d_%H%M')

mkdir -p "$PG_DIR" "$REDIS_DIR" "$MINIO_DIR"

#
# 2) Бэкап PostgreSQL (через docker exec)
#
echo "[1/3] PostgreSQL (docker exec): $DB_NAME → $PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Имя контейнера с PostgreSQL. Проверьте через `docker ps`, возможно у вас другое название.
PG_CONTAINER="yanda_shop_db_1"

# Генерируем дамп внутри контейнера:
docker exec -i "$PG_CONTAINER" sh -c "export PGPASSWORD=\"$DB_PASSWORD\" && \
    pg_dump -U \"$DB_USER\" -F c -v -f \"/tmp/${DB_NAME}_${TIMESTAMP}.dump\" \"$DB_NAME\""

# Копируем его из контейнера на хост:
docker cp "${PG_CONTAINER}:/tmp/${DB_NAME}_${TIMESTAMP}.dump" "$PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Удаляем временный файл внутри контейнера:
docker exec -i "$PG_CONTAINER" rm "/tmp/${DB_NAME}_${TIMESTAMP}.dump"

echo "Done: $PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"


#
# 3) Бэкап Redis (через docker exec)
#
echo "[2/3] Redis RDB backup..."

# Имя контейнера с Redis:
REDIS_CONTAINER="yanda_shop_redis_1"

# Запрашиваем бэкап RDB (BGSAVE) внутри контейнера:
docker exec -i "$REDIS_CONTAINER" sh -c "redis-cli -a \"$REDIS_PASSWORD\" BGSAVE"

# Ждём, пока завершится BGSAVE (проверяем флаг в INFO):
while true; do
  STATUS=$(docker exec -i "$REDIS_CONTAINER" sh -c "redis-cli -a \"$REDIS_PASSWORD\" INFO persistence | grep 'rdb_bgsave_in_progress:'")
  # STATUS будет напоминать: rdb_bgsave_in_progress:0  (значение 0 значит, что фоновой сохранения нет)
  if echo "$STATUS" | grep -q 'rdb_bgsave_in_progress:0'; then
    break
  fi
  sleep 1
done

# Определяем docker-volume, в котором лежит файл dump.rdb:
REDIS_VOL=$(docker volume ls -qf "name=redis_data$")
VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")

# Копируем RDB-файл на хост:
cp "$VOL_PATH/dump.rdb" "$REDIS_DIR/redis_${TIMESTAMP}.rdb"
echo "Done → $REDIS_DIR/redis_${TIMESTAMP}.rdb"


#
# 4) Бэкап MinIO (через mc mirror)
#
echo "[3/3] MinIO bucket backup..."
# Для работы mc из этого скрипта предполагается, что вы уже один раз настроили алиас:
#   mc alias set shopminio http://${MINIO_HOST} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} --api S3v4
MC_ALIAS="shopminio"

# Каталог, куда mc будет зеркалить содержимое бакета:
TARGET="$MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}"
./mc mirror --overwrite "$MC_ALIAS/$MINIO_BUCKET" "$TARGET"

# Упаковываем в tar.gz и удаляем временный каталог:
tar czf "$MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}.tar.gz" -C "$MINIO_DIR" "${MINIO_BUCKET}_${TIMESTAMP}"
rm -rf "$TARGET"

echo "Done → $MINIO_DIR/${MINIO_BUCKET}_${TIMESTAMP}.tar.gz"


#
# 5) Ротация: удаляем файлы бэкапов старше 7 дней
#
echo "Cleaning backups older than 7 days..."
find "$BACKUP_ROOT" -type f -mtime +7 -print -delete

echo "All backups completed successfully."
