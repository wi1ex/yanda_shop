from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from .cors.config import SQLALCHEMY_DATABASE_URI, CORS_ORIGINS, SECRET_KEY
from .cors.logging import setup_logging, logger
from .models import db
from .utils import load_delivery_options
from .routes.general import general_api
from .routes.product import product_api
from .routes.admin import admin_api


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

    # 4) Blueprint’ы
    app.register_blueprint(general_api)  # общий API (/api/general/...)
    app.register_blueprint(product_api)  # товары    (/api/product/...)
    app.register_blueprint(admin_api)    # админка   (/api/admin/...)

    # 5) Кэшируем delivery options
    with app.app_context():
        load_delivery_options()
        logger.debug("Delivery options cached")

    return app
