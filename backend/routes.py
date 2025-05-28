from flask import Blueprint, jsonify, request
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


def register_routes(app):
    app.register_blueprint(api)
