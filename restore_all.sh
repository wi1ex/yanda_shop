#!/usr/bin/env bash
set -euo pipefail

# 1. Останавливаем сервисы, чтобы никто не писал в БД/Redis/MinIO во время restore
docker-compose stop backend bot frontend proxy redis

# 2. Восстанавливаем PostgreSQL
echo "[1/3] Восстановление PostgreSQL..."
cd /root/app/yanda_shop/backups/postgres
DUMP_FILE=$(ls -1t shop_db_*.dump | head -n1)   # берём последний по дате дамп
PG_CONTAINER="yanda_shop_db_1"
docker cp "${DUMP_FILE}" "${PG_CONTAINER}:/tmp/restore.dump"
docker exec -i "${PG_CONTAINER}" sh -c "\
  export PGPASSWORD=\"$DB_PASSWORD\" && \
  pg_restore -U \"$DB_USER\" -d \"$DB_NAME\" --clean --no-owner --if-exists /tmp/restore.dump \
"
docker exec -i "${PG_CONTAINER}" sh -c "rm -f /tmp/restore.dump"
echo "[OK] PostgreSQL восстановлен из ${DUMP_FILE}"

# 3. Восстанавливаем Redis
echo "[2/3] Восстановление Redis..."
REDIS_CONTAINER="yanda_shop_redis_1"
REDIS_VOL=$(docker volume ls -qf "name=redis_data$")
VOL_PATH=$(docker volume inspect -f '{{ .Mountpoint }}' "$REDIS_VOL")
RDB_FILE=$(ls -1t /root/app/yanda_shop/backups/redis/redis_*.rdb | head -n1)
cp "$RDB_FILE" "${VOL_PATH}/dump.rdb"
echo "[OK] Redis восстановлен из $(basename "$RDB_FILE")"

# 4. Восстанавливаем MinIO
echo "[3/3] Восстановление MinIO..."
cd /root/app/yanda_shop/backups/minio
ARCHIVE=$(ls -1t ${MINIO_BUCKET}_*.tar.gz | head -n1)
tar xzf "$ARCHIVE"   # распакует, например, product-images_20250531_1744/
DIRNAME=${ARCHIVE%.tar.gz}
# Устанавливаем aliас (чтобы mc знал, куда копать):
./mc alias set shopminio http://127.0.0.1:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}" --api S3v4
# Mirror обратно с удалением лишнего:
./mc mirror --overwrite --remove "${DIRNAME}" "shopminio/${MINIO_BUCKET}"
# Удаляем распакованную папку, если нужно:
rm -rf "${DIRNAME}"
echo "[OK] MinIO восстановлен из ${ARCHIVE}"

# 5. Запускаем все сервисы
docker-compose start redis backend bot frontend proxy
echo "=== Восстановление завершено успешно! ==="
