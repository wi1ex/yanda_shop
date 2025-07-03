from redis import Redis
from redis.exceptions import ConnectionError
from minio import Minio
from tenacity import retry, wait_exponential, wait_fixed, stop_after_attempt, retry_if_exception_type
from .core.logging import logger
from .core.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    MINIO_HOST,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
    MINIO_BUCKET,
)

# ——— Redis client + retry ———
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
)
logger.debug("Redis client initialized for %s:%s", REDIS_HOST, REDIS_PORT)

@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(ConnectionError)
)
def redis_cmd(cmd: str, *args, **kwargs):
    """
    Выполняет команду cmd у redis_client с авто-retry при ConnectionError.
    """
    try:
        return getattr(redis_client, cmd)(*args, **kwargs)
    except ConnectionError as e:
        logger.warning("Redis connection lost, retrying %s: %s", cmd, e)
        raise


# ——— MinIO client + retry ———
minio_client = Minio(
    endpoint=MINIO_HOST,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)
logger.debug("MinIO client initialized for host %s", MINIO_HOST)

BUCKET: str = MINIO_BUCKET

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(Exception)
)
def _ensure_bucket():
    """
    Проверяем/создаём бакет с retry.
    """
    if not minio_client.bucket_exists(BUCKET):
        minio_client.make_bucket(BUCKET)
        logger.info("Created MinIO bucket %s", BUCKET)
    else:
        logger.debug("MinIO bucket %s already exists", BUCKET)

# Гарантируем существование бакета сразу при импорте
_ensure_bucket()
