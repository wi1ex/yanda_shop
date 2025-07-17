import json
from typing import List, Dict, Any
from sqlalchemy import or_
from .db_utils import session_scope
from ..core.logging import logger
from ..extensions import redis_client
from ..models import AdminSetting


# Client Options Cache
def load_parameters() -> None:
    """
    Загружает все faq_question_*, faq_answer_*, url_social_* и info_* из БД в Redis.
    Вызывать при старте и после изменений в админке.
    """
    context = "load_parameters"
    logger.info("%s START", context)
    try:
        with session_scope() as session:
            settings = session.query(AdminSetting).filter(
                or_(
                    AdminSetting.key.like("faq_question_%"),
                    AdminSetting.key.like("faq_answer_%"),
                    AdminSetting.key.like("url_social_%"),
                    AdminSetting.key.like("info_%"),
                )
            ).all()
            payload = {s.key: s.value or "" for s in settings}
            redis_client.set("parameters", json.dumps(payload))
            logger.info("%s END loaded_count=%d", context, len(payload))
    except Exception as exc:
        logger.exception("%s: failed to load parameters", context, exc_info=exc)


# Delivery Options Cache
def load_delivery_options() -> None:
    """
    Загружает delivery_time_i и delivery_price_i из БД в Redis.
    После обновления настроек доставки нужно вызвать снова.
    """
    context = "load_delivery_options"
    logger.info("%s START", context)
    opts: List[Dict[str, Any]] = []

    try:
        with session_scope() as session:
            for i in range(1, 4):
                time_key = f"delivery_time_{i}"
                price_key = f"delivery_price_{i}"
                st_time = session.get(AdminSetting, time_key)
                st_price = session.get(AdminSetting, price_key)

                if not st_time or not st_price:
                    logger.debug("%s: missing setting for keys %s / %s", context, time_key, price_key)
                    continue

                try:
                    multiplier = float(st_price.value)
                except (TypeError, ValueError) as exc:
                    logger.warning("%s: invalid price for %s: %s", context, price_key, exc)
                    continue

                opts.append({"label": st_time.value, "multiplier": multiplier})

    except Exception as exc:
        logger.exception("%s: unexpected error loading delivery options", context, exc_info=exc)
        return

    redis_client.set("delivery_options", json.dumps(opts))
    logger.info("%s END loaded_count=%d", context, len(opts))


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
