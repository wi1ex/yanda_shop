from flask import Blueprint, Flask, jsonify, request, Response
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import io
import csv
import os
import zipfile
import json
import requests

from minio.error import S3Error
from extensions import redis_client, minio_client, BUCKET
from models import (
    Shoe,
    Clothing,
    Accessory,
    Users,
    ChangeLog,
    AdminSetting,
    db
)
from cors.config import BACKEND_URL, ADMIN_IDS

logger: logging.Logger = logging.getLogger(__name__)
api: Blueprint = Blueprint("api", __name__)


def model_by_category(cat: str) -> Optional[type]:
    return {"shoes": Shoe, "clothing": Clothing, "accessories": Accessory,
            "обувь": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat.lower())


def get_sheet_url(category: str) -> Optional[str]:
    key = f"sheet_url_{category}"
    setting = AdminSetting.query.get(key)
    return setting.value if setting else None


def process_rows(category: str, rows: List[Dict[str, str]]) -> Tuple[int, int, int]:
    Model = model_by_category(category)
    if Model is None:
        raise ValueError(f"Unknown category {category}")

    added = updated = deleted = 0
    # Собираем все variant_sku
    variants = [row["variant_sku"].strip() for row in rows]
    # Подгружаем существующие объекты по variant_sku
    existing = {obj.variant_sku: obj for obj in Model.query.filter(Model.variant_sku.in_(variants)).all()}

    for row in rows:
        variant = row["variant_sku"].strip()
        sku = row["sku"].strip()
        data = {k: row[k].strip() for k in row if k not in ("sku", "variant_sku")}
        # Удаление, если все поля пусты
        if variant and all(not v for v in data.values()):
            obj = existing.get(variant)
            if obj:
                db.session.delete(obj)
                deleted += 1
            continue

        obj = existing.get(variant)
        if not obj:
            # Создаём новую запись
            obj = Model(variant_sku=variant, sku=sku)
            for k, v in data.items():
                if not hasattr(obj, k):
                    continue
                # price, count_in_stock, count_images  → integer
                if k in ("price", "count_in_stock", "count_images"):
                    raw = v.replace(" ", "")
                    try:
                        val = int(raw)
                    except ValueError:
                        val = 0
                # size_label  → string for Clothing, float otherwise
                elif k == "size_label":
                    if Model is Clothing:
                        val = v  # оставляем строку
                    else:
                        raw = v.replace(",", ".").replace(" ", "")
                        try:
                            val = float(raw)
                        except ValueError:
                            val = None
                # width_mm, height_mm, depth_mm → float
                elif k in ("width_mm", "height_mm", "depth_mm"):
                    raw = v.replace(",", ".").replace(" ", "")
                    try:
                        val = float(raw)
                    except ValueError:
                        val = None
                # все прочие поля — строки
                else:
                    val = v
                setattr(obj, k, val)
            db.session.add(obj)
            added += 1

        else:
            # Обновляем существующую запись
            has_changes = False
            # Если sku поменялся — сохранить
            if obj.sku != sku:
                obj.sku = sku
                has_changes = True
            for k, v in data.items():
                if not hasattr(obj, k):
                    continue
                # та же нормализация, что и при создании
                if k in ("price", "count_in_stock", "count_images"):
                    raw = v.replace(" ", "")
                    try:
                        new_val = int(raw)
                    except ValueError:
                        new_val = 0
                elif k == "size_label":
                    if Model is Clothing:
                        new_val = v
                    else:
                        raw = v.replace(",", ".").replace(" ", "")
                        try:
                            new_val = float(raw)
                        except ValueError:
                            new_val = None
                elif k in ("width_mm", "height_mm", "depth_mm"):
                    raw = v.replace(",", ".").replace(" ", "")
                    try:
                        new_val = float(raw)
                    except ValueError:
                        new_val = None
                else:
                    new_val = v
                if getattr(obj, k) != new_val:
                    setattr(obj, k, new_val)
                    has_changes = True
            if has_changes:
                obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                updated += 1

    return added, updated, deleted


@api.route("/api/")
def home() -> Tuple[Response, int]:
    logger.debug("Health check: /api/ called")
    return jsonify({"message": "App is working!"}), 200


@api.route("/api/admin_ids")
def get_admin_ids() -> Tuple[Response, int]:
    logger.debug("Health check: /api/admin_ids called")
    return jsonify({"admin_ids": ADMIN_IDS}), 200


