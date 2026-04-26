from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..services.auth_service import AuthService
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password: return jsonify({"msg": "Email and password required"}), 400
    try:
        user = AuthService.register_user(email, password)
        return jsonify({"msg": "User created successfully", "role": user.role.value}), 201
    except ValueError as e: return jsonify({"msg": str(e)}), 400

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value, "email": user.email})
        return jsonify(access_token=access_token, role=user.role.value), 200
    return jsonify({"msg": "Bad email or password"}), 401
