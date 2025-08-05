from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text

db = SQLAlchemy()


class Users(db.Model):
    __tablename__  = 'users'
    user_id        = db.Column(db.BigInteger, primary_key=True)
    first_name     = db.Column(db.String(50), nullable=False)
    last_name      = db.Column(db.String(50), nullable=False)
    middle_name    = db.Column(db.String(50), nullable=True)
    role           = db.Column(db.String(50), default='customer', nullable=False)
    avatar_url     = db.Column(db.String(200), nullable=True)
    phone          = db.Column(db.String(50), nullable=True)
    email          = db.Column(db.String(50), nullable=True)
    email_verified = db.Column(db.Boolean, nullable=True)
    date_of_birth  = db.Column(db.Date, nullable=True)
    gender         = db.Column(db.String(50), nullable=True)
    mailing        = db.Column(db.Boolean, nullable=True)
    loyalty_points = db.Column(db.Integer, nullable=True)
    total_spent    = db.Column(db.Integer, nullable=True)
    order_count    = db.Column(db.Integer, nullable=True)
    last_visit     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class ChangeLog(db.Model):
    __tablename__  = 'change_logs'
    id             = db.Column(db.Integer, primary_key=True)
    author_id      = db.Column(db.BigInteger, nullable=False)
    action_type    = db.Column(db.String(50), nullable=False)
    description    = db.Column(db.Text, nullable=False)
    timestamp      = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AdminSetting(db.Model):
    __tablename__  = 'admin_settings'
    key            = db.Column(db.String(50), primary_key=True)
    value          = db.Column(db.Text, nullable=True)
    updated_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Review(db.Model):
    __tablename__  = 'reviews'
    id             = db.Column(db.Integer, primary_key=True)
    client_name    = db.Column(db.String(50), nullable=False)
    client_text1   = db.Column(db.Text, nullable=False)
    shop_response  = db.Column(db.Text, nullable=False)
    client_text2   = db.Column(db.Text, nullable=True)
    link_url       = db.Column(db.String(200), nullable=False)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class RequestItem(db.Model):
    __tablename__  = 'requests'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(50), nullable=False)
    email          = db.Column(db.String(50), nullable=False)
    sku            = db.Column(db.String(100), nullable=True)
    has_file       = db.Column(db.Boolean, default=False, nullable=False)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Addresses(db.Model):
    __tablename__ = 'addresses'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    city          = db.Column(db.String(50), nullable=False)
    street        = db.Column(db.String(50), nullable=False)
    house         = db.Column(db.String(50), nullable=False)
    apartment     = db.Column(db.String(50))
    intercom      = db.Column(db.String(50))
    entrance      = db.Column(db.String(50))
    floor         = db.Column(db.String(50))
    comment       = db.Column(db.String(200))


class Orders(db.Model):
    __tablename__  = 'orders'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    status         = db.Column(db.String(50), nullable=False, default='new')
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at   = db.Column(db.DateTime(timezone=True))
    shipped_at     = db.Column(db.DateTime(timezone=True))
    delivered_at   = db.Column(db.DateTime(timezone=True))
    payment_method = db.Column(db.String(50))
    delivery_type  = db.Column(db.String(50))
    delivery_price = db.Column(db.Integer, default=0, nullable=False)
    total          = db.Column(db.Integer, nullable=False)
    address_id     = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    items_json     = db.Column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))


class BaseProduct(db.Model):
    __abstract__   = True
    id             = db.Column(db.Integer, primary_key=True)
    variant_sku    = db.Column(db.String(100), unique=True, nullable=False, index=True)
    color_sku      = db.Column(db.String(100), index=True)
    world_sku      = db.Column(db.String(100))
    sku            = db.Column(db.String(100))
    name           = db.Column(db.String(100), index=True)
    gender         = db.Column(db.String(50))
    category       = db.Column(db.String(50))
    subcategory    = db.Column(db.String(50), index=True)
    brand          = db.Column(db.String(50), index=True)
    description    = db.Column(db.Text)
    material       = db.Column(db.String(100))
    color          = db.Column(db.String(50), index=True)
    size_label     = db.Column(db.String(50), index=True)
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
    depth_mm       = db.Column(db.Float)


class Clothing(BaseProduct):
    __tablename__  = "clothing"
    chest_cm       = db.Column(db.Float)
    height_cm      = db.Column(db.Float)


class Accessory(BaseProduct):
    __tablename__  = "accessories"
    width_cm       = db.Column(db.Float)
    height_cm      = db.Column(db.Float)
    depth_cm       = db.Column(db.Float)
