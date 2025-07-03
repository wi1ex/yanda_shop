from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .core.config import SQLALCHEMY_DATABASE_URI, CORS_ORIGINS, SECRET_KEY
from .core.logging import setup_logging, logger
from .models import db
from .utils.product_serializer import load_delivery_options
from .routes.general import general_api
from .routes.product import product_api
from .routes.admin import admin_api
from .routes.auth import auth_bp


def create_app() -> Flask:
    # 1) Логирование
    setup_logging()
    logger.info("Starting application")

    # 2) Flask + конфиг SQLAlchemy
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # 3) Расширения
    db.init_app(app)
    Migrate(app, db)
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

    # 4) Flask-JWT-Extended
    app.config['JWT_SECRET_KEY'] = SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(err_str):
        logger.debug("JWT unauthorized: %s", err_str)
        return jsonify({"error": "Authorization header required"}), 401

    @jwt.invalid_token_loader
    def invalid_token(err_str):
        logger.debug("JWT invalid token: %s", err_str)
        return jsonify({"error": "Invalid token"}), 422

    @jwt.expired_token_loader
    def expired_token(header, payload):
        logger.debug("JWT expired token: header=%s payload=%s", header, payload)
        return jsonify({"error": "Token has expired"}), 401

    # 5) Blueprint’ы
    app.register_blueprint(general_api)  # /api/general/...
    app.register_blueprint(product_api)  # /api/product/...
    app.register_blueprint(admin_api)    # /api/admin/...
    app.register_blueprint(auth_bp)      # /api/auth

    # 6) Кэшируем delivery options
    with app.app_context():
        load_delivery_options()
        logger.debug("Delivery options cached")

    return app
