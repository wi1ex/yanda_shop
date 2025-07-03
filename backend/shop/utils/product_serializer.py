from datetime import datetime
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from ..core.config import BACKEND_URL
from ..utils.db_utils import session_scope
from ..models import AdminSetting, Shoe, Clothing, Accessory


# Сериализация товара
_delivery_options: List[Dict[str, Any]] = []
def load_delivery_options():
    """
    Загружает delivery_time_i и delivery_price_i из БД в _delivery_options
    !!! При изменении delivery_time или delivery_price обязательно вызывать load_delivery_options()
    - load_delivery_options()
    - logger.info("Delivery options reloaded after admin update")
    """
    global _delivery_options
    opts = []
    with session_scope() as session:
        for i in range(1, 4):
            st_time  = session.get(AdminSetting, f"delivery_time_{i}")
            st_price = session.get(AdminSetting, f"delivery_price_{i}")
            if st_time and st_price:
                opts.append({
                    "label":      st_time.value,
                    "multiplier": float(st_price.value)
                })
    _delivery_options = opts


def serialize_product(obj):
    data = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            data[col.name] = val.astimezone(ZoneInfo("Europe/Moscow")).isoformat(timespec="microseconds") + "Z"
        else:
            data[col.name] = val

    # delivery_options — берем из заранее загруженного кэша (_delivery_options)
    data["delivery_options"] = _delivery_options

    # картинки
    cnt = getattr(obj, "count_images", 0) or 0
    folder = obj.__tablename__
    images = [f"{BACKEND_URL}/images/{folder}/{obj.color_sku}_{i}.webp" for i in range(1, cnt+1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    return data


# Каталог моделей по категории
def model_by_category(cat: str) -> Optional[type]:
    return {"shoes": Shoe, "clothing": Clothing, "accessories": Accessory,
            "обувь": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat.lower())
