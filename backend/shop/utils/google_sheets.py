from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from zoneinfo import ZoneInfo
from psycopg2.errors import StringDataRightTruncation
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.exc import DataError
from .db_utils import session_scope
from .validators import (
    parse_int, parse_float, normalize_str,
    validate_sku, validate_gender, validate_category,
    validate_subcategory, validate_required_fields,
    validate_int_field, validate_float_field,
    validate_length, validate_and_correct_color,
    find_duplicate_skus, validate_count_images_consistency
)
from .product_serializer import model_by_category
from ..core.logging import logger
from ..models import AdminSetting

# Маппинг подкатегорий
SUBCATEGORY_MAP: Dict[str, str] = {
    # Одежда
    'Блузы':              'Blouse',
    'Бомберы':            'Bomber',
    'Брюки':              'Trousers',
    'Верхняя Одежда':     'Outerwear',
    'Джемперы':           'Jumper',
    'Джинсы':             'Jeans',
    'Жилетки':            'Vest',
    'Кардиганы':          'Cardigan',
    'Купальники':         'Swimsuit',
    'Лонгсливы':          'Longsleeve',
    'Майки':              'T_shirt',
    'Нижнее Белье':       'Underwear',
    'Пиджаки':            'Blazer',
    'Платья':             'Dress',
    'Поло':               'Polo',
    'Пуховики':           'Down_jacket',
    'Рубашки':            'Shirt',
    'Свитеры':            'Sweater',
    'Свитшоты':           'Sweatshirt',
    'Спортивные Костюмы': 'Sports_suit',
    'Футболки':           'Tee_shirt',
    'Худи':               'Hoodie',
    'Шорты':              'Shorts',
    'Юбки':               'Skirt',
    'Плавательные шорты': 'Swimming_shorts',
    # Обувь
    'Балетки':            'Ballet',
    'Босоножки':          'Slingbacks',
    'Ботильоны':          'Ankle_boots',
    'Казаки':             'Cossacks',
    'Кеды':               'Keds',
    'Кроссовки':          'Sneakers',
    'Мокасины':           'Moccasins',
    'Мюли':               'Mules',
    'Резиновая обувь':    'Rubber_shoes',
    'Сабо':               'Sabo',
    'Сандалии':           'Sandals',
    'Сапоги':             'Boots',
    'Слипоны':            'Slip_ons',
    'Топсайдеры':         'Topsiders',
    'Туфли':              'Shoes',
    'Шлепки':             'Flip_flops',
    'Эспадрильи':         'Espadrilles',
    # Аксессуары
    'Головные Уборы':     'Headwear',
    'Очки':               'Glasses',
    'Ремни':              'Belts',
    'Сумки':              'Bags',
    'Рюкзаки':            'Backpacks',
    'Кошельки':           'Wallets',
    'Платки':             'Handkerchiefs',
    'Украшения':          'Decorations',
    'Часы':               'Watch',
    'Шарфы':              'Scarves',
}
VALID_SUBCATS: Set[str] = set(SUBCATEGORY_MAP.keys())
# Константы
VALID_GENDERS  = {"U", "F", "M"}
VALID_CATS     = {"Обувь", "Одежда", "Аксессуары"}
OPTIONAL_EMPTY = {"description", "width_cm", "height_cm", "depth_cm", "chest_cm", "depth_mm"}
INT_FIELDS     = {"price", "count_in_stock", "count_images", "size_category"}
FLOAT_FIELDS   = {"chest_cm", "width_cm", "height_cm", "depth_cm", "depth_mm"}


# --- Google Sheets utilities ---
def get_sheet_url(category: str) -> Optional[str]:
    context = "get_sheet_url"
    logger.debug("%s START category=%s", context, category)
    key = f"sheet_url_{category}"
    try:
        with session_scope() as session:
            setting = session.get(AdminSetting, key)
            url = setting.value if setting else None
            logger.debug("%s END url=%s", context, url)
            return url
    except Exception:
        logger.exception("%s: failed to fetch sheet URL for %s", context, category)
        return None


def validate_row(row: Dict[str, str]) -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
    variant = row.get("variant_sku", "").strip()
    # SKU
    err = validate_sku(variant)
    if err:
        return variant, None, variant
    # Gender
    err = validate_gender(row.get("gender", "").strip(), VALID_GENDERS)
    if err:
        return variant, None, variant
    # Category
    err = validate_category(row.get("category", "").strip(), VALID_CATS)
    if err:
        return variant, None, variant
    # Собираем данные и проверяем обязательные
    data = {k: v.strip() for k, v in row.items() if k != "variant_sku"}
    req_errs = validate_required_fields(data, OPTIONAL_EMPTY)
    if req_errs:
        return variant, None, variant

    return variant, data, None


