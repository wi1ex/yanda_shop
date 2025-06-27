from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Users(db.Model):
    __tablename__  = 'users'
    user_id        = db.Column(db.BigInteger, primary_key=True)
    username       = db.Column(db.String(100), nullable=False)
    first_name     = db.Column(db.String(100), nullable=False)
    last_name      = db.Column(db.String(100), nullable=False)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ChangeLog(db.Model):
    __tablename__  = 'change_logs'
    id             = db.Column(db.Integer, primary_key=True)
    author_id      = db.Column(db.BigInteger, nullable=False)
    author_name    = db.Column(db.String(100), nullable=False)
    action_type    = db.Column(db.String(100), nullable=False)
    description    = db.Column(db.Text, nullable=False)
    timestamp      = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AdminSetting(db.Model):
    __tablename__  = 'admin_settings'
    key            = db.Column(db.String(100), primary_key=True)
    value          = db.Column(db.Text)
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class BaseProduct(db.Model):
    __abstract__   = True
    id             = db.Column(db.Integer, primary_key=True)
    variant_sku    = db.Column(db.String(100), unique=True, nullable=False, index=True)
    color_sku      = db.Column(db.String(100), index=True)
    world_sku      = db.Column(db.String(100), index=True)
    sku            = db.Column(db.String(100), index=True)
    name           = db.Column(db.String(100))
    gender         = db.Column(db.String(100))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100), index=True)
    brand          = db.Column(db.String(100), index=True)
    description    = db.Column(db.Text)
    material       = db.Column(db.String(100))
    color          = db.Column(db.String(100), index=True)
    size_category  = db.Column(db.Integer)
    price          = db.Column(db.Integer, index=True)
    count_in_stock = db.Column(db.Integer, index=True)
    count_images   = db.Column(db.Integer)
    count_sales    = db.Column(db.Integer, default=0, nullable=False)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Shoe(BaseProduct):
    __tablename__  = "shoes"
    size_label     = db.Column(db.Float)
    depth_mm       = db.Column(db.Float)


class Clothing(BaseProduct):
    __tablename__  = "clothing"
    size_label     = db.Column(db.String(100))
    chest_cm       = db.Column(db.Float)
    height_cm      = db.Column(db.Float)


class Accessory(BaseProduct):
    __tablename__  = "accessories"
    size_label     = db.Column(db.String(100))
    width_cm       = db.Column(db.Float)
    height_cm      = db.Column(db.Float)
    depth_cm       = db.Column(db.Float)
