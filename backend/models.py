from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Visitor(db.Model):
    __tablename__ = 'visitors'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.BigInteger, nullable=False)
    username      = db.Column(db.String(100))
    visit_time    = db.Column(db.DateTime, default=datetime.utcnow)

class Shoe(db.Model):
    __tablename__  = "shoes"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    width_mm       = db.Column(db.Integer)
    height_mm      = db.Column(db.Integer)
    depth_mm       = db.Column(db.Integer)
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    image_filename = db.Column(db.String(200))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

class Clothing(db.Model):
    __tablename__  = "clothing"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    size_label     = db.Column(db.String(20))
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    image_filename = db.Column(db.String(200))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

class Accessory(db.Model):
    __tablename__  = "accessories"
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(100), unique=True, nullable=False)
    name           = db.Column(db.String(200), nullable=False)
    gender         = db.Column(db.String(20))
    category       = db.Column(db.String(100))
    subcategory    = db.Column(db.String(100))
    brand          = db.Column(db.String(100))
    description    = db.Column(db.Text)
    material       = db.Column(db.String(200))
    color          = db.Column(db.String(100))
    price          = db.Column(db.Integer, nullable=False)
    size_guide_url = db.Column(db.String(300))
    delivery_time  = db.Column(db.String(100))
    image_filename = db.Column(db.String(200))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
