from flask import Flask, jsonify, send_from_directory, abort
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .core import config
from .core.logging import setup_logging, logger
from .extensions import mail
from .models import db
from .utils.cache_utils import load_delivery_options, load_parameters
from .routes.general import general_api
from .routes.product import product_api
from .routes.admin import admin_api
from .routes.auth import auth_bp

def create_app() -> Flask:
    context = "create_app"
    setup_logging()
    logger.debug("%s START", context)

    try:
        # ——— Flask и конфигурация ————————————————————————————————
        app = Flask(__name__)
        app.config.from_object(config)
        logger.debug("%s: Flask app configured", context)

        # ——— Расширения —————————————————————————————————————————
        db.init_app(app)
        Migrate(app, db)
        CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
        mail.init_app(app)
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
            logger.warning("%s: JWT expired token — header=%s, payload=%s", context, header, payload)
            return jsonify({"error": "Token has expired"}), 401

        logger.debug("%s: JWT callbacks registered", context)

        # ——— Роуты ————————————————————————————————————————————
        for bp in (general_api, product_api, admin_api, auth_bp):
            app.register_blueprint(bp)
            logger.debug("%s: registered blueprint %s", context, bp.name)

        # ——— Скачивание документов ————————————————————————
        @app.route("/download/<path:filename>")
        def download_file(filename):
            # Базовая защита: отдаём только PDF
            if not filename.lower().endswith(".pdf"):
                abort(404)
            return send_from_directory('static/files', filename)

        # ——— Кэширование опций доставки ————————————————————————
        with app.app_context():
            load_parameters()
            load_delivery_options()
            logger.debug("%s: delivery options cached", context)

    except Exception:
        logger.exception("%s: Error during app initialization", context)
        raise

    logger.debug("%s END", context)
    return app
