from typing import Any
from flask_mail import Mail
from redis import Redis
from redis.exceptions import ConnectionError
from minio import Minio
from tenacity import (
    retry,
    wait_exponential,
    wait_fixed,
    stop_after_attempt,
    retry_if_exception_type,
)
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

# Constants & Context
_context = "extensions"

mail = Mail()

# Redis Client Initialization
try:
    redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    logger.info("%s: Redis client initialized for %s:%d", _context, REDIS_HOST, REDIS_PORT)
except Exception as e:
    logger.exception("%s: failed to initialize Redis client", _context)
    raise

@retry(
    reraise=True,
    wait=wait_exponential(max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(ConnectionError),
)
def redis_cmd(cmd: str, *args: Any, **kwargs: Any) -> Any:
    """
    Выполняет команду cmd у redis_client с авто-retry при ConnectionError.
    """
    try:
        result = getattr(redis_client, cmd)(*args, **kwargs)
        logger.debug("%s: redis_cmd %s args=%r kwargs=%r -> %r", _context, cmd, args, kwargs, result)
        return result
    except ConnectionError as exp:
        logger.warning("%s: Redis connection lost, retrying %s: %s", _context, cmd, exp)
        raise
    except Exception:
        logger.exception("%s: unexpected error executing redis_cmd %s", _context, cmd)
        raise

# MinIO Client Initialization
try:
    minio_client = Minio(
        endpoint=MINIO_HOST,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=False,
    )
    logger.info("%s: MinIO client initialized for host %s", _context, MINIO_HOST)
except Exception:
    logger.exception("%s: failed to initialize MinIO client", _context)
    raise

BUCKET: str = MINIO_BUCKET

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(),
)
def ensure_bucket_exists() -> None:
    """
    Проверяет существование бакета и создаёт его при отсутствии (с retry).
    """
    try:
        if not minio_client.bucket_exists(BUCKET):
            minio_client.make_bucket(BUCKET)
            logger.info("%s: Created MinIO bucket %s", _context, BUCKET)
        else:
            logger.debug("%s: MinIO bucket %s already exists", _context, BUCKET)
    except Exception:
        logger.exception("%s: error ensuring MinIO bucket %s exists", _context, BUCKET)
        raise

# Guarantee Bucket on Startup
try:
    ensure_bucket_exists()
    logger.info("%s: ensure_bucket_exists completed", _context)
except Exception:
    logger.error("%s: could not ensure bucket existence", _context)
    raise
