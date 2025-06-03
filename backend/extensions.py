import os
import redis
from minio import Minio

# Redis клиент
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# MinIO клиент
minio_client = Minio(
    os.getenv("MINIO_HOST"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

BUCKET = os.getenv('MINIO_BUCKET')

if not minio_client.bucket_exists(BUCKET):
    minio_client.make_bucket(BUCKET)
