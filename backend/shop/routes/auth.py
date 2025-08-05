import secrets
import string
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
from typing import Tuple, Dict
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, Response, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_mail import Message
from ..models import Users, ChangeLog
from ..utils.db_utils import session_scope
from ..core.logging import logger
from ..extensions import redis_client, mail
from ..utils.redis_utils import track_visit_counts
from ..utils.route_utils import handle_errors, require_json

auth_bp: Blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


# Internal helpers
def make_tokens(user_id: str, role: str) -> Dict[str, str]:
    """
    Генерирует пару access/refresh токенов для заданного user_id и роли.
    """
    claims = {"role": role}
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
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# Authentication endpoints
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@handle_errors
def refresh() -> Tuple[Response, int]:
    """POST /api/auth/refresh (refresh token required)"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "")
    logger.debug("refresh: user_id=%s", user_id)

    claims = {"role": role}
    access_token = create_access_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=timedelta(hours=1),
    )
    logger.debug("refresh: new access token generated for user_id=%s", user_id)
    return jsonify({"access_token": access_token}), 200


# Регистрация: запрос кода
@auth_bp.route("/request_registration_code", methods=["POST"])
@handle_errors
@require_json("email", "first_name", "last_name")
def request_registration_code() -> Tuple[Response, int]:
    data = request.get_json()
    logger.debug("request_registration_code: payload=%s", data)
    raw_email = data["email"].lower().strip()
    first_name, last_name = data["first_name"].strip(), data["last_name"].strip()
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # Нормализация и валидация e-mail
    try:
        validated = validate_email(raw_email)
        email = validated.normalized
        logger.debug("request_registration_code: validated email=%s", email)
    except EmailNotValidError as e:
        logger.warning("request_registration_code: invalid email %s: %s", raw_email, e)
        return jsonify({"error": str(e)}), 400

    # проверяем, что пользователя с таким e-mail ещё нет
    with session_scope() as session:
        exists_email = session.query(Users).filter_by(email=email).first()
    if exists_email:
        logger.debug("request_registration_code: registration attempt with existing email %s", email)
        return jsonify({"error": "Пользователь с таким e-mail уже зарегистрирован"}), 400

    # Генерация кода и отправка письма
    logger.debug("request_registration_code: generating code for %s", email)
    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    key  = f"email_reg:{email}"
    redis_client.setex(key, 600, "|".join([code, first_name, last_name]))
    logger.debug("request_registration_code: stored code in redis key=%s", key)

    # шлём письмо
    msg = Message(
        subject="Код подтверждения регистрации на Yanda Shop",
        recipients=[email],
        body=(
            f"Здравствуйте, {first_name}!\n\n"
            f"Ваш код регистрации: {code}\n"
            "Он действителен 10 минут.\n\n"
            "Если вы не запрашивали, просто проигнорируйте."
        )
    )
    mail.send(msg)
    logger.debug("request_registration_code: confirmation email sent to %s", email)

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=0,
            action_type="Регистрация",
            description=f"Попытка регистрации пользователя: {first_name} {last_name}",
            timestamp=now,
        ))
    logger.debug("request_registration_code: change log saved for new registration attempt")

    logger.debug("Registration code sent to %s", email)
    return jsonify({"status": "code_sent"}), 200


# Регистрация: верификация кода
@auth_bp.route("/verify_registration_code", methods=["POST"])
@handle_errors
@require_json("email", "code")
def verify_registration_code():
    data = request.get_json()
    logger.debug("verify_registration_code: payload=%s", data)
    email = data["email"].lower().strip()
    code = data["code"].strip()
    key = f"email_reg:{email}"
    stored = redis_client.get(key)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    if not stored:
        logger.warning("verify_registration_code: no code found in redis for %s", email)
        return jsonify({"error": "Код не найден или истёк"}), 400

    stored_code, first_name, last_name = stored.split("|", 2)
    if code != stored_code:
        logger.warning("verify_registration_code: invalid code %s for %s", code, email)
        return jsonify({"error": "Неверный код"}), 400

    redis_client.delete(key)
    logger.debug("verify_registration_code: deleted redis key %s", key)

    # создаём пользователя
    with session_scope() as session:
        user = Users(
            first_name=first_name,
            last_name=last_name,
            email=email,
            email_verified=True,
            last_visit=now
        )
        session.add(user)
        session.flush()
        user_id = str(user.user_id)
    logger.debug("verify_registration_code: new user created id=%d email=%s", user_id, email)

    # Redis: track visit counts
    track_visit_counts(str(user_id))

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=user_id,
            action_type="Регистрация",
            description=f"Успешная регистрация пользователя: {first_name} {last_name}",
            timestamp=now,
        ))
    logger.debug("verify_registration_code: change log saved for user_id=%s", user_id)

    tokens = make_tokens(user_id, "customer")
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    logger.debug("verify_registration_code: tokens issued for new user_id=%s", user_id)
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200


# Авторизация: запрос кода
@auth_bp.route("/request_login_code", methods=["POST"])
@handle_errors
@require_json("email")
def request_login_code():
    data = request.get_json()
    logger.debug("request_login_code: payload=%s", data)
    raw_email = data["email"].lower().strip()
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # Нормализация и валидация e-mail
    try:
        validated = validate_email(raw_email)
        email = validated.normalized
        logger.debug("request_login_code: validated email=%s", email)
    except EmailNotValidError as e:
        logger.warning("request_login_code: invalid email %s: %s", raw_email, e)
        return jsonify({"error": str(e)}), 400

    # проверяем, что пользователь есть
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            logger.debug("request_login_code: login attempt for unknown email %s", email)
            return jsonify({"error": "Пользователь не найден"}), 404
        user_id = user.user_id
        first_name = user.first_name
        last_name = user.last_name

    logger.debug("request_login_code: generating code for user_id=%d", user_id)
    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    key = f"email_login:{email}"
    redis_client.setex(key, 600, code)
    logger.debug("request_login_code: stored login code in redis key=%s", key)

    msg = Message(
        subject="Код входа на Yanda Shop",
        recipients=[email],
        body=(
            f"Здравствуйте, {first_name}!\n\n"
            f"Ваш код входа: {code}\n"
            f"Он действителен 10 минут.\n\n"
            "Если вы не запрашивали, просто проигнорируйте."
        )
    )
    mail.send(msg)
    logger.debug("request_login_code: login email sent to %s", email)

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=user_id,
            action_type="Авторизация",
            description=f"Попытка входа в аккаунт: {first_name} {last_name}",
            timestamp=now,
        ))
    logger.debug("request_login_code: change log saved for login attempt user_id=%d", user_id)

    logger.debug("Login code sent to %s", email)
    return jsonify({"status": "code_sent"}), 200


# Авторизация: верификация кода
@auth_bp.route("/verify_login_code", methods=["POST"])
@handle_errors
@require_json("email", "code")
def verify_login_code():
    data = request.get_json()
    logger.debug("verify_login_code: payload=%s", data)
    email = data["email"].lower().strip()
    code = data["code"].strip()
    key = f"email_login:{email}"
    stored = redis_client.get(key)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    if not stored:
        logger.warning("verify_login_code: no code in redis for %s", email)
        return jsonify({"error": "Код не найден или истёк"}), 400

    if code != stored:
        logger.warning("verify_login_code: invalid code %s for %s", code, email)
        return jsonify({"error": "Неверный код"}), 400

    # получаем пользователя из БД
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            logger.warning("verify_login_code: user not found after code match for %s", email)
            return jsonify({"error": "Пользователь не найден"}), 404
        user.last_visit = now
        user_id = user.user_id
        first_name = user.first_name
        last_name = user.last_name
        role = user.role
    logger.debug("verify_login_code: user found id=%d, updating last_visit", user_id)

    # Redis: track visit counts
    track_visit_counts(str(user_id))

    redis_client.delete(key)
    logger.debug("verify_login_code: deleted redis key %s", key)

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=user_id,
            action_type="Авторизация",
            description=f"Успешный вход в аккаунт: {first_name} {last_name}",
            timestamp=now,
        ))
    logger.debug("verify_login_code: change log saved for successful login user_id=%d", user_id)

    tokens = make_tokens(str(user_id), role)
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    logger.debug("verify_login_code: tokens issued for user_id=%s", user_id)
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200