@api.route("/api/save_user", methods=["POST"])
def save_user() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    logger.debug("save_user payload: %s", data)

    if "id" not in data:
        logger.error("save_user: missing 'id'")
        return jsonify({"error": "missing user id"}), 400

    raw_id = data["id"]
    try:
        user_id: int = int(raw_id)
        is_tg: bool = True
    except (TypeError, ValueError):
        # Неконвертируемый id — это не Telegram-пользователь, но не ошибка!
        logger.debug("save_user: non-integer id %r, skipping Postgres", raw_id)
        is_tg = False

    first_name: Optional[str] = data.get("first_name")
    last_name: Optional[str] = data.get("last_name")
    username: Optional[str] = data.get("username")

    # --- Postgres только для целых id ---
    if is_tg:
        try:
            tg_user = Users.query.get(user_id)
            if not tg_user:
                tg_user = Users(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username
                )
                db.session.add(tg_user)
                logger.info("Registered new Telegram user %d", user_id)
            else:
                updated = False
                for field in ("first_name", "last_name", "username"):
                    new_val = data.get(field)
                    if new_val and getattr(tg_user, field) != new_val:
                        setattr(tg_user, field, new_val)
                        updated = True
                if updated:
                    logger.info("Updated Telegram user %d", user_id)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
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

        logger.debug("Redis visit counters updated for user %r", raw_id)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        logger.exception("Redis error in save_user: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/visits")
def get_daily_visits() -> Tuple[Response, int]:
    date_str: str = request.args.get("date") or datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d")
    logger.debug("get_daily_visits for date %s", date_str)

    try:
        hours: List[Dict[str, Any]] = []
        for h in range(24):
            hour = f"{h:02d}"
            total = int(redis_client.get(f"visits:{date_str}:{hour}:total") or 0)
            unique = int(redis_client.scard(f"visits:{date_str}:{hour}:unique") or 0)
            hours.append({"hour": hour, "total": total, "unique": unique})
        return jsonify({"date": date_str, "hours": hours}), 200
    except Exception as e:
        logger.exception("Error fetching visits for %s: %s", date_str, e)
        return jsonify({"error": "cannot fetch data"}), 500


@api.route("/api/products")
def list_products() -> Response:
    cat: str = request.args.get("category", "").lower()
    logger.debug("list_products category=%s", cat)

    Model = model_by_category(cat)
    if not Model:
        logger.error("Unknown category %s", cat)
        return jsonify({"error": "unknown category"}), 400

    ms_tz = ZoneInfo("Europe/Moscow")
    items = Model.query.all()
    result = []
    for obj in items:
        # 1) сериализуем все колонки
        data: Dict[str, Any] = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, datetime):
                data[col.name] = val.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S")
            else:
                data[col.name] = val
        # 2) добавляем картинки
        count = getattr(obj, "count_images", 0) or 0
        images = [f"{BACKEND_URL}/images/{obj.variant_sku}-{i}.webp" for i in range(1, count+1)]
        data["images"] = images
        data["image"]  = images[0] if images else None

        result.append(data)

    return jsonify(result), 200


