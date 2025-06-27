import csv
import io
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple, List, Dict, Any
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, Response
from ..cors.config import ADMIN_IDS, BACKEND_URL
from ..db_utils import session_scope
from ..extensions import redis_client, minio_client, BUCKET
from ..cors.logging import logger
from ..models import (
    ChangeLog,
    AdminSetting,
    Users,
    Review,
)
from ..utils import (
    cleanup_old_images,
    upload_new_images,
    model_by_category,
    get_sheet_url,
    process_rows,
)

admin_api: Blueprint = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@admin_api.route("/get_admin_ids")
def get_admin_ids() -> Tuple[Response, int]:
    logger.debug("Health check: /api/admin_ids called")
    return jsonify({"admin_ids": ADMIN_IDS}), 200


@admin_api.route("/get_daily_visits")
def get_daily_visits() -> Tuple[Response, int]:
    date_str = request.args.get("date") or datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d")
    pipe = redis_client.pipeline()
    for h in range(24):
        hour = f"{h:02d}"
        pipe.get(f"visits:{date_str}:{hour}:total")
        pipe.scard(f"visits:{date_str}:{hour}:unique")

    resp = pipe.execute()  # список ответов длиной 48
    hours = []
    for h in range(24):
        total  = int(resp[2*h] or 0)
        unique = int(resp[2*h + 1] or 0)
        hours.append({"hour": f"{h:02d}", "total": total, "unique": unique})

    return jsonify({"date": date_str, "hours": hours}), 200


@admin_api.route("/get_logs")
def get_logs() -> Tuple[Response, int]:
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        limit = 10

    with session_scope() as session:
        logs_qs = (session.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).limit(limit).all())

        result = [{
            "id":          lg.id,
            "author_id":   lg.author_id,
            "author_name": lg.author_name,
            "action_type": lg.action_type,
            "description": lg.description,
            "timestamp":   lg.timestamp.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
        } for lg in logs_qs]

    return jsonify({"logs": result}), 200


@admin_api.route("/get_sheet_urls")
def get_sheet_urls() -> Tuple[Response, int]:
    urls = {cat: get_sheet_url(cat) for cat in ("shoes", "clothing", "accessories")}
    return jsonify(urls), 200


@admin_api.route("/update_sheet_url", methods=["POST"])
def update_sheet_url() -> Tuple[Response, int]:
    data = request.get_json(force=True, silent=True) or {}
    category = data.get("category", "").lower()
    url = data.get("url", "").strip()
    if category not in ("shoes", "clothing", "accessories"):
        return jsonify({"error": "unknown category"}), 400
    if not url:
        return jsonify({"error": "url required"}), 400

    try:
        key = f"sheet_url_{category}"
        with session_scope() as session:
            setting = session.get(AdminSetting, key)
            if setting:
                setting.value = url
            else:
                session.add(AdminSetting(key=key, value=url))
                setting = session.get(AdminSetting, key)
            setting.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
        logger.info("Updated sheet URL for %s", category)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.exception("Error setting sheet url: %s", e)
        return jsonify({"error": "internal error"}), 500


@admin_api.route("/import_sheet", methods=["POST"])
def import_sheet() -> Tuple[Response, int]:
    data = request.get_json(force=True, silent=True) or {}
    category = data.get("category", "").lower()
    author_id = data.get("author_id")
    author_name = data.get("author_name", "").strip() or "unknown"

    if category not in ("shoes", "clothing", "accessories"):
        return jsonify({"error": "unknown category"}), 400

    try:
        author_id = int(author_id)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid author_id"}), 400

    url = get_sheet_url(category)
    if not url:
        return jsonify({"error": "sheet url not set"}), 400

    logger.debug("import_sheet called category=%s author_id=%d url=%s", category, author_id, url)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        csv_text = r.content.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(csv_text)))
    except Exception as e:
        logger.exception("Error fetching CSV for %s from %s", category, url)
        return jsonify({"error": str(e)}), 500

    try:
        with session_scope() as session:
            added, updated, deleted, warns = process_rows(category, rows)
            desc = f"Добавлено: {added}. Изменено: {updated}. Удалено: {deleted}. Ошибки: {warns}"
            session.add(ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type=f"Успешная загрузка {category}.csv",
                description=desc,
                timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
            ))

        logger.info("Imported sheet %s: added=%d updated=%d deleted=%d warns=%d", category, added, updated, deleted, warns)
        return jsonify({
            "status":  "ok",
            "added":   added,
            "updated": updated,
            "deleted": deleted,
            "warns":   warns
        }), 201

    except Exception as e:
        logger.exception("Error in import_sheet: %s", e)
        return jsonify({"error": "import_sheet failed", "message": str(e)}), 500


