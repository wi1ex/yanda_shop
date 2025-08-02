from datetime import datetime
from zoneinfo import ZoneInfo
from ..core.logging import logger
from ..extensions import redis_client

def track_visit_counts(raw_id: str) -> None:
    # Redis: track visit counts
    try:
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")
        total_key = f"visits:{date_str}:{hour_str}:total"
        unique_key = f"visits:{date_str}:{hour_str}:unique"

        redis_client.incr(total_key)
        redis_client.sadd(unique_key, raw_id)
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(total_key, ttl)
        redis_client.expire(unique_key, ttl)

        logger.debug("save_user: Redis visit counters updated for %r", raw_id)
    except Exception:
        logger.exception("save_user: Redis error")
