import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..services.ingestion_service import IngestionService
from functools import wraps

ingestion_bp = Blueprint('ingestion', __name__)

def admin_required(f):
    """Decorator to restrict access to Admin role only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'ADMIN':
            return jsonify({"msg": "Admin privilege required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@ingestion_bp.route('/seed', methods=['POST'])
@jwt_required()
@admin_required
def trigger_system_seeding():
    """Seeds the database with initial institutional data."""
    try:
        from flask import current_app
        seed_path = os.path.join(current_app.instance_path, 'seed_data.json')
        if not os.path.exists(seed_path):
            # Fallback for validation/dev environments
            seed_path = os.path.join(current_app.instance_path, 'seed_data_mini.json')
            
        results = IngestionService.perform_initial_seeding(seed_path)
        return jsonify(results), 200
    except Exception as e: 
        return jsonify({"msg": str(e)}), 500

@ingestion_bp.route('/templates', methods=['GET'])
@jwt_required()
@admin_required
def download_templates():
    """Provides a ZIP archive of CSV templates for data ingestion."""
    import zipfile
    import io
    from flask import send_file, current_app
    
    template_dir = os.path.join(current_app.instance_path, 'templates')
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                zf.write(os.path.join(root, file), file)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='timetable_templates.zip'
    )

@ingestion_bp.route('/upload/<data_type>', methods=['POST'])
@jwt_required()
@admin_required
def upload_data_file(data_type):
    """Handles manual file uploads for bulk data ingestion."""
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    try:
        import pandas as pd
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file).to_dict(orient='records')
        elif file.filename.endswith('.json'):
            import json
            data = json.load(file)
        else:
            return jsonify({"msg": "Unsupported file format"}), 400

        if data_type == 'faculty':
            count = IngestionService.ingest_faculty_data(data)
        elif data_type == 'rooms':
            count = IngestionService.ingest_room_data(data)
        elif data_type == 'courses':
            count = IngestionService.ingest_course_data(data)
        else:
            return jsonify({"msg": "Invalid data type"}), 400

        return jsonify({"msg": f"Successfully ingested {count} records"}), 200
    except Exception as e: 
        return jsonify({"msg": str(e)}), 500
