import csv
import io
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple, List, Dict, Any
import requests
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from ..core.logging import logger
from ..core.config import BACKEND_URL
from ..extensions import redis_client, minio_client, BUCKET
from ..models import ChangeLog, AdminSetting, Users, Review, RequestItem, Addresses, Orders
from ..utils.db_utils import session_scope
from ..utils.google_sheets import get_sheet_url, process_rows, preview_rows
from ..utils.jwt_utils import admin_required
from ..utils.logging_utils import log_change
from ..utils.route_utils import handle_errors, require_json
from ..utils.cache_utils import load_delivery_options, load_parameters
from ..utils.storage_utils import (
    cleanup_product_images,
    upload_product_images,
    cleanup_review_images,
    upload_review_images,
    preview_product_images,
    cleanup_request_files,
)

admin_api: Blueprint = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@admin_api.route("/get_daily_visits", methods=["GET"])
@admin_required
@handle_errors
def get_daily_visits() -> Tuple[Response, int]:
    """GET /api/admin/get_daily_visits?date=YYYY-MM-DD"""
    date_str = request.args.get("date", datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d"))
    logger.debug("get_daily_visits: date=%s", date_str)
    pipe = redis_client.pipeline()
    for h in range(24):
        hour = f"{h:02d}"
        pipe.get(f"visits:{date_str}:{hour}:total")
        pipe.scard(f"visits:{date_str}:{hour}:unique")

    resp = pipe.execute()
    hours = []
    for h in range(24):
        total = int(resp[2 * h] or 0)
        unique = int(resp[2 * h + 1] or 0)
        hours.append({"hour": f"{h:02d}", "total": total, "unique": unique})

    logger.debug("get_daily_visits: returning stats for date=%s", date_str)
    return jsonify({"date": date_str, "hours": hours}), 200


@admin_api.route("/get_logs", methods=["GET"])
@admin_required
@handle_errors
def get_logs() -> Tuple[Response, int]:
    """GET /api/admin/get_logs?limit=&offset="""
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        limit = 10
    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        offset = 0

    limit = min(limit, 100)
    offset = max(offset, 0)

    logger.debug("get_logs: limit=%d offset=%d", limit, offset)
    with session_scope() as session:
        total = session.query(func.count(ChangeLog.id)).scalar()
        logs_qs = session.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).offset(offset).limit(limit).all()
        result = [
            {
                "id": lg.id,
                "author_id": lg.author_id,
                "action_type": lg.action_type,
                "description": lg.description,
                "timestamp": lg.timestamp
                .astimezone(ZoneInfo("Europe/Moscow"))
                .strftime("%Y-%m-%d %H:%M:%S"),
            }
            for lg in logs_qs
        ]

    logger.debug("get_logs: returned %d logs (total=%d)", len(result), total)
    return jsonify({"logs": result, "total": total}), 200


