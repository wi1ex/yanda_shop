from typing import Optional
from ..core.logging import logger


# ——— Parsers with logging and error handling —————————————————————————
def parse_int(s: str) -> Optional[int]:
    """
    Преобразует строку s в int, убирая пробелы.
    Возвращает None при невозможности преобразования.
    """
    context = "parse_int"
    if not isinstance(s, str):
        logger.debug("%s: expected str, got %r", context, s)
        return None
    raw = s.replace(" ", "")
    try:
        value = int(raw)
    except (TypeError, ValueError) as e:
        logger.warning("%s: failed to parse '%s' as int: %s", context, s, e)
        return None
    else:
        logger.debug("%s: parsed '%s' -> %d", context, s, value)
        return value


def parse_float(s: str) -> Optional[float]:
    """
    Преобразует строку s в float, заменяя запятые на точки и убирая пробелы.
    Возвращает None при невозможности преобразования.
    """
    context = "parse_float"
    if not isinstance(s, str):
        logger.debug("%s: expected str, got %r", context, s)
        return None
    raw = s.replace(" ", "").replace(",", ".")
    try:
        value = float(raw)
    except (TypeError, ValueError) as e:
        logger.warning("%s: failed to parse '%s' as float: %s", context, s, e)
        return None
    else:
        logger.debug("%s: parsed '%s' -> %f", context, s, value)
        return value


def normalize_str(s: str) -> Optional[str]:
    """
    Нормализует строку: заменяет запятые на точки, делает первую букву заглавной.
    Возвращает исходное значение, если s не является непустой строкой.
    """
    context = "normalize_str"
    if not isinstance(s, str) or not s:
        logger.debug("%s: skip normalization for %r", context, s)
        return s
    cleaned = s.replace(",", ".")
    result = cleaned[0].upper() + cleaned[1:]
    logger.debug("%s: normalized '%s' -> '%s'", context, s, result)
    return result
