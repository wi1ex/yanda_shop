import functools
from functools import wraps
from typing import List
from flask import request, jsonify
from ..core.logging import logger


# Parsers: request args and JSON validation
def require_args(*names: str):
    """
    Проверка обязательных GET-параметров.
    Возвращает 400 с JSON-ошибкой, если чего-то нет.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            context = fn.__name__
            missing: List[str] = [n for n in names if not request.args.get(n)]
            if missing:
                logger.warning("%s: missing params %s", context, missing)
                return jsonify({"error": f"missing params: {', '.join(missing)}"}), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_json(*names: str):
    """
    Проверка обязательных полей в JSON-теле запроса.
    Возвращает 400 с JSON-ошибкой, если чего-то нет.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            context = fn.__name__
            data = request.get_json(silent=True) or {}
            missing: List[str] = [n for n in names if data.get(n) is None]
            if missing:
                logger.warning("%s: missing json fields %s", context, missing)
                return jsonify({"error": f"missing json fields: {', '.join(missing)}"}), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Route utilities: error handling, logging, DB session
def handle_errors(fn):
    """
    Декоратор! Для каждого запроса:
      - логирует START/END
      - при исключении логирует stacktrace и возвращает 500.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        context = fn.__name__
        logger.info("%s START", context)
        try:
            result = fn(*args, **kwargs)
            logger.info("%s END", context)
            return result
        except Exception:
            logger.exception("%s: unexpected error", context)
            return jsonify({"error": "internal error"}), 500
    return wrapper
