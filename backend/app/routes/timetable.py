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
    """Returns the active schedule entries for the authenticated user."""
    claims = get_jwt()
    role, email = claims.get('role'), claims.get('email')
    user_id = get_jwt_identity()
    
    group_filter = request.args.get('group')
    entries = TimetableService.get_active_schedule_for_user(
        role, 
        int(user_id) if user_id else None, 
        email
    )
    
    if group_filter: 
        entries = [e for e in entries if e['group'] == group_filter]
        
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

    # Determine system status
    active_schedule = Schedule.query.filter_by(is_active=True).first()
    stats_package = {
        "active_schedule": active_schedule is not None,
        "activities": [],
        "upcoming": []
    }

    # Retrieve recent activity logs
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    stats_package["activities"] = [
        {
            "id": log.id, "category": log.category, "title": log.title,
            "message": log.message, "time": log.created_at.isoformat()
        } for log in recent_logs
    ]

    # Calculate role-based metrics
    if role == 'ADMIN':
        stats_package.update({
            "primary": {"label": "Total Instances", "value": CourseInstance.query.count()},
            "secondary": {"label": "Active Faculty", "value": Professor.query.count()},
            "tertiary": {"label": "Total Rooms", "value": Room.query.count()},
            "quaternary": {"label": "Global Conflicts", "value": 0 if stats_package["active_schedule"] else "N/A"},
            "requirements": CourseInstance.query.count(), # UI Legacy Compatibility
            "professors": Professor.query.count()
        })
    
    elif role == 'FACULTY':
        professor = Professor.query.filter_by(user_id=user_id).first() or \
                    Professor.query.filter_by(email=email).first()
        if professor:
            assigned_instances = CourseInstance.query.filter_by(instructor_id=professor.id).all()
            total_hours = sum(inst.slots_required for inst in assigned_instances)
            
            # Determine primary preference
            pref_bin = assigned_instances[0].preference_bin if assigned_instances else 1
            pref_label = {1: "Morning", 2: "Afternoon", 3: "Evening"}.get(pref_bin, "Morning")
            
            stats_package.update({
                "primary": {"label": "My Courses", "value": len(set(i.course_id for i in assigned_instances))},
                "secondary": {"label": "Weekly Hours", "value": total_hours},
                "tertiary": {"label": "Student Groups", "value": len(set(i.student_group_id for i in assigned_instances))},
                "quaternary": {"label": "My Preference", "value": pref_label},
                "requirements": len(assigned_instances),
                "professors": 1
            })
    
    elif role == 'STUDENT':
        group_name = AuthService.identify_group_by_email(email)
        group = StudentGroup.query.filter_by(name=group_name).first() or StudentGroup.query.first()
            
        if group:
            enrolled_instances = CourseInstance.query.filter_by(student_group_id=group.id).all()
            distinct_rooms = 0
            if active_schedule:
                distinct_rooms = db.session.query(db.func.count(db.distinct(TimetableEntry.room_id))).filter(
                    TimetableEntry.student_group_id == group.id,
                    TimetableEntry.schedule_id == active_schedule.id
                ).scalar() or 0

            stats_package.update({
                "primary": {"label": "Enrolled Courses", "value": len(set(i.course_id for i in enrolled_instances))},
                "secondary": {"label": "Active Rooms", "value": distinct_rooms},
                "tertiary": {"label": "Total Professors", "value": len(set(i.instructor_id for i in enrolled_instances))},
                "quaternary": {"label": "My Group", "value": group.name},
                "requirements": len(enrolled_instances),
                "professors": len(set(i.instructor_id for i in enrolled_instances))
            })

    # Fetch next scheduled sessions
    stats_package["upcoming"] = TimetableService.get_active_schedule_for_user(
        role, 
        int(user_id) if user_id else None, 
        email
    )[:6]

    return jsonify(stats_package), 200

@timetable_bp.route('/export', methods=['GET'])
@jwt_required()
def export_timetable_csv():
    """Generates and returns a CSV export of the current active schedule."""
    import csv
    import io
    from flask import Response
    from ..models import TimetableEntry, CourseInstance, Professor, Room, StudentGroup

    try:
        entries = TimetableEntry.query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Day', 'Slot', 'Course', 'Professor', 'Room', 'Student Group', 'Type'])
        
        for e in entries:
            # Safely fetch relationships
            prof_name = e.course_instance.professor.name if e.course_instance and e.course_instance.professor else 'N/A'
            room_name = e.room.name if e.room else 'N/A'
            group_name = e.student_group.name if e.student_group else 'N/A'
            course_id = e.course_instance.course_id if e.course_instance else 'Unknown'
            session_type = e.course_instance.session_type if e.course_instance else 'lecture'
            
            writer.writerow([
                e.id,
                e.day_of_week,
                e.time_slot,
                course_id,
                prof_name,
                room_name,
                group_name,
                session_type
            ])
            
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=timetable_export.csv"}
        )
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@timetable_bp.route('/generate', methods=['POST'])
@jwt_required()
@admin_required
def trigger_schedule_generation():
    """Initiates the GA-based timetable optimization process."""
    try:
        new_schedule = SchedulingService.generate_optimized_schedule()
        return jsonify({
            "msg": "Schedule generated successfully", 
            "schedule_id": new_schedule.id, 
            "fitness": new_schedule.fitness_score
        }), 201
    except Exception as e: 
        return jsonify({"msg": str(e)}), 500
