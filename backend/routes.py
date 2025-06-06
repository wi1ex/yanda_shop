from extensions import redis_client, minio_client, BUCKET
from flask import Blueprint, jsonify, request
from models import Shoe, Clothing, Accessory, Users, ChangeLog, db
from minio.error import S3Error
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import zipfile
import json
import io
import csv
import os

logger = logging.getLogger(__name__)
api = Blueprint("api", __name__)


def model_by_category(cat: str):
    return {
        "shoes": Shoe,
        "clothing": Clothing,
        "accessories": Accessory,
        "обувь": Shoe,
        "одежда": Clothing,
        "аксессуары": Accessory
    }.get(cat.lower())


@api.route("/api/")
def home():
    return jsonify({"message": "App is working!"})


@api.route("/api/save_user", methods=["POST"])
def save_user():
    data = request.get_json(force=True, silent=True)
    if not data or 'id' not in data:
        return jsonify({"error": "missing user id"}), 400

    user_id = str(data['id'])
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')

    now = datetime.now(ZoneInfo("Europe/Moscow"))
    date_str = now.strftime("%Y-%m-%d")
    hour_str = now.strftime("%H")

    try:
        user_id = int(user_id)
        is_tg = True
    except ValueError:
        is_tg = False

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
            else:
                # Обновляем имя/фамилию/юзернейм, если поменялись
                if tg_user.first_name != first_name:
                    tg_user.first_name = first_name
                if tg_user.last_name != last_name:
                    tg_user.last_name = last_name
                if tg_user.username != username:
                    tg_user.username = username
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Postgres save error: {e}")

    try:
        total_key = f"visits:{date_str}:{hour_str}:total"
        unique_key = f"visits:{date_str}:{hour_str}:unique"

        redis_client.incr(total_key)
        redis_client.sadd(unique_key, user_id)

        year = 60 * 60 * 24 * 365
        redis_client.expire(total_key, year)
        redis_client.expire(unique_key, year)

        return jsonify({"status": "ok"}), 201

    except Exception as e:
        logger.error(f"Redis error in save_user: {e}")
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/visits")
def get_daily_visits():
    """
    Параметр запроса: ?date=2025-01-01 (формат YYYY-MM-DD). Если date не указан, можно вернуть за «сегодня» (UTC-дата).
    Возвращает JSON вида:
    {"date": "2025-01-01", "hours": [{"hour": "00", "unique": 12, "total": 34},
                                      {"hour": "01", "unique": 23, "total": 45},
                                      ...
                                      {"hour": "23", "unique": 56, "total": 78}]}
    """
    date_str = request.args.get("date")
    if not date_str:
        date_str = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d")
    try:
        hours_data = []
        for h in range(24):
            hour_str = f"{h:02d}"
            total_key = f"visits:{date_str}:{hour_str}:total"
            unique_key = f"visits:{date_str}:{hour_str}:unique"

            total = redis_client.get(total_key)
            unique = redis_client.scard(unique_key)

            hours_data.append({
                "hour": hour_str,
                "unique": int(unique),
                "total": int(total) if total is not None else 0
            })

        return jsonify({"date": date_str, "hours": hours_data}), 200

    except Exception as e:
        logger.error(f"Error getting daily visits for {date_str}: {e}")
        return jsonify({"error": "cannot fetch data"}), 500


@api.route("/api/products")
def list_products():
    """
    GET /api/products?category=<категория>
    Возвращает список товаров:
    [ {sku, name, price, category, image, color, created_at, updated_at}, ... ]
    """
    cat = request.args.get("category", "").lower()

    Model = model_by_category(cat)
    if not Model:
        return jsonify({"error": "unknown category"}), 400

    items = Model.query.all()
    result = []

    for i in items:
        image_url = f'{os.getenv("BACKEND_URL")}/images/{i.sku}-1.webp'
        created_ms = i.created_at.strftime("%Y-%m-%d %H:%M:%S") if i.created_at else None
        updated_ms = i.updated_at.strftime("%Y-%m-%d %H:%M:%S") if i.updated_at else None

        result.append({
            "sku":        i.sku,
            "name":       i.name,
            "price":      i.price,
            "category":   i.category,
            "image":      image_url,
            "color":      i.color,
            "created_at": created_ms,
            "updated_at": updated_ms
        })

    return jsonify(result)


