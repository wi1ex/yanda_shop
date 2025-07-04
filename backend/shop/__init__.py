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
    context = "create_app"
    setup_logging()
    logger.info("%s START", context)

    try:
        # ——— Flask и конфигурация ————————————————————————————————
        app = Flask(__name__)
        app.config.update({
            "SQLALCHEMY_DATABASE_URI":        SQLALCHEMY_DATABASE_URI,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY":                     SECRET_KEY,
            "JWT_SECRET_KEY":                 SECRET_KEY,
            "JWT_TOKEN_LOCATION":             ["headers"],
            "JWT_HEADER_NAME":                "Authorization",
            "JWT_HEADER_TYPE":                "Bearer",
            "JWT_ACCESS_TOKEN_EXPIRES":       3600,
        })
        logger.debug("%s: Flask app configured", context)

        # ——— Расширения —————————————————————————————————————————
        db.init_app(app)
        Migrate(app, db)
        CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})
        logger.debug("%s: Extensions initialized", context)

        # ——— JWT менеджер и ошибки —————————————————————————
        jwt = JWTManager(app)

        @jwt.unauthorized_loader
        def _missing_token(err_str):
            logger.warning("%s: JWT unauthorized: %s", context, err_str)
            return jsonify({"error": "Authorization header required"}), 401

        @jwt.invalid_token_loader
        def _invalid_token(err_str):
            logger.warning("%s: JWT invalid token: %s", context, err_str)
            return jsonify({"error": "Invalid token"}), 422

        @jwt.expired_token_loader
        def _expired_token(header, payload):
            logger.warning("%s: JWT expired token", context, header, payload)
            return jsonify({"error": "Token has expired"}), 401

        logger.debug("%s: JWT callbacks registered", context)

        # ——— Роуты ————————————————————————————————————————————
        for bp in (general_api, product_api, admin_api, auth_bp):
            app.register_blueprint(bp)
            logger.debug("%s: registered blueprint %s", context, bp.name)

        # ——— Кэширование опций доставки ————————————————————————
        with app.app_context():
            load_delivery_options()
            logger.debug("%s: delivery options cached", context)

    except Exception:
        logger.exception("%s: Error during app initialization", context)
        raise

    logger.info("%s END", context)
    return app
