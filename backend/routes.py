from flask import Blueprint, jsonify, request
from models import Shoe, Clothing, Accessory, db
from datetime import datetime
from io import StringIO
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
    # Параметр ?category=Кроссовки|Одежда|Аксессуары
    cat = request.args.get("category", "").lower()
    Model = {"кроссовки": Shoe, "одежда": Clothing, "аксессуары": Accessory}.get(cat)
    if not Model:
        return jsonify([])

    items = Model.query.order_by(Model.created_at.desc()).all()
    result = []
    for i in items:
        result.append({
            "sku":       i.sku,
            "name":      i.name,
            "price":     i.price,
            "category":  i.category,
            "image":     f'https://shop.yanda.twc1.net/images/{i.image_filename}'
        })
    return jsonify(result)


@api.route("/api/import_products", methods=["POST"])
def import_products():
    """
    Загрузка CSV: form-data с полями:
      - file  = CSV-файл
      - type  = один из: shoe, clothing, accessory
    """
    f = request.files.get("file")
    typ = request.form.get("type")
    if not f or typ not in ("shoe", "clothing", "accessory"):
        return jsonify({"error": "bad request"}), 400

    Model = {"shoe": Shoe, "clothing": Clothing, "accessory": Accessory}[typ]
    reader = csv.DictReader(StringIO(f.stream.read().decode("utf-8")))

    for row in reader:
        obj = Model.query.filter_by(sku=row["sku"]).first()
        if not obj:
            obj = Model(sku=row["sku"])
            db.session.add(obj)
        for key, val in row.items():
            if hasattr(obj, key) and key != "sku":
                setattr(obj, key, val or None)
    db.session.commit()
    return jsonify({"status": "ok"}), 201


def register_routes(app):
    app.register_blueprint(api)
