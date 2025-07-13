from typing import Optional
from ..core.logging import logger


# Parsers: numeric conversion and string normalization
def parse_int(s: str) -> Optional[int]:
    """
    Преобразует строку s в int, убирая все пробелы.
    Возвращает None при невозможности преобразования.
    """
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
    """
    Преобразует строку s в float:
      - заменяет запятые на точки
      - убирает все пробелы
    Возвращает None при невозможности преобразования.
    """
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
    """
    Нормализует строку s:
      - заменяет запятые на точки
      - переводит первую букву в верхний регистр
    Если s не является непустой строкой, возвращает s без изменений.
    """
    context = "normalize_str"
    if not isinstance(s, str) or not s:
        logger.debug("%s: skip normalization for %r", context, s)
        return s

    cleaned = s.replace(",", ".")
    result = cleaned[0].upper() + cleaned[1:]
    logger.debug("%s: normalized '%s' -> '%s'", context, s, result)
    return result
