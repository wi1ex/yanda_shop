from datetime import datetime
from typing import Tuple, Optional, List, Dict
from zoneinfo import ZoneInfo
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..models import AdminSetting, Shoe
from ..utils.parsers import parse_int, parse_float, normalize_str
from ..utils.product_serializer import model_by_category


def get_sheet_url(category: str) -> Optional[str]:
    key = f"sheet_url_{category}"
    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        return setting.value if setting else None


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int]:
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    logger.info("process_rows START category=%s rows=%d", category, len(rows))
    with session_scope() as session:
        # 1) получаем существующие объекты
        variants = [r["variant_sku"].strip() for r in rows]
        existing = {obj.variant_sku: obj for obj in session.query(Model).filter(Model.variant_sku.in_(variants)).all()}

        # 2) перебор всех строк
        for row in rows:
            variant = row["variant_sku"].strip()
            data = {k: row[k].strip() for k in row if k != "variant_sku"}

            # 2a) удаление
            if variant and all(not v for v in data.values()):
                obj = existing.get(variant)
                if obj:
                    session.delete(obj)
                    deleted += 1
                continue

            obj = existing.get(variant)
            if not obj:
                # 2b) создание
                obj = Model(variant_sku=variant)
                for k, v in data.items():
                    if not hasattr(obj, k):
                        continue
                    # примеры парсинга
                    if k in ("price", "count_in_stock", "count_images", "size_category"):
                        val = parse_int(v)
                        if val is None:
                            warns += 1
                    elif k in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                        val = parse_float(v)
                        if val is None:
                            warns += 1
                    else:
                        val = normalize_str(v)
                    setattr(obj, k, val)

                obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                session.add(obj)
                added += 1

            else:
                # 2c) обновление
                has_changes = False
                for k, v in data.items():
                    if not hasattr(obj, k):
                        continue
                    if k in ("price", "count_in_stock", "count_images", "size_category"):
                        new_val = parse_int(v)
                        if new_val is None:
                            warns += 1
                    elif k in ("chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"):
                        new_val = parse_float(v)
                        if new_val is None:
                            warns += 1
                    else:
                        new_val = normalize_str(v)
                    if getattr(obj, k) != new_val:
                        setattr(obj, k, new_val)
                        has_changes = True

                # проверим color_sku
                new_cs = f"{obj.sku}_{obj.world_sku}"
                if obj.color_sku != new_cs:
                    obj.color_sku = new_cs
                    has_changes = True

                if has_changes:
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1

    logger.info("process_rows END category=%s added=%d updated=%d deleted=%d warns=%d",
                category, added, updated, deleted, warns)
    return added, updated, deleted, warns
