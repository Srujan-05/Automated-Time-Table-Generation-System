from ..models import db, TimetableEntry, Schedule, Professor, StudentGroup
from .auth_service import AuthService

class TimetableService:
    @staticmethod
    def get_active_timetable(role, user_id=None, email=None):
        schedule = Schedule.query.filter_by(is_active=True).first()
        if not schedule:
            return []

        query = TimetableEntry.query.filter_by(schedule_id=schedule.id)
        
        if role == 'FACULTY':
            prof = Professor.query.filter_by(user_id=user_id).first()
            if not prof:
                prof = Professor.query.filter_by(email=email).first()
            
            if prof:
                query = query.filter_by(professor_id=prof.id)
            else:
                return []
        
        elif role == 'STUDENT':
            group_name = AuthService.get_group_from_email(email)
            group = StudentGroup.query.filter_by(name=group_name).first()
            
            if not group:
                # Debug/Fallback: try to find any group if the specific mapping fails
                group = StudentGroup.query.first()
            
            if group:
                query = query.filter_by(student_group_id=group.id)
            else:
                return []

        entries = query.all()
        return [
            {
                "id": e.id,
                "day": e.day,
                "slot": e.time_slot,
                "course": e.course_code,
                "room": e.room.name,
                "professor": db.session.get(Professor, e.professor_id).name,
                "group": db.session.get(StudentGroup, e.student_group_id).name,
                "type": e.session_type
            } for e in entries
        ]
