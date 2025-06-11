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
from minio.error import S3Error
from extensions import redis_client, minio_client, BUCKET
from models import Shoe, Clothing, Accessory, Users, ChangeLog, db
from cors.config import BACKEND_URL


logger: logging.Logger = logging.getLogger(__name__)
api: Blueprint = Blueprint("api", __name__)


def model_by_category(cat: str) -> Optional[type]:
    return {
        "shoes": Shoe,
        "clothing": Clothing,
        "accessories": Accessory,
        "обувь": Shoe,
        "одежда": Clothing,
        "аксессуары": Accessory,
    }.get(cat.lower())


@api.route("/api/")
def home() -> Tuple[Response, int]:
    logger.debug("Health check: /api/ called")
    return jsonify({"message": "App is working!"}), 200


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
        logger.warning("save_user: non-integer id %r, skipping Postgres", raw_id)
        is_tg = False

    first_name: Optional[str] = data.get("first_name")
    last_name: Optional[str] = data.get("last_name")
    username: Optional[str] = data.get("username")

    # --- Postgres только для целых id ---
    if is_tg:
        try:
            tg_user: Optional[Users] = Users.query.get(user_id)
            if not tg_user:
                tg_user = Users(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
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

    items = Model.query.all()
    result: List[Dict[str, Any]] = []
    ms_tz = ZoneInfo("Europe/Moscow")

    for i in items:
        created = i.created_at.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S") if i.created_at else None
        updated = i.updated_at.astimezone(ms_tz).strftime("%Y-%m-%d %H:%M:%S") if i.updated_at else None
        result.append({
            "sku": i.sku,
            "name": i.name,
            "price": i.price,
            "category": i.category,
            "image": f"{BACKEND_URL}/images/{i.sku}-1.webp",
            "color": i.color,
            "created_at": created,
            "updated_at": updated,
        })

    logger.info("Returned %d products for category %s", len(result), cat)
    return jsonify(result)


@api.route("/api/product")
def get_product() -> Tuple[Response, int]:
    cat = request.args.get("category", "").lower()
    sku = request.args.get("sku", "").strip()
    logger.debug("get_product category=%s sku=%s", cat, sku)

    if not cat or not sku:
        logger.error("Missing category or sku")
        return jsonify({"error": "category and sku required"}), 400

    Model = model_by_category(cat)
    if not Model:
        logger.error("Unknown category %s", cat)
        return jsonify({"error": "unknown category"}), 400

    obj = Model.query.filter_by(sku=sku).first()
    if not obj:
        logger.warning("Product not found %s/%s", cat, sku)
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
    images = [f"{BACKEND_URL}/images/{obj.sku}-{i}.webp" for i in range(1, count + 1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    logger.info("Fetched product %s/%s", cat, sku)
    return jsonify(data), 200


@api.route("/api/import_products", methods=["POST"])
def import_products() -> Tuple[Response, int]:
    logger.debug("import_products called")
    f = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name = request.form.get("author_name", "").strip() or "unknown"

    if not f or not author_id_str:
        logger.error("import_products: missing file or author_id")
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        logger.error("import_products: invalid author_id %r", author_id_str)
        return jsonify({"error": "invalid author_id"}), 400

    name, ext = os.path.splitext(f.filename.lower())
    if ext != ".csv":
        logger.error("Wrong file extension %s", ext)
        return jsonify({"error": "not a CSV"}), 400

    Model = model_by_category(name)
    if Model is None:
        logger.error("import_products: unknown category %r", name)
        return jsonify({"error": "unknown category"}), 400

    reader = csv.DictReader(io.StringIO(f.stream.read().decode("utf-8")))
    rows = list(reader)

    added, updated, deleted = 0, 0, 0
    skus = [row["sku"].strip() for row in rows]
    existing = {obj.sku: obj for obj in Model.query.filter(Model.sku.in_(skus)).all()}

    try:
        for row in rows:
            sku = row["sku"].strip()
            other = {k: row[k].strip() for k in row if k != "sku"}

            # delete if all other fields empty
            if sku and all(not v for v in other.values()):
                obj = existing.get(sku)
                if obj:
                    db.session.delete(obj)
                    deleted += 1
                continue

            obj = existing.get(sku)
            if not obj:
                obj = Model(sku=sku)
                for k, v in other.items():
                    if hasattr(obj, k):
                        setattr(obj, k, int(v) if k in ("price", "count_in_stock", "count_images") else float(v) if k in ("size_label", "width_mm", "height_mm", "depth_mm") else v)
                db.session.add(obj)
                added += 1
            else:
                changed = False
                for k, v in other.items():
                    if hasattr(obj, k):
                        new = int(v) if k in ("price", "count_in_stock", "count_images") else float(v) if k in ("size_label", "width_mm", "height_mm", "depth_mm") else v
                        if getattr(obj, k) != new:
                            setattr(obj, k, new)
                            changed = True
                if changed:
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1

        db.session.commit()
        desc = f"Добавлено {added}, Изменено {updated}, Удалено {deleted}"
        log = ChangeLog(
            author_id=author_id,
            author_name=author_name,
            action_type=f"успешная загрузка {name}.csv",
            description=desc,
            timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
        )
        db.session.add(log)
        db.session.commit()
        logger.info("import_products finished: %s", desc)
        return jsonify({"status": "ok", "added": added, "updated": updated, "deleted": deleted}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Error in import_products: %s", e)
        try:
            err_log = ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type=f"неудачная загрузка {name}.csv",
                description=str(e),
                timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
            )
            db.session.add(err_log)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({"error": "db error", "message": str(e)}), 500


@api.route("/api/upload_images", methods=["POST"])
def upload_images() -> Tuple[Response, int]:
    logger.debug("upload_images called")
    z = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name = request.form.get("author_name", "").strip() or "unknown"

    if not z or not author_id_str:
        logger.error("upload_images: missing file or author_id")
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        logger.error("upload_images: invalid author_id %r", author_id_str)
        return jsonify({"error": "invalid author_id"}), 400

    if not z.filename.lower().endswith(".zip"):
        logger.error("Wrong archive extension: %s", z.filename)
        return jsonify({"error": "not a ZIP"}), 400

    try:
        # clean old
        expected = set()
        for M in (Shoe, Clothing, Accessory):
            for o in M.query:
                cnt = getattr(o, "count_images", 0) or 0
                for i in range(1, cnt+1):
                    expected.add(f"{o.sku}-{i}")

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
        logger.info("upload_images finished: %s", desc)
        return jsonify({"status": "ok", "added": added, "replaced": replaced, "deleted": deleted}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Error in upload_images: %s", e)
        try:
            err_log = ChangeLog(
                author_id=author_id,
                author_name=author_name,
                action_type=f"неудачная загрузка {z.filename}",
                description=str(e),
                timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
            )
            db.session.add(err_log)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({"error": "upload error", "message": str(e)}), 500


@api.route("/api/logs")
def get_logs() -> Tuple[Response, int]:
    logger.debug("get_logs called")
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
        logger.info("Returned %d change logs", len(result))
        return jsonify({"logs": result}), 200
    except Exception as e:
        logger.exception("Error fetching logs: %s", e)
        return jsonify({"error": "cannot fetch logs"}), 500


@api.route("/api/user")
def get_user_profile() -> Tuple[Response, int]:
    logger.debug("get_user_profile called with args: %s", request.args)
    uid_str = request.args.get("user_id")
    if not uid_str:
        logger.error("get_user_profile: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        logger.error("get_user_profile: invalid user_id %r", uid_str)
        return jsonify({"error": "invalid user_id"}), 400

    try:
        u = Users.query.get(uid)
        if not u:
            logger.warning("User %d not found", uid)
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


@api.route("/api/cart", methods=["GET"])
def get_cart() -> Tuple[Response, int]:
    logger.debug("get_cart called with args: %s", request.args)
    uid_str = request.args.get("user_id")
    if not uid_str:
        logger.error("get_cart: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(uid_str)
    except ValueError:
        logger.error("get_cart: invalid user_id %r", uid_str)
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
    logger.debug("save_cart payload: %s", data)

    if "user_id" not in data:
        logger.error("save_cart: missing user_id")
        return jsonify({"error": "user_id required"}), 400

    try:
        uid = int(data["user_id"])
    except (TypeError, ValueError):
        logger.error("save_cart: invalid user_id %r", data.get("user_id"))
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    count = data.get("count", 0)
    total = data.get("total", 0)

    try:
        key = f"cart:{uid}"
        redis_client.set(key, json.dumps({"items": items, "count": count, "total": total}))
        ttl = 60 * 60 * 24 * 365
        redis_client.expire(key, ttl)
        logger.debug("Cart saved for user %d", uid)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Redis error in save_cart: %s", e)
        return jsonify({"error": "internal redis error"}), 500


def register_routes(app: Flask) -> None:
    """
    Регистрируем blueprint с API.
    """
    logger.debug("Registering API routes")
    app.register_blueprint(api)
