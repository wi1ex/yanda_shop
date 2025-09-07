import io
import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, Tuple, List
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .auth import make_tokens
from ..core.logging import logger
from ..core.config import BACKEND_URL
from ..utils.db_utils import session_scope, adjust_user_order_stats
from ..models import Users, ChangeLog, Review, RequestItem, Addresses, Orders
from ..extensions import redis_client, minio_client, BUCKET
from ..utils.logging_utils import log_change
from ..utils.redis_utils import track_visit_counts
from ..utils.route_utils import handle_errors, require_args, require_json
from ..utils.storage_utils import upload_request_file

general_api: Blueprint = Blueprint("general_api", __name__, url_prefix="/api/general")


@general_api.route("/")
@handle_errors
def home() -> Tuple[Response, int]:
    """Health check endpoint"""
    logger.debug("home: health check OK")
    return jsonify({"message": "App is working!"}), 200


@general_api.route("/save_user", methods=["POST"])
@handle_errors
@require_json("id")
def save_user() -> Tuple[Response, int]:
    """
    POST /api/general/save_user
    JSON body must include "id"; optional fields:
      first_name, last_name, photo_url
    """
    data: Dict[str, Any] = request.get_json()
    logger.debug("save_user: payload=%s", data)
    raw_id = data["id"]
    user_id = int(raw_id)
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    photo_url = data.get("photo_url")
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    try:
        with session_scope() as session:
            tg_user = session.get(Users, user_id)
            if not tg_user:
                tg_user = Users(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                )
                session.add(tg_user)

                session.add(ChangeLog(
                    author_id=user_id,
                    action_type="Регистрация",
                    description=f"Успешная Регистрация TG: {first_name} {last_name}",
                    timestamp=now,
                ))

                if photo_url:
                    filename = secure_filename(photo_url.split("/")[-1])
                    resp = requests.get(photo_url, timeout=10)
                    if resp.ok:
                        content = resp.content
                        new_key = f"users/{user_id}_{filename}"
                        try:
                            minio_client.put_object(BUCKET, new_key, io.BytesIO(content), len(content))
                            tg_user.avatar_url = filename
                        except Exception as exc:
                            logger.warning("save_user: failed upload new avatar %s: %s", new_key, exc)

            # Redis: track visit counts
            track_visit_counts(raw_id)

            role = tg_user.role
            tokens = make_tokens(str(user_id), role)
            logger.debug("save_user: user_id=%d tokens issued", user_id)
            return jsonify({
                "status": "ok",
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"]
            }), 201

    except Exception:
        logger.exception("save_user: Postgres error")
        return jsonify({"error": "internal server error"}), 500


@general_api.route("/get_user_profile", methods=["GET"])
@jwt_required()
@handle_errors
@require_args("user_id")
def get_user_profile() -> Tuple[Response, int]:
    """
    GET /api/general/get_user_profile?user_id=<int>
    """
    uid_str = request.args["user_id"]
    logger.debug("get_user_profile: request for user_id=%s", uid_str)
    try:
        uid = int(uid_str)
    except ValueError:
        logger.warning("get_user_profile: invalid user_id param %s", uid_str)
        return jsonify({"error": "invalid user_id"}), 400

    current = int(get_jwt_identity())
    if current != uid:
        logger.warning("get_user_profile: access denied for user_id=%d (token %d)", uid, current)
        return jsonify({"error": "Access denied"}), 403

    with session_scope() as session:
        u = session.get(Users, uid)
        if not u:
            logger.warning("get_user_profile: user %d not found", uid)
            return jsonify({"error": "not found"}), 404

        profile: Dict[str, Any] = {
            "user_id": u.user_id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "middle_name": u.middle_name,
            "role": u.role,
            "phone": u.phone,
            "email": u.email,
            "date_of_birth": u.date_of_birth.isoformat() if u.date_of_birth else None,
            "gender": u.gender,
            "photo_url": f"{BACKEND_URL}/{BUCKET}/users/{u.user_id}_{u.avatar_url}" if u.avatar_url else None,
            "created_at": u.created_at.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        }

    logger.debug("get_user_profile: returning profile for user_id=%d", uid)
    return jsonify(profile), 200


