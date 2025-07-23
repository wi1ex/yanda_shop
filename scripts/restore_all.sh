#!/usr/bin/env bash
set -euo pipefail
# chmod +x scripts/restore_all.sh
# scripts/restore_all.sh

# === 0) Блокировка и трапы ===
LOCKFILE="/var/lock/restore_all.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { echo "$(date '+%F %T') [ERROR] Restore already running"; exit 1; }

cleanup() {
  rc=$?
  flock -u 200
  rm -f "$LOCKFILE"
  if [ $rc -ne 0 ]; then
    echo "$(date '+%F %T') [ERROR] Restore failed (rc=$rc)"
  fi
  exit $rc
}
trap cleanup EXIT

log(){ echo "$(date '+%F %T') [INFO] $*"; }
error(){ echo "$(date '+%F %T') [ERROR] $*" >&2; }

# === 1) Подготовка ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
[ -f "$PROJECT_ROOT/.env" ] || { error ".env not found"; exit 1; }
source "$PROJECT_ROOT/.env"

: "${COMPOSE_PROJECT_NAME:=$(basename "$PROJECT_ROOT")}"
: "${DB_NAME:?DB_NAME not set}"
: "${DB_USER:?DB_USER not set}"
: "${DB_PASSWORD:?DB_PASSWORD not set}"
: "${REDIS_PASSWORD:?REDIS_PASSWORD not set}"
: "${MINIO_BUCKET:?MINIO_BUCKET not set}"

BACKUP_ROOT="$PROJECT_ROOT/backups"

# Функция для поиска последнего архива
find_latest(){
  ls -1t "$1"/*.tar.gz 2>/dev/null | head -n1
}

# === 2) Остановка сервисов ===
log "[0/6] Stopping services: backend frontend db redis minio"
docker-compose stop backend frontend db redis minio

# === 3) Восстановление PostgreSQL ===
log "[1/6] Restoring PostgreSQL"
PG_ARCHIVE=$(find_latest "$BACKUP_ROOT/postgres")
[ -f "$PG_ARCHIVE" ] || { error "Postgres archive not found"; exit 1; }
TMP=$(mktemp -d)

tar xzf "$PG_ARCHIVE" -C "$TMP"
cd "$TMP"
# Проверка целостности
sha256sum -c "${DB_NAME}.sha256"

PG_CONTAINER=$(docker-compose ps -q db)
[ -n "$PG_CONTAINER" ] || { error "Postgres container not found"; exit 1; }

docker exec -i "$PG_CONTAINER" \
  sh -c "export PGPASSWORD='$DB_PASSWORD' && pg_restore -U '$DB_USER' -d '$DB_NAME' --clean --no-owner --if-exists" \
  < "$TMP/${DB_NAME}.dump"
log "→ PostgreSQL restored from $(basename "$PG_ARCHIVE")"
rm -rf "$TMP"

# === 4) Восстановление Redis ===
log "[2/6] Restoring Redis"
REDIS_ARCHIVE=$(find_latest "$BACKUP_ROOT/redis")
[ -f "$REDIS_ARCHIVE" ] || { error "Redis archive not found"; exit 1; }
TMP=$(mktemp -d)

tar xzf "$REDIS_ARCHIVE" -C "$TMP"
cd "$TMP"
sha256sum -c "dump.sha256"

# Находим том Redis по проекту
REDIS_VOL=$(docker volume ls -q --filter name="${COMPOSE_PROJECT_NAME}_redis_data")
[ -n "$REDIS_VOL" ] || { error "Redis volume not found"; exit 1; }
MNT=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")

cp "\$PWD/dump.rdb" "$MNT/dump.rdb"
log "→ Redis restored from $(basename "$REDIS_ARCHIVE")"
rm -rf "$TMP"

# === 5) Восстановление MinIO ===
log "[3/6] Restoring MinIO bucket"
MINIO_ARCHIVE=$(find_latest "$BACKUP_ROOT/minio")
[ -f "$MINIO_ARCHIVE" ] || { error "MinIO archive not found"; exit 1; }
TMP=$(mktemp -d)

tar xzf "$MINIO_ARCHIVE" -C "$TMP"
cd "$TMP"
sha256sum -c "${MINIO_BUCKET}.sha256"

# Находим том MinIO
MINIO_VOL=$(docker volume ls -q --filter name="${COMPOSE_PROJECT_NAME}_minio_data")
[ -n "$MINIO_VOL" ] || { error "MinIO volume not found"; exit 1; }
MNT=$(docker volume inspect -f '{{ .Mountpoint }}' "$MINIO_VOL")

# Извлекаем содержимое бакета
LOGDIR="$PWD"
tar xf "${MINIO_BUCKET}.tar" -C "$MNT"
log "→ MinIO bucket '$MINIO_BUCKET' restored from $(basename "$MINIO_ARCHIVE")"
rm -rf "$TMP"

# === 6) Запуск сервисов ===
log "[5/6] Starting services: db redis minio backend frontend"
docker-compose start db redis minio backend frontend

log "Restore completed successfully"
