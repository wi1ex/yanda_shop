from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Users(db.Model):
    __tablename__  = 'users'
    user_id        = db.Column(db.BigInteger, primary_key=True)
    first_name     = db.Column(db.String(100))
    last_name      = db.Column(db.String(100))
    username       = db.Column(db.String(100))
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ChangeLog(db.Model):
    __tablename__  = 'change_logs'
    id             = db.Column(db.Integer, primary_key=True)
    author_id      = db.Column(db.BigInteger, nullable=False)
    author_name    = db.Column(db.String(50), nullable=False)
    action_type    = db.Column(db.String(300), nullable=False)
    description    = db.Column(db.Text, nullable=False)
    timestamp      = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Shoe(db.Model):
    __tablename__  = "shoes"
    id             = db.Column(db.Integer, primary_key=True)
    variant_sku    = db.Column(db.String(100), unique=True, nullable=False, index=True)
    sku            = db.Column(db.String(100), nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100), index=True)
    brand          = db.Column(db.String(100), index=True)
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100), index=True)
    size_label     = db.Column(db.Float)
    depth_mm       = db.Column(db.Float)
    size_guide_url = db.Column(db.String(300))
    price          = db.Column(db.Integer, nullable=False, index=True)
    count_in_stock = db.Column(db.Integer, default=0, index=True)
    delivery_time  = db.Column(db.String(100))
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))

class Clothing(db.Model):
    __tablename__  = "clothing"
    id             = db.Column(db.Integer, primary_key=True)
    variant_sku    = db.Column(db.String(100), unique=True, nullable=False, index=True)
    sku            = db.Column(db.String(100), nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100), index=True)
    brand          = db.Column(db.String(100), index=True)
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100), index=True)
    size_label     = db.Column(db.String(20))
    width_mm       = db.Column(db.Float)
    height_mm      = db.Column(db.Float)
    size_guide_url = db.Column(db.String(300))
    price          = db.Column(db.Integer, nullable=False, index=True)
    count_in_stock = db.Column(db.Integer, default=0, index=True)
    delivery_time  = db.Column(db.String(100))
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))

class Accessory(db.Model):
    __tablename__  = "accessories"
    id             = db.Column(db.Integer, primary_key=True)
    variant_sku    = db.Column(db.String(100), unique=True, nullable=False, index=True)
    sku            = db.Column(db.String(100), nullable=False, index=True)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100), index=True)
    brand          = db.Column(db.String(100), index=True)
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100), index=True)
    width_mm       = db.Column(db.Float)
    height_mm      = db.Column(db.Float)
    depth_mm       = db.Column(db.Float)
    size_guide_url = db.Column(db.String(300))
    price          = db.Column(db.Integer, nullable=False, index=True)
    count_in_stock = db.Column(db.Integer, default=0, index=True)
    delivery_time  = db.Column(db.String(100))
    count_images   = db.Column(db.Integer, default=10)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))