@general_api.route("/update_profile", methods=["PUT"])
@jwt_required()
@handle_errors
def update_profile() -> Tuple[Response, int]:
    """
    PUT /api/general/update_profile
    Form-data: все поля профиля
    Логирует каждое изменение через log_change.
    """
    user_id = int(get_jwt_identity())
    logger.debug("update_profile: start for user_id=%d", user_id)
    data = request.form.to_dict()
    changed_fields = []

    with session_scope() as session:
        u = session.get(Users, user_id)
        if not u:
            logger.warning("update_profile: user %d not found", user_id)
            return jsonify({"error": "not found"}), 404

        dob_str = data.get("date_of_birth")
        if dob_str:
            try:
                dob = datetime.fromisoformat(dob_str).date()
            except ValueError:
                logger.warning("update_profile: invalid date_of_birth format")
                return jsonify({"error": "Неверный формат date_of_birth"}), 400

            if u.date_of_birth != dob:
                old = u.date_of_birth
                u.date_of_birth = dob
                changed_fields.append(f"date_of_birth: '{old}' → '{dob}'")
                logger.debug("update_profile: date_of_birth changed from %r to %r", old, dob)

        # Обновляем остальные текстовые поля
        for fld in ("first_name", "last_name", "middle_name", "phone", "email", "gender"):
            if fld in data and data[fld] != "" and getattr(u, fld) != data[fld]:
                old = getattr(u, fld)
                new = data[fld]
                setattr(u, fld, new)
                changed_fields.append(f"{fld}: '{old}' → '{new}'")
                logger.debug("update_profile: field %s changed from %r to %r", fld, old, new)

    # После выхода из session_scope() — логируем через log_change
    if changed_fields:
        log_text = "Обновлены поля: " + "; ".join(changed_fields)
        log_change("Обновление профиля", log_text)
        logger.debug("update_profile: %s", log_text)
    else:
        logger.debug("update_profile: no changes detected for user_id=%d", user_id)

    return jsonify({"status": "ok"}), 200


@general_api.route("/upload_avatar", methods=["POST"])
@jwt_required()
@handle_errors
def upload_avatar() -> Tuple[Response, int]:
    user_id = int(get_jwt_identity())
    logger.debug("upload_avatar: start for user_id=%d", user_id)

    file = request.files.get("photo")
    if not file:
        logger.warning("upload_avatar: no file provided for user_id=%d", user_id)
        return jsonify({"error": "photo file is required"}), 400

    with session_scope() as session:
        u = session.get(Users, user_id)
        if not u:
            logger.warning("upload_avatar: user %d not found", user_id)
            return jsonify({"error": "not found"}), 404

        # удаляем старый
        if u.avatar_url:
            old_key = f"users/{user_id}_{u.avatar_url}"
            try:
                minio_client.remove_object(BUCKET, old_key)
                logger.debug("upload_avatar: removed old avatar %s", old_key)
            except Exception as exc:
                logger.warning("upload_avatar: failed removing old avatar %s: %s", old_key, exc)

        # загружаем новый
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name.lower()}{ext.lower()}"
        new_key = f"users/{user_id}_{filename}"
        url = f"{BACKEND_URL}/{BUCKET}/{new_key}"
        content = file.read()
        try:
            minio_client.put_object(BUCKET, new_key, io.BytesIO(content), len(content), content_type=file.mimetype)
            old_avatar_url = u.avatar_url
            u.avatar_url = filename
            session.flush()
            logger.debug("upload_avatar: uploaded new avatar %s", new_key)
        except Exception as exc:
            logger.error("upload_avatar: failed upload new avatar %s: %s", new_key, exc)
            return jsonify({"error": "avatar upload failed"}), 500

    # логируем
    log_change("Обновление аватара", f"{old_avatar_url} → {filename}")
    return jsonify({"photo_url": url}), 200


@general_api.route("/delete_avatar", methods=["DELETE"])
@jwt_required()
@handle_errors
def delete_avatar() -> Tuple[Response, int]:
    user_id = int(get_jwt_identity())
    logger.debug("delete_avatar: start for user_id=%d", user_id)

    with session_scope() as session:
        u = session.get(Users, user_id)
        if not u:
            logger.warning("delete_avatar: user %d not found", user_id)
            return jsonify({"error": "not found"}), 404

        if not u.avatar_url:
            logger.debug("delete_avatar: no avatar to delete for user_id=%d", user_id)
            return jsonify({"status": "ok", "photo_url": None}), 200

        old_key = f"users/{user_id}_{u.avatar_url}"
        try:
            minio_client.remove_object(BUCKET, old_key)
            logger.debug("delete_avatar: removed avatar %s", old_key)
        except Exception as exc:
            logger.warning("delete_avatar: failed remove %s: %s", old_key, exc)

        old_avatar_url = u.avatar_url
        u.avatar_url = None
        session.flush()

        log_change("Удаление аватара", f"{old_avatar_url} → None")
        return jsonify({"status": "ok", "photo_url": None}), 200


