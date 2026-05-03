from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..services.timetable_service import TimetableService
from ..services.scheduling_service import SchedulingService
from .ingestion import admin_required
from ..extensions import db

timetable_bp = Blueprint('timetable', __name__)

@timetable_bp.route('', methods=['GET'])
@jwt_required()
def fetch_timetable_data():
    """Returns the active schedule entries with multi-faceted filtering."""
    claims = get_jwt()
    role, email = claims.get('role'), claims.get('email')
    user_id = get_jwt_identity()
    
    filters = {
        'group': request.args.get('group'),
        'year': request.args.get('year'),
        'professor': request.args.get('professor'),
        'room': request.args.get('room'),
        'course': request.args.get('course')
    }
    
    entries = TimetableService.get_active_schedule_for_user(
        role, 
        int(user_id) if user_id else None, 
        email,
        filters=filters
    )
        
    return jsonify(entries), 200

@timetable_bp.route('/stats', methods=['GET'])
@jwt_required()
def fetch_dashboard_statistics():
    """Compiles role-specific statistics for the user dashboard."""
    from ..models import Professor, Room, CourseInstance, Schedule, ActivityLog, StudentGroup, TimetableEntry
    from ..services.auth_service import AuthService
    
    claims = get_jwt()
    role, email = claims.get('role'), claims.get('email')
    user_id = get_jwt_identity()

    active_schedule = Schedule.query.filter_by(is_active=True).first()
    stats_package = {
        "active_schedule": active_schedule is not None,
        "activities": [],
        "upcoming": []
    }

    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    stats_package["activities"] = [
        {
            "id": log.id, "category": log.category, "title": log.title,
            "message": log.message, "time": log.created_at.isoformat()
        } for log in recent_logs
    ]

    if role == 'ADMIN':
        stats_package.update({
            "primary": {"label": "Total Instances", "value": CourseInstance.query.count()},
            "secondary": {"label": "Active Faculty", "value": Professor.query.count()},
            "tertiary": {"label": "Total Rooms", "value": Room.query.count()},
            "quaternary": {"label": "Active Schedule", "value": active_schedule.name if active_schedule else "None"},
            "requirements": CourseInstance.query.count(),
            "professors": Professor.query.count()
        })
    
    elif role == 'FACULTY':
        professor = Professor.query.filter_by(user_id=user_id).first() or \
                    Professor.query.filter_by(email=email).first()
        if professor:
            assigned_instances = CourseInstance.query.filter_by(instructor_id=professor.id).all()
            stats_package.update({
                "primary": {"label": "My Courses", "value": len(set(i.course_id for i in assigned_instances))},
                "secondary": {"label": "Weekly Load", "value": f"{len(assigned_instances)} hrs"},
                "tertiary": {"label": "Student Groups", "value": len(set(i.student_group_id for i in assigned_instances))},
                "quaternary": {"label": "Status", "value": "Profile Active"},
                "requirements": len(assigned_instances),
                "professors": 1
            })
    
    elif role == 'STUDENT':
        group_name = AuthService.identify_group_by_email(email)
        group = StudentGroup.query.filter_by(name=group_name).first() or StudentGroup.query.first()
            
        if group:
            stats_package.update({
                "primary": {"label": "My Courses", "value": CourseInstance.query.filter_by(student_group_id=group.id).count()},
                "secondary": {"label": "My Group", "value": group.name},
                "tertiary": {"label": "Status", "value": "Enrolled"},
                "quaternary": {"label": "Schedule", "value": "Active" if active_schedule else "Pending"},
                "requirements": 0,
                "professors": 0
            })

    stats_package["upcoming"] = TimetableService.get_active_schedule_for_user(role, int(user_id) if user_id else None, email)[:6]
    return jsonify(stats_package), 200

@timetable_bp.route('/export', methods=['GET'])
@jwt_required()
def export_timetable_csv():
    """Generates and returns a CSV export of the current active schedule."""
    import csv
    import io
    from flask import Response
    from ..models import TimetableEntry

    try:
        entries = TimetableEntry.query.all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Day', 'Slot', 'Course', 'Professor', 'Room', 'Student Group', 'Type'])
        
        for e in entries:
            writer.writerow([
                e.id, e.day_of_week, e.time_slot, e.course_instance.course_id,
                e.instructor.name, e.room.name, e.student_grp.name, e.course_instance.session_type
            ])
            
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=timetable_export.csv"}
        )
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@timetable_bp.route('/rooms', methods=['GET'])
@jwt_required()
def list_rooms():
    """Returns a list of all rooms with optional detailed information."""
    from ..models import Room
    
    # Check if detail parameter is passed for detailed room info
    detailed = request.args.get('detailed', 'false').lower() == 'true'
    rooms = Room.query.order_by(Room.name).all()
    
    if detailed:
        return jsonify([{
            'id': r.id,
            'name': r.name,
            'is_lab': r.is_lab,
            'capacity': r.capacity,
            'allowed_batches': r.allowed_batches,
            'x': r.x,
            'y': r.y,
            'z': r.z
        } for r in rooms]), 200
    else:
        return jsonify([r.name for r in rooms]), 200

@timetable_bp.route('/courses', methods=['GET'])
@jwt_required()
def list_courses():
    """Returns a simple list of all unique course IDs."""
    from ..models import Course
    courses = Course.query.order_by(Course.course_id).all()
    return jsonify([c.course_id for c in courses]), 200

@timetable_bp.route('/professors', methods=['GET'])
@jwt_required()
def list_professors():
    """Returns a simple list of all professor names."""
    from ..models import Professor
    profs = Professor.query.order_by(Professor.name).all()
    return jsonify([p.name for p in profs]), 200

@timetable_bp.route('/groups', methods=['GET'])
@jwt_required()
def list_groups():
    """Returns all unique student group names."""
    from ..models import StudentGroup
    groups = StudentGroup.query.order_by(StudentGroup.name).all()
    return jsonify([g.name for g in groups]), 200

@timetable_bp.route('/search', methods=['GET'])
@jwt_required()
def search_entities():
    """Returns a list of searchable items (profs, courses, rooms) for the UI combobox."""
    from ..models import Professor, Room, Course
    
    query = request.args.get('q', '').lower()
    results = []

    # Professors
    profs = Professor.query.filter(Professor.name.ilike(f'%{query}%')).limit(5).all()
    for p in profs:
        results.append({"id": p.id, "label": p.name, "type": "professor", "value": p.name})

    # Courses
    courses = Course.query.filter(Course.course_id.ilike(f'%{query}%')).limit(5).all()
    for c in courses:
        results.append({"id": c.id, "label": c.course_id, "type": "course", "value": c.course_id})

    # Rooms
    rooms = Room.query.filter(Room.name.ilike(f'%{query}%')).limit(5).all()
    for r in rooms:
        results.append({"id": r.id, "label": r.name, "type": "room", "value": r.name})

    return jsonify(results), 200

@timetable_bp.route('/generate', methods=['POST'])
@jwt_required()
@admin_required
def trigger_schedule_generation():
    """Initiates the GA-based timetable optimization process with dynamic config."""
    try:
        config = request.get_json(force=True, silent=True) or {}
        new_schedule = SchedulingService.generate_optimized_schedule(config)
        return jsonify({
            "msg": "Schedule generated successfully", 
            "schedule_id": new_schedule.id, 
            "fitness": new_schedule.fitness_score
        }), 201
    except Exception as e: 
        return jsonify({"msg": str(e)}), 500
