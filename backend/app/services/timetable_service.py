"""
Timetable Retrieval Service: Fetches and formats scheduled timetable entries for users.
"""
from ..models import db, TimetableEntry, Schedule, Professor, StudentGroup, CourseInstance
from .auth_service import AuthService

class TimetableService:
    @staticmethod
    def get_active_schedule_for_user(role, user_id=None, email=None):
        """Retrieves the current active schedule filtered by user role and identity."""
        active_schedule = Schedule.query.filter_by(is_active=True).first()
        if not active_schedule: 
            return []

        base_query = TimetableEntry.query.filter_by(schedule_id=active_schedule.id)
        
        # Apply role-based filtering
        if role == 'FACULTY':
            professor = Professor.query.filter_by(user_id=user_id).first() or \
                        Professor.query.filter_by(email=email).first()
            if professor: 
                base_query = base_query.filter_by(instructor_id=professor.id)
            else: 
                return []
        
        elif role == 'STUDENT':
            group_name = AuthService.identify_group_by_email(email)
            group = StudentGroup.query.filter_by(name=group_name).first() or StudentGroup.query.first()
            if group: 
                base_query = base_query.filter_by(student_group_id=group.id)
            else: 
                return []

        entries = base_query.all()
        
        # Format for Frontend consumption
        formatted_entries = []
        for entry in entries:
            instance = CourseInstance.query.get(entry.course_instance_id)
            professor = Professor.query.get(entry.instructor_id)
            group = StudentGroup.query.get(entry.student_group_id)
            
            formatted_entries.append({
                "id": entry.id,
                "day": entry.day_of_week,
                "slot": entry.time_slot,
                "course": instance.course_id if instance else "Unknown",
                "room": entry.room.name if entry.room else "Unknown",
                "professor": professor.name if professor else "Unknown",
                "group": group.name if group else "Unknown",
                "type": instance.session_type if instance else "Unknown"
            })
        
        return formatted_entries
