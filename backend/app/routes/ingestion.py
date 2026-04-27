import io
import zipfile
import os
import pandas as pd
import json
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from flask_jwt_extended import jwt_required, get_jwt
from ..services.ingestion_service import IngestionService
from functools import wraps

ingestion_bp = Blueprint('ingestion', __name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'ADMIN': return jsonify({"msg": "Admin privilege required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@ingestion_bp.route('/template/<filename>', methods=['GET'])
def download_template(filename):
    if not filename.endswith('.csv'):
        return jsonify({"msg": "Only .csv templates allowed"}), 400
    from flask import current_app
    return send_from_directory(current_app.instance_path, filename, as_attachment=True)

@ingestion_bp.route('/templates', methods=['GET'])
def download_all_templates():
    files = ['faculties.csv', 'rooms.csv', 'courses.csv']
    from flask import current_app
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in files:
            path = os.path.join(current_app.instance_path, filename)
            if not os.path.exists(path):
                # Fallback for development
                path = os.path.join(os.getcwd(), 'instance', filename)
                
            if os.path.exists(path):
                zf.write(path, filename)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='timetable_templates.zip'
    )

@ingestion_bp.route('/upload/<type>', methods=['POST'])
@jwt_required()
@admin_required
def upload_data(type):
    if 'file' not in request.files: return jsonify({"msg": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"msg": "No selected file"}), 400
    if file.filename.endswith('.csv'): data = pd.read_csv(file).to_dict(orient='records')
    elif file.filename.endswith('.json'): data = json.load(file)
    else: return jsonify({"msg": "Invalid file format"}), 400
    count = 0
    if type == 'faculties': count = IngestionService.process_faculties(data)
    elif type == 'rooms': count = IngestionService.process_rooms(data)
    elif type == 'courses': count = IngestionService.process_courses(data)
    return jsonify({"msg": f"Processed {count} records"}), 200

@ingestion_bp.route('/seed', methods=['POST'])
@jwt_required()
@admin_required
def seed():
    # Look for instance folder in current app path
    from flask import current_app
    seed_path = os.path.join(current_app.instance_path, 'seed_data.json')
    if not os.path.exists(seed_path):
        # Fallback to local path for tests
        seed_path = os.path.join(os.getcwd(), 'instance', 'seed_data.json')
        
    if not os.path.exists(seed_path):
        return jsonify({"msg": "Seed file not found"}), 404
    f, r, c = IngestionService.seed_initial_data(seed_path)
    return jsonify({"faculties": f, "rooms": r, "courses": c}), 200