@admin_api.route("/upload_images", methods=["POST"])
def upload_images() -> Tuple[Response, int]:
    # 1) Проверяем входные данные
    z             = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name   = request.form.get("author_name", "").strip()

    if not z or not author_id_str or not author_name:
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        return jsonify({"error": "invalid author_id"}), 400

    if not z.filename.lower().endswith(".zip"):
        return jsonify({"error": "not a ZIP"}), 400

    logger.debug("upload_images START filename=%s author_id=%d author_name=%s", z.filename, author_id, author_name)
    # 2) Определяем папку и expected-набор имён
    folder   = os.path.splitext(z.filename)[0].lower()
    expected = set()
    if folder in ("shoes", "clothing", "accessories"):
        Model = model_by_category(folder)
        with session_scope() as session:
            models = session.query(Model).all()
            for obj in models:
                cs  = obj.color_sku
                cnt = getattr(obj, "count_images", 0) or 0
                for i in range(1, cnt + 1):
                    expected.add(f"{cs}_{i}")

    # 3) Удаляем «лишние» файлы
    deleted, cleanup_warns = cleanup_old_images(folder, expected)
    logger.debug("upload_images cleanup done deleted=%d warns=%d", deleted, cleanup_warns)

    # 4) Загружаем новые/заменяем существующие из ZIP
    archive_bytes = z.stream.read()
    added, replaced = upload_new_images(folder, archive_bytes)
    logger.debug("upload_images upload done added=%d replaced=%d", added, replaced)

    # 5) Логируем результат (в Postgres через session_scope)
    desc = f"Добавлено: {added}. Изменено: {replaced}. Удалено: {deleted}. Ошибки при cleanup: {cleanup_warns}"
    try:
        with session_scope() as session:
            session.add(ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type=f"Успешная загрузка {z.filename}",
                description=desc,
                timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
            ))
        logger.info("upload_images FIN filename=%s added=%d replaced=%d deleted=%d warns=%d",
                    z.filename, added, replaced, deleted, cleanup_warns)
        # 6) Ответ клиенту
        return jsonify({
            "status":   "ok",
            "added":    added,
            "replaced": replaced,
            "deleted":  deleted,
            "warns":    cleanup_warns
        }), 201

    except Exception as e:
        logger.exception("Error saving upload_images log: %s", e)
        return jsonify({"error": "upload error"}), 500


@admin_api.route('/get_settings', methods=['GET'])
def get_settings() -> Tuple[Response, int]:
    logger.info("GET /api/admin/settings called")
    try:
        with session_scope() as session:
            settings = session.query(AdminSetting).order_by(AdminSetting.key).all()
            data: List[Dict[str, Any]] = [{"key": s.key, "value": s.value} for s in settings]
        return jsonify({"settings": data}), 200
    except Exception as e:
        logger.exception("Failed to fetch settings: %s", e)
        return jsonify({"error": "internal error"}), 500


@admin_api.route('/update_setting', methods=['POST'])
def update_setting() -> Tuple[Response, int]:
    logger.info("POST /api/admin/settings called with %s", request.get_json())
    try:
        data = request.get_json(force=True)
        key = data.get("key")
        value = data.get("value")
        if not key:
            logger.info("update_setting: key missing")
            return jsonify({"error": "key required"}), 400

        with session_scope() as session:
            setting = session.get(AdminSetting, key)
            if setting:
                setting.value = value
            else:
                session.add(AdminSetting(key=key, value=value))
            session.flush()
        logger.info("Setting %s updated to %s", key, value)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.exception("Error in update_setting: %s", e)
        return jsonify({"error": "internal error"}), 500


@admin_api.route('/create_review', methods=['POST'])
def create_review() -> Tuple[Response, int]:
    form = request.form
    # проверка client_id
    try:
        client_id = int(form.get('client_id', ''))
    except ValueError:
        return jsonify({'error': 'client_id должен быть числом'}), 400

    try:
        texts = ['client_text1', 'shop_response', 'client_text2', 'link_url']
        for fld in texts:
            if not form.get(fld, '').strip():
                return jsonify({'error': f'Поле {fld} не заполнено'}), 400

        with session_scope() as session:
            if not session.get(Users, client_id):
                return jsonify({'error': 'client_id не найден'}), 404
            review = Review(
                client_id=client_id,
                client_text1=form['client_text1'].strip(),
                shop_response=form['shop_response'].strip(),
                client_text2=form['client_text2'].strip(),
                link_url=form['link_url'].strip()
            )
            session.add(review)
            session.flush()

            # сохраняем фото
            saved = 0
            for i in range(1, 4):
                f = request.files.get(f'photo{i}')
                if f:
                    ext = secure_filename(f.filename).rsplit('.', 1)[-1]
                    key = f'reviews/{review.id}_{i}.{ext}'
                    minio_client.put_object(BUCKET, key, f.stream, length=-1, part_size=10*1024*1024)
                    saved += 1

        logger.info("Review %d created, photos=%d", review.id)
        return jsonify({'status': 'ok', 'message': 'Отзыв успешно добавлен', 'review_id': review.id}), 201

    except Exception as e:
        logger.exception("Error in create_review: %s", e)
        return jsonify({'error': 'internal error'}), 500


@admin_api.route('/delete_review/<int:review_id>', methods=['DELETE'])
def delete_review(review_id: int) -> Tuple[Response, int]:
    logger.info("DELETE /api/admin/delete_review/%d", review_id)
    try:
        with session_scope() as session:
            rev = session.get(Review, review_id)
            if not rev:
                logger.info("delete_review: %d not found", review_id)
                return jsonify({'error': 'not found'}), 404

            # удаляем все файлы reviews/{review_id}_*
            prefix = f'reviews/{review_id}_'
            for obj in minio_client.list_objects(BUCKET, prefix=prefix, recursive=True):
                minio_client.remove_object(BUCKET, obj.object_name)

            session.delete(rev)
        logger.info("Review %d deleted", review_id)
        return jsonify({'status': 'deleted'}), 200

    except Exception as e:
        logger.exception("Error deleting review %d: %s", review_id, e)
        return jsonify({'error': 'internal error'}), 500