@admin_api.route("/sync_all", methods=["POST"])
@admin_required
@handle_errors
def sync_all() -> Tuple[Any, int]:
    """
    Atomically:
      1) preview_rows for shoes/clothing/accessories
      2) preview_product_images for each provided ZIP
      — if any errors: 400 + { sheet_errors, image_errors }
      — else: process_rows + cleanup/upload images + 201 + { sheet_stats, image_stats }
    """
    categories = ("shoes", "clothing", "accessories")
    logger.debug("sync_all: start sync for categories %s", categories)

    # --- 1) Проверка таблиц ---
    sheet_errors: Dict[str, Dict[str, Any]] = {}
    sheets_data: Dict[str, List[Dict[str, str]]] = {}

    for cat in categories:
        url = get_sheet_url(cat)
        if not url:
            sheet_errors[cat] = {
                "total_rows": 0,
                "invalid_count": 1,
                "errors": [{"variant_sku": cat, "messages": ["sheet_url not set"]}]
            }
            continue

        # Скачиваем CSV
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            text = resp.content.decode("utf-8-sig")
            rows = list(csv.DictReader(io.StringIO(text)))
        except Exception as e:
            logger.exception("sync_all: failed fetching sheet %s", cat)
            sheet_errors[cat] = {
                "total_rows": 0,
                "invalid_count": 1,
                "errors": [{"variant_sku": cat, "messages": [f"failed fetching sheet: {e}"]}]
            }
            continue

        errors = preview_rows(cat, rows)
        if errors:
            sheet_errors[cat] = {
                "total_rows": len(rows),
                "invalid_count": len(errors),
                "errors": errors
            }
        else:
            sheets_data[cat] = rows

    # --- 2) Проверка ZIP-архивов изображений ---
    provided = {cat: request.files.get(f"file_{cat}") for cat in categories}
    logger.debug("sync_all: start sync for files=%s", list(provided.keys()))
    image_errors: Dict[str, Any] = {}
    archives: Dict[str, Dict[str, Any]] = {}

    for cat, zf in provided.items():
        if not zf or not zf.filename.lower().endswith(".zip"):
            continue
        data = zf.stream.read()
        report = preview_product_images(cat, data)
        if report.get("errors"):
            image_errors[cat] = report
        else:
            archives[cat] = {
                "bytes": data,
                "expected_map": report["expected_map"],
                "folder": os.path.splitext(zf.filename)[0].lower()
            }
    logger.debug("sync_all: sheet_errors=%s, image_errors=%s", sheet_errors.keys(), image_errors.keys())

    # Если есть ошибки в таблицах или картинках — логируем и возвращаем 400
    if sheet_errors or image_errors:
        # Общий лог о неудачной попытке синхронизации
        log_change(
            action_type="Синхронизация данных (неуспешно)",
            description=f"Ошибки валидации: таблицы={list(sheet_errors.keys()) or 'нет'}, "
                        f"изображения={list(image_errors.keys()) or 'нет'}"
        )
        logger.warning("sync_all: validation failed, sheets=%s, images=%s", sheet_errors, image_errors)
        return jsonify({
            "status": "validation_failed",
            "sheet_errors": sheet_errors,
            "image_errors": image_errors
        }), 400
    logger.debug("sync_all: processing %d valid sheets, %d archives", len(sheets_data), len(archives))

    # --- 3) Импорт таблиц и загрузка картинок ---
    sheet_stats: Dict[str, Any] = {}
    for cat, rows in sheets_data.items():
        added, updated, deleted = process_rows(cat, rows)
        sheet_stats[cat] = {
            "added": added,
            "updated": updated,
            "deleted": deleted,
        }
        desc = f"{cat}.csv → added={added}, updated={updated}, deleted={deleted}"
        log_change(action_type=f"Импорт {cat}.csv", description=desc)

    image_stats: Dict[str, Any] = {}
    for cat, info in archives.items():
        folder = info["folder"]
        expected = set(info["expected_map"].keys())

        deleted_count, warn_count = cleanup_product_images(folder, expected)
        added_count, replaced_count = upload_product_images(folder, info["bytes"])

        image_stats[cat] = {
            "added": added_count,
            "replaced": replaced_count,
            "deleted": deleted_count,
            "warns": warn_count
        }
        log_change(action_type=f"Импорт {cat}.zip", description=str(image_stats[cat]))

    # Лог успешной синхронизации
    log_change(action_type="Синхронизация данных (успешно)",
               description=f"sheet_stats={sheet_stats}, image_stats={image_stats}")
    logger.debug("sync_all: completed successfully, sheet_stats=%s, image_stats=%s", sheet_stats, image_stats)
    return jsonify({
        "status": "ok",
        "sheet_stats": sheet_stats,
        "image_stats": image_stats
    }), 201


@admin_api.route("/get_settings", methods=["GET"])
@admin_required
@handle_errors
def get_settings() -> Tuple[Response, int]:
    """GET /api/admin/get_settings"""
    with session_scope() as session:
        settings_objs = session.query(AdminSetting).order_by(AdminSetting.key).all()
        data: List[Dict[str, Any]] = [{"key": s.key, "value": s.value} for s in settings_objs]

    logger.debug("get_settings: returned %d entries", len(data))
    return jsonify({"settings": data}), 200


