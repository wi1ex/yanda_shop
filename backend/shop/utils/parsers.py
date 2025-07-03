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
    return s[0].upper() + s[1:] if isinstance(s, str) and s else s
