from datetime import timedelta
from typing import Dict, Tuple
from flask import Blueprint, jsonify, Response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from ..core.logging import logger
from ..utils.route_utils import handle_errors

auth_bp: Blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


# Internal helpers

def make_tokens(user_id: str, username: str, role: str) -> Dict[str, str]:
    """
    Генерирует пару access/refresh токенов для заданного user_id и роли.
    """
    claims = {"role": role, "username": username}
    access_token = create_access_token(
            identity=user_id,
            additional_claims=claims,
            expires_delta=timedelta(hours=1),
        )
    refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims=claims,
            expires_delta=timedelta(days=7),
        )
    return access_token, refresh_token


# Authentication endpoints
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@handle_errors
def refresh() -> Tuple[Response, int]:
    """POST /api/auth/refresh (refresh token required)"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "")
    username = claims.get("username", "")
    logger.debug("refresh: user_id=%s", user_id)

    claims = {"role": role, "username": username}
    access_token = create_access_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=timedelta(hours=1),
    )
    logger.info("refresh: new access token generated for user_id=%s", user_id)
    return jsonify({"access_token": access_token}), 200
