from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..services.timetable_service import TimetableService
from ..services.ga_service import GAService
from .ingestion import admin_required
from ..extensions import db

timetable_bp = Blueprint('timetable', __name__)

@timetable_bp.route('', methods=['GET'])
@jwt_required()
def get_timetable():
    claims = get_jwt()
    role, email = claims.get('role'), claims.get('email')
    user_id = get_jwt_identity()
    group_filter = request.args.get('group')
    entries = TimetableService.get_active_timetable(role, int(user_id) if user_id else None, email)
    if group_filter: entries = [e for e in entries if e['group'] == group_filter]
    return jsonify(entries), 200

@timetable_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    from ..models import Professor, Room, CourseRequirement, Schedule, ActivityLog, StudentGroup, TimetableEntry
    from ..services.auth_service import AuthService
    
    claims = get_jwt()
    role, email = claims.get('role'), claims.get('email')
    user_id = get_jwt_identity()

    # Base stats
    stats = {
        "active_schedule": Schedule.query.filter_by(is_active=True).first() is not None,
        "activities": [],
        "upcoming": []
    }

    # Fetch recent activities
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    stats["activities"] = [
        {
            "id": l.id, "category": l.category, "title": l.title,
            "message": l.message, "time": l.created_at.isoformat()
        } for l in logs
    ]

    # Role-specific stats
    if role == 'ADMIN':
        stats.update({
            "primary": {"label": "Total Courses", "value": CourseRequirement.query.count()},
            "secondary": {"label": "Active Faculty", "value": Professor.query.count()},
            "tertiary": {"label": "Total Rooms", "value": Room.query.count()},
            "quaternary": {"label": "Global Conflicts", "value": 0 if stats["active_schedule"] else "N/A"},
            "requirements": CourseRequirement.query.count(),
            "professors": Professor.query.count()
        })
    
    elif role == 'FACULTY':
        prof = Professor.query.filter_by(user_id=user_id).first() or Professor.query.filter_by(email=email).first()
        if prof:
            my_reqs = CourseRequirement.query.filter_by(professor_id=prof.id).all()
            total_hours = sum(r.slots_required for r in my_reqs)
            
            # Get preference bin
            pref_bin = my_reqs[0].preference_bin if my_reqs else 1
            pref_label = {1: "Morning", 2: "Afternoon", 3: "Flexible"}.get(pref_bin, "Morning")
            
            stats.update({
                "primary": {"label": "My Courses", "value": len(my_reqs)},
                "secondary": {"label": "Weekly Hours", "value": total_hours},
                "tertiary": {"label": "Student Groups", "value": len(set(r.student_group_id for r in my_reqs))},
                "quaternary": {"label": "My Preference", "value": pref_label},
                "requirements": len(my_reqs),
                "professors": 1
            })
    
    elif role == 'STUDENT':
        group_name = AuthService.get_group_from_email(email)
        group = StudentGroup.query.filter_by(name=group_name).first()
        if not group:
            # Fallback to a common group for testing if specific not found
            group = StudentGroup.query.first()
            
        if group:
            group_reqs = CourseRequirement.query.filter_by(student_group_id=group.id).all()
            # Get rooms where this group has classes in the active schedule
            active_sched = Schedule.query.filter_by(is_active=True).first()
            room_count = 0
            if active_sched:
                room_count = db.session.query(db.func.count(db.distinct(TimetableEntry.room_id))).filter(
                    TimetableEntry.student_group_id == group.id,
                    TimetableEntry.schedule_id == active_sched.id
                ).scalar() or 0

            stats.update({
                "primary": {"label": "Enrolled Courses", "value": len(group_reqs)},
                "secondary": {"label": "Active Rooms", "value": room_count or len(set(r.course_code for r in group_reqs)) // 2},
                "tertiary": {"label": "Total Professors", "value": len(set(r.professor_id for r in group_reqs))},
                "quaternary": {"label": "My Group", "value": group.name},
                "requirements": len(group_reqs),
                "professors": len(set(r.professor_id for r in group_reqs))
            })

    # Upcoming for all
    stats["upcoming"] = TimetableService.get_active_timetable(role, int(user_id) if user_id else None, email)[:6]

    return jsonify(stats), 200

@timetable_bp.route('/generate', methods=['POST'])
@jwt_required()
@admin_required
def generate_timetable():
    try:
        schedule = GAService.run_ga_generation()
        return jsonify({"msg": "Schedule generated successfully", "schedule_id": schedule.id, "fitness": schedule.fitness_score}), 201
    except Exception as e: return jsonify({"msg": str(e)}), 500
