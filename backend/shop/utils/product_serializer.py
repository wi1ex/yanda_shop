import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from ..extensions import BUCKET, redis_client
from ..core.config import BACKEND_URL
from ..core.logging import logger
from ..models import Shoe, Clothing, Accessory


# Product Serialization
def serialize_product(obj: Any) -> Dict[str, Any]:
    """
    Преобразует объект продукта в dict для JSON-ответа,
    включая delivery_options и ссылки на изображения.
    """
    context = "serialize_product"
    sku = getattr(obj, "variant_sku", None)
    logger.debug("%s START variant_sku=%s", context, sku)

    data: Dict[str, Any] = {}
    try:
        # Основные поля из таблицы
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, datetime):
                data[col.name] = val.astimezone(ZoneInfo("Europe/Moscow")).isoformat(timespec="microseconds") + "Z"
            else:
                data[col.name] = val

        # Опции доставки из Redis
        raw = redis_client.get("delivery_options") or "[]"
        data["delivery_options"] = json.loads(raw)

        # Ссылки на изображения
        cnt = getattr(obj, "count_images", 0) or 0
        folder = obj.__tablename__
        images: List[str] = []
        for i in range(1, cnt + 1):
            key_path = f"{folder}/{obj.color_sku}_{i}.webp"
            images.append(f"{BACKEND_URL}/{BUCKET}/{key_path}")

        data["images"] = images
        data["image"] = images[0] if images else None

    except Exception as exc:
        logger.exception("%s: failed to serialize product %s", context, sku, exc_info=exc)
        return {}

    logger.debug("%s END variant_sku=%s", context, sku)
    return data


# Category Model Mapping
def model_by_category(cat: str) -> Optional[type]:
    """
    Возвращает SQLAlchemy-модель по названию категории cat.
    """
    context = "model_by_category"
    key = cat.strip().lower()

    mapping: Dict[str, Any] = {
        "shoes":       Shoe,
        "clothing":    Clothing,
        "accessories": Accessory,
        "обувь":       Shoe,
        "одежда":      Clothing,
        "аксессуары":  Accessory,
    }

    model = mapping.get(key)
    if model:
        logger.debug("%s: category '%s' -> model %s", context, cat, model.__name__)
    else:
        logger.warning("%s: unknown category '%s'", context, cat)

    return model
