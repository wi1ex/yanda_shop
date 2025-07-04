from datetime import datetime
from typing import Optional, List, Dict, Tuple
from zoneinfo import ZoneInfo
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..models import AdminSetting
from ..utils.parsers import parse_int, parse_float, normalize_str
from ..utils.product_serializer import model_by_category


def get_sheet_url(category: str) -> Optional[str]:
    """
    Возвращает URL Google Sheets для заданной категории или None.
    """
    context = "get_sheet_url"
    logger.info("%s START category=%s", context, category)
    key = f"sheet_url_{category}"
    try:
        with session_scope() as session:
            setting = session.get(AdminSetting, key)
            url = setting.value if setting else None
    except Exception:
        logger.exception("%s: failed to get sheet URL for %s", context, category)
        return None
    else:
        logger.info("%s END url=%s", context, url)
        return url


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int]:
    """
    Обрабатывает список строк из CSV для категории category:
      - добавляет новые записи
      - обновляет существующие
      - удаляет пустые
    Возвращает (added, updated, deleted, warns).
    """
    context = "process_rows"
    logger.info("%s START category=%s rows=%d", context, category, len(rows))

    Model = model_by_category(category)
    if Model is None:
        logger.error("%s: unknown category '%s'", context, category)
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    try:
        with session_scope() as session:
            # Получаем существующие объекты
            variants = [row.get("variant_sku", "").strip() for row in rows]
            existing_objs = session.query(Model).filter(Model.variant_sku.in_(variants)).all()
            existing_map = {obj.variant_sku: obj for obj in existing_objs}

            for row in rows:
                variant = row.get("variant_sku", "").strip()
                data = {k: v.strip() for k, v in row.items() if k != "variant_sku"}

                # 1) Удаление: все поля пустые
                if variant and all(not v for v in data.values()):
                    obj = existing_map.get(variant)
                    if obj:
                        session.delete(obj)
                        deleted += 1
                        logger.debug("%s: deleted variant=%s", context, variant)
                    continue

                obj = existing_map.get(variant)
                if obj is None:
                    # 2) Создание нового объекта
                    obj = Model(variant_sku=variant)
                    for field, val_str in data.items():
                        if not hasattr(obj, field):
                            continue
                        if field in ("price", "count_in_stock", "count_images", "size_category"):
                            val = parse_int(val_str)
                        elif field in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                            val = parse_float(val_str)
                        else:
                            val = normalize_str(val_str)
                        if val is None:
                            warns += 1
                        setattr(obj, field, val)

                    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                    session.add(obj)
                    added += 1
                    logger.debug("%s: added variant=%s", context, variant)

                else:
                    # 3) Обновление существующего
                    has_changes = False
                    for field, val_str in data.items():
                        if not hasattr(obj, field):
                            continue
                        if field in ("price", "count_in_stock", "count_images", "size_category"):
                            new_val = parse_int(val_str)
                        elif field in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                            new_val = parse_float(val_str)
                        else:
                            new_val = normalize_str(val_str)

                        if new_val is None:
                            warns += 1
                        if getattr(obj, field) != new_val:
                            setattr(obj, field, new_val)
                            has_changes = True

                    # Проверяем и обновляем color_sku
                    new_cs = f"{obj.sku}_{obj.world_sku}"
                    if getattr(obj, "color_sku", None) != new_cs:
                        obj.color_sku = new_cs
                        has_changes = True

                    if has_changes:
                        obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                        updated += 1
                        logger.debug("%s: updated variant=%s", context, variant)

    except Exception:
        logger.exception("%s: error processing rows for category=%s", context, category)
        raise
    else:
        logger.info("%s END added=%d updated=%d deleted=%d warns=%d", context, added, updated, deleted, warns)
        return added, updated, deleted, warns