@general_api.route("/get_parameters", methods=["GET"])
@handle_errors
def get_parameters() -> Tuple[Response, int]:
    """
    GET /api/general/get_parameters
    Returns social URLs and FAQ parameters.
    """
    logger.debug("get_parameters: fetching from redis")
    try:
        raw = redis_client.get("parameters") or "{}"
        result = json.loads(raw)
        logger.debug("get_parameters: returning %d params", len(result))
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
    logger.debug("list_reviews: start")
    data: List[Dict[str, Any]] = []
    with session_scope() as session:
        revs = session.query(Review).order_by(Review.created_at.desc()).all()
        for r in revs:
            objs = minio_client.list_objects(BUCKET, prefix=f"reviews/{r.id}_", recursive=True)
            urls = [f"{BACKEND_URL}/{BUCKET}/{obj.object_name}" for obj in objs]
            data.append({
                "id": r.id,
                "client_name": r.client_name,
                "client_text1": r.client_text1,
                "shop_response": r.shop_response,
                "client_text2": r.client_text2,
                "link_url": r.link_url,
                "photo_urls": urls,
                "created_at": r.created_at.astimezone(ZoneInfo("Europe/Moscow")).isoformat(),
            })

    logger.debug("list_reviews: returned %d reviews", len(data))
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
    logger.debug("create_request: ip=%s", ip)
    if redis_client.get(key):
        logger.debug("create_request: rate limited for ip=%s", ip)
        return jsonify({"error": "Подождите 10 секунд перед новым запросом"}), 429
    # ставим TTL 10 сек
    redis_client.set(key, "1", ex=10)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    sku = request.form.get("sku", "").strip()

    if not name or not email:
        logger.warning("create_request: missing name/email from ip=%s", ip)
        return jsonify({"error": "Поля «Имя» и «Почта» обязательны"}), 400

    file = request.files.get("file")
    if file and request.content_length and request.content_length > 10 * 1024 * 1024:
        logger.warning("create_request: file too large from ip=%s", ip)
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

    logger.debug("create_request: id=%d name=%s", req_id, name)
    return jsonify({"status": "ok"}), 201


@general_api.route("/create_order", methods=["POST"])
@jwt_required()
@handle_errors
@require_json("items")
def create_order() -> Tuple[Response, int]:
    """
    POST /api/general/create_order
    JSON body:
      - items: список объектов { variant_sku, price, qty, delivery_option }
      - address_id
      - payment_method
      - delivery_type
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    items = data.get("items", [])
    logger.debug("create_order: user_id=%s", user_id)

    est_str = data.get("delivery_date")  # строка "YYYY-MM-DD"
    est_date = None
    if est_str:
        try:
            est_date = datetime.fromisoformat(est_str.replace("Z", "+00:00"))
        except ValueError:
            logger.warning("create_order: invalid delivery_date %s", est_str)
            return jsonify({"error": "Invalid delivery_date"}), 400

    if not isinstance(items, list) or not items:
        logger.warning("create_order: invalid or empty items for user_id=%d", user_id)
        return jsonify({"error": "items must be a non-empty list"}), 400

    # Определяем адрес доставки
    address_id = data.get("address_id")
    with session_scope() as session:
        if not address_id:
            primary = session.query(Addresses).filter_by(user_id=user_id, select=True).first()
            if not primary:
                logger.warning("create_order: no primary address for user_id=%d", user_id)
                return jsonify({"error": "No primary address set"}), 400
            address_id = primary.id

        # Подсчёт суммы товаров
        subtotal = 0
        for it in items:
            price = it.get("price") or 0
            qty = it.get("qty") or 0
            subtotal += int(price) * int(qty)

        # Параметры оплаты и доставки
        first_name = data.get("first_name", "Неизвестное имя")
        last_name = data.get("last_name", "Неизвестная фамилия")
        middle_name = data.get("middle_name", "Неизвестное отчество")
        phone = data.get("phone", "Неизвестный телефон")
        email = data.get("email", "Неизвестный адрес эл.почты")
        payment_method = data.get("payment_method", "Нет данных")
        delivery_type = data.get("delivery_type", "Нет данных")
        delivery_price = data.get("delivery_price", 0)
        total = subtotal + delivery_price

        if delivery_type.startswith("Курьер") and not address_id:
            return jsonify({"error": "address_required"}), 400

        # Создаём заказ
        order = Orders(
            user_id=user_id,
            status='Дата заказа',
            items_json=items,
            address_id=address_id,
            delivery_date=est_date,
            payment_method=payment_method,
            delivery_type=delivery_type,
            delivery_price=delivery_price,
            total=total,
        )
        session.add(order)
        session.flush()
        order_id = order.id

        adjust_user_order_stats(session, user_id, count_delta=1, amount_delta=total)

        log_text = (f"Номер заказа: {order_id}. Сумма заказа: {subtotal}. "
                    f"Клиент: #{user_id} {first_name} {last_name} {middle_name}. "
                    f"Контакты: {phone} {email}")
        logger.debug("create_order: created order_id=%d for user_id=%d subtotal=%.2f total=%.2f address_id=%d",
                     order_id, user_id, subtotal, total, address_id)

    # Логируем создание
    log_change("Создание заказа", log_text)

    return jsonify({"order_id": order_id}), 201


@general_api.route("/get_user_orders", methods=["GET"])
@jwt_required()
@handle_errors
def get_user_orders() -> Tuple[Response, int]:
    """
    GET /api/general/get_user_orders
    Возвращает список заказов текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    logger.debug("get_user_orders: user_id=%d", user_id)

    with session_scope() as session:
        qs = (
            session
            .query(Orders)
            .filter_by(user_id=user_id)
            .order_by(Orders.created_at.desc())
            .all()
        )
        out: List[Dict[str, Any]] = []
        for o in qs:
            out.append({
                "id":            o.id,
                "status":        o.status,
                "items":         o.items_json,
                "created_at":    o.created_at.strftime("%d.%m"),
                "total":         o.total,
                "finish_date": (
                    (o.completed_at or o.delivery_date).strftime("%d.%m")
                    if (o.completed_at or o.delivery_date) else None
                ),
            })

    logger.debug("get_user_orders: returned %d orders", len(out))
    return jsonify({"orders": out}), 200


