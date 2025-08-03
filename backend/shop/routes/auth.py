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


# Регистрация: запрос кода
@auth_bp.route("/request_registration_code", methods=["POST"])
@handle_errors
@require_json("email", "username", "first_name", "last_name")
def request_registration_code() -> Tuple[Response, int]:
    data = request.get_json()
    raw_email = data["email"].lower().strip()
    username, first_name, last_name = (
        data["username"].strip(),
        data["first_name"].strip(),
        data["last_name"].strip(),
    )
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # Нормализация и валидация e-mail
    try:
        validated = validate_email(raw_email)
        email = validated.normalized
    except EmailNotValidError as e:
        return jsonify({"error": str(e)}), 400

    # проверяем, что пользователя с таким e-mail ещё нет
    with session_scope() as session:
        exists_email = session.query(Users).filter_by(email=email).first()
        exists_username = session.query(Users).filter_by(username=username).first()
    if exists_email:
        return jsonify({"error": "Пользователь с таким e-mail уже зарегистрирован"}), 400
    if exists_username:
        return jsonify({"error": "Пользователь с таким никнеймом уже зарегистрирован"}), 400

    # Генерация кода и отправка письма
    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    key  = f"email_reg:{email}"
    redis_client.setex(key, 600, "|".join([code, username, first_name, last_name]))

    # шлём письмо
    msg = Message(
        subject="Код подтверждения регистрации на Yanda Shop",
        recipients=[email],
        body=(
            f"Здравствуйте, {username}!\n\n"
            f"Ваш код регистрации: {code}\n"
            "Он действителен 10 минут.\n\n"
            "Если вы не запрашивали, просто проигнорируйте."
        )
    )
    mail.send(msg)

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=0,
            author_name=username,
            action_type="Регистрация",
            description=f"Попытка регистрации пользователя: {first_name} {last_name}",
            timestamp=now,
        ))

    logger.info("Registration code sent to %s", email)
    return jsonify({"status": "code_sent"}), 200


# Регистрация: верификация кода
@auth_bp.route("/verify_registration_code", methods=["POST"])
@handle_errors
@require_json("email", "code")
def verify_registration_code():
    data = request.get_json()
    email = data["email"].lower().strip()
    code = data["code"].strip()
    key = f"email_reg:{email}"
    stored = redis_client.get(key)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    if not stored:
        return jsonify({"error": "Код не найден или истёк"}), 400

    stored_code, username, first_name, last_name = stored.split("|", 3)
    if code != stored_code:
        return jsonify({"error": "Неверный код"}), 400

    redis_client.delete(key)

    # создаём пользователя
    with session_scope() as session:
        user = Users(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            email_verified=True,
            last_visit=now
        )
        session.add(user)
        session.flush()
        user_id = str(user.user_id)

        session.add(ChangeLog(
            author_id=user_id,
            author_name=username,
            action_type="Регистрация",
            description=f"Успешная регистрация пользователя: {first_name} {last_name}",
            timestamp=now,
        ))

    tokens = make_tokens(user_id, username, "customer")
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
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
    raw_email = data["email"].lower().strip()
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # Нормализация и валидация e-mail
    try:
        validated = validate_email(raw_email)
        email = validated.normalized
    except EmailNotValidError as e:
        return jsonify({"error": str(e)}), 400

    # проверяем, что пользователь есть
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        user_id = user.user_id
        username = user.username
        first_name = user.first_name
        last_name = user.last_name

    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    key = f"email_login:{email}"
    redis_client.setex(key, 600, f"{code}|{username}")

    msg = Message(
        subject="Код входа на Yanda Shop",
        recipients=[email],
        body=(
            f"Здравствуйте, {username}!\n\n"
            f"Ваш код входа: {code}\n"
            f"Он действителен 10 минут.\n\n"
            "Если вы не запрашивали, просто проигнорируйте."
        )
    )
    mail.send(msg)

    with session_scope() as session:
        session.add(ChangeLog(
            author_id=user_id,
            author_name=username,
            action_type="Авторизация",
            description=f"Попытка входа в аккаунт: {first_name} {last_name}",
            timestamp=now,
        ))

    logger.info("Login code sent to %s", email)
    return jsonify({"status": "code_sent"}), 200


# Авторизация: верификация кода
@auth_bp.route("/verify_login_code", methods=["POST"])
@handle_errors
@require_json("email", "code")
def verify_login_code():
    data = request.get_json()
    email = data["email"].lower().strip()
    code = data["code"].strip()
    key = f"email_login:{email}"
    stored = redis_client.get(key)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    if not stored:
        return jsonify({"error": "Код не найден или истёк"}), 400

    stored_code, username = stored.split("|", 1)
    if code != stored_code:
        return jsonify({"error": "Неверный код"}), 400

    redis_client.delete(key)

    # получаем пользователя из БД
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        user.last_visit = now

        session.add(ChangeLog(
            author_id=user.user_id,
            author_name=user.username,
            action_type="Авторизация",
            description=f"Успешный вход в аккаунт: {user.first_name} {user.last_name}",
            timestamp=now,
        ))

    # Redis: track visit counts
    track_visit_counts(str(user.user_id))

    tokens = make_tokens(str(user.user_id), user.username, user.role)
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200
