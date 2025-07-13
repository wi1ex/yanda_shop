import json
from ..extensions import redis_client
from ..core.logging import logger


# Cache utils: Redis JSON access
def cache_get(key: str):
    """
    Получить значение из Redis по ключу, десериализуя JSON.
    Если ключ не найден или при ошибке — возвращает None.
    """
    context = "cache_get"
    logger.info("%s START key=%s", context, key)
    raw = redis_client.get(key)
    if not raw:
        logger.debug("%s: key not found %s", context, key)
        return None
    try:
        value = json.loads(raw)
        logger.info("%s END loaded", context)
        return value
    except json.JSONDecodeError:
        logger.exception("%s: JSON decode error for key %s", context, key)
        return None


def cache_set(key: str, value, ttl_seconds: int):
    """
    Сохранить в Redis значение value (сериализует в JSON) с TTL в секундах.
    """
    context = "cache_set"
    logger.info("%s START key=%s ttl=%s", context, key, ttl_seconds)
    try:
        payload = json.dumps(value)
        redis_client.set(key, payload)
        redis_client.expire(key, ttl_seconds)
        logger.info("%s END stored", context)
    except Exception:
        logger.exception("%s: failed to set key %s", context, key)
