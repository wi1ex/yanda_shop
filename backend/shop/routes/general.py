import io
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, Tuple, List
from flask import Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename
from .auth import make_tokens
from ..core.logging import logger
from ..core.config import BACKEND_URL
from ..utils.db_utils import session_scope
from ..models import Users, ChangeLog, Review, RequestItem
from ..extensions import redis_client, minio_client, BUCKET
from ..utils.route_utils import handle_errors, require_args, require_json
from ..utils.storage_utils import upload_request_file

general_api: Blueprint = Blueprint("general_api", __name__, url_prefix="/api/general")


@general_api.route("/")
@handle_errors
def home() -> Tuple[Response, int]:
    """Health check endpoint"""
    return jsonify({"message": "App is working!"}), 200


@general_api.route("/save_user", methods=["POST"])
@handle_errors
@require_json("id")
def save_user() -> Tuple[Response, int]:
    """
    POST /api/general/save_user
    JSON body must include "id"; optional fields:
      first_name, last_name, username, photo_url
    """
    data: Dict[str, Any] = request.get_json()
    logger.debug("save_user: payload=%s", data)
    raw_id = data["id"]
    is_tg = False
    # Determine if Telegram user (numeric)
    try:
        int(raw_id)
        is_tg = True
    except (TypeError, ValueError):
        logger.debug("save_user: non-integer id %r, skip Postgres", raw_id)

    now = datetime.now(ZoneInfo("Europe/Moscow"))
    if is_tg:
        user_id    = int(raw_id)
        first_name = data.get("first_name")
        last_name  = data.get("last_name")
        username   = data.get("username")
        photo_url  = data.get("photo_url")

        try:
            with session_scope() as session:
                tg_user = session.get(Users, user_id)
                if not tg_user:
                    tg_user = Users(
                        user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        last_visit=now,
                    )
                    session.add(tg_user)
                    session.add(ChangeLog(
                        author_id=user_id,
                        author_name=username,
                        action_type="Регистрация",
                        description=f"Новый Telegram-пользователь: {first_name} {last_name}",
                        timestamp=now,
                    ))
                else:
                    updated = False
                    for fld in ("first_name", "last_name", "username"):
                        val = data.get(fld)
                        if val and getattr(tg_user, fld) != val:
                            setattr(tg_user, fld, val)
                            updated = True
                    tg_user.last_visit = now
                    if updated:
                        session.merge(tg_user)

                # Avatar handling
                if photo_url:
                    filename = secure_filename(photo_url.split("/")[-1])
                    if tg_user.avatar_url != filename:
                        if tg_user.avatar_url:
                            old_key = f"users/{user_id}_{tg_user.avatar_url}"
                            try:
                                minio_client.remove_object(BUCKET, old_key)
                            except Exception as exc:
                                logger.warning("save_user: failed remove old avatar %s: %s", old_key, exc)
                        resp = requests.get(photo_url, timeout=10)
                        if resp.ok:
                            content = resp.content
                            new_key = f"users/{user_id}_{filename}"
                            try:
                                minio_client.put_object(BUCKET, new_key, io.BytesIO(content), len(content))
                                tg_user.avatar_url = filename
                            except Exception as exc:
                                logger.warning("save_user: failed upload new avatar %s: %s", new_key, exc)
        except Exception:
            logger.exception("save_user: Postgres error")
            return jsonify({"error": "internal server error"}), 500

    # Redis: track visit counts
    try:
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")
        total_key = f"visits:{date_str}:{hour_str}:total"
        unique_key = f"visits:{date_str}:{hour_str}:unique"

        redis_client.incr(total_key)
        redis_client.sadd(unique_key, raw_id)
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(total_key, ttl)
        redis_client.expire(unique_key, ttl)

        logger.debug("save_user: Redis visit counters updated for %r", raw_id)
        return jsonify({"status": "ok"}), 201
    except Exception:
        logger.exception("save_user: Redis error")
        return jsonify({"error": "internal redis error"}), 500


@general_api.route("/get_user_profile", methods=["GET"])
@handle_errors
@require_args("user_id")
def get_user_profile() -> Tuple[Response, int]:
    """
    GET /api/general/get_user_profile?user_id=<int>
    Returns user profile and tokens if admin.
    """
    uid_str = request.args["user_id"]
    try:
        uid = int(uid_str)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    with session_scope() as session:
        u = session.get(Users, uid)
        if not u:
            return jsonify({"error": "not found"}), 404

        profile: Dict[str, Any] = {
            "user_id":    u.user_id,
            "first_name": u.first_name,
            "last_name":  u.last_name,
            "username":   u.username,
            "role":       u.role,
            "photo_url":  f"{BACKEND_URL}/{BUCKET}/users/{u.user_id}_{u.avatar_url}" if u.avatar_url else None,
            "created_at": u.created_at.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        }
        if u.role == "admin":
            profile["access_token"], profile["refresh_token"] = make_tokens(str(u.user_id), u.username, u.role)

    return jsonify(profile), 200


@general_api.route("/get_parameters", methods=["GET"])
@handle_errors
def get_parameters() -> Tuple[Response, int]:
    """
    GET /api/general/get_parameters
    Returns social URLs and FAQ parameters.
    """
    try:
        raw = redis_client.get("parameters") or "{}"
        result = json.loads(raw)
        return jsonify(result), 200
    except Exception:
        logger.exception("get_parameters: failed")
        return jsonify({}), 500


@general_api.route("/list_reviews", methods=["GET"])
@handle_errors
def list_reviews() -> Tuple[Response, int]:
    """
    GET /api/general/list_reviews
    Returns reviews with associated photo URLs.
    """
    data: List[Dict[str, Any]] = []
    with session_scope() as session:
        revs = session.query(Review).order_by(Review.created_at.desc()).all()
        for r in revs:
            objs = minio_client.list_objects(BUCKET, prefix=f"reviews/{r.id}_", recursive=True)
            urls = [f"{BACKEND_URL}/{BUCKET}/{obj.object_name}" for obj in objs]
            data.append({
                "id":            r.id,
                "client_name":   r.client_name,
                "client_text1":  r.client_text1,
                "shop_response": r.shop_response,
                "client_text2":  r.client_text2,
                "link_url":      r.link_url,
                "photo_urls":    urls,
                "created_at":    r.created_at.astimezone(ZoneInfo("Europe/Moscow")).isoformat(),
            })

    return jsonify({"reviews": data}), 200


@general_api.route("/create_request", methods=["POST"])
@handle_errors
def create_request() -> Tuple[Response, int]:
    """
    POST /api/general/create_request
    Form-data: name*, email*, sku, file?
    """
    ip = request.remote_addr or "anon"
    key = f"rate:create_request:{ip}"
    if redis_client.get(key):
        return jsonify({"error": "Подождите 10 секунд перед новым запросом"}), 429
    # ставим TTL 10 сек
    redis_client.set(key, "1", ex=10)

    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    sku   = request.form.get("sku", "").strip()

    if not name or not email:
        return jsonify({"error": "Поля «Имя» и «Почта» обязательны"}), 400

    file = request.files.get("file")
    if file and request.content_length and request.content_length > 10 * 1024 * 1024:
        return jsonify({"error": "Файл не должен превышать 10 МБ"}), 400

    with session_scope() as session:
        req = RequestItem(
            name=name,
            email=email or None,
            sku=sku or None,
            has_file=bool(file)
        )
        session.add(req)
        session.flush()

        if file:
            upload_request_file(req.id, file)
        req_id = req.id

    logger.info("create_request: id=%d name=%s", req_id, name)
    return jsonify({"status": "ok"}), 201