@admin_api.route("/update_setting", methods=["POST"])
@admin_required
@handle_errors
@require_json("key", "value")
def update_setting() -> Tuple[Response, int]:
    """POST /api/admin/update_setting {key, value}"""
    data = request.get_json()
    logger.debug("update_setting: payload=%s", data)
    key = data["key"]
    value = data["value"]
    new_key = False
    old_value = str()

    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        if setting:
            old_value = setting.value
            setting.value = value
        else:
            new_key = True
            session.add(AdminSetting(key=key, value=value))
        session.flush()

    # обновить кеш параметров
    load_parameters()
    load_delivery_options()

    action_type = "Создание параметра" if new_key else "Изменение параметра"
    description = f"{key}: {value}" if new_key else f"{key}: {old_value} -> {value}"
    log_change(action_type=action_type, description=description)

    logger.debug("update_setting: %s -> %s", key, value)
    return jsonify({"status": "ok"}), 200


@admin_api.route("/delete_setting/<string:key>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_setting(key: str) -> Tuple[Response, int]:
    """
    DELETE /api/admin/delete_setting/<key>
    Удаляет AdminSetting по ключу и обновляет кеш параметров.
    """
    logger.debug("delete_setting: called for key=%s", key)
    # защита системных delivery_ параметров
    if key.startswith("delivery_"):
        logger.warning("delete_setting: attempt to delete protected key=%s", key)
        return jsonify({"error": "protected setting"}), 400

    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        if not setting:
            logger.warning("delete_setting: key=%s not found", key)
            return jsonify({"error": "not found"}), 404
        old_value = setting.value
        session.delete(setting)

    # обновить кеш публичных параметров
    load_parameters()
    load_delivery_options()

    log_change(action_type="Удаление параметра", description=f"{key}: {old_value}")

    logger.debug("delete_setting: %s deleted", key)
    return jsonify({"status": "deleted"}), 200


@admin_api.route("/create_review", methods=["POST"])
@admin_required
@handle_errors
def create_review() -> Tuple[Response, int]:
    """POST /api/admin/create_review form-data"""
    form = request.form
    required_fields = {
        "client_name": "Имя клиента",
        "client_text1": "Текст клиента 1",
        "shop_response": "Ответ магазина",
        "link_url": "Ссылка",
    }
    logger.debug("create_review: form data=%s", {k: form[k] for k in required_fields})
    for fld, fld_name in required_fields.items():
        if not form.get(fld, "").strip():
            logger.warning("create_review: missing field %s", fld)
            return jsonify({"error": f'Поле "{fld_name}" не заполнено'}), 400

    photos = [request.files.get(f"photo{i}") for i in range(1, 4)]
    if not any(photos):
        logger.warning("create_review: no photos attached")
        return jsonify({"error": "Необходимо прикрепить хотя бы одну фотографию"}), 400

    with session_scope() as session:
        review = Review(
            client_name=form["client_name"].strip(),
            client_text1=form["client_text1"].strip(),
            shop_response=form["shop_response"].strip(),
            client_text2=form.get("client_text2", "").strip() or None,
            link_url=form["link_url"].strip(),
        )
        session.add(review)
        session.flush()
        saved = upload_review_images(review.id, photos)
        logger.debug("create_review: saved review_id=%d photos=%d", review.id, saved)
        review_id = review.id

    log_change(action_type="Создание отзыва", description=f"id={review_id}")

    return jsonify({"status": "ok", "message": "Отзыв успешно добавлен", "review_id": review_id}), 201


@admin_api.route("/delete_review/<int:review_id>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_review(review_id: int) -> Tuple[Response, int]:
    """DELETE /api/admin/delete_review/<review_id>"""
    with session_scope() as session:
        rev = session.get(Review, review_id)
        if not rev:
            logger.warning("delete_review: review_id=%d not found", review_id)
            return jsonify({"error": "not found"}), 404
        session.delete(rev)

    removed = cleanup_review_images()

    log_change(action_type="Удаление отзыва", description=f"id={review_id}")

    logger.debug("delete_review: cleanup removed=%d", removed)
    logger.debug("delete_review: %d deleted", review_id)
    return jsonify({"status": "deleted"}), 200


@admin_api.route("/list_users", methods=["GET"])
@admin_required
@handle_errors
def list_users() -> Tuple[Response, int]:
    """GET /api/admin/list_users"""
    hidden_fields = {"avatar_url", "email_verified", "updated_at"}
    users_list: List[Dict[str, Any]] = []
    logger.debug("list_users: called")

    with session_scope() as session:
        users = session.query(Users).order_by(Users.user_id).all()
        for u in users:
            row: Dict[str, Any] = {}
            for col in Users.__table__.columns:
                name = col.name
                if name in hidden_fields:
                    continue
                val = getattr(u, name)
                if isinstance(val, datetime):
                    val = val.astimezone(ZoneInfo("Europe/Moscow")).isoformat()
                row[name] = val
            users_list.append(row)

    logger.debug("list_users: returned %d users", len(users_list))
    return jsonify({"users": users_list}), 200


@admin_api.route("/list_requests", methods=["GET"])
@admin_required
@handle_errors
def list_requests() -> Tuple[Response, int]:
    """
    GET /api/admin/list_requests
    Возвращает все заявки.
    """
    logger.debug("list_requests: called")
    data = []
    with session_scope() as session:
        items = session.query(RequestItem).order_by(RequestItem.created_at.desc()).all()
        for r in items:
            file_url = None
            if r.has_file:
                objs = minio_client.list_objects(BUCKET, prefix=f"requests/{r.id}_", recursive=True)
                for obj in objs:
                    file_url = f"{BACKEND_URL}/{BUCKET}/{obj.object_name}"
                    break
            data.append({
                "id":         r.id,
                "name":       r.name,
                "email":      r.email,
                "sku":        r.sku,
                "file_url":   file_url,
                "created_at": r.created_at.isoformat()
            })

    logger.debug("list_requests: returned %d requests", len(data))
    return jsonify({"requests": data}), 200


@admin_api.route("/delete_request/<int:request_id>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_request(request_id: int) -> Tuple[Response, int]:
    """
    DELETE /api/admin/delete_request/<request_id>
    Удаляет заявку и её файл.
    """
    logger.debug("delete_request: request_id=%d", request_id)
    with session_scope() as session:
        r = session.get(RequestItem, request_id)
        if not r:
            logger.warning("delete_request: request_id=%d not found", request_id)
            return jsonify({"error": "not found"}), 404
        session.delete(r)
    cleanup_request_files(request_id)
    logger.debug("delete_request: %d deleted", request_id)
    return jsonify({"status": "deleted"}), 200


@admin_api.route("/set_user_role", methods=["POST"])
@admin_required
@handle_errors
@require_json("user_id", "role")
def set_user_role() -> Tuple[Response, int]:
    """POST /api/admin/set_user_role {author_id, user_id, role}"""
    data = request.get_json()
    logger.debug("set_user_role: payload=%s", data)
    user_id = data["user_id"]
    new_role = data["role"]

    if new_role not in ("admin", "customer"):
        logger.warning("set_user_role: invalid role %s", new_role)
        return jsonify({"error": "invalid input"}), 400

    with session_scope() as session:
        user = session.get(Users, user_id)
        if not user:
            logger.warning("set_user_role: user_id=%s not found", user_id)
            return jsonify({"error": "user not found"}), 404
        user.role = new_role
        desc = f"Пользователю {user.first_name} {user.last_name} назначена роль {new_role}"

    log_change(action_type="Назначение роли", description=desc)
    logger.debug("set_user_role: user_id=%s role set to %s", user_id, new_role)
    return jsonify({"status": "ok"}), 200


@admin_api.route("/list_orders", methods=["GET"])
@admin_required
@handle_errors
def admin_list_orders() -> Tuple[Response, int]:
    """
    GET /api/admin/list_orders
    Возвращает краткие данные по всем заказам с полями пользователя/адреса.
    """
    logger.debug("list_orders: called")
    with session_scope() as session:
        qs = session.query(Orders).order_by(Orders.created_at.desc()).all()
        out = []
        tz = ZoneInfo("Europe/Moscow")
        for o in qs:
            u = session.get(Users, o.user_id)
            a = session.get(Addresses, o.address_id) if o.address_id else None
            address_short = None
            if a:
                address_short = f"г.{a.city}, ул. {a.street}, дом {a.house}"

            created_local = o.created_at.astimezone(tz).isoformat() if o.created_at else None

            out.append({
                "id":             o.id,
                "status":         o.status,
                "created_at":     created_local,
                "total":          o.total,
                "delivery_price": o.delivery_price,
                "user": {
                    "id":         u.user_id if u else None,
                    "first_name": u.first_name if u else None,
                    "last_name":  u.last_name if u else None,
                    "phone":      u.phone if u else None,
                    "email":      u.email if u else None,
                },
                "address": address_short,
            })

    logger.debug("list_orders: returned %d orders", len(out))
    return jsonify({"orders": out}), 200


@admin_api.route("/get_order/<int:order_id>", methods=["GET"])
@admin_required
@handle_errors
def admin_get_order(order_id: int) -> Tuple[Response, int]:
    logger.debug("get_order: order_id=%d", order_id)
    with session_scope() as session:
        o = session.get(Orders, order_id)
        if not o:
            logger.warning("get_order: not found order_id=%d", order_id)
            return jsonify({"error": "not found"}), 404

        a = session.get(Addresses, o.address_id) if o.address_id else None
        delivery_address = None
        if a:
            delivery_address = f"г.{a.city}, ул. {a.street}, дом {a.house}" + (f", кв.{a.apartment}" if a.apartment else "")

        # даты на таймлайне показываем «ДД.ММ» если есть
        def d(dt):
            return dt.strftime("%d.%m") if dt else None

        timeline = [
            {"label": "Дата заказа",        "date": d(o.created_at),   "done": True},
            {"label": "В обработке",        "date": d(o.processed_at), "done": bool(o.processed_at)},
            {"label": "Выкуплен",           "date": d(o.purchased_at), "done": bool(o.purchased_at)},
            {"label": "Собран",             "date": d(o.assembled_at), "done": bool(o.assembled_at)},
            {"label": "В пути",             "date": d(o.shipped_at),   "done": bool(o.shipped_at)},
            {"label": "Передан в доставку", "date": d(o.delivered_at), "done": bool(o.delivered_at)},
            {"label": "Выполнен",           "date": d(o.completed_at), "done": bool(o.completed_at)},
        ]

        subtotal = 0
        for i in (o.items_json or []):
            price = i.get("price", 0) or 0
            qty   = i.get("qty", 0) or 0
            subtotal += int(price) * int(qty)

        data = {
            "id":               o.id,
            "status":           o.status,
            "timeline":         timeline,
            "payment_method":   o.payment_method,
            "delivery_type":    o.delivery_type,
            "delivery_address": delivery_address,
            "subtotal":         subtotal,
            "delivery_price":   o.delivery_price,
            "total":            o.total,
            "items":            o.items_json,
            "user":             {"id": o.user_id},
        }

    logger.debug("get_order: ok order_id=%d status=%s", order_id, data["status"])
    return jsonify({"order": data}), 200


@admin_api.route("/set_next_status/<int:order_id>", methods=["POST"])
@admin_required
@handle_errors
def admin_set_next_status(order_id: int) -> Tuple[Response, int]:
    """
    POST /api/admin/set_next_status/<id>
    Переводит заказ на следующий статус и проставляет соответствующую *_at дату.
    Переход из 'Отменен'/'Выполнен' запрещён.
    """
    STATUS_FLOW = [
        "Дата заказа",         # created_at
        "В обработке",         # processed_at
        "Выкуплен",            # purchased_at
        "Собран",              # assembled_at
        "В пути",              # shipped_at
        "Передан в доставку",  # delivered_at
        "Выполнен",            # completed_at
    ]
    STATUS_TO_COLUMN = {
        "В обработке":         "processed_at",
        "Выкуплен":            "purchased_at",
        "Собран":              "assembled_at",
        "В пути":              "shipped_at",
        "Передан в доставку":  "delivered_at",
        "Выполнен":            "completed_at",
    }

    logger.debug("set_next_status: order_id=%d", order_id)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    with session_scope() as session:
        o = session.get(Orders, order_id)
        if not o:
            logger.warning("set_next_status: not found order_id=%d", order_id)
            return jsonify({"error": "not found"}), 404

        # запрет перехода из финальных статусов
        if o.status in ("Отменен", "Выполнен"):
            logger.debug("set_next_status: blocked from status=%s order_id=%d", o.status, order_id)
            return jsonify({"status": o.status, "message": "blocked from final status"}), 400

        # если статус не из цепочки — считаем его как «Дата заказа»
        try:
            idx = STATUS_FLOW.index(o.status)
        except ValueError:
            logger.warning("set_next_status: unknown status=%s, normalizing to 'Дата заказа' (order_id=%d)", o.status, order_id)
            idx = 0
            o.status = STATUS_FLOW[idx]

        if idx >= len(STATUS_FLOW) - 1:
            logger.debug("set_next_status: already final order_id=%d status=%s", order_id, o.status)
            return jsonify({"status": o.status, "message": "already final"}), 200

        next_status = STATUS_FLOW[idx + 1]
        col = STATUS_TO_COLUMN.get(next_status)
        if col:
            setattr(o, col, now)
        o.status = next_status

        session.flush()  # гарантируем, что БД приняла изменения

        # Снимаем примитивы до любой потенциальной ошибки / выхода из with
        out_order_id = o.id
        out_status   = o.status
        out_set_at   = now.isoformat()

        admin_id = get_jwt_identity()
        admin_user = session.get(Users, admin_id)
        admin_name = f"{admin_user.first_name} {admin_user.last_name}" if admin_user else f"id={admin_id}"

        # Если логирование вдруг бросит исключение — пусть его перехватит handle_errors,
        # но к этому моменту мы уже не трогаем ORM-объект.
        log_change(action_type="Смена статуса заказа",
                   description=f"{admin_name} обновил статус заказа #{out_order_id} → {next_status}")

        logger.debug("set_next_status: ok order_id=%d new_status=%s set_at=%s", out_order_id, next_status, out_set_at)
        return jsonify({"order_id": out_order_id, "status": out_status, "set_at": out_set_at}), 200


@admin_api.route("/cancel_order/<int:order_id>", methods=["POST"])
@admin_required
@handle_errors
def admin_cancel_order(order_id: int) -> Tuple[Response, int]:
    """
    POST /api/admin/cancel_order/<id>
    Ставит статус 'Отменен' и дату canceled_at (идемпотентно).
    """
    logger.debug("cancel_order: order_id=%d", order_id)
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    with session_scope() as session:
        o = session.get(Orders, order_id)
        if not o:
            logger.warning("cancel_order: not found order_id=%d", order_id)
            return jsonify({"error": "not found"}), 404

        if o.status == "Выполнен":
            logger.debug("cancel_order: already completed order_id=%d", order_id)
            return jsonify({"error": "already completed"}), 400

        if o.status == "Отменен":
            logger.debug("cancel_order: already canceled order_id=%d", order_id)
            return jsonify({"status": o.status, "message": "already canceled"}), 200

        o.status = "Отменен"
        o.canceled_at = now
        session.flush()

        out_order_id = o.id
        out_status   = o.status
        out_canceled = now.isoformat()

        admin_id = get_jwt_identity()
        admin_user = session.get(Users, admin_id)
        admin_name = f"{admin_user.first_name} {admin_user.last_name}" if admin_user else f"id={admin_id}"
        log_change(action_type="Отмена заказа", description=f"{admin_name} отменил заказ #{out_order_id}")

        logger.debug("cancel_order: ok order_id=%d canceled_at=%s", out_order_id, out_canceled)
        return jsonify({"order_id": out_order_id, "status": out_status, "canceled_at": out_canceled}), 200


@admin_api.route("/delete_order/<int:order_id>", methods=["DELETE"])
@admin_required
@handle_errors
def admin_delete_order(order_id: int):
    """
    DELETE /api/admin/delete_order/<id>
    Полное удаление заказа из БД (безвозвратно).
    """
    logger.debug("delete_order: order_id=%d", order_id)
    with session_scope() as session:
        o = session.get(Orders, order_id)
        if not o:
            logger.warning("delete_order: not found order_id=%d", order_id)
            return jsonify({"error": "not found"}), 404

        session.delete(o)

        admin_id = get_jwt_identity()
        admin_user = session.get(Users, admin_id)
        admin_name = f"{admin_user.first_name} {admin_user.last_name}" if admin_user else f"id={admin_id}"
        log_change(action_type="Удаление заказа", description=f"{admin_name} удалил заказ #{order_id}")

        logger.debug("delete_order: deleted order_id=%d", order_id)
        return jsonify({"message": f"Order {order_id} deleted"}), 200
