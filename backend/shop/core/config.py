import os
from typing import List

BACKEND_URL: str = os.environ.get("BACKEND_URL", "")
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()
CORS_ORIGINS: List[str] = [origin.strip() for origin in BACKEND_URL.split(",")]

SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")
JWT_TOKEN_LOCATION: List[str] = ["headers"]
JWT_HEADER_NAME: str = "Authorization"
JWT_HEADER_TYPE: str = "Bearer"
JWT_ACCESS_TOKEN_EXPIRES: int = 3600

DB_USER: str = os.environ["DB_USER"]
DB_PASSWORD: str = os.environ["DB_PASSWORD"]
DB_HOST: str = os.environ["DB_HOST"]
DB_PORT: int = int(os.environ.get("DB_PORT", 5432))
DB_NAME: str = os.environ["DB_NAME"]
SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
SQLALCHEMY_DATABASE_URI: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

REDIS_HOST: str = os.environ["REDIS_HOST"]
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.environ["REDIS_PASSWORD"]

MINIO_HOST: str = os.environ["MINIO_HOST"]
MINIO_ROOT_USER: str = os.environ["MINIO_ROOT_USER"]
MINIO_ROOT_PASSWORD: str = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_BUCKET: str = os.environ["MINIO_BUCKET"]

MAIL_SERVER: str = os.environ.get("MAIL_SERVER")
MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
MAIL_USE_TLS: bool = bool(os.environ.get("MAIL_USE_TLS", "True"))
MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER: str = os.environ.get("MAIL_DEFAULT_SENDER")
