import os
from flask import Flask
from flask_cors import CORS
from models import db
from routes import register_routes
import logging
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('DB_USER')}:"
                                         f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
                                         f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
register_routes(app)

# Создаем таблицы при старте, если их нет
with app.app_context():
    db.create_all()

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