@general_api.route("/get_user_order/<int:order_id>", methods=["GET"])
@jwt_required()
@handle_errors
def get_user_order(order_id: int) -> Tuple[Response, int]:
    """
    GET /api/general/get_user_order/<order_id>
    Возвращает полные детали заказа.
    """
    user_id = int(get_jwt_identity())
    logger.debug("get_user_order: user_id=%d order_id=%d", user_id, order_id)

    with session_scope() as session:
        o = session.get(Orders, order_id)
        if not o or o.user_id != user_id:
            logger.warning("get_user_order: order %d not found or access denied", order_id)
            return jsonify({"error": "not found"}), 404

        timeline = [
            {"label": "Дата заказа", "date": o.created_at.strftime("%d.%m"), "done": True},
            {"label": "В обработке", "date": o.processed_at.strftime("%d.%m") if o.processed_at else None, "done": bool(o.processed_at)},
            {"label": "Выкуплен", "date": o.purchased_at.strftime("%d.%m") if o.purchased_at else None, "done": bool(o.purchased_at)},
            {"label": "Собран", "date": o.assembled_at.strftime("%d.%m") if o.assembled_at else None, "done": bool(o.assembled_at)},
            {"label": "В пути", "date": o.shipped_at.strftime("%d.%m") if o.shipped_at else None, "done": bool(o.shipped_at)},
            {"label": "Передан в доставку", "date": o.delivered_at.strftime("%d.%m") if o.delivered_at else None, "done": bool(o.delivered_at)},
            {"label": "Выполнен", "date": o.completed_at.strftime("%d.%m") if o.completed_at else None, "done": bool(o.completed_at)},
        ]

        items = o.items_json
        addr = session.get(Addresses, o.address_id) if o.address_id else None
        delivery_address = None
        if addr:
            delivery_address = f"г.{addr.city}, ул. {addr.street}, дом {addr.house}"

        result = {
            "id":               o.id,
            "status":           o.status,
            "timeline":         timeline,
            "payment_method":   o.payment_method,
            "delivery_type":    o.delivery_type,
            "delivery_address": delivery_address,
            "subtotal":         sum(i["price"] * i["qty"] for i in items),
            "delivery_price":   o.delivery_price,
            "total":            o.total,
            "items":            items,
            "canRepeat":        True,
        }

    logger.debug("get_user_order: returning details for order %d", order_id)
    return jsonify({"order": result}), 200


