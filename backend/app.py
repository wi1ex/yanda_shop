from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models import db
from routes import register_routes
from admin_routes import admin_api
from cors.config import SQLALCHEMY_DATABASE_URI, CORS_ORIGINS
from cors.logging import setup_logging

# 1) Настраиваем логирование по конфику
setup_logging()

# 2) Создаём Flask-приложение
app: Flask = Flask(__name__)

# 3) Загружаем конфиг для SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 4) Инициализируем расширения
db.init_app(app)
migrate = Migrate(app, db)

# 5) CORS
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

# 6) Регистрируем Blueprint
register_routes(app)
app.register_blueprint(admin_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
