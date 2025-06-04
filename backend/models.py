from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

db = SQLAlchemy()

class Users(db.Model):
    __tablename__  = 'users'
    user_id        = db.Column(db.BigInteger, primary_key=True)
    first_name     = db.Column(db.String(100))
    last_name      = db.Column(db.String(100))
    username       = db.Column(db.String(100))

class Shoe(db.Model):
    __tablename__  = "shoes"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    size_label     = db.Column(db.Float)
    depth_mm       = db.Column(db.Float)
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    count_in_stock = db.Column(db.Integer, default=0)
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")))
    updated_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")),
                               onupdate=lambda: datetime.now(ZoneInfo("Europe/Moscow")))

class Clothing(db.Model):
    __tablename__  = "clothing"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    size_label     = db.Column(db.String(20))
    width_mm       = db.Column(db.Float)
    height_mm      = db.Column(db.Float)
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    count_in_stock = db.Column(db.Integer, default=0)
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")))
    updated_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")),
                               onupdate=lambda: datetime.now(ZoneInfo("Europe/Moscow")))

class Accessory(db.Model):
    __tablename__  = "accessories"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    width_mm       = db.Column(db.Float)
    height_mm      = db.Column(db.Float)
    depth_mm       = db.Column(db.Float)
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    count_in_stock = db.Column(db.Integer, default=0)
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")))
    updated_at     = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Moscow")),
                               onupdate=lambda: datetime.now(ZoneInfo("Europe/Moscow")))