@general_api.route("/list_addresses", methods=["GET"])
@jwt_required()
@handle_errors
def list_addresses() -> Tuple[Response, int]:
    """
    GET /api/general/list_addresses
    Возвращает список адресов текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    logger.debug("list_addresses: user_id=%d", user_id)

    with session_scope() as session:
        qs = session.query(Addresses).filter_by(user_id=user_id).all()
        out: List[Dict[str, Any]] = []
        for a in qs:
            out.append({
                "id":        a.id,
                "label":     a.label,
                "city":      a.city,
                "street":    a.street,
                "house":     a.house,
                "apartment": a.apartment,
                "intercom":  a.intercom,
                "entrance":  a.entrance,
                "floor":     a.floor,
                "comment":   a.comment,
                "selected":  a.select,
            })

    logger.debug("list_addresses: returned %d addresses", len(out))
    return jsonify({"addresses": out}), 200


@general_api.route("/add_address", methods=["POST"])
@jwt_required()
@handle_errors
@require_json("city", "street", "house")
def add_address() -> Tuple[Response, int]:
    """
    POST /api/general/add_address
    Добавляет новый адрес для текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    logger.debug("add_address: user_id=%d payload=%s", user_id, data)

    with session_scope() as session:
        a = Addresses(
            user_id=user_id,
            label=data.get("label").strip(),
            city=data.get("city").strip(),
            street=data.get("street").strip(),
            house=data.get("house").strip(),
            apartment=data.get("apartment").strip(),
            intercom=data.get("intercom").strip(),
            entrance=data.get("entrance").strip(),
            floor=data.get("floor").strip(),
            comment=data.get("comment").strip(),
        )
        session.add(a)
        session.flush()
        address_id = a.id

    logger.debug("add_address: created address_id=%d for user_id=%d", address_id, user_id)
    return jsonify({"id": address_id}), 201


@general_api.route("/update_address/<int:address_id>", methods=["PUT"])
@jwt_required()
@handle_errors
def update_address(address_id: int) -> Tuple[Response, int]:
    """
    PUT /api/general/update_address/<address_id>
    Обновляет существующий адрес текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    logger.debug("update_address: user_id=%d address_id=%d payload=%s", user_id, address_id, data)

    with session_scope() as session:
        a = session.get(Addresses, address_id)
        if not a or a.user_id != user_id:
            logger.warning("update_address: address %d not found or access denied", address_id)
            return jsonify({"error": "not found"}), 404

        for field in ("label", "city", "street", "house", "apartment", "intercom", "entrance", "floor", "comment"):
            if field in data:
                setattr(a, field, data[field])

    logger.debug("update_address: updated address_id=%d for user_id=%d", address_id, user_id)
    return jsonify({"status": "ok"}), 200


@general_api.route("/delete_address/<int:address_id>", methods=["DELETE"])
@jwt_required()
@handle_errors
def delete_address(address_id: int) -> Tuple[Response, int]:
    """
    DELETE /api/general/delete_address/<address_id>
    Удаляет адрес текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    logger.debug("delete_address: user_id=%d address_id=%d", user_id, address_id)

    with session_scope() as session:
        a = session.get(Addresses, address_id)
        if not a or a.user_id != user_id:
            logger.warning("delete_address: address %d not found or access denied", address_id)
            return jsonify({"error": "not found"}), 404
        session.delete(a)

    logger.debug("delete_address: removed address_id=%d for user_id=%d", address_id, user_id)
    return jsonify({"status": "ok"}), 200


@general_api.route("/select_address/<int:address_id>", methods=["POST"])
@jwt_required()
@handle_errors
def select_address_api(address_id: int) -> Tuple[Response, int]:
    """
    POST /api/general/select_address/<address_id>
    Отмечает один адрес как основной и снимает флаг с остальных.
    """
    user_id = int(get_jwt_identity())
    logger.debug("select_address: user_id=%d address_id=%d", user_id, address_id)

    with session_scope() as session:
        # 1) Проверяем доступ
        a = session.get(Addresses, address_id)
        if not a or a.user_id != user_id:
            logger.warning("select_address: address %d not found or access denied", address_id)
            return jsonify({"error": "not found"}), 404

        # 2) Снимаем флаг у всех адресов пользователя и устанавливаем на выбранном
        session.query(Addresses).filter_by(user_id=user_id, select=True).update({"select": False}, synchronize_session=False)
        a.select = True

    logger.debug("select_address: address %d marked as primary for user_id=%d", address_id, user_id)
    return jsonify({"status": "ok"}), 200
