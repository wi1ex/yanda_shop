from datetime import datetime
from typing import Any, Dict, Tuple
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify, request, Response
from ..cors.logging import logger
from ..db_utils import session_scope
from ..extensions import redis_client
from ..models import (
    Users,
    ChangeLog,
    AdminSetting,
)

general_api: Blueprint = Blueprint("general_api", __name__, url_prefix="/api/general")


@general_api.route("/")
def home() -> Tuple[Response, int]:
    logger.debug("Health check: /api/ called")
    return jsonify({"message": "App is working!"}), 200


@general_api.route("/save_user", methods=["POST"])
def save_user() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    logger.debug("save_user payload: %s", data)

    if "id" not in data:
        logger.error("save_user: missing 'id'")
        return jsonify({"error": "missing user id"}), 400

    raw_id = data["id"]
    try:
        int(raw_id)
        is_tg = True
    except (TypeError, ValueError):
        # Неконвертируемый id — это не Telegram-пользователь, но не ошибка!
        logger.debug("save_user: non-integer id %r, skipping Postgres", raw_id)
        is_tg = False

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    # photo_url = data.get("photo_url")

    # --- Postgres только для целых id ---
    if is_tg:
        user_id = int(raw_id)
        try:
            with session_scope() as session:
                # получаем пользователя из сессии
                tg_user = session.get(Users, user_id)
                if not tg_user:
                    tg_user = Users(
                        user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        username=username
                    )
                    session.add(tg_user)
                    session.add(ChangeLog(
                        author_id=user_id,
                        author_name=username,
                        action_type="Регистрация",
                        description=f"Новый пользователь Telegram: {first_name} {last_name}",
                        timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
                    ))
                else:
                    # обновляем только если изменилось
                    changed = False
                    for fld in ("first_name", "last_name", "username"):
                        new = data.get(fld)
                        if new and getattr(tg_user, fld) != new:
                            setattr(tg_user, fld, new)
                            changed = True
                    if changed:
                        session.merge(tg_user)
        except Exception as e:
            logger.exception("Postgres error in save_user: %s", e)
            return jsonify({"error": "internal server error"}), 500

    # --- Redis всегда ---
    try:
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")

        total_key = f"visits:{date_str}:{hour_str}:total"
        unique_key = f"visits:{date_str}:{hour_str}:unique"

        # если raw_id не число, всё равно кладём в Redis строку raw_id
        redis_client.incr(total_key)
        redis_client.sadd(unique_key, raw_id)
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(total_key, ttl)
        redis_client.expire(unique_key, ttl)

        logger.debug("save_user REDIS updated visit counters for %r", raw_id)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        logger.exception("Redis error in save_user: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@general_api.route("/get_user_profile")
def get_user_profile() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    if not uid_str:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        with session_scope() as session:
            u = session.get(Users, uid)
            if not u:
                return jsonify({"error": "not found"}), 404

            profile = {
                "user_id": u.user_id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "username": u.username,
                "created_at": u.created_at.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
            }

        return jsonify(profile), 200

    except Exception as e:
        logger.exception("Error fetching user %d: %s", uid, e)
        return jsonify({"error": "internal error"}), 500


@general_api.route("/get_social_urls")
def get_social_urls() -> Tuple[Response, int]:
    keys = ["url_telegram", "url_instagram", "url_email"]
    try:
        # сразу формируем результат внутри сессии
        with session_scope() as session:
            raw = session.query(AdminSetting).filter(AdminSetting.key.in_(keys)).all()
            result = {k: "" for k in keys}
            for s in raw:
                # s.value уже подгружен, т. е. нет lazy-load после закрытия
                result[s.key] = s.value or ""
        return jsonify(result), 200

    except Exception as e:
        logger.exception("Error in get_social_urls: %s", e)
        return jsonify({k: "" for k in keys}), 200
