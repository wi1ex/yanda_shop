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
from ..core.config import BACKEND_URL
from ..extensions import redis_client, minio_client, BUCKET
from ..models import ChangeLog, AdminSetting, Users, Review, RequestItem
from ..utils.db_utils import session_scope
from ..utils.google_sheets import get_sheet_url, process_rows, preview_rows
from ..utils.jwt_utils import admin_required
from ..utils.logging_utils import log_change
from ..utils.route_utils import handle_errors, require_json
from ..utils.cache_utils import load_delivery_options, load_parameters
from ..utils.product_serializer import model_by_category
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


@admin_api.route("/import_and_preview_sheet", methods=["POST"])
@admin_required
@handle_errors
@require_json("category")
def import_and_preview_sheet() -> Tuple[Response, int]:
    """
    1) Скачивает CSV
    2) preview_rows → если есть ошибки → 400 + ошибки
    3) process_rows → возвращает статистику загрузки
    """
    category = request.json["category"].lower()
    if category not in ("shoes", "clothing", "accessories"):
        return jsonify({"error": "unknown category"}), 400

    url = get_sheet_url(category)
    if not url:
        return jsonify({"error": "sheet url not set"}), 400

    # скачиваем и парсим CSV
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        text = r.content.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
    except Exception as e:
        logger.exception("import_and_preview_sheet fetch failed for %s", category)
        return jsonify({"error": str(e)}), 500

    # 1) валидация
    errors = preview_rows(category, rows)
    if errors:
        return jsonify({
            "status": "validation_failed",
            "total_rows": len(rows),
            "invalid_count": len(errors),
            "errors": errors
        }), 400

    # 2) загрузка
    added, updated, deleted, warns, warn_skus = process_rows(category, rows)
    desc = (f"Добавлено:{added}. Обновлено:{updated}. Удалено:{deleted}. "
            f"Ошибок:{warns}. SKU-проблемы:{','.join(warn_skus) or 'нет'}")
    log_change(action_type=f"Импорт и проверка {category}.csv", description=desc)

    return jsonify({
        "status": "ok", "added": added, "updated": updated,
        "deleted": deleted, "warns": warns, "warn_skus": warn_skus
    }), 201


@admin_api.route("/upload_and_preview_images", methods=["POST"])
@admin_required
@handle_errors
def upload_and_preview_images() -> Tuple[Response, int]:
    """
    1) preview_product_images для каждого ZIP
    2) если есть errors → 400 + описание
    3) иначе cleanup + upload_product_images → 201 + статистика
    """
    provided = {cat: request.files.get(f"file_{cat}") for cat in ("shoes", "clothing", "accessories")}
    if not any(provided.values()):
        return jsonify({"error": "no archive provided"}), 400

    archive_bytes = {}
    preview_reports = {}
    for cat, zf in provided.items():
        if not zf or not zf.filename.lower().endswith(".zip"):
            continue
        archive_bytes[cat] = zf.stream.read()
        report = preview_product_images(cat, archive_bytes[cat])
        preview_reports[cat] = report
    # собираем все ошибки
    errs = sum(len(r.get("errors", [])) for r in preview_reports.values())
    if errs:
        return jsonify({"status": "validation_failed", "reports": preview_reports}), 400

    # во всех папках: cleanup + upload
    results = {}
    for cat, zf in provided.items():
        if not zf or not zf.filename.lower().endswith(".zip"):
            continue
        # чистка
        folder = os.path.splitext(zf.filename)[0].lower()
        expected = set(preview_reports[cat].get("expected_map", {}).keys())
        deleted, warn = cleanup_product_images(folder, expected)
        # загрузка
        added, replaced = upload_product_images(folder, archive_bytes[cat])
        results[cat] = {"added": added, "replaced": replaced, "deleted": deleted, "warns": warn}
        log_change(action_type=f"Импорт и проверка {cat}.zip", description=str(results[cat]))
    return jsonify({"status": "ok", "results": results}), 201


@admin_api.route("/get_settings", methods=["GET"])
@admin_required
@handle_errors
def get_settings() -> Tuple[Response, int]:
    """GET /api/admin/get_settings"""
    with session_scope() as session:
        settings_objs = session.query(AdminSetting).order_by(AdminSetting.key).all()
        data: List[Dict[str, Any]] = [{"key": s.key, "value": s.value} for s in settings_objs]

    logger.info("get_settings: returned %d entries", len(data))
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

    logger.info("update_setting: %s -> %s", key, value)
    return jsonify({"status": "ok"}), 200


@admin_api.route("/delete_setting/<string:key>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_setting(key: str) -> Tuple[Response, int]:
    """
    DELETE /api/admin/delete_setting/<key>
    Удаляет AdminSetting по ключу и обновляет кеш параметров.
    """

    # защита системных delivery_ параметров
    if key.startswith("delivery_"):
        return jsonify({"error": "protected setting"}), 400

    with session_scope() as session:
        setting = session.get(AdminSetting, key)
        if not setting:
            return jsonify({"error": "not found"}), 404
        old_value = setting.value
        session.delete(setting)

    # обновить кеш публичных параметров
    load_parameters()
    load_delivery_options()

    log_change(action_type="Удаление параметра", description=f"{key}: {old_value}")

    logger.info("delete_setting: %s deleted", key)
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
            return jsonify({"error": "not found"}), 404
        session.delete(rev)

    removed = cleanup_review_images()

    log_change(action_type="Удаление отзыва", description=f"id={review_id}")

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


@admin_api.route("/list_requests", methods=["GET"])
@admin_required
@handle_errors
def list_requests() -> Tuple[Response, int]:
    """
    GET /api/admin/list_requests
    Возвращает все заявки.
    """
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
    return jsonify({"requests": data}), 200


@admin_api.route("/delete_request/<int:request_id>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_request(request_id: int) -> Tuple[Response, int]:
    """
    DELETE /api/admin/delete_request/<request_id>
    Удаляет заявку и её файл.
    """
    with session_scope() as session:
        r = session.get(RequestItem, request_id)
        if not r:
            return jsonify({"error": "not found"}), 404
        session.delete(r)
    cleanup_request_files(request_id)
    return jsonify({"status": "deleted"}), 200


@admin_api.route("/set_user_role", methods=["POST"])
@admin_required
@handle_errors
@require_json("user_id", "role")
def set_user_role() -> Tuple[Response, int]:
    """POST /api/admin/set_user_role {author_id, author_name, user_id, role}"""
    data = request.get_json()
    user_id = data["user_id"]
    new_role = data["role"]

    if new_role not in ("admin", "customer"):
        return jsonify({"error": "invalid input"}), 400

    with session_scope() as session:
        user = session.get(Users, user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404
        user.role = new_role
        desc = f"Пользователю {user.username} {user.first_name} {user.last_name} назначена роль {new_role}"

    log_change(action_type="Назначение роли", description=desc)

    return jsonify({"status": "ok"}), 200
