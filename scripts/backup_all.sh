#!/usr/bin/env bash
set -euo pipefail

# 0) Определяем корень проекта и проверяем .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$PROJECT_ROOT/.env" ] || { echo ".env not found in $PROJECT_ROOT"; exit 1; }
source "$PROJECT_ROOT/.env"

TIMESTAMP="$(date +'%Y%m%d_%H%M')"
BACKUP_ROOT="$PROJECT_ROOT/backups"
PG_DIR="$BACKUP_ROOT/postgres"
REDIS_DIR="$BACKUP_ROOT/redis"
MINIO_DIR="$BACKUP_ROOT/minio"
mkdir -p "$PG_DIR" "$REDIS_DIR" "$MINIO_DIR"

# 1) PostgreSQL backup
echo "[1/3] PostgreSQL: ${DB_NAME} → $PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"
PG_CONTAINER="${PG_CONTAINER:-$(docker-compose ps -q db)}"
[ -n "$PG_CONTAINER" ] || { echo "Postgres container not found"; exit 1; }
docker exec "$PG_CONTAINER" \
  sh -c "export PGPASSWORD=\"$DB_PASSWORD\" && pg_dump -U \"$DB_USER\" -F c \"$DB_NAME\"" \
  > "$PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"
echo "→ $PG_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# 2) Redis RDB backup
echo "[2/3] Redis RDB backup"
REDIS_CONTAINER="${REDIS_CONTAINER:-$(docker-compose ps -q redis)}"
: "${REDIS_CONTAINER:?Redis container not found}"
docker exec "$REDIS_CONTAINER" \
  sh -c "redis-cli --no-auth-warning -a '$REDIS_PASSWORD' BGSAVE" \
  >/dev/null 2>&1

timeout=30; elapsed=0
while true; do
  status=$(docker exec "$REDIS_CONTAINER" \
    sh -c "redis-cli --no-auth-warning -a '$REDIS_PASSWORD' INFO persistence" 2>/dev/null \
    | awk -F: '/^rdb_bgsave_in_progress:/ {print $2}' \
    | tr -d '\r')
  [ "$status" = "0" ] && break
  (( elapsed++ )) || true
  [ $elapsed -ge $timeout ] && { echo "Error: Redis BGSAVE timeout"; exit 1; }
  sleep 1
done

REDIS_VOL=$(docker volume ls -q | grep redisdata | head -n1)
: "${REDIS_VOL:?Redis volume not found}"
VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")
cp "$VOL_PATH/dump.rdb" "$REDIS_DIR/redis_${TIMESTAMP}.rdb"
echo "→ $REDIS_DIR/redis_${TIMESTAMP}.rdb"

# 3) MinIO backup
echo "[3/3] MinIO bucket backup"
MINIO_VOL=$(docker volume ls -q | grep miniodata | head -n1)
: "${MINIO_VOL:?MinIO volume not found}"
VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$MINIO_VOL")

[ -d "$VOL_PATH/${MINIO_BUCKET_NAME}" ] || {
  echo "Error: bucket directory $VOL_PATH/${MINIO_BUCKET_NAME} not found"
  exit 1
}

TARGET_ARCHIVE="$MINIO_DIR/${MINIO_BUCKET_NAME}_${TIMESTAMP}.tar.gz"
tar czf "$TARGET_ARCHIVE" -C "$VOL_PATH" "${MINIO_BUCKET_NAME}"
echo "→ $TARGET_ARCHIVE"

# 4) Ротация
echo "Cleaning backups >7 days"
find "$BACKUP_ROOT" -type f -mtime +7 -delete

echo "Backup completed successfully"
