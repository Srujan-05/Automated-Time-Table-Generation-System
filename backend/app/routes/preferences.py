from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..services.preference_service import PreferenceService

preferences_bp = Blueprint('preferences', __name__)

@preferences_bp.route('/professors', methods=['GET'])
@jwt_required()
def list_professors():
    claims = get_jwt()
    if claims.get('role') != 'ADMIN':
        return jsonify({"msg": "Admin privilege required"}), 403
    return jsonify(PreferenceService.list_professors()), 200

@preferences_bp.route('/shift', methods=['GET'])
@jwt_required()
def get_shift():
    claims = get_jwt()
    role = claims.get('role')
    professor_id = request.args.get('professor_id')
    
    if role != 'ADMIN' and professor_id:
        return jsonify({"msg": "Admin privilege required to view other preferences"}), 403
        
    try:
        bin_id = PreferenceService.get_professor_preference(
            professor_id=int(professor_id) if professor_id else None,
            user_id=int(get_jwt_identity()),
            email=claims.get('email')
        )
        return jsonify({"bin_id": bin_id}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 404

@preferences_bp.route('/shift', methods=['POST'])
@jwt_required()
def update_shift():
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['FACULTY', 'ADMIN']:
        return jsonify({"msg": "Faculty privilege required"}), 403
    
    data = request.get_json()
    bin_id = data.get('bin_id')
    professor_id = data.get('professor_id')
    
    if role != 'ADMIN' and professor_id:
        return jsonify({"msg": "Admin privilege required to update other preferences"}), 403

    if bin_id not in [1, 2, 3]:
        return jsonify({"msg": "Invalid bin_id. Must be 1, 2, or 3"}), 400
        
    try:
        count = PreferenceService.update_professor_shift(
            bin_id=bin_id,
            professor_id=int(professor_id) if professor_id else None,
            user_id=int(get_jwt_identity()), 
            email=claims.get('email')
        )
        return jsonify({"msg": f"Updated preferences for {count} courses"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404
