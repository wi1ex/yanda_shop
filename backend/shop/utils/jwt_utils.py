from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from ..core.logging import logger


def admin_required(fn):
    """
    Декоратор, проверяющий, что в JWT есть роль 'admin'.
    При ошибках верификации или недостаточном уровне — возвращает JSON-ответ 401/403.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        context = "admin_required"
        logger.info("%s START function=%s", context, fn.__name__)

        # 1) Проверка валидности токена
        try:
            verify_jwt_in_request()  # при невалидном токене даст 401/422
            logger.debug("%s: token verified", context)
        except Exception as e:
            logger.warning("%s: JWT verification failed: %s", context, e)
            return jsonify({"error": "Invalid or missing JWT"}), 401

        # 2) Извлекаем права
        try:
            claims = get_jwt()
            logger.debug("%s: JWT claims=%s", context, claims)
        except Exception as e:
            logger.error("%s: failed to get JWT claims: %s", context, e)
            return jsonify({"error": "Failed to extract JWT claims"}), 401

        # 3) Проверяем роль
        if claims.get("role") != "admin":
            logger.warning("%s: access denied, role=%s", context, claims.get("role"))
            return jsonify({"error": "Admin access required"}), 403

        # 4) Успех
        logger.info("%s END: access granted for %s", context, fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
