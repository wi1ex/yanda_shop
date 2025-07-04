from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
from typing import Dict
from ..core.logging import logger
from ..models import Users

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def _make_tokens(user_id: str, role: str) -> Dict[str, str]:
    """
    Генерирует пару access/refresh токенов для заданного user_id и роли.
    """
    return {
        "access_token": create_access_token(
            identity=user_id,
            additional_claims={"role": role},
            expires_delta=timedelta(hours=1)
        ),
        "refresh_token": create_refresh_token(
            identity=user_id,
            additional_claims={"role": role},
            expires_delta=timedelta(days=7)
        )
    }


@auth_bp.route('/login', methods=['POST'])
def login():
    context = "auth_login"
    logger.info("%s START", context)
    try:
        data = request.get_json(silent=True) or {}
        logger.debug("%s: payload=%s", context, data)

        username = data.get("username", "").strip()
        password = data.get("password", "")

        user = Users.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            logger.warning("%s: authentication failed for username=%r", context, username)
            return jsonify({"error": "Bad credentials"}), 401

        tokens = _make_tokens(str(user.user_id), user.role)
        logger.info("%s: user_id=%s role=%s logged in", context, user.user_id, user.role)
        logger.debug("%s END", context)
        return jsonify(tokens), 200

    except Exception:
        logger.exception("%s: unexpected error", context)
        return jsonify({"error": "internal error"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    context = "auth_refresh"
    logger.info("%s START", context)
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role", "")
        logger.debug("%s: refreshing token for user_id=%s role=%s", context, user_id, role)

        access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": role},
            expires_delta=timedelta(hours=1)
        )
        logger.info("%s: generated new access token for user_id=%s", context, user_id)
        logger.debug("%s END", context)
        return jsonify({"access_token": access_token}), 200

    except Exception:
        logger.exception("%s: unexpected error", context)
        return jsonify({"error": "internal error"}), 500


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    context = "auth_protected"
    logger.info("%s START", context)
    try:
        user_id = get_jwt_identity()
        logger.debug("%s: accessed by user_id=%s", context, user_id)
        response = {"msg": f"Hello, user {user_id}"}
        logger.info("%s END", context)
        return jsonify(response), 200

    except Exception:
        logger.exception("%s: unexpected error", context)
        return jsonify({"error": "internal error"}), 500
