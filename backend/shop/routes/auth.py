import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from ..cors.config import SECRET_KEY


def create_access_token(user_id: int, role: str, expires_delta: timedelta = None) -> str:
    now = datetime.utcnow()
    if not expires_delta:
        expires_delta = timedelta(hours=1)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": now + expires_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "Authorization header required"}), 401
        data = decode_token(parts[1])
        if not data or data.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper
