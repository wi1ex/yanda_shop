from cors.logging import logger
from redis import Redis
from minio import Minio
from cors.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    MINIO_HOST,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
    MINIO_BUCKET,
)


# Redis клиент
redis_client: Redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)
logger.debug("Redis client initialized for %s:%s", REDIS_HOST, REDIS_PORT)

# MinIO клиент
minio_client: Minio = Minio(
    endpoint=MINIO_HOST,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)
logger.debug("MinIO client initialized for host %s", MINIO_HOST)

BUCKET: str = MINIO_BUCKET

def _ensure_bucket() -> None:
    try:
        if not minio_client.bucket_exists(BUCKET):
            minio_client.make_bucket(BUCKET)
            logger.info("Created MinIO bucket %s", BUCKET)
        else:
            logger.debug("MinIO bucket %s already exists", BUCKET)
    except Exception as e:
        logger.exception("Error ensuring MinIO bucket %s exists: %s", BUCKET, e)
        raise

# Проверяем бакет сразу при импорте
_ensure_bucket()
