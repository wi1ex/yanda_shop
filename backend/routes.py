from flask import Blueprint, jsonify, request
from models import db, Visitor
from datetime import datetime
import logging
import redis
import json
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


@api.route("/save_user", methods=["POST"])
def save_user():
    data = request.json  # ожидаем id, first_name, last_name, username
    # 1) Сохраняем в Postgres
    visitor = Visitor(
        user_id=data['id'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        username=data.get('username')
    )
    db.session.add(visitor)
    db.session.commit()

    # 2) Пишем в Redis (sorted set) и чистим старые (>24 ч)
    key = "recent_visitors"
    timestamp = int(datetime.utcnow().timestamp())
    visitor_record = json.dumps({
        "db_id": visitor.id,
        "user_id": data['id'],
        "username": data.get('username'),
        "first_name": data.get('first_name'),
        "visit_time": timestamp
    })
    redis_client.zadd(key, {visitor_record: timestamp})
    # Удаляем записи старше 24 часов
    cutoff = timestamp - 24*3600
    redis_client.zremrangebyscore(key, 0, cutoff)

    return jsonify({"status": "ok"}), 201


def register_routes(app):
    app.register_blueprint(api)
