#!/usr/bin/env bash
set -euo pipefail

# 0) Определяем корень проекта и проверяем .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$PROJECT_ROOT/.env" ] || { echo ".env not found in $PROJECT_ROOT"; exit 1; }
source "$PROJECT_ROOT/.env"

# 1) Останавливаем write-сервисы, чтобы никто не писал во время восстановления
echo "[0/3] Stopping services: backend, frontend, redis"
docker-compose stop backend frontend redis

# 2) PostgreSQL restore
echo "[1/3] Restoring PostgreSQL"
PG_DUMP_DIR="$PROJECT_ROOT/backups/postgres"
DUMP_FILE=$(ls -1t "$PG_DUMP_DIR"/"${DB_NAME}"_*.dump 2>/dev/null | head -n1)
[ -f "$DUMP_FILE" ] || { echo "Error: No PostgreSQL dump file found in $PG_DUMP_DIR"; exit 1; }

PG_CONTAINER="${PG_CONTAINER:-$(docker-compose ps -q db)}"
[ -n "$PG_CONTAINER" ] || { echo "Error: Postgres container not found"; exit 1; }

docker exec -i "$PG_CONTAINER" \
  sh -c "export PGPASSWORD=\"$DB_PASSWORD\" && \
         pg_restore -U \"$DB_USER\" \
           -d \"$DB_NAME\" --clean --no-owner --if-exists" \
  < "$DUMP_FILE"

echo "→ PostgreSQL restored from $(basename "$DUMP_FILE")"

# 3) Redis restore
echo "[2/3] Restoring Redis"
REDIS_CONTAINER="${REDIS_CONTAINER:-$(docker-compose ps -q redis)}"
[ -n "$REDIS_CONTAINER" ] || { echo "Error: Redis container not found"; exit 1; }

# Определяем том Redis по шаблону
REDIS_VOL=$(docker volume ls -q | grep redisdata | head -n1)
[ -n "$REDIS_VOL" ] || { echo "Error: Redis volume not found"; exit 1; }

VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")

RDB_DIR="$PROJECT_ROOT/backups/redis"
RDB_FILE=$(ls -1t "$RDB_DIR"/redis_*.rdb 2>/dev/null | head -n1)
[ -f "$RDB_FILE" ] || { echo "Error: No Redis RDB file found in $RDB_DIR"; exit 1; }

cp "$RDB_FILE" "$VOL_PATH/dump.rdb"
echo "→ Redis restored from $(basename "$RDB_FILE")"

# 4) MinIO restore
echo "[3/3] Restoring MinIO bucket data"
MINIO_VOL=$(docker volume ls -q | grep miniodata | head -n1)
[ -n "$MINIO_VOL" ] || { echo "Error: MinIO volume not found"; exit 1; }

VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$MINIO_VOL")

MINIO_BACKUP_DIR="$PROJECT_ROOT/backups/minio"
ARCHIVE=$(ls -1t "$MINIO_BACKUP_DIR"/"${MINIO_BUCKET_NAME}"_*.tar.gz 2>/dev/null | head -n1)
[ -f "$ARCHIVE" ] || { echo "Error: No MinIO archive found in $MINIO_BACKUP_DIR"; exit 1; }

tar xzf "$ARCHIVE" -C "$VOL_PATH"
echo "→ MinIO restored from $(basename "$ARCHIVE")"

# 5) Запускаем сервисы обратно
echo "[4/3] Starting services: redis, backend, frontend"
docker-compose start redis backend frontend

echo "=== Restore completed successfully ==="
