from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)
api = Blueprint("api", __name__)

@api.route("/api/")
def home():
    return jsonify({"message": "App is working!"})

@api.route("/send-data", methods=["POST"])
def send_data():
    data = request.json
    logger.info("Получены данные: %s", data)
    return jsonify({"status": "success", "data": data})

@api.route("/save_user", methods=["POST"])
def save_user():
    data = request.json
    logger.info("Данные пользователя: %s", data)
    return jsonify({"status": "ok"})

def register_routes(app):
    app.register_blueprint(api)
