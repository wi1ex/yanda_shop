import json
from datetime import datetime
from typing import Any, Dict, Tuple
from zoneinfo import ZoneInfo
from flask import Blueprint, Flask, jsonify, request, Response
from .extensions import redis_client
from .db_utils import session_scope
from .cors.logging import logger
from .models import (
    Shoe,
    Clothing,
    Accessory,
    Users,
    ChangeLog,
    AdminSetting,
)
from .utils import (
    serialize_product,
    model_by_category,
)

api: Blueprint = Blueprint("api", __name__, url_prefix="/api")


@api.route("/")
def home() -> Tuple[Response, int]:
    logger.debug("Health check: /api/ called")
    return jsonify({"message": "App is working!"}), 200


@api.route("/save_user", methods=["POST"])
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

        logger.info("save_user REDIS updated visit counters for %r", raw_id)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        logger.exception("Redis error in save_user: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@api.route("/list_products")
def list_products() -> Response:
    cat = request.args.get("category", "").lower()
    logger.debug("list_products category=%s", cat)

    # если категория указана — фильтруем по ней, иначе — все три модели
    if cat:
        Model = model_by_category(cat)
        if not Model:
            logger.error("Unknown category %s", cat)
            return jsonify({"error": "unknown category"}), 400
        models = [Model]
    else:
        models = [Shoe, Clothing, Accessory]

    result = []
    with session_scope() as session:
        for Model in models:
            objs = session.query(Model).filter(Model.count_in_stock >= 0).all()
            for obj in objs:
                result.append(serialize_product(obj))

    return jsonify(result), 200


@api.route("/get_product")
def get_product() -> Tuple[Response, int]:
    category = request.args.get("category", "").lower()
    variant_sku = request.args.get("variant_sku", "").strip()
    logger.debug("get_product category=%s variant_sku=%s", category, variant_sku)

    if not category or not variant_sku:
        logger.error("Missing category or variant_sku")
        return jsonify({"error": "category and variant_sku required"}), 400

    Model = model_by_category(category)
    if not Model:
        logger.error("Unknown category %s", category)
        return jsonify({"error": "unknown category"}), 400

    with session_scope() as session:
        obj = session.query(Model).filter_by(variant_sku=variant_sku).first()
        if not obj:
            logger.warning("Product not found %s/%s", category, variant_sku)
            return jsonify({"error": "not found"}), 404
        # сериализуем пока сессия ещё жива
        data = serialize_product(obj)

    return jsonify(data), 200


@api.route("/get_user_profile")
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


@api.route("/get_social_urls")
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


@api.route("/get_cart", methods=["GET"])
def get_cart() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    logger.debug("get_cart called with user_id=%r", uid_str)
    if not uid_str:
        logger.warning("get_cart: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        logger.warning("get_cart: invalid user_id %r", uid_str)
        return jsonify({"error": "invalid user_id"}), 400

    try:
        key = f"cart:{uid}"
        raw = redis_client.get(key)
        logger.debug("Redis GET %s → %r", key, raw)
        if not raw:
            logger.info("get_cart: no cart found for user %d", uid)
            return jsonify({"items": [], "count": 0, "total": 0}), 200

        payload = json.loads(raw)
        records = payload.get("items", [])
        logger.debug("Found %d records in cart payload", len(records))

        result_items = []
        total = 0

        with session_scope() as session:
            for rec in records:
                sku = rec.get("variant_sku")
                lbl = rec.get("delivery_label")
                logger.debug("Processing record sku=%r, label=%r", sku, lbl)

                obj = (
                    session.query(Shoe).filter_by(variant_sku=sku).first() or
                    session.query(Clothing).filter_by(variant_sku=sku).first() or
                    session.query(Accessory).filter_by(variant_sku=sku).first()
                )
                if not obj:
                    logger.warning("Item %r not found in DB, skipping", sku)
                    continue

                data = serialize_product(obj)
                opt = next((o for o in data["delivery_options"] if o["label"] == lbl), None)
                unit_price = round(obj.price * (opt["multiplier"] if opt else 1))

                data["price"] = unit_price
                data["delivery_option"] = opt

                result_items.append(data)
                total += unit_price

        logger.info("get_cart: returning %d items, total=%d", len(result_items), total)
        return jsonify({"items": result_items, "count": len(result_items), "total": total}), 200

    except Exception as e:
        logger.exception("Exception in get_cart:")
        return jsonify({"error": "internal error"}), 500


@api.route("/save_cart", methods=["POST"])
def save_cart() -> Tuple[Response, int]:
    data = request.get_json(force=True, silent=True) or {}
    logger.debug("save_cart payload: %r", data)
    if "user_id" not in data:
        logger.warning("save_cart: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(data["user_id"])
    except (TypeError, ValueError):
        logger.warning("save_cart: invalid user_id %r", data.get("user_id"))
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    try:
        key = f"cart:{uid}"
        redis_client.set(key, json.dumps({"items": items}))
        redis_client.expire(key, 60 * 60 * 24 * 365)
        logger.info("save_cart: saved %d items for user %d", len(items), uid)
        return jsonify({"status": "ok"}), 200
    except Exception:
        logger.exception("Exception in save_cart:")
        return jsonify({"error": "internal redis error"}), 500


@api.route("/get_favorites", methods=["GET"])
def get_favorites() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    logger.debug("get_favorites called with user_id=%r", uid_str)
    if not uid_str:
        logger.warning("get_favorites: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        logger.warning("get_favorites: invalid user_id %r", uid_str)
        return jsonify({"error": "invalid user_id"}), 400

    try:
        key = f"favorites:{uid}"
        raw = redis_client.get(key)
        logger.debug("Redis GET %s → %r", key, raw)
        if not raw:
            logger.info("get_favorites: no favorites for user %d", uid)
            return jsonify({"items": [], "count": 0}), 200
        payload = json.loads(raw)
        logger.info("get_favorites: returning %d items", payload.get("count", 0))
        return jsonify(payload), 200
    except Exception:
        logger.exception("Exception in get_favorites:")
        return jsonify({"error": "internal redis error"}), 500


@api.route("/save_favorites", methods=["POST"])
def save_favorites() -> Tuple[Response, int]:
    data = request.get_json(force=True, silent=True) or {}
    logger.debug("save_favorites payload: %r", data)
    if "user_id" not in data:
        logger.warning("save_favorites: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(data["user_id"])
    except (TypeError, ValueError):
        logger.warning("save_favorites: invalid user_id %r", data.get("user_id"))
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    payload = {"items": items, "count": len(items)}
    try:
        key = f"favorites:{uid}"
        redis_client.set(key, json.dumps(payload))
        redis_client.expire(key, 60 * 60 * 24 * 365)
        logger.info("save_favorites: saved %d items for user %d", len(items), uid)
        return jsonify({"status": "ok"}), 200
    except Exception:
        logger.exception("Exception in save_favorites:")
        return jsonify({"error": "internal redis error"}), 500


def register_routes(app: Flask) -> None:
    # Регистрируем все ваши @api маршруты
    app.register_blueprint(api)