@api.route("/api/product")
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

    obj = Model.query.filter_by(variant_sku=variant_sku).first()
    if not obj:
        logger.warning("Product not found %s/%s", category, variant_sku)
        return jsonify({"error": "not found"}), 404

    ms_tz = ZoneInfo("Europe/Moscow")
    data: Dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            data[col.name] = val.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            data[col.name] = val

    count = getattr(obj, "count_images", 0) or 0
    images = [f"{BACKEND_URL}/images/{obj.variant_sku}-{i}.webp" for i in range(1, count + 1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    logger.info("Fetched product %s/%s", category, variant_sku)
    return jsonify(data), 200


@api.route("/api/upload_images", methods=["POST"])
def upload_images() -> Tuple[Response, int]:
    z = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name = request.form.get("author_name", "").strip() or "unknown"

    if not z or not author_id_str:
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        return jsonify({"error": "invalid author_id"}), 400

    if not z.filename.lower().endswith(".zip"):
        return jsonify({"error": "not a ZIP"}), 400

    try:
        # clean old
        expected = set()
        for M in (Shoe, Clothing, Accessory):
            for o in M.query:
                cnt = getattr(o, "count_images", 0) or 0
                for i in range(1, cnt + 1):
                    expected.add(f"{o.variant_sku}-{i}")

        deleted = 0
        for obj in minio_client.list_objects(BUCKET, recursive=True):
            if os.path.splitext(obj.object_name)[0] not in expected:
                minio_client.remove_object(BUCKET, obj.object_name)
                deleted += 1

        # upload new
        data = io.BytesIO(z.stream.read())
        added = replaced = 0
        with zipfile.ZipFile(data) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                key = info.filename
                content = archive.read(key)
                try:
                    minio_client.stat_object(BUCKET, key)
                    replaced += 1
                except S3Error:
                    added += 1
                minio_client.put_object(BUCKET, key, io.BytesIO(content), len(content))

        desc = f"Добавлено {added}, Заменено {replaced}, Удалено {deleted}"
        log = ChangeLog(
            author_id=author_id,
            author_name=author_name,
            action_type=f"успешная загрузка {z.filename}",
            description=desc,
            timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"status": "ok", "added": added, "replaced": replaced, "deleted": deleted}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Error in upload_images: %s", e)
        return jsonify({"error": "upload error", "message": str(e)}), 500


@api.route("/api/logs")
def get_logs() -> Tuple[Response, int]:
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        limit = 10

    try:
        logs_qs = ChangeLog.query.order_by(ChangeLog.timestamp.desc()).limit(limit).all()
        ms_tz = ZoneInfo("Europe/Moscow")
        result = [{
            "id": lg.id,
            "author_id": lg.author_id,
            "author_name": lg.author_name,
            "action_type": lg.action_type,
            "description": lg.description,
            "timestamp": lg.timestamp.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S")
        } for lg in logs_qs]
        return jsonify({"logs": result}), 200
    except Exception as e:
        logger.exception("Error fetching logs: %s", e)
        return jsonify({"error": "cannot fetch logs"}), 500


@api.route("/api/user")
def get_user_profile() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    if not uid_str:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        u = Users.query.get(uid)
        if not u:
            return jsonify({"error": "not found"}), 404

        ms_tz = ZoneInfo("Europe/Moscow")
        return jsonify({
            "user_id": u.user_id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "username": u.username,
            "created_at": u.created_at.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S")
        }), 200
    except Exception as e:
        logger.exception("Error fetching user %d: %s", uid, e)
        return jsonify({"error": "internal error"}), 500


@api.route("/api/admin/sheet_urls")
def get_sheet_urls() -> Tuple[Response, int]:
    urls = {cat: get_sheet_url(cat) for cat in ("shoes", "clothing", "accessories")}
    return jsonify(urls), 200


@api.route("/api/admin/sheet_url", methods=["POST"])
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
        setting = AdminSetting.query.get(key)
        if setting:
            setting.value = url
        else:
            setting = AdminSetting(key=key, value=url)
            db.session.add(setting)
        db.session.commit()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Error setting sheet url: %s", e)
        return jsonify({"error": "internal error"}), 500


@api.route("/api/import_sheet", methods=["POST"])
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

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        csv_text = r.content.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        a, u, d = process_rows(category, rows)
        db.session.commit()
        desc = f"Добавлено {a}, Изменено {u}, Удалено {d}"
        log = ChangeLog(
            author_id=author_id,
            author_name=author_name,
            action_type=f"успешная загрузка {category} из Sheets",
            description=desc,
            timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"status": "ok", "added": a, "updated": u, "deleted": d}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Error in import_sheet: %s", e)
        return jsonify({"error": "import_sheet failed", "message": str(e)}), 500


@api.route("/api/cart", methods=["GET"])
def get_cart() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    if not uid_str:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        key = f"cart:{uid}"
        stored = redis_client.get(key)
        if not stored:
            return jsonify({"items": [], "count": 0, "total": 0}), 200
        return jsonify(json.loads(stored)), 200
    except Exception as e:
        logger.exception("Redis error in get_cart: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/cart", methods=["POST"])
def save_cart() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    if "user_id" not in data:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(data["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    count = data.get("count", 0)
    total = data.get("total", 0)

    try:
        key = f"cart:{uid}"
        redis_client.set(key, json.dumps({"items": items, "count": count, "total": total}))
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(key, ttl)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Redis error in save_cart: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/favorites", methods=["GET"])
def get_favorites() -> Tuple[Response, int]:
    uid_str = request.args.get("user_id")
    if not uid_str:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        key = f"favorites:{uid}"
        stored = redis_client.get(key)
        if not stored:
            return jsonify({"items": [], "count": 0}), 200
        return jsonify(json.loads(stored)), 200
    except Exception as e:
        logger.exception("Redis error in get_favorites: %s", e)
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/favorites", methods=["POST"])
def save_favorites() -> Tuple[Response, int]:
    data = request.get_json(force=True, silent=True) or {}
    if "user_id" not in data:
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(data["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    # count храним для фронта
    payload = {"items": items, "count": len(items)}

    try:
        key = f"favorites:{uid}"
        redis_client.set(key, json.dumps(payload))
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(key, ttl)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Redis error in save_favorites: %s", e)
        return jsonify({"error": "internal redis error"}), 500


def register_routes(app: Flask) -> None:
    app.register_blueprint(api)
