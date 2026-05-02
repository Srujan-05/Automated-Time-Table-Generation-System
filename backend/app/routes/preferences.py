from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..services.preference_service import PreferenceService

preferences_bp = Blueprint('preferences', __name__)

@preferences_bp.route('/professors', methods=['GET'])
@jwt_required()
def list_available_faculty():
    """Admin-only endpoint to list all faculty members."""
    claims = get_jwt()
    if claims.get('role') != 'ADMIN':
        return jsonify({"msg": "Admin privilege required"}), 403
    return jsonify(PreferenceService.get_all_faculty_profiles()), 200

@preferences_bp.route('/shift', methods=['GET'])
@jwt_required()
def get_current_shift_preference():
    """Retrieves the shift preference for the user or a target professor (Admin)."""
    claims = get_jwt()
    role = claims.get('role')
    target_professor_id = request.args.get('professor_id')
    
    if role != 'ADMIN' and target_professor_id:
        return jsonify({"msg": "Admin privilege required to view other preferences"}), 403
        
    try:
        bin_id = PreferenceService.fetch_instructor_preference(
            professor_id=int(target_professor_id) if target_professor_id else None,
            user_id=int(get_jwt_identity()),
            email=claims.get('email')
        )
        return jsonify({"bin_id": bin_id}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 404

@preferences_bp.route('/shift', methods=['POST'])
@jwt_required()
def update_shift_preference():
    """Updates the shift preference (morning/noon/evening) for an instructor."""
    claims = get_jwt()
    role = claims.get('role')
    if role not in ['FACULTY', 'ADMIN']:
        return jsonify({"msg": "Faculty privilege required"}), 403
    
    request_data = request.get_json()
    new_bin_id = request_data.get('bin_id')
    target_professor_id = request_data.get('professor_id')
    
    if role != 'ADMIN' and target_professor_id:
        return jsonify({"msg": "Admin privilege required to update other preferences"}), 403

    if new_bin_id not in [1, 2, 3]:
        return jsonify({"msg": "Invalid bin_id. Must be 1 (Morning), 2 (Noon), or 3 (Evening)"}), 400
        
    try:
        updated_count = PreferenceService.update_instructor_shift_preference(
            bin_id=new_bin_id,
            professor_id=int(target_professor_id) if target_professor_id else None,
            user_id=int(get_jwt_identity()), 
            email=claims.get('email')
        )
        return jsonify({"msg": f"Updated preferences for {updated_count} course instances"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404
