import json
from typing import Tuple
from flask import Blueprint, jsonify, request, Response
from ..core.logging import logger
from ..utils.db_utils import session_scope
from ..extensions import redis_client
from ..models import (
    Shoe,
    Clothing,
    Accessory,
)
from ..utils.product_serializer import (
    serialize_product,
    model_by_category,
)

product_api: Blueprint = Blueprint("product_api", __name__, url_prefix="/api/product")


@product_api.route("/list_products")
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
    try:
        with session_scope() as session:
            for Model in models:
                objs = session.query(Model).filter(Model.count_in_stock >= 0).all()
                for obj in objs:
                    result.append(serialize_product(obj))

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Exception in list_products: %s", e)
        return jsonify({"error": "internal error"}), 500


@product_api.route("/get_product")
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

    try:
        with session_scope() as session:
            obj = session.query(Model).filter_by(variant_sku=variant_sku).first()
            if not obj:
                logger.warning("Product not found %s/%s", category, variant_sku)
                return jsonify({"error": "not found"}), 404
            # сериализуем пока сессия ещё жива
            data = serialize_product(obj)

        return jsonify(data), 200

    except Exception as e:
        logger.exception("Exception in get_product: %s", e)
        return jsonify({"error": "internal error"}), 500


@product_api.route("/get_cart", methods=["GET"])
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

                data["unit_price"] = unit_price
                data["delivery_option"] = opt

                result_items.append(data)
                total += unit_price

        logger.info("get_cart: returning %d items, total=%d", len(result_items), total)
        return jsonify({"items": result_items, "count": len(result_items), "total": total}), 200

    except Exception as e:
        logger.exception("Exception in get_cart: %s", e)
        return jsonify({"error": "internal error"}), 500


@product_api.route("/save_cart", methods=["POST"])
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
    except Exception as e:
        logger.exception("Exception in save_cart: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@product_api.route("/get_favorites", methods=["GET"])
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
    except Exception as e:
        logger.exception("Exception in get_favorites: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@product_api.route("/save_favorites", methods=["POST"])
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
    except Exception as e:
        logger.exception("Exception in save_favorites: %s", e)
        return jsonify({"error": "internal redis error"}), 500
