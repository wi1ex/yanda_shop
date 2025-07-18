import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from zoneinfo import ZoneInfo
from .db_utils import session_scope
from .parsers import parse_int, parse_float, normalize_str
from .product_serializer import model_by_category
from ..core.logging import logger
from ..models import AdminSetting


# Google Sheets utilities
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
            logger.info("%s END url=%s", context, url)
            return url
    except Exception:
        logger.exception("%s: failed to fetch sheet URL for %s", context, category)
        return None


SKU_PATTERN    = re.compile(r"^[^_]+_[^_]+_.+")
VALID_GENDERS  = {"U", "F", "M"}
VALID_CATS     = {"Обувь", "Одежда", "Аксессуары"}
OPTIONAL_EMPTY = {"description", "width_cm", "height_cm", "depth_cm", "chest_cm", "depth_mm"}
INT_FIELDS     = {"price", "count_in_stock", "count_images", "size_category"}
FLOAT_FIELDS   = {"chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"}

def validate_row(row: Dict[str, str]) -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
    """
    Валидация одной строки:
      - variant_sku, gender, category
      - обязательные поля не пусты
    Возвращает tuple(variant_sku, clean_data, error_sku):
      • если всё ок — возвращается (variant, data, None)
      • иначе — (variant, None, variant)
    """
    variant = row.get("variant_sku", "").strip()
    if not SKU_PATTERN.match(variant):
        return variant, None, variant

    gender = row.get("gender", "").strip()
    if gender not in VALID_GENDERS:
        return variant, None, variant

    cat_val = row.get("category", "").strip()
    if cat_val not in VALID_CATS:
        return variant, None, variant

    # собираем и чистим поля
    data = {k: v.strip() for k, v in row.items() if k != "variant_sku"}
    # проверяем непустоту обязательных
    missing = [fld for fld, val in data.items() if not val and fld not in OPTIONAL_EMPTY]
    if missing:
        return variant, None, variant

    return variant, data, None


# Creation / Update helpers
def apply_creation(obj, data: Dict[str, str], warn_skus: List[str], context: str) -> Tuple[int, int]:
    """
    Заполняет и сохраняет новый объект из data.
    Возвращает (1_added, warns_increment).
    """
    warns = 0
    for field, val_str in data.items():
        if not hasattr(obj, field):
            continue
        # int-поля
        if field in INT_FIELDS:
            val = parse_int(val_str)
            if val is None or val < 0:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: invalid int %s='%s' for %s", context, field, val_str, obj.variant_sku)
                continue
        # float-поля
        elif field in FLOAT_FIELDS:
            val = parse_float(val_str)
            if val is None or val < 0:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: invalid float %s='%s' for %s", context, field, val_str, obj.variant_sku)
                continue
        # остальные
        else:
            val = normalize_str(val_str)

        setattr(obj, field, val)
    # финальное поле
    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
    return 1, warns


def apply_update(obj, data: Dict[str, str], warn_skus: List[str], context: str) -> Tuple[int, int]:
    """
    Обновляет существующий объект полями из data.
    Возвращает (1_updated, warns_increment).
    """
    updated = warns = 0
    has_changes = False
    for field, val_str in data.items():
        if not hasattr(obj, field):
            continue
        if field in INT_FIELDS:
            new_val = parse_int(val_str)
            if new_val is None or new_val < 0:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: invalid int %s='%s' for %s", context, field, val_str, obj.variant_sku)
                continue
        elif field in FLOAT_FIELDS:
            new_val = parse_float(val_str)
            if new_val is None or new_val < 0:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: invalid float %s='%s' for %s", context, field, val_str, obj.variant_sku)
                continue
        else:
            new_val = normalize_str(val_str)

        if getattr(obj, field) != new_val:
            setattr(obj, field, new_val)
            has_changes = True

    # пересчитать color_sku
    new_cs = f"{obj.sku}_{obj.world_sku}"
    if obj.color_sku != new_cs:
        obj.color_sku = new_cs
        has_changes = True

    if has_changes:
        obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
        updated = 1
    return updated, warns


def preview_rows(category: str, rows: List[Dict[str, str]]) -> List[str]:
    """
    Превью-валидация CSV-строк для категории category:
      - вызывает validate_row для базовой проверки
      - дополнительно парсит INT_FIELDS и FLOAT_FIELDS
    Возвращает упорядоченный список уникальных variant_sku с ошибками.
    """
    context = "preview_rows"
    logger.info("%s START category=%s rows=%d", context, category, len(rows))

    # 0) Проверка категории
    Model = model_by_category(category)
    if Model is None:
        logger.error("%s: unknown category %s", context, category)
        raise ValueError(f"Unknown category {category}")

    warn_skus: List[str] = []

    # 1) Проходим по всем строкам
    for row in rows:
        variant, _, err = validate_row(row)
        if err:
            warn_skus.append(variant)
            continue

        # 2) Проверяем целочисленные поля
        for fld in INT_FIELDS:
            raw = row.get(fld, "").strip()
            if not raw:
                continue
            val = parse_int(raw)
            if val is None or val < 0:
                warn_skus.append(variant)
                break

        # 3) Проверяем числовые с плавающей точкой
        for fld in FLOAT_FIELDS:
            raw = row.get(fld, "").strip()
            if not raw:
                continue
            val = parse_float(raw)
            if val is None or val < 0:
                warn_skus.append(variant)
                break

    # 4) Финальный лог и возврат
    unique_warns = sorted(set(warn_skus))
    logger.info("%s END invalid=%d", context, len(unique_warns))
    return unique_warns


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int, List[str]]:
    """
    Обрабатывает CSV-строки:
      - добавляет, обновляет, удаляет записи
    Возвращает (added, updated, deleted, warns, warn_skus).
    """
    context = "process_rows"
    logger.info("%s START category=%s rows=%d", context, category, len(rows))

    Model = model_by_category(category)
    if Model is None:
        logger.error("%s: unknown category %s", context, category)
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    warn_skus: List[str] = []

    with session_scope() as session:
        variants      = [r.get("variant_sku", "").strip() for r in rows]
        existing_objs = session.query(Model).filter(Model.variant_sku.in_(variants)).all()
        existing_map  = {o.variant_sku: o for o in existing_objs}

        for row in rows:
            variant = row.get("variant_sku", "").strip()
            # 0) Удаление: если есть SKU и все остальные поля пустые — удаляем
            data_for_delete = {k: v.strip() for k, v in row.items() if k != "variant_sku"}
            if variant and all(not v for v in data_for_delete.values()):
                obj = existing_map.get(variant)
                if obj:
                    session.delete(obj)
                    deleted += 1
                    logger.debug("%s: deleted %s", context, variant)
                continue

            # 1) Валидация
            variant, data, err = validate_row(row)
            if err:
                warns += 1
                warn_skus.append(variant)
                continue

            # 2) Создание или обновление
            obj = existing_map.get(variant)
            if obj is None:
                obj = Model(variant_sku=variant)
                inc_added, inc_warn = apply_creation(obj, data, warn_skus, context)
                session.add(obj)
                added += inc_added
                warns += inc_warn
                logger.debug("%s: added %s", context, variant)
            else:
                inc_upd, inc_warn = apply_update(obj, data, warn_skus, context)
                if inc_upd:
                    session.merge(obj)
                    updated += inc_upd
                    logger.debug("%s: updated %s", context, variant)
                warns += inc_warn

    logger.info("%s END added=%d updated=%d deleted=%d warns=%d", context, added, updated, deleted, warns)
    return added, updated, deleted, warns, warn_skus
