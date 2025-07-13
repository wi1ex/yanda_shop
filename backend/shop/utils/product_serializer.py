from datetime import datetime
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from ..extensions import BUCKET
from ..core.config import BACKEND_URL
from ..core.logging import logger
from ..models import AdminSetting, Shoe, Clothing, Accessory
from .db_utils import session_scope


# Delivery Options Cache
_delivery_options: List[Dict[str, Any]] = []

def load_delivery_options() -> None:
    """
    Загружает delivery_time_i и delivery_price_i из БД в _delivery_options.
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

    _delivery_options.clear()
    _delivery_options.extend(opts)
    logger.info("%s END loaded_count=%d", context, len(opts))


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

        # Опции доставки из кэша
        data["delivery_options"] = list(_delivery_options)

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
