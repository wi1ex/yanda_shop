from flask import Blueprint, jsonify, request
from models import Shoe, Clothing, Accessory, db
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import zipfile
import io
import logging
import redis
import json
import csv
import os

logger = logging.getLogger(__name__)
api = Blueprint("api", __name__)

# Инициализация Redis-клиента
redis_client = redis.Redis(host=os.getenv('REDIS_HOST'),
                           port=int(os.getenv('REDIS_PORT')),
                           password=os.getenv('REDIS_PASSWORD'),
                           decode_responses=True)

# создаём MinIO-клиент
minio_client = Minio(os.getenv("MINIO_HOST"),
                     access_key=os.getenv("MINIO_ROOT_USER"),
                     secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
                     secure=False)
BUCKET = os.getenv('MINIO_BUCKET')
# создаём бакет, если нет
if not minio_client.bucket_exists(BUCKET):
    minio_client.make_bucket(BUCKET)


def model_by_category(cat: str):
    return {"shoes": Shoe, "clothing": Clothing, "accessories": Accessory}.get(cat)


@api.route("/api/")
def home():
    return jsonify({"message": "App is working!"})


@api.route("/api/save_user", methods=["POST"])
def save_user():
    data = request.json  # ожидаем поля id, first_name, last_name, username

    timestamp = int(datetime.utcnow().timestamp())
    # Составляем запись без db_id
    visitor_record = json.dumps({
        "user_id":    data['id'],
        "first_name": data.get('first_name'),
        "last_name":  data.get('last_name'),
        "username":   data.get('username'),
        "visit_time": timestamp
    })

    # Добавляем в сортированное множество
    redis_client.zadd("recent_visitors", {visitor_record: timestamp})

    # Очищаем старые записи (старше 24 ч)
    cutoff = timestamp - 24*3600
    redis_client.zremrangebyscore("recent_visitors", 0, cutoff)

    return jsonify({"status": "ok"}), 201


@api.route("/api/products")
def list_products():
    # Параметр ?category=Обувь|Одежда|Аксессуары
    cat = request.args.get("category", "").lower()
    Model = {"обувь": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat)
    if not Model:
        return jsonify([])

    items = Model.query.order_by(Model.created_at.desc()).all()
    result = []
    for i in items:
        image_url = f'{os.getenv("BACKEND_URL")}/images/{i.sku}-1.webp'
        result.append({"sku":      i.sku,
                       "name":     i.name,
                       "price":    i.price,
                       "category": i.category,
                       "image":    image_url})
    return jsonify(result)


@api.route("/api/product")
def get_product():
    """
    Новый endpoint: /api/product?category=<категория>&sku=<sku>
    Возвращает JSON со всеми полями этой записи из таблицы.
    """
    cat = request.args.get("category", "").lower()
    sku = request.args.get("sku", "").strip()
    if not cat or not sku:
        return jsonify({"error": "category and sku required"}), 400

    # Определяем модель по category (понимаем, что пользователь передаёт, например, "Обувь" или "Кроссовки")
    Model = {"обувь": Shoe,
             "одежда": Clothing,
             "аксессуары": Accessory}.get(cat)
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

    # Добавим к JSON ещё прямой URL картинки (если image_filename есть)
    if obj.image_filename:
        data["image_url"] = f'{os.getenv("BACKEND_URL")}/images/{obj.image_filename}'

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

    reader = csv.DictReader(io.StringIO(f.stream.read().decode("utf-8")))
    added = updated = 0
    for row in reader:
        obj = Model.query.filter_by(sku=row["sku"]).first()
        if obj is None:
            obj = Model(sku=row["sku"])
            db.session.add(obj)
            added += 1
        else:
            updated += 1
        for key, val in row.items():
            if hasattr(obj, key) and key != "sku":
                setattr(obj, key, val or None)
    db.session.commit()
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

    # Теперь удаляем «чужие» файлы:
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


def register_routes(app):
    app.register_blueprint(api)