def apply_creation(obj, data: Dict[str, str], warn_skus: List[str], context: str) -> Tuple[int, int]:
    warns = 0
    for field, val_str in data.items():
        if not hasattr(obj, field):
            continue
        if field in INT_FIELDS:
            val, err = validate_int_field(field, val_str)
            if err:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: %s for %s", context, err, obj.variant_sku)
                continue
        elif field in FLOAT_FIELDS:
            val, err = validate_float_field(field, val_str)
            if err:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: %s for %s", context, err, obj.variant_sku)
                continue
        else:
            val = normalize_str(val_str)

        setattr(obj, field, val)
    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
    return 1, warns


def apply_update(obj, data: Dict[str, str], warn_skus: List[str], context: str) -> Tuple[int, int]:
    updated = warns = 0
    has_changes = False
    for field, val_str in data.items():
        if not hasattr(obj, field):
            continue
        if field in INT_FIELDS:
            new_val, err = validate_int_field(field, val_str)
            if err:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: %s for %s", context, err, obj.variant_sku)
                continue
        elif field in FLOAT_FIELDS:
            new_val, err = validate_float_field(field, val_str)
            if err:
                warns += 1
                warn_skus.append(obj.variant_sku)
                logger.warning("%s: %s for %s", context, err, obj.variant_sku)
                continue
        else:
            new_val = normalize_str(val_str)

        if getattr(obj, field) != new_val:
            setattr(obj, field, new_val)
            has_changes = True

    new_cs = f"{obj.sku}_{obj.world_sku}"
    if obj.color_sku != new_cs:
        obj.color_sku = new_cs
        has_changes = True

    if has_changes:
        obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
        updated = 1
    return updated, warns


