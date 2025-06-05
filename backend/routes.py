from extensions import redis_client, minio_client, BUCKET
from flask import Blueprint, jsonify, request
from models import Shoe, Clothing, Accessory, Users, db
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
    return {"shoes": Shoe, "clothing": Clothing, "accessories": Accessory,
            "обувь": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat.lower())


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
                tg_user = Users(user_id=user_id,
                                first_name=first_name,
                                last_name=last_name,
                                username=username)
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

            hours_data.append({"hour": hour_str,
                               "unique": int(unique),
                               "total": int(total) if total is not None else 0})

        return jsonify({"date": date_str, "hours": hours_data}), 200

    except Exception as e:
        logger.error(f"Error getting daily visits for {date_str}: {e}")
        return jsonify({"error": "cannot fetch data"}), 500


@api.route("/api/products")
def list_products():
    # Параметр ?category=Обувь|Одежда|Аксессуары
    cat = request.args.get("category", "").lower()

    # Определяем модель по category
    Model = model_by_category(cat)
    if not Model:
        return jsonify({"error": "unknown category"}), 400

    # Возвращаем все товары выбранной категории
    items = Model.query.all()
    result = []
    for i in items:
        image_url = f'{os.getenv("BACKEND_URL")}/images/{i.sku}-1.webp'
        result.append({"sku":        i.sku,
                       "name":       i.name,
                       "price":      i.price,
                       "category":   i.category,
                       "image":      image_url,
                       "color":      i.color,
                       "created_at": i.created_at.isoformat()})
    return jsonify(result)


@api.route("/api/product")
def get_product():
    """
    Новый endpoint: /api/product?category=<категория>&sku=<sku>
    Возвращает JSON со всеми полями этой записи из таблицы,
    а также массив URL всех изображений (по count_images).
    """
    cat = request.args.get("category", "").lower()
    sku = request.args.get("sku", "").strip()
    if not cat or not sku:
        return jsonify({"error": "category and sku required"}), 400

    # Определяем модель по category
    Model = model_by_category(cat)
    if not Model:
        return jsonify({"error": "unknown category"}), 400
    obj = Model.query.filter_by(sku=sku).first()
    if not obj:
        return jsonify({"error": "not found"}), 404

    # Собираем все поля из объекта в словарь
    data = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        # Для DateTime, если нужно, можно сериализовать, но тут пока просто возвращаем как строку
        if isinstance(val, datetime):
            data[column.name] = val.isoformat()
        else:
            data[column.name] = val

    # Вытаскиваем число картинок из count_images (если у вас в модели есть это поле)
    count = getattr(obj, "count_images", 0) or 0
    images = [f"{os.getenv('BACKEND_URL')}/images/{obj.sku}-{i}.webp" for i in range(1, count + 1)]
    data["images"] = images
    data["image"] = images[0] if images else None

    return jsonify(data)


@api.route("/api/import_products", methods=["POST"])
def import_products():
    """
    Принимает form-data с одним полем file=<csv>,
    название файла определяет категорию: shoes.csv, clothing.csv или accessories.csv
    """
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400

    name = f.filename.lower()
    base, ext = os.path.splitext(name)
    if ext != ".csv":
        return jsonify({"error": "not a CSV"}), 400

    Model = model_by_category(base)
    if not Model:
        return jsonify({"error": "unknown category"}), 400

    # Читаем CSV целиком в список строк (каждая строка – dict)
    data_str = f.stream.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(data_str))
    rows = list(reader)  # теперь это список, и мы можем итерировать сколько угодно раз

    added, updated = 0, 0

    # Собираем все SKU из файла
    skus = [row["sku"] for row in rows]
    # Берём из БД уже существующие объекты с этими SKU
    existing_objs = {obj.sku: obj for obj in Model.query.filter(Model.sku.in_(skus)).all()}

    try:
        for row in rows:
            sku = row["sku"]
            obj = existing_objs.get(sku)
            if not obj:
                # Создаём новую запись
                obj = Model(sku=sku)
                db.session.add(obj)
                added += 1
            else:
                updated += 1

            # Обновляем все поля (кроме SKU)
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

            # Явно выставляем updated_at, чтобы не полагаться на onupdate
            obj.updated_at = datetime.now(ZoneInfo("Europe/Moscow"))

        db.session.commit()
    except Exception as e:
        logger.error(f"Import error: {e}")
        db.session.rollback()
        return jsonify({"error": "db error"}), 500

    return jsonify({"status": "ok", "added": added, "updated": updated}), 201


@api.route("/api/upload_images", methods=["POST"])
def upload_images():
    """
    Принимает form-data с одним полем file=<zip>,
    разворачивает и заливает все файлы в MinIO (bucket=product-images),
    затем удаляет «лишние» файлы, не относящиеся к текущим SKU.
    """
    z = request.files.get("file")
    if not z:
        return jsonify({"error": "no file"}), 400
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
                # Проверяем, есть ли уже в бакете
                minio_client.stat_object(BUCKET, key)
                replaced += 1
            except S3Error:
                added += 1
            # Загружаем (перезаписываем, если существует)
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

    return jsonify({"status": "ok", "added": added, "replaced": replaced, "deleted": deleted}), 201


@api.route("/api/user")
def get_user_profile():
    """
    GET /api/user?user_id=<id>
    Возвращает информацию о пользователе из таблицы Users:
    { user_id, first_name, last_name, username }
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
        return jsonify({
            "user_id": u.user_id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "username": u.username
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user {uid}: {e}")
        return jsonify({"error": "internal error"}), 500


@api.route("/api/cart", methods=["GET"])
def get_cart():
    """
    GET /api/cart?user_id=<id>
    Возвращает JSON: { items: [...], total: <int>, count: <int> }
    Данные храним/берём из Redis по ключу "cart:{user_id}"
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
            # Пустая корзина
            return jsonify({"items": [], "count": 0, "total": 0}), 200

        # Данные хранятся как JSON-строка: {"items": [...], "count": X, "total": Y}
        cart_data = json.loads(stored)
        return jsonify(cart_data), 200
    except Exception as e:
        logger.error(f"Redis error in get_cart: {e}")
        return jsonify({"error": "internal redis error"}), 500


@api.route("/api/cart", methods=["POST"])
def save_cart():
    """
    POST /api/cart
    Принимает JSON: { user_id: <int>, items: [...], count: <int>, total: <int> }
    Сохраняет в Redis (key="cart:{user_id}", value=JSON).
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
        # Сохраняем как JSON
        redis_client.set(key, json.dumps(to_store))
        # Ставим TTL год (так же, как посещения)
        year = 60 * 60 * 24 * 365
        redis_client.expire(key, year)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Redis error in save_cart: {e}")
        return jsonify({"error": "internal redis error"}), 500


def register_routes(app):
    app.register_blueprint(api)
