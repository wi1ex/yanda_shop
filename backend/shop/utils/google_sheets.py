import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from zoneinfo import ZoneInfo
from psycopg2.errors import StringDataRightTruncation
from sqlalchemy.exc import DataError
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


def preview_rows(category: str, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Превью-валидация CSV-строк:
      • базовая валидация SKU, gender, category и обязательных полей
      • нормализация строк через normalize_str
      • проверка int/float
      • проверка реальных ограничений длины из модели (включая Text vs String(N))
      • проверка производного color_sku
      • дубли variant_sku внутри файла
      • согласованность count_images
    """
    logger.debug("preview_rows START category=%s rows=%d", category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    # 0) собираем реальные ограничения по длине из модели
    FIELD_MAX: Dict[str, Optional[int]] = {col.name: getattr(col.type, "length", None) for col in Model.__table__.columns}
    per_row_errors: Dict[str, List[str]] = {}
    seen: Set[str] = set()

    for idx, raw in enumerate(rows, start=1):
        sku_variant = raw.get("variant_sku", "").strip()
        errs: List[str] = []

        # -- БАЗОВАЯ ВАЛИДАЦИЯ + очистка полей ------------------
        # SKU
        if not SKU_PATTERN.match(sku_variant):
            errs.append("Неправильный формат variant_sku")
        # gender
        gen = raw.get("gender", "").strip()
        if gen and gen not in VALID_GENDERS:
            errs.append(f"Недопустимый gender='{gen}'")
        # category
        cat = raw.get("category", "").strip()
        if cat not in VALID_CATS:
            errs.append(f"Недопустимый category='{cat}'")
        # обязательные поля
        data_stripped = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
        missing = [f for f, v in data_stripped.items() if not v and f not in OPTIONAL_EMPTY]
        if missing:
            errs.append(f"Пустые обязательные поля: {', '.join(missing)}")
        # stop if базовая провалилась
        if errs:
            per_row_errors.setdefault(sku_variant or f"<строка{idx}>", []).extend(errs)
            continue

        # -- НОРМАЛИЗАЦИЯ + проверка чисел ---------------------
        clean: Dict[str, Any] = {}
        for f, s in data_stripped.items():
            if f in INT_FIELDS:
                ival = parse_int(s)
                if ival is None or ival < 0:
                    errs.append(f"Неверное целое {f}='{s}'")
                    break
                clean[f] = ival
            elif f in FLOAT_FIELDS:
                fval = parse_float(s)
                if fval is None or fval < 0:
                    errs.append(f"Неверное число {f}='{s}'")
                    break
                clean[f] = fval
            else:
                clean[f] = normalize_str(s)
        if errs:
            per_row_errors.setdefault(sku_variant, []).extend(errs)
            continue

        # -- ПРОВЕРКА ДЛИНЫ ВСЕХ ПОЛЕЙ -------------------------
        for field, limit in FIELD_MAX.items():
            if limit is None:
                continue
            # берём либо нормализованное, либо из raw
            orig = raw.get(field, "")
            val = clean.get(field, normalize_str(orig))
            if len(val) > limit:
                errs.append(f"Поле '{field}' слишком длинное ({len(val)} > {limit})")

        # -- ПРОВЕРКА color_sku (производное) ------------------
        sku_norm   = normalize_str(raw.get("sku", ""))
        world_norm = normalize_str(raw.get("world_sku", ""))
        derived_cs = f"{sku_norm}_{world_norm}"
        max_cs = FIELD_MAX.get("color_sku")
        if max_cs and len(derived_cs) > max_cs:
            errs.append(f"Сгенерированный color_sku '{derived_cs}' слишком длинный ({len(derived_cs)} > {max_cs})")

        # -- ДУБЛИ variant_sku В ФАЙЛЕ ------------------------
        if sku_variant in seen:
            errs.append(f"Дублирование variant_sku в файле (строка {idx})")
        seen.add(sku_variant)
        if errs:
            per_row_errors.setdefault(sku_variant, []).extend(errs)

    # -- СОГЛАСОВАННОСТЬ count_images ------------------------
    cm: Dict[str, Set[str]] = {}
    for raw in rows:
        v, w = raw.get("variant_sku", "").strip(), raw.get("world_sku", "").strip()
        if not v or not w: continue
        key = f"{v}_{w}"
        ci = raw.get("count_images", "").strip() or "<пусто>"
        cm.setdefault(key, set()).add(ci)

    for key, vals in cm.items():
        if len(vals) > 1:
            msg = f"Несогласованное count_images для color_sku='{key}': {', '.join(sorted(vals))}"
            for raw in rows:
                if f"{raw.get('variant_sku','')}_{raw.get('world_sku','')}" == key:
                    per_row_errors.setdefault(raw.get("variant_sku"), []).append(msg)

    errors = [{"variant_sku": sku, "messages": msgs} for sku, msgs in per_row_errors.items()]
    logger.debug("preview_rows END errors=%d", len(errors))
    return errors


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int, int, List[str]]:
    """
    Облегчённая загрузка:
      • только проверяем формат variant_sku
      • чистим все строки и сохраняем (create/update/delete)
      • ловим DataError(тримминг) как предупреждение, чтобы не упасть
    """
    context = "process_rows"
    logger.info("%s START cat=%s rows=%d", context, category, len(rows))
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = warns = 0
    warn_skus: List[str] = []

    with session_scope() as session:
        # получаем существующие объекты
        variants = [r.get("variant_sku", "").strip() for r in rows]
        existing = session.query(Model).filter(Model.variant_sku.in_(variants)).all()
        exist_map = {o.variant_sku: o for o in existing}

        for raw in rows:
            sku_var = raw.get("variant_sku", "").strip()
            # 0) удаление если все прочие поля пусты
            data_no_sku = {k: v.strip() for k, v in raw.items() if k != "variant_sku"}
            if sku_var and all(not v for v in data_no_sku.values()):
                obj = exist_map.get(sku_var)
                if obj:
                    session.delete(obj)
                    deleted += 1
                continue

            # 1) минимальная валидация SKU
            if not SKU_PATTERN.match(sku_var):
                warns += 1
                warn_skus.append(sku_var)
                continue

            missing = [f for f, v in raw.items() if f != "variant_sku" and not v.strip() and f not in OPTIONAL_EMPTY]
            if missing:
                warns += 1
                warn_skus.append(sku_var)
                logger.warning("%s: missing fields %s for %s", context, missing, sku_var)
                continue

            # 2) готовим словарь для записи (строки очищены)
            clean: Dict[str, Any] = {}
            for f, s in raw.items():
                if f == "variant_sku": continue
                val = s.strip()
                clean[f] = (parse_int(val) if f in INT_FIELDS else
                            parse_float(val) if f in FLOAT_FIELDS else
                            normalize_str(val))

            # 3) создание / обновление
            obj = exist_map.get(sku_var)
            try:
                if obj is None:
                    obj = Model(variant_sku=sku_var)
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
                    # пересчёт цветового SKU
                    obj.color_sku = f"{obj.sku}_{obj.world_sku}"
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1
                # пытаемся «пробить» вставку, чтобы сразу словить StringDataRightTruncation
                with session.begin_nested():
                    session.flush()
            except (StringDataRightTruncation, DataError) as e:
                warns += 1
                warn_skus.append(sku_var)
                logger.warning("%s: truncation for %s — %s", context, sku_var, e)
                continue
            except Exception:
                # любые другие ошибки — считаем критичными, прерываем
                logger.exception("%s: unexpected error for %s", context, sku_var)
                raise

    logger.info("%s END added=%d updated=%d deleted=%d warns=%d", context, added, updated, deleted, warns)
    return added, updated, deleted, warns, warn_skus
