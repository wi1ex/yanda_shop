from typing import Tuple, Dict, Any, List
from flask import Blueprint, request, jsonify, Response
from ..core.logging import logger
from ..models import Shoe, Clothing, Accessory
from ..utils.cache_utils import cache_get, cache_set
from ..utils.db_utils import session_scope
from ..utils.product_serializer import serialize_product, model_by_category
from ..utils.route_utils import handle_errors, require_args, require_json

product_api: Blueprint = Blueprint("product_api", __name__, url_prefix="/api/product")


@product_api.route("/list_products", methods=["GET"])
@handle_errors
def list_products() -> Tuple[Response, int]:
    """
    GET /api/product/list_products?category=<cat>
    Возвращает все товары или только указанной категории.
    """
    category = request.args.get("category", "").lower().strip()
    logger.debug("list_products: category=%s", category)

    if category:
        Model = model_by_category(category)
        if not Model:
            logger.error("list_products: unknown category %s", category)
            return jsonify({"error": "unknown category"}), 400
        models = [Model]
    else:
        models = [Shoe, Clothing, Accessory]

    result: List[Dict[str, Any]] = []
    with session_scope() as session:
        for Model in models:
            objs = session.query(Model).filter(Model.count_in_stock >= 0).all()
            for obj in objs:
                result.append(serialize_product(obj))

    logger.info("list_products: returned %d items", len(result))
    return jsonify(result), 200


@product_api.route("/get_product", methods=["GET"])
@handle_errors
@require_args("category", "variant_sku")
def get_product() -> Tuple[Response, int]:
    """
    GET /api/product/get_product?category=<cat>&variant_sku=<sku>
    Возвращает один товар по SKU.
    """
    category = request.args["category"].lower().strip()
    variant_sku = request.args["variant_sku"].strip()
    logger.debug("get_product: category=%s variant_sku=%s", category, variant_sku)

    Model = model_by_category(category)
    if not Model:
        logger.error("get_product: unknown category %s", category)
        return jsonify({"error": "unknown category"}), 400

    with session_scope() as session:
        obj = session.query(Model).filter_by(variant_sku=variant_sku).first()
        if not obj:
            logger.warning("get_product: not found %s/%s", category, variant_sku)
            return jsonify({"error": "not found"}), 404
        data = serialize_product(obj)

    logger.info("get_product: found product %s/%s", category, variant_sku)
    return jsonify(data), 200


@product_api.route("/get_cart", methods=["GET"])
@handle_errors
@require_args("user_id")
def get_cart() -> Tuple[Response, int]:
    """
    GET /api/product/get_cart?user_id=<id>
    Возвращает содержимое корзины из Redis.
    """
    uid = int(request.args["user_id"])
    logger.debug("get_cart: user_id=%d", uid)

    key = f"cart:{uid}"
    payload = cache_get(key) or {"items": []}
    records = payload.get("items", [])

    result_items: List[Dict[str, Any]] = []
    total = 0
    with session_scope() as session:
        for rec in records:
            sku = rec.get("variant_sku")
            label = rec.get("delivery_label")
            logger.debug("get_cart: processing sku=%r label=%r", sku, label)

            obj = (
                session.query(Shoe).filter_by(variant_sku=sku).first() or
                session.query(Clothing).filter_by(variant_sku=sku).first() or
                session.query(Accessory).filter_by(variant_sku=sku).first()
            )
            if not obj:
                logger.warning("get_cart: item %r not found, skipping", sku)
                continue

            data = serialize_product(obj)
            opt = next((o for o in data["delivery_options"] if o["label"] == label), None)
            price = obj.price * (opt["multiplier"] if opt else 1)
            unit_price = round(price)
            data["unit_price"] = unit_price
            data["delivery_option"] = opt

            result_items.append(data)
            total += unit_price

    logger.info("get_cart: returning %d items, total=%d", len(result_items), total)
    return jsonify({"items": result_items, "count": len(result_items), "total": total}), 200


@product_api.route("/save_cart", methods=["POST"])
@handle_errors
@require_json("user_id", "items")
def save_cart() -> Tuple[Response, int]:
    """
    POST /api/product/save_cart
    JSON {user_id: int, items: List[...] }
    """
    data = request.get_json()
    uid = int(data["user_id"])
    items = data["items"]
    logger.debug("save_cart: user_id=%d items=%d", uid, len(items))

    key = f"cart:{uid}"
    cache_set(key, {"items": items}, ttl_seconds=60*60*24*365)

    logger.info("save_cart: saved %d items for user %d", len(items), uid)
    return jsonify({"status": "ok"}), 200


@product_api.route("/get_favorites", methods=["GET"])
@handle_errors
@require_args("user_id")
def get_favorites() -> Tuple[Response, int]:
    """
    GET /api/product/get_favorites?user_id=<id>
    Возвращает избранное из Redis.
    """
    uid = int(request.args["user_id"])
    logger.debug("get_favorites: user_id=%d", uid)

    key = f"favorites:{uid}"
    payload = cache_get(key) or {"items": [], "count": 0}

    logger.info("get_favorites: returning %d items", payload.get("count", 0))
    return jsonify(payload), 200


@product_api.route("/save_favorites", methods=["POST"])
@handle_errors
@require_json("user_id", "items")
def save_favorites() -> Tuple[Response, int]:
    """
    POST /api/product/save_favorites
    JSON {user_id: int, items: List[...] }
    """
    data = request.get_json()
    uid = int(data["user_id"])
    items = data["items"]
    payload = {"items": items, "count": len(items)}
    logger.debug("save_favorites: user_id=%d items=%d", uid, len(items))

    key = f"favorites:{uid}"
    cache_set(key, payload, ttl_seconds=60*60*24*365)

    logger.info("save_favorites: saved %d items for user %d", len(items), uid)
    return jsonify({"status": "ok"}), 200