@api.route("/api/product")
def get_product():
    """
    GET /api/product?category=<категория>&sku=<sku>
    Возвращает: все поля товара + массив URL изображений.
    """
    cat = request.args.get("category", "").lower()
    sku = request.args.get("sku", "").strip()
    if not cat or not sku:
        return jsonify({"error": "category and sku required"}), 400

    Model = model_by_category(cat)
    if not Model:
        return jsonify({"error": "unknown category"}), 400
    obj = Model.query.filter_by(sku=sku).first()
    if not obj:
        return jsonify({"error": "not found"}), 404

    data = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        if isinstance(val, datetime):
            data[column.name] = val.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data[column.name] = val

    count = getattr(obj, "count_images", 0) or 0
    images = [f"{os.getenv('BACKEND_URL')}/images/{obj.sku}-{i}.webp" for i in range(1, count + 1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    return jsonify(data)


@api.route("/api/import_products", methods=["POST"])
def import_products():
    """
    POST /api/import_products
    Поле form-data: file=<csv>, author_id=<число>
    Имя файла определяет категорию: shoes.csv, clothing.csv или accessories.csv.
    Если все значения в строке CSV (кроме sku) пустые → удаляем товар.
    """
    f = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name_str = request.form.get("author_name", "").strip()
    if not f or not author_id_str:
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        return jsonify({"error": "invalid author_id"}), 400

    if not author_name_str:
        author_name_str = "unknown"

    name = f.filename.lower()
    base, ext = os.path.splitext(name)
    if ext != ".csv":
        return jsonify({"error": "not a CSV"}), 400

    Model = model_by_category(base)
    if not Model:
        return jsonify({"error": "unknown category"}), 400

    data_str = f.stream.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(data_str))
    rows = list(reader)

    added, updated, deleted = 0, 0, 0
    skus = [row["sku"].strip() for row in rows]
    existing_objs = {obj.sku: obj for obj in Model.query.filter(Model.sku.in_(skus)).all()}

    try:
        for row in rows:
            sku = row["sku"].strip()
            other_fields = {k: row[k].strip() for k in row if k != "sku"}
            if sku and all(not vv for vv in other_fields.values()):
                # Удаляем товар (если существует)
                obj_to_delete = existing_objs.get(sku)
                if obj_to_delete:
                    db.session.delete(obj_to_delete)
                    deleted += 1
                continue

            obj = existing_objs.get(sku)
            if not obj:
                # Новая запись
                obj = Model(sku=sku)
                for key, val in row.items():
                    if hasattr(obj, key) and key != "sku":
                        if key in ["price", "count_in_stock", "count_images"]:
                            try:
                                val = int(val)
                            except ValueError:
                                val = 0
                        elif key in ["size_label", "depth_mm", "width_mm", "height_mm"]:
                            try:
                                val = float(val)
                            except ValueError:
                                val = None
                        setattr(obj, key, val)
                db.session.add(obj)
                added += 1
            else:
                # Обновляем существующий товар
                has_changes = False
                for key, val in row.items():
                    if hasattr(obj, key) and key != "sku":
                        if key in ["price", "count_in_stock", "count_images"]:
                            try:
                                new_val = int(val)
                            except ValueError:
                                new_val = 0
                        elif key in ["size_label", "depth_mm", "width_mm", "height_mm"]:
                            try:
                                new_val = float(val)
                            except ValueError:
                                new_val = None
                        else:
                            new_val = val
                        old_val = getattr(obj, key)
                        if old_val != new_val:
                            setattr(obj, key, new_val)
                            has_changes = True
                if has_changes:
                    obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))
                    updated += 1

        db.session.commit()
    except Exception as e:
        logger.error(f"Import error: {e}")
        db.session.rollback()
        return jsonify({"error": "db error"}), 500

    # Формируем описание: "Добавлено X, Изменено Y, Удалено Z"
    desc = f"Добавлено {added}, Изменено {updated}, Удалено {deleted}"
    try:
        log = ChangeLog(
            author_id=author_id,
            author_name=author_name_str,
            action_type="загрузка csv",
            description=desc,
            timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при сохранении лога (товары): {e}")

    return jsonify({"status": "ok", "added": added, "updated": updated, "deleted": deleted}), 201


@api.route("/api/upload_images", methods=["POST"])
def upload_images():
    """
    POST /api/upload_images
    Поле form-data: file=<zip>, author_id=<число>
    Распаковывает ZIP, загружает файлы в MinIO, удаляет лишние.
    """
    z = request.files.get("file")
    author_id_str = request.form.get("author_id", "").strip()
    author_name_str = request.form.get("author_name", "").strip()
    if not z or not author_id_str:
        return jsonify({"error": "file and author_id required"}), 400

    try:
        author_id = int(author_id_str)
    except ValueError:
        return jsonify({"error": "invalid author_id"}), 400

    if not author_name_str:
        author_name_str = "unknown"

    if not z.filename.lower().endswith(".zip"):
        return jsonify({"error": "not a ZIP"}), 400

    data = io.BytesIO(z.stream.read())
    added = replaced = 0
    with zipfile.ZipFile(data) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            key = info.filename
            content = archive.read(info)
            try:
                minio_client.stat_object(BUCKET, key)
                replaced += 1
            except S3Error:
                added += 1
            minio_client.put_object(BUCKET, key, io.BytesIO(content), length=len(content), content_type="application/octet-stream")

    # Удаляем “чужие” файлы
    expected = set()
    for Model in (Shoe, Clothing, Accessory):
        for obj in Model.query:
            count = getattr(obj, "count_images", 0) or 0
            for i in range(1, count + 1):
                expected.add(f"{obj.sku}-{i}")

    deleted = 0
    for item in minio_client.list_objects(BUCKET, recursive=True):
        base = os.path.splitext(item.object_name)[0]
        if base not in expected:
            minio_client.remove_object(BUCKET, item.object_name)
            deleted += 1

    # Логируем действие
    desc = f"Добавлено {added}, Заменено {replaced}, Удалено {deleted}"
    try:
        log = ChangeLog(
            author_id=author_id,
            author_name=author_name_str,
            action_type="загрузка zip",
            description=desc,
            timestamp=datetime.now(ZoneInfo("Europe/Moscow"))
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при сохранении лога (изображения): {e}")

    return jsonify({"status": "ok", "added": added, "replaced": replaced, "deleted": deleted}), 201


@api.route("/api/logs")
def get_logs():
    """
    GET /api/logs?limit=<N>
    Возвращает последние N записей из таблицы change_logs:
    { logs: [ {id, author_id, action_type, description, timestamp}, ... ] }
    """
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    try:
        logs_qs = ChangeLog.query.order_by(ChangeLog.timestamp.desc()).limit(limit).all()
        result = []
        for lg in logs_qs:
            result.append({
                "id": lg.id,
                "author_id": lg.author_id,
                "author_name": lg.author_name,
                "action_type": lg.action_type,
                "description": lg.description,
                "timestamp": lg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"logs": result}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении логов: {e}")
        return jsonify({"error": "cannot fetch logs"}), 500


@api.route("/api/user")
def get_user_profile():
    """
    GET /api/user?user_id=<id>
    Возвращает: { user_id, first_name, last_name, username, created_at }
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    try:
        uid = int(user_id)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        u = Users.query.get(uid)
        if not u:
            return jsonify({"error": "not found"}), 404

        created_ms = u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else None
        return jsonify({
            "user_id":    u.user_id,
            "first_name": u.first_name,
            "last_name":  u.last_name,
            "username":   u.username,
            "created_at": created_ms
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user {uid}: {e}")
        return jsonify({"error": "internal error"}), 500


@api.route("/api/cart", methods=["GET"])
def get_cart():
    """
    GET /api/cart?user_id=<id>
    Возвращает JSON: { items: [...], count, total }
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    try:
        uid = int(user_id)
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    try:
        key = f"cart:{uid}"
        stored = redis_client.get(key)
        if not stored:
            return jsonify({"items": [], "count": 0, "total": 0}), 200

        cart_data = json.loads(stored)
        return jsonify(cart_data), 200
    except Exception as e:
        logger.error(f"Redis error in get_cart: {e}")
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/cart", methods=["POST"])
def save_cart():
    """
    POST /api/cart
    Сохраняет корзину в Redis: { user_id, items, count, total }
    """
    data = request.get_json(force=True, silent=True)
    if not data or "user_id" not in data:
        return jsonify({"error": "user_id required"}), 400
    try:
        uid = int(data["user_id"])
    except ValueError:
        return jsonify({"error": "invalid user_id"}), 400

    items = data.get("items", [])
    count = data.get("count", 0)
    total = data.get("total", 0)

    to_store = {"items": items, "count": count, "total": total}
    try:
        key = f"cart:{uid}"
        redis_client.set(key, json.dumps(to_store))
        year = 60 * 60 * 24 * 365
        redis_client.expire(key, year)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Redis error in save_cart: {e}")
        return jsonify({"error": "internal redis error"}), 500


def register_routes(app):
    app.register_blueprint(api)
