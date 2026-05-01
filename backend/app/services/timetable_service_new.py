"""
Updated Timetable Service to use new CourseInstance schema
"""
from ..models import db, TimetableEntry, Schedule, Professor, StudentGroup, CourseInstance
from .auth_service import AuthService

class TimetableService:
    @staticmethod
    def get_active_timetable(role, user_id=None, email=None):
        """
        Get the active timetable entries for a user based on their role
        
        Args:
            role: User role (FACULTY, STUDENT, ADMIN)
            user_id: User ID (optional)
            email: User email (optional)
            
        Returns:
            List of timetable entry dicts
        """
        schedule = Schedule.query.filter_by(is_active=True).first()
        if not schedule:
            return []

        query = TimetableEntry.query.filter_by(schedule_id=schedule.id)
        
        if role == 'FACULTY':
            prof = Professor.query.filter_by(user_id=user_id).first()
            if not prof:
                prof = Professor.query.filter_by(email=email).first()
            
            if prof:
                query = query.filter_by(instructor_id=prof.id)
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
        
        # Format entries for response
        formatted_entries = []
        for e in entries:
            instance = CourseInstance.query.get(e.course_instance_id)
            prof = Professor.query.get(e.instructor_id)
            group = StudentGroup.query.get(e.student_group_id)
            
            formatted_entries.append({
                "id": e.id,
                "day": e.day_of_week,
                "slot": e.time_slot,
                "course": instance.course_id if instance else e.course_instance_id,
                "course_instance_id": e.course_instance_id,
                "room": e.room.name if e.room else "Unknown",
                "professor": prof.name if prof else "Unknown",
                "group": group.name if group else "Unknown",
                "type": instance.session_type if instance else "Unknown"
            })
        
        return formatted_entries
