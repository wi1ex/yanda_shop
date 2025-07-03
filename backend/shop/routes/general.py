import io
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import or_
from typing import Any, Dict, Tuple, List
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token, create_refresh_token
from ..core.config import BACKEND_URL
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..extensions import redis_client, minio_client, BUCKET
from ..models import (
    Users,
    ChangeLog,
    AdminSetting,
    Review,
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
        logger.debug("save_user: non-integer id %r, skipping Postgres", raw_id)
        is_tg = False

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    photo_url = data.get("photo_url")
    now = datetime.now(ZoneInfo("Europe/Moscow"))

    # --- Postgres only for Telegram users ---
    if is_tg:
        try:
            user_id = int(raw_id)
            with session_scope() as session:
                # Get or create user
                tg_user = session.get(Users, user_id)
                if not tg_user:
                    tg_user = Users(
                        user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        last_visit=now
                    )
                    session.add(tg_user)
                    session.add(ChangeLog(
                        author_id=user_id,
                        author_name=username,
                        action_type="Регистрация",
                        description=f"Новый пользователь Telegram: {first_name} {last_name}",
                        timestamp=now
                    ))
                else:
                    # Update changed fields
                    updated = False
                    for fld in ("first_name", "last_name", "username"):
                        val = data.get(fld)
                        if val and getattr(tg_user, fld) != val:
                            setattr(tg_user, fld, val)
                            updated = True
                    tg_user.last_visit = now
                    if updated:
                        session.merge(tg_user)

                # Handle avatar update
                if photo_url:
                    filename = secure_filename(photo_url.split("/")[-1])
                    new_key = f"users/{user_id}_{filename}"
                    if tg_user.avatar_url != new_key:
                        # Remove old avatar if exists
                        if tg_user.avatar_url:
                            try:
                                minio_client.remove_object(BUCKET, tg_user.avatar_url)
                            except Exception as e:
                                logger.warning("Failed to remove old avatar %s: %s", tg_user.avatar_url, e)
                        # Download and upload new avatar
                        resp = requests.get(photo_url, timeout=10)
                        if resp.ok:
                            content = resp.content
                            minio_client.put_object(BUCKET, new_key, io.BytesIO(content), len(content))
                            tg_user.avatar_url = new_key

        except Exception as e:
            logger.exception("Postgres error in save_user: %s", e)
            return jsonify({"error": "internal server error"}), 500

    # --- Redis always for visits ---
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
    logger.info("GET /api/general/get_user_profile?user_id=%s", uid_str)
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
                "role": u.role,
                "photo_url": u.avatar_url and f"{BACKEND_URL}/images/{u.avatar_url}" or None,
                "created_at": u.created_at.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
            }
            # если админ — вручаем JWT
            if u.role == "admin":
                access = create_access_token(identity=str(u.user_id), additional_claims={"role": u.role})
                refresh = create_refresh_token(identity=str(u.user_id), additional_claims={"role": u.role})
                profile["access_token"] = access
                profile["refresh_token"] = refresh

        return jsonify(profile), 200

    except Exception as e:
        logger.exception("Failed to get_user_profile: %s", e)
        return jsonify({"error": "internal error"}), 500


@general_api.route("/get_parameters")
def get_parameters() -> Tuple[Response, int]:
    base_keys = ["url_telegram", "url_instagram", "url_email"]
    default_result = {k: "" for k in base_keys}

    try:
        with session_scope() as session:
            faq_keys_query = session.query(AdminSetting.key).filter(or_(AdminSetting.key.like('faq_question_%'), AdminSetting.key.like('faq_answer_%'))).distinct()
            faq_keys = [result.key for result in faq_keys_query]
            all_keys = base_keys + faq_keys
            settings = session.query(AdminSetting).filter(AdminSetting.key.in_(all_keys)).all()
            result = {k: "" for k in all_keys}
            for setting in settings:
                result[setting.key] = setting.value or ""

            return jsonify(result), 200

    except Exception as e:
        logger.exception("Failed to get_parameters: %s", e)
        return jsonify(default_result), 500


@general_api.route('/list_reviews', methods=['GET'])
def list_reviews() -> Tuple[Response, int]:
    logger.info("GET /api/general/list_reviews")
    try:
        with session_scope() as session:
            revs = session.query(Review).order_by(Review.created_at.desc()).all()
            data: List[Dict[str, Any]] = []
            for r in revs:
                # находим в MinIO все объекты reviews/{r.id}_*
                objs = minio_client.list_objects(BUCKET, prefix=f'reviews/{r.id}_', recursive=True)
                urls = [f"{BACKEND_URL}/images/{obj.object_name}" for obj in objs]
                data.append({
                    "id":            r.id,
                    "client_name":   r.client_name,
                    "client_text1":  r.client_text1,
                    "shop_response": r.shop_response,
                    "client_text2":  r.client_text2,
                    "link_url":      r.link_url,
                    "photo_urls":    urls,
                    "created_at":    r.created_at.astimezone(ZoneInfo("Europe/Moscow")).isoformat()
                })
        return jsonify({"reviews": data}), 200

    except Exception as e:
        logger.exception("Failed to list_reviews: %s", e)
        return jsonify({"error": "internal error"}), 500
