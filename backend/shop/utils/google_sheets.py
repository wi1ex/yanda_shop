from typing import Dict, List, Tuple, Optional, Any, Set
from sqlalchemy import Enum as SQLEnum
from .db_utils import session_scope
from .product_serializer import model_by_category
from .validators import (
    normalize_str, validate_sku, validate_gender, validate_category,
    validate_subcategory, validate_required_fields,
    validate_int_field, validate_float_field,
    validate_length, validate_and_correct_color,
    find_duplicate_skus, validate_count_images_consistency
)
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


def preview_rows(category: str, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    logger.debug("preview_rows START category=%s rows=%d", category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")
    # 1) Метаданные из модели
    FIELD_MAX: Dict[str, Optional[int]] = {col.name: getattr(col.type, "length", None) for col in Model.__table__.columns}
    # Колонки NUMERIC → (precision, scale)
    NUM_CONSTRAINTS: Dict[str, Tuple[int, int]] = {}
    # ENUM- и NULLABLE-инфо
    ENUM_CONSTRAINTS: Dict[str, Set[str]] = {}
    NULLABLE: Dict[str, bool] = {}
    # Колонки, для которых NOT NULL не валидируем (авто-PK, default, server_default)
    DEFAULTABLE: Set[str] = set()
    for col in Model.__table__.columns:
        NULLABLE[col.name] = col.nullable
        # PK или явный default – отключаем NOT NULL-проверку
        if col.primary_key or col.default is not None or col.server_default is not None:
            DEFAULTABLE.add(col.name)
        # Numeric precision/scale
        if getattr(col.type, "precision", None) and getattr(col.type, "scale", None) is not None:
            NUM_CONSTRAINTS[col.name] = (col.type.precision, col.type.scale)
        # ENUM
        if isinstance(col.type, SQLEnum):
            ENUM_CONSTRAINTS[col.name] = set(col.type.enums)
    per_row_errors: Dict[str, List[str]] = {}
    # 2) Валидация по строкам
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
        # 2.2) NOT NULL (кроме DEFAULTABLE)
        for field, is_nullable in NULLABLE.items():
            if not is_nullable and field not in DEFAULTABLE:
                if not raw.get(field, "").strip():
                    errs.append(f"Поле '{field}' не может быть пустым")
        # 2.3) ENUM
        for field, allowed in ENUM_CONSTRAINTS.items():
            val = raw.get(field, "").strip()
            if val and val not in allowed:
                errs.append(f"Недопустимое значение '{val}' для поля '{field}'")
        # 2.4) Проверка обязательных полей (OPTIONAL_EMPTY)
        data_strip = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
        allowed_empty = OPTIONAL_EMPTY.union(DEFAULTABLE)
        errs += validate_required_fields(data_strip, allowed_empty)
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


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int]:
    """
    Получает гарантированно валидные rows и выполняет:
      - удаление записей с пустыми данными
      - создание новых
      - обновление существующих
    Возвращает кортеж (added, updated, deleted).
    """
    context = "process_rows"
    logger.debug("%s START category=%s rows=%d", context, category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")
    added = updated = deleted = 0
    skus = [r.get("variant_sku", "").strip() for r in rows]
    with session_scope() as session:
        # Подгружаем все существующие объекты одной операцией
        existing = session.query(Model).filter(Model.variant_sku.in_(skus)).all()
        exist_map = {obj.variant_sku: obj for obj in existing}
        for raw in rows:
            sku = raw.get("variant_sku", "").strip()
            data = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
            # 1) Удаление: если все поля, кроме SKU, пустые
            if all(not val for val in data.values()):
                obj = exist_map.pop(sku, None)
                if obj:
                    session.delete(obj)
                    deleted += 1
                continue
            obj = exist_map.get(sku)
            if obj is None:
                # 2) Создание новой записи
                try:
                    obj = Model(variant_sku=sku, **data)
                    session.add(obj)
                    added += 1
                except Exception:
                    logger.exception("%s: failed to create %s", context, sku)
                    continue
            else:
                # 3) Обновление существующей записи
                changed = False
                for field, val in data.items():
                    if hasattr(obj, field) and getattr(obj, field) != val:
                        setattr(obj, field, val)
                        changed = True
                if changed:
                    updated += 1
        # Применяем все изменения
        session.flush()

    logger.debug("%s END added=%d updated=%d deleted=%d", context, added, updated, deleted)
    return added, updated, deleted
