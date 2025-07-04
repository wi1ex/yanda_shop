from typing import Optional


def parse_int(s: str) -> Optional[int]:
    raw = s.replace(" ", "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def parse_float(s: str) -> Optional[float]:
    raw = s.replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def normalize_str(s: str) -> Optional[str]:
    if not (isinstance(s, str) and s):
        return s
    cleaned = s.replace(",", ".")
    return cleaned[0].upper() + cleaned[1:]