def preview_rows(category: str, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    logger.debug("preview_rows START category=%s rows=%d", category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    # 1) Собираем метаданные из модели
    FIELD_MAX: Dict[str, Optional[int]] = {col.name: getattr(col.type, "length", None) for col in Model.__table__.columns}
    NUM_CONSTRAINTS: Dict[str, Tuple[int, int]] = {}
    ENUM_CONSTRAINTS: Dict[str, Set[str]] = {}
    NULLABLE: Dict[str, bool] = {}
    for col in Model.__table__.columns:
        # precision & scale для Numeric
        if hasattr(col.type, "precision") and hasattr(col.type, "scale") and col.type.precision:
            NUM_CONSTRAINTS[col.name] = (col.type.precision, col.type.scale)
        # ENUM
        if isinstance(col.type, SQLEnum):
            ENUM_CONSTRAINTS[col.name] = set(col.type.enums)
        # NOT NULL
        NULLABLE[col.name] = col.nullable

    per_row_errors: Dict[str, List[str]] = {}

    # 2) Перебираем каждую строку
    for idx, raw in enumerate(rows, start=1):
        sku = raw.get("variant_sku", "").strip()
        errs: List[str] = []

        # 2.1) Базовая валидация SKU/Gender/Category/Subcategory
        for fn, arg in [
            (validate_sku, sku),
            (lambda v: validate_gender(v, VALID_GENDERS), raw.get("gender", "").strip()),
            (lambda v: validate_category(v, VALID_CATS), raw.get("category", "").strip()),
            (lambda v: validate_subcategory(v, VALID_SUBCATS), raw.get("subcategory", "").strip()),
        ]:
            err = fn(arg)
            if err:
                errs.append(err)

        # 2.2) NOT NULL
        for field, is_nullable in NULLABLE.items():
            if not is_nullable and not raw.get(field, "").strip():
                errs.append(f"Поле '{field}' не может быть пустым")

        # 2.3) ENUM
        for field, allowed in ENUM_CONSTRAINTS.items():
            val = raw.get(field, "").strip()
            if val and val not in allowed:
                errs.append(f"Недопустимое значение '{val}' для поля '{field}'")

        # 2.4) Проверка обязательных полей (OPTIONAL_EMPTY)
        data_strip = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
        errs += validate_required_fields(data_strip, OPTIONAL_EMPTY)

        if errs:
            per_row_errors.setdefault(sku or f"<строка{idx}>", []).extend(errs)
            continue

        # 2.5) Нормализация и проверка чисел
        clean: Dict[str, Any] = {}
        for f, s in data_strip.items():
            if not s and f in OPTIONAL_EMPTY:
                clean[f] = None
                continue
            if f in INT_FIELDS:
                val, err = validate_int_field(f, s)
                if err:
                    errs.append(err)
                    break
                clean[f] = val
            elif f in FLOAT_FIELDS:
                val, err = validate_float_field(f, s)
                if err:
                    errs.append(err)
                    break
                clean[f] = val
            else:
                clean[f] = normalize_str(s)
        if errs:
            per_row_errors.setdefault(sku, []).extend(errs)
            continue

        # 2.6) Эмуляция ограничения precision/scale
        for field, (prec, scale) in NUM_CONSTRAINTS.items():
            val = clean.get(field)
            if val is None:
                continue
            # Формируем строку с фиксированным количеством дробных знаков
            formatted = f"{val:.{scale}f}"
            int_part, _, frac_part = formatted.partition('.')
            if len(int_part) > (prec - scale) or len(frac_part) > scale:
                errs.append(f"Число '{field}={val}' выходит за Numeric({prec},{scale})")

        # 2.7) Проверка длины VARCHAR
        for field, limit in FIELD_MAX.items():
            val = clean.get(field, normalize_str(raw.get(field, "")))
            err = validate_length(field, val, limit)
            if err:
                errs.append(err)

        # 2.8) Валидация и автокоррекция цвета
        ok, corrected_color, err_msg = validate_and_correct_color(raw.get("color", "").strip())
        if not ok:
            errs.append(err_msg)
        else:
            clean["color"] = corrected_color

        if errs:
            per_row_errors.setdefault(sku, []).extend(errs)

    # 3) Дубликаты SKU
    for sku, idxs in find_duplicate_skus(rows).items():
        per_row_errors.setdefault(sku, []).append(f"Дублирование variant_sku в файле (строки {idxs})")

    # 4) Согласованность count_images
    for sku, msg in validate_count_images_consistency(rows).items():
        per_row_errors.setdefault(sku, []).append(msg)

    errors = [{"variant_sku": sku, "messages": msgs} for sku, msgs in per_row_errors.items()]
    logger.debug("preview_rows END errors=%d", len(errors))
    return errors


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int, List[str]]:
    context = "process_rows"
    logger.debug("%s START cat=%s rows=%d", context, category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    warn_skus: List[str] = []

    with session_scope() as session:
        existing = session.query(Model).filter(Model.variant_sku.in_([r.get("variant_sku", "").strip() for r in rows])).all()
        exist_map = {o.variant_sku: o for o in existing}

        for raw in rows:
            sku = raw.get("variant_sku", "").strip()
            # Удаление
            data_no = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
            if sku and all(not v for v in data_no.values()):
                obj = exist_map.get(sku)
                if obj:
                    session.delete(obj)
                    deleted += 1
                continue
            # Минимальная валидация SKU
            if validate_sku(sku):
                warns += 1
                warn_skus.append(sku)
                continue
            # Проверка обязательных
            missing = [f for f, v in raw.items() if f != "variant_sku" and not v.strip() and f not in OPTIONAL_EMPTY]
            if missing:
                warns += 1
                warn_skus.append(sku)
                logger.warning("%s: missing fields %s for %s", context, missing, sku)
                continue
            # Подготовка clean
            clean: Dict[str, Any] = {}
            for f, s in raw.items():
                if f == "variant_sku": continue
                val = s.strip()
                clean[f] = (parse_int(val) if f in INT_FIELDS else
                            parse_float(val) if f in FLOAT_FIELDS else
                            normalize_str(val))
            # Валидация цвета
            ok, corrected_color, err_msg = validate_and_correct_color(raw.get("color", "").strip())
            if not ok:
                warns += 1
                warn_skus.append(sku)
                logger.warning("%s: invalid color '%s' for %s — %s", context, raw.get("color"), sku, err_msg)
                continue
            clean["color"] = corrected_color
            # Create or update
            obj = exist_map.get(sku)
            try:
                if obj is None:
                    obj = Model(variant_sku=sku)
                    for f, v in clean.items():
                        if hasattr(obj, f):
                            setattr(obj, f, v)
                    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                    session.add(obj)
                    added += 1
                else:
                    for f, v in clean.items():
                        if hasattr(obj, f):
                            setattr(obj, f, v)
                    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1
                with session.begin_nested():
                    session.flush()
            except (StringDataRightTruncation, DataError) as e:
                warns += 1
                warn_skus.append(sku)
                logger.warning("%s: truncation for %s — %s", context, sku, e)
                continue
            except Exception:
                logger.exception("%s: unexpected error for %s", context, sku)
                raise

    logger.debug("%s END added=%d updated=%d deleted=%d warns=%d", context, added, updated, deleted, warns)
    return added, updated, deleted, warns, warn_skus
