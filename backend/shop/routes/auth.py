from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
from ..models import Users


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = Users.query.filter_by(username=data.get("username", "")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Bad credentials"}), 401

    claims = {"role": user.role}
    access_token = create_access_token(identity=user.user_id,
                                       additional_claims=claims,
                                       expires_delta=timedelta(hours=1))
    refresh_token = create_refresh_token(identity=user.user_id,
                                         additional_claims=claims,
                                         expires_delta=timedelta(days=7))

    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    claims = get_jwt()
    new_access = create_access_token(identity=uid, additional_claims={"role": claims.get("role")})
    return jsonify({"access_token": new_access}), 200


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({"msg": f"Hello, user {get_jwt_identity()}"}), 200
