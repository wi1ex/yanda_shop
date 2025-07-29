import re
from typing import Optional, Tuple, List, Dict, Any, Set
from ..core.logging import logger


# --- Parsers: numeric conversion and string normalization ---
def parse_int(s: str) -> Optional[int]:
    context = "parse_int"
    if not isinstance(s, str):
        logger.debug("%s: expected str, got %r", context, s)
        return None
    raw = s.replace(" ", "")
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        logger.warning("%s: failed to parse '%s' as int: %s", context, s, exc)
        return None
    logger.debug("%s: parsed '%s' -> %d", context, s, value)
    return value


def parse_float(s: str) -> Optional[float]:
    context = "parse_float"
    if not isinstance(s, str):
        logger.debug("%s: expected str, got %r", context, s)
        return None
    raw = s.replace(" ", "").replace(",", ".")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        logger.warning("%s: failed to parse '%s' as float: %s", context, s, exc)
        return None
    logger.debug("%s: parsed '%s' -> %s", context, s, value)
    return value


def normalize_str(s: str) -> Optional[str]:
    context = "normalize_str"
    if not isinstance(s, str) or not s:
        logger.debug("%s: skip normalization for %r", context, s)
        return s
    cleaned = s.replace(",", ".")
    result = cleaned[0].upper() + cleaned[1:]
    logger.debug("%s: normalized '%s' -> '%s'", context, s, result)
    return result


# --- Validators: field-level and row-level checks ---

# SKU pattern
SKU_PATTERN = re.compile(r"^[^_]+_[^_]+_.+")
# Color entry pattern: single or double component
COLOR_ENTRY_PATTERN = re.compile(r'^[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?$')

def validate_sku(sku: str) -> Optional[str]:
    if not sku or not SKU_PATTERN.match(sku):
        return f"Неправильный формат variant_sku='{sku}'"
    return None


def validate_gender(gender: str, valid_set: Set[str]) -> Optional[str]:
    if gender and gender not in valid_set:
        return f"Недопустимый gender='{gender}'"
    return None


def validate_category(cat: str, valid_set: Set[str]) -> Optional[str]:
    if cat not in valid_set:
        return f"Недопустимый category='{cat}'"
    return None


def validate_subcategory(subcat: str, valid_set: Set[str]) -> Optional[str]:
    if subcat not in valid_set:
        return f"Недопустимая подкатегория='{subcat}'"
    return None


def validate_required_fields(data: Dict[str, str], optional_empty: Set[str]) -> List[str]:
    missing = [f for f, v in data.items() if not v and f not in optional_empty]
    if missing:
        return [f"Пустые обязательные поля: {', '.join(missing)}"]
    return []


def validate_int_field(name: str, s: str) -> Tuple[Optional[int], Optional[str]]:
    val = parse_int(s)
    if val is None or val < 0:
        return None, f"Неверное целое {name}='{s}'"
    return val, None


def validate_float_field(name: str, s: str) -> Tuple[Optional[float], Optional[str]]:
    val = parse_float(s)
    if val is None or val < 0:
        return None, f"Неверное число {name}='{s}'"
    return val, None


def validate_length(field: str, value: str, max_len: Optional[int]) -> Optional[str]:
    if max_len is not None and value and len(value) > max_len:
        return f"Поле '{field}' слишком длинное ({len(value)} > {max_len})"
    return None


def validate_and_correct_color(color_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Проверка и автокоррекция поля color.
    Возвращает (valid, corrected_value, message).
    """
    original = color_str or ''
    normalized = re.sub(r'\s*-\s*', '-', original.strip())
    normalized = re.sub(r'\s+', ' ', normalized)
    parts = [p.strip() for p in normalized.split(',')]
    corrected_parts: List[str] = []

    for part in parts:
        if not part:
            return False, None, f"Пустой элемент цвета в строке '{original}'"
        sub = [w.lower().capitalize() for w in part.split('-')]
        candidate = '-'.join(sub)
        if not COLOR_ENTRY_PATTERN.match(candidate):
            return False, None, f"Неправильный формат цвета '{part}'"
        corrected_parts.append(candidate)

    corrected = ', '.join(corrected_parts)
    if corrected != original:
        return True, corrected, f"Цвет '{original}' автоматически исправлен на '{corrected}'"
    return True, corrected, None


def find_duplicate_skus(rows: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    seen: Dict[str, List[int]] = {}
    for idx, raw in enumerate(rows, start=1):
        sku = raw.get("variant_sku", "").strip()
        if sku:
            seen.setdefault(sku, []).append(idx)
    return {sku: idxs for sku, idxs in seen.items() if len(idxs) > 1}


def validate_count_images_consistency(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    cm: Dict[str, Set[str]] = {}
    for raw in rows:
        v = raw.get("variant_sku", "").strip()
        w = raw.get("world_sku", "").strip()
        if not v or not w:
            continue
        key = f"{v}_{w}"
        ci = raw.get("count_images", "").strip() or '<пусто>'
        cm.setdefault(key, set()).add(ci)

    errors: Dict[str, str] = {}
    for key, vals in cm.items():
        if len(vals) > 1:
            variant, _ = key.split("_", 1)
            errors[variant] = f"Несогласованное count_images для color_sku='{key}': {', '.join(sorted(vals))}"

    return errors
