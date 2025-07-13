import csv
import io
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple, List, Dict, Any
import requests
from flask import Blueprint, jsonify, request, Response
from sqlalchemy import func
from ..core.logging import logger
from ..extensions import redis_client
from ..models import ChangeLog, AdminSetting, Users, Review
from ..utils.db_utils import session_scope
from ..utils.google_sheets import get_sheet_url, process_rows
from ..utils.jwt_utils import admin_required
from ..utils.route_utils import handle_errors, require_json
from ..utils.storage_utils import (
    cleanup_product_images,
    upload_product_images,
    cleanup_review_images,
    upload_review_images,
)
from ..utils.product_serializer import model_by_category

admin_api: Blueprint = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@admin_api.route("/get_daily_visits", methods=["GET"])
@admin_required
@handle_errors
def get_daily_visits() -> Tuple[Response, int]:
    """GET /api/admin/get_daily_visits?date=YYYY-MM-DD"""
    date_str = request.args.get("date", datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d"))
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

    with session_scope() as session:
        total = session.query(func.count(ChangeLog.id)).scalar()
        logs_qs = session.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).offset(offset).limit(limit).all()
        result = [
            {
                "id": lg.id,
                "author_id": lg.author_id,
                "author_name": lg.author_name,
                "action_type": lg.action_type,
                "description": lg.description,
                "timestamp": lg.timestamp
                .astimezone(ZoneInfo("Europe/Moscow"))
                .strftime("%Y-%m-%d %H:%M:%S"),
            }
            for lg in logs_qs
        ]

    return jsonify({"logs": result, "total": total}), 200


@admin_api.route("/get_sheet_urls", methods=["GET"])
@admin_required
@handle_errors
def get_sheet_urls() -> Tuple[Response, int]:
    """GET /api/admin/get_sheet_urls"""
    urls = {cat: get_sheet_url(cat) for cat in ("shoes", "clothing", "accessories")}
    return jsonify(urls), 200


@admin_api.route("/update_sheet_url", methods=["POST"])
@admin_required
@handle_errors
@require_json("category", "url")
def update_sheet_url() -> Tuple[Response, int]:
    """POST /api/admin/update_sheet_url {category, url}"""
    data = request.get_json()
    category = data["category"].lower()
    url = data["url"].strip()

    if category not in ("shoes", "clothing", "accessories"):
        return jsonify({"error": "unknown category"}), 400

    with session_scope() as session:
        key = f"sheet_url_{category}"
        setting = session.get(AdminSetting, key)
        if setting:
            setting.value = url
        else:
            session.add(AdminSetting(key=key, value=url))
            setting = session.get(AdminSetting, key)
        setting.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))

    logger.info("update_sheet_url: updated %s -> %s", category, url)
    return jsonify({"status": "ok"}), 200


@admin_api.route("/import_sheet", methods=["POST"])
@admin_required
@handle_errors
@require_json("author_id", "author_name", "category")
def import_sheet() -> Tuple[Response, int]:
    """POST /api/admin/import_sheet {author_id, author_name, category}"""
    data = request.get_json()
    author_id_raw = data["author_id"]
    author_name = data["author_name"].strip()
    category = data["category"].lower()

    if category not in ("shoes", "clothing", "accessories"):
        return jsonify({"error": "unknown category"}), 400

    url = get_sheet_url(category)
    if not url:
        return jsonify({"error": "sheet url not set"}), 400

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        csv_text = r.content.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(csv_text)))
    except Exception as e:
        logger.exception("import_sheet: fetch CSV failed for %s", category)
        return jsonify({"error": str(e)}), 500

    with session_scope() as session:
        added, updated, deleted, warns, warn_skus = process_rows(category, rows)
        desc = (
            f"Добавлено: {added}. "
            f"Изменено: {updated}. "
            f"Удалено: {deleted}. "
            f"Ошибки: {warns}. "
            f"Проблемные SKU: {','.join(warn_skus) if warn_skus else 'нет'}"
        )
        session.add(
            ChangeLog(
                author_id=int(author_id_raw),
                author_name=author_name,
                action_type=f"Успешная загрузка {category}.csv",
                description=desc,
                timestamp=datetime.now(ZoneInfo("Europe/Moscow")),
            )
        )

    logger.info("import_sheet: %s added=%d updated=%d deleted=%d warns=%d", category, added, updated, deleted, warns)
    return jsonify({"status": "ok",
                    "added": added,
                    "updated": updated,
                    "deleted": deleted,
                    "warns": warns,
                    "warn_skus": warn_skus}), 201


