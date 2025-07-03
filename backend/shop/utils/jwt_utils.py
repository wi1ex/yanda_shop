from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from ..core.logging import logger

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.debug("admin_required: verifying JWT for %s", fn.__name__)
        verify_jwt_in_request()  # 401/422/401 обрабатываются хуками
        claims = get_jwt()
        logger.debug("admin_required: JWT claims=%s", claims)
        if claims.get("role") != "admin":
            logger.debug("admin_required: access denied for claims=%s", claims)
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper
