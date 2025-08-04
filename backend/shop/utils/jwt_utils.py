import functools
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from ..core.logging import logger


# JWT utils: admin role decorator
def admin_required(fn):
    """
    Декоратор проверки JWT на роль 'admin'.
    Возвращает 401 при неверном или отсутствующем токене,
    403 при недостаточном уровне доступа.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        context = "admin_required"
        logger.debug("%s START function=%s", context, fn.__name__)

        # 1) Проверка валидности токена
        try:
            verify_jwt_in_request()
            logger.debug("%s: token verified", context)
        except Exception as exc:
            logger.warning("%s: JWT verification failed: %s", context, exc)
            return jsonify({"error": "Invalid or missing JWT"}), 401

        # 2) Извлечение claims
        try:
            claims = get_jwt()
            logger.debug("%s: JWT claims=%s", context, claims)
        except Exception as exc:
            logger.error("%s: failed to get JWT claims: %s", context, exc)
            return jsonify({"error": "Failed to extract JWT claims"}), 401

        # 3) Проверка роли
        if claims.get("role") != "admin":
            logger.warning("%s: access denied, role=%s", context, claims.get("role"))
            return jsonify({"error": "Admin access required"}), 403

        # 4) Успех
        logger.debug("%s END: access granted for %s", context, fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