@admin_api.route("/upload_images", methods=["POST"])
@admin_required
@handle_errors
def upload_images() -> Tuple[Response, int]:
    """POST /api/admin/upload_images form-data: author_id, author_name, file(.zip)"""
    form = request.form
    if "author_id" not in form or not form["author_id"].strip():
        return jsonify({"error": "author_id required"}), 400

    try:
        author_id = int(form["author_id"].strip())
    except ValueError:
        return jsonify({"error": "invalid author_id"}), 400

    author_name = form.get("author_name", "").strip()
    if not author_name:
        return jsonify({"error": "author_name required"}), 400

    z = request.files.get("file")
    if not z or not z.filename.lower().endswith(".zip"):
        return jsonify({"error": "file required and must be .zip"}), 400

    folder = os.path.splitext(z.filename)[0].lower()
    expected = set()
    if folder in ("shoes", "clothing", "accessories"):
        Model = model_by_category(folder)
        with session_scope() as session:
            for obj in session.query(Model).all():
                cnt = getattr(obj, "count_images", 0) or 0
                for i in range(1, cnt + 1):
                    expected.add(f"{obj.color_sku}_{i}")

    deleted, cleanup_warns = cleanup_product_images(folder, expected)
    logger.debug("upload_images: cleanup done deleted=%d warns=%d", deleted, cleanup_warns)

    archive_bytes = z.stream.read()
    added, replaced = upload_product_images(folder, archive_bytes)
    logger.debug("upload_images: upload done added=%d replaced=%d", added, replaced)

    desc = f"Добавлено: {added}. Изменено: {replaced}. Удалено: {deleted}. Ошибки при cleanup: {cleanup_warns}"
    with session_scope() as session:
        session.add(
            ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type=f"Успешная загрузка {z.filename}",
                description=desc,
                timestamp=datetime.now(ZoneInfo("Europe/Moscow")),
            )
        )

    logger.info("upload_images: finished filename=%s added=%d replaced=%d deleted=%d warns=%d",
                z.filename, added, replaced, deleted, cleanup_warns)
    return jsonify({"status": "ok", "added": added, "replaced": replaced, "deleted": deleted, "warns": cleanup_warns}), 201


@admin_api.route("/get_settings", methods=["GET"])
@admin_required
@handle_errors
def get_settings() -> Tuple[Response, int]:
    """GET /api/admin/get_settings"""
    with session_scope() as session:
        settings = session.query(AdminSetting).order_by(AdminSetting.key).all()
        data: List[Dict[str, Any]] = [{"key": s.key, "value": s.value} for s in settings]
    return jsonify({"settings": data}), 200


@admin_api.route("/update_setting", methods=["POST"])
@admin_required
@handle_errors
@require_json("key", "value")
def update_setting() -> Tuple[Response, int]:
    """POST /api/admin/update_setting {key, value}"""
    data = request.get_json()
    key = data["key"]
    value = data["value"]

    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        if setting:
            setting.value = value
        else:
            session.add(AdminSetting(key=key, value=value))
        session.flush()

    logger.info("update_setting: %s -> %s", key, value)
    return jsonify({"status": "ok"}), 200


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
    for fld, fld_name in required_fields.items():
        if not form.get(fld, "").strip():
            return jsonify({"error": f'Поле "{fld_name}" не заполнено'}), 400

    photos = [request.files.get(f"photo{i}") for i in range(1, 4)]
    if not any(photos):
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
        logger.info("create_review: saved review_id=%d photos=%d", review.id, saved)
        review_id = review.id

    return jsonify({"status": "ok", "message": "Отзыв успешно добавлен", "review_id": review_id}), 201


@admin_api.route("/delete_review/<int:review_id>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_review(review_id: int) -> Tuple[Response, int]:
    """DELETE /api/admin/delete_review/<review_id>"""
    with session_scope() as session:
        rev = session.get(Review, review_id)
        if not rev:
            return jsonify({"error": "not found"}), 404
        session.delete(rev)

    removed = cleanup_review_images()
    logger.debug("delete_review: cleanup removed=%d", removed)
    logger.info("delete_review: %d deleted", review_id)
    return jsonify({"status": "deleted"}), 200


@admin_api.route("/list_users", methods=["GET"])
@admin_required
@handle_errors
def list_users() -> Tuple[Response, int]:
    """GET /api/admin/list_users"""
    hidden_fields = {"avatar_url", "password_hash", "email_verified", "phone_verified", "updated_at"}
    users_list: List[Dict[str, Any]] = []

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

    return jsonify({"users": users_list}), 200


@admin_api.route("/set_user_role", methods=["POST"])
@admin_required
@handle_errors
@require_json("author_id", "author_name", "user_id", "role")
def set_user_role() -> Tuple[Response, int]:
    """POST /api/admin/set_user_role {author_id, author_name, user_id, role}"""
    data = request.get_json()
    try:
        author_id = int(data["author_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "invalid author_id"}), 400

    author_name = data["author_name"].strip()
    user_id = data["user_id"]
    new_role = data["role"]

    if not author_name or new_role not in ("admin", "customer"):
        return jsonify({"error": "invalid input"}), 400

    with session_scope() as session:
        user = session.get(Users, user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404
        user.role = new_role
        desc = f"Пользователю {user.username} {user.first_name} {user.last_name} назначена роль {new_role}"
        session.add(
            ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type="Назначение роли",
                description=desc,
                timestamp=datetime.now(ZoneInfo("Europe/Moscow")),
            )
        )

    return jsonify({"status": "ok"}), 200
