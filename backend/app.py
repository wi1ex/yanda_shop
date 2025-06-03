from flask_migrate import Migrate
from flask_cors import CORS
from flask import Flask
from routes import register_routes
from models import db
import extensions
import logging
import sys
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('DB_USER')}:"
                                         f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
                                         f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

CORS(app, resources={r"/api/*": {"origins": "https://shop.yanda.twc1.net"}})

register_routes(app)

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
