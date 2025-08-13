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
def touch_last_visit(user_id: int, strict: bool = False) -> None:
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    try:
        with session_scope() as session:
            updated = (
                session.query(Users)
                .filter(Users.user_id == user_id)
                .update({Users.last_visit: now}, synchronize_session=False)
            )
        if updated == 0:
            logger.warning("touch_last_visit: no rows updated for user_id=%s", user_id)
        else:
            logger.debug("touch_last_visit: user_id=%s last_visit=%s", user_id, now.isoformat())
    except Exception as exc:
        if strict:
            raise
        logger.warning("touch_last_visit: failed to update last_visit for user_id=%s: %s", user_id, exc, exc_info=True)


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
    logger.debug("make_tokens: new access token generated for user_id=%s", user_id)

    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=timedelta(days=7),
    )
    logger.debug("make_tokens: new refresh token generated for user_id=%s", user_id)

    touch_last_visit(int(user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# Authentication endpoints

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@handle_errors
def refresh() -> Tuple[Response, int]:
    """POST /api/auth/refresh (refresh token required)"""
    user_id = get_jwt_identity()
    jwt_claims = get_jwt()
    role = jwt_claims.get("role", "")
    logger.debug("refresh: user_id=%s role=%s", user_id, role)

    claims = {"role": role}
    access_token = create_access_token(
        identity=user_id,
        additional_claims=claims,
        expires_delta=timedelta(hours=1),
    )

    touch_last_visit(int(user_id))

    logger.debug("refresh: new access token generated for user_id=%s", user_id)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/request_code", methods=["POST"])
@handle_errors
@require_json("email")
def request_code() -> Tuple[Response, int]:
    """
    POST /api/auth/request_code
    Запрос кода для входа или регистрации по e-mail.
    Реализован анти-спам кулдаун (30 сек) по email и ip.
    """
    data = request.get_json()
    logger.debug("request_code: payload=%s", data)

    raw_email = data["email"].lower().strip()
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # Валидация e-mail
    try:
        validated = validate_email(raw_email)
        email = validated.normalized
        logger.debug("request_code: validated email=%s", email)
    except EmailNotValidError as e:
        logger.warning("request_code: invalid email %s: %s", raw_email, e)
        return jsonify({"error": str(e)}), 400

    # Кулдаун повторной отправки
    fwd_for = request.headers.get("X-Forwarded-For", "")
    ip = (fwd_for.split(",")[0].strip() if fwd_for else request.remote_addr) or "unknown"
    cooldown_key_email = f"email_code_cooldown:{email}"
    cooldown_key_ip    = f"email_code_cooldown_ip:{ip}"
    cooldown_seconds   = 30

    if redis_client.get(cooldown_key_email) or redis_client.get(cooldown_key_ip):
        ttl_email = redis_client.ttl(cooldown_key_email) or cooldown_seconds
        ttl_ip    = redis_client.ttl(cooldown_key_ip) or cooldown_seconds
        ttl = max(ttl_email, ttl_ip)
        ttl = ttl if ttl > 0 else cooldown_seconds
        logger.debug("request_code: cooldown active for %s (ip=%s), ttl=%s", email, ip, ttl)
        return jsonify({"error": f"Пожалуйста, подождите {ttl} сек перед повторной отправкой"}), 429

    # Новый или существующий пользователь
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        user_id = user.user_id if user else None

    is_new = user_id is None
    if is_new:
        logger.debug("request_code: no existing user for %s", email)
    else:
        logger.debug("request_code: existing user found id=%s for %s", user_id, email)

    # Генерация и хранение кода
    code_ttl_seconds = 600
    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    key = f"email_code:{email}"
    redis_client.setex(key, code_ttl_seconds, code)
    logger.debug("request_code: stored for %s", email)

    # Кулдаун
    redis_client.setex(cooldown_key_email, cooldown_seconds, "1")
    redis_client.setex(cooldown_key_ip, cooldown_seconds, "1")

    # Отправка письма
    subject = (
        "Код подтверждения регистрации на Yanda Shop"
        if is_new
        else "Код для входа на Yanda Shop"
    )
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш код {'регистрации' if is_new else 'входа'}: {code}\n"
        "Он действителен 10 минут.\n\n"
        "Если вы не запрашивали, просто проигнорируйте это письмо."
    )
    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)
    logger.debug("request_code: email sent to %s (action=%s)", email, "Регистрация" if is_new else "Авторизация")

    # Лог
    action = "Регистрация" if is_new else "Авторизация"
    with session_scope() as session:
        session.add(ChangeLog(
            author_id=0 if is_new else user_id,
            action_type=action,
            description=f"Попытка {action.lower()} по e-mail: {email}",
            timestamp=now,
        ))

    logger.debug("request_code: change log saved for %s attempt on %s", action.lower(), email)
    return jsonify({"status": "code_sent"}), 200


@auth_bp.route("/verify_code", methods=["POST"])
@handle_errors
@require_json("email", "code")
def verify_code() -> Tuple[Response, int]:
    """
    POST /api/auth/verify_code
    Верификация кода и выдача токенов.
    """
    data = request.get_json()
    logger.debug("verify_code: payload=%s", data)

    email = data["email"].lower().strip()
    code = data["code"].strip()
    key = f"email_code:{email}"
    stored = redis_client.get(key)
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    if not stored:
        logger.warning("verify_code: no code found in redis for %s", email)
        return jsonify({"error": "Код не найден или истёк"}), 400

    if code != stored:
        logger.warning("verify_code: invalid email %s", email)
        return jsonify({"error": "Неверный или просроченный код"}), 400

    redis_client.delete(key)
    logger.debug("verify_code: deleted redis key %s", key)

    # Получение или создание пользователя
    with session_scope() as session:
        user = session.query(Users).filter_by(email=email).first()
        if not user:
            user = Users(
                email=email,
                email_verified=True,
            )
            session.add(user)
            session.flush()
            user_id = str(user.user_id)
            role = "customer"
            action = "Регистрация"
            logger.debug("verify_code: created new user_id=%s for %s", user_id, email)
        else:
            user_id = str(user.user_id)
            role = user.role
            action = "Авторизация"
            logger.debug("verify_code: existing user_id=%s logged in", user_id)

        session.add(ChangeLog(
            author_id=int(user_id),
            action_type=action,
            description=f"Успешная {action.lower()}: {email}",
            timestamp=now,
        ))
    logger.debug("verify_code: change log saved for user_id=%s action=%s", user_id, action)

    # Обновляем счётчик визитов
    track_visit_counts(user_id)
    logger.debug("verify_code: visit count tracked for user_id=%s", user_id)

    # Генерация токенов
    tokens = make_tokens(user_id, role)
    logger.debug("verify_code: tokens issued for user_id=%s", user_id)

    return jsonify({
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }), 200
