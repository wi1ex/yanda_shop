from datetime import timedelta
from typing import Dict, Tuple
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from ..core.logging import logger
from ..models import Users
from ..utils.route_utils import handle_errors, require_json

auth_bp: Blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


# Internal helpers

def _make_tokens(user_id: str, username: str, role: str) -> Dict[str, str]:
    """
    Генерирует пару access/refresh токенов для заданного user_id и роли.
    """
    claims = {"role": role, "username": username}
    return {
        "access_token": create_access_token(
            identity=user_id,
            additional_claims=claims,
            expires_delta=timedelta(hours=1),
        ),
        "refresh_token": create_refresh_token(
            identity=user_id,
            additional_claims=claims,
            expires_delta=timedelta(days=7),
        ),
    }


# Authentication endpoints

@auth_bp.route("/login", methods=["POST"])
@handle_errors
@require_json("username", "password")
def login() -> Tuple[Response, int]:
    """POST /api/auth/login {username, password}"""
    data = request.get_json()
    logger.debug("login: payload=%s", data)

    username = data["username"].strip()
    password = data["password"]

    user = Users.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning("login: authentication failed for username=%r", username)
        return jsonify({"error": "Bad credentials"}), 401

    tokens = _make_tokens(str(user.user_id), user.username, user.role)
    logger.info("login: user_id=%s role=%s logged in", user.user_id, user.role)
    return jsonify(tokens), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@handle_errors
def refresh() -> Tuple[Response, int]:
    """POST /api/auth/refresh (refresh token required)"""
    identity = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "")
    logger.debug("refresh: user_id=%s role=%s", identity, role)

    access_token = create_access_token(
        identity=identity,
        additional_claims={"role": role},
        expires_delta=timedelta(hours=1),
    )
    logger.info("refresh: new access token generated for user_id=%s", identity)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
@handle_errors
def protected() -> Tuple[Response, int]:
    """GET /api/auth/protected (access token required)"""
    identity = get_jwt_identity()
    logger.debug("protected: accessed by user_id=%s", identity)
    response = {"msg": f"Hello, user {identity}"}
    logger.info("protected: response sent for user_id=%s", identity)
    return jsonify(response), 200
