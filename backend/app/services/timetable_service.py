"""
Timetable Retrieval Service: Fetches and formats scheduled timetable entries for users.
"""
from ..models import db, TimetableEntry, Schedule, Professor, StudentGroup, CourseInstance, Room
from .auth_service import AuthService

class TimetableService:
    @staticmethod
    def get_active_schedule_for_user(role, user_id=None, email=None, filters=None):
        """Retrieves the active schedule filtered by identity and custom criteria."""
        filters = filters or {}
        active_schedule = Schedule.query.filter_by(is_active=True).first()
        if not active_schedule: 
            return []

        base_query = TimetableEntry.query.filter_by(schedule_id=active_schedule.id)
        
        # 1. Role-based Scope
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
                # Include parent classes (Inheritance)
                group_ids = [group.id] + [p.id for p in group.parent_groups]
                base_query = base_query.filter(TimetableEntry.student_group_id.in_(group_ids))
            else: 
                return []

        # 2. Apply Custom Filters (Admin/Dashboard)
        group_filter = filters.get('group')
        if group_filter:
            target_group = StudentGroup.query.filter_by(name=group_filter).first()
            if target_group:
                # Aggregate IDs: Current + Parents + Children
                group_ids = {target_group.id}
                group_ids.update(p.id for p in target_group.parent_groups)
                group_ids.update(c.id for c in target_group.child_groups)
                base_query = base_query.filter(TimetableEntry.student_group_id.in_(list(group_ids)))

        room_filter = filters.get('room')
        if room_filter:
            base_query = base_query.join(Room).filter(Room.name == room_filter)

        prof_filter = filters.get('professor')
        if prof_filter:
            base_query = base_query.join(Professor).filter(Professor.name == prof_filter)

        course_filter = filters.get('course')
        if course_filter:
            base_query = base_query.join(CourseInstance).filter(CourseInstance.course_id == course_filter)

        year_filter = filters.get('year')
        if year_filter:
            # We want to find all groups that are named "Year X" OR have a parent named "Year X"
            # Since names are unique enough, we can find the parent group first
            year_tag = f"Year {year_filter}"
            parent_group = StudentGroup.query.filter(StudentGroup.name.ilike(f"%{year_tag}%")).first()
            if parent_group:
                # Find all children of this year group
                child_ids = [c.id for c in parent_group.child_groups]
                target_ids = [parent_group.id] + child_ids
                base_query = base_query.filter(TimetableEntry.student_group_id.in_(target_ids))
            else:
                # Fallback to direct name match if no parent group found
                base_query = base_query.join(StudentGroup).filter(StudentGroup.name.ilike(f"%{year_tag}%"))

        entries = base_query.all()
        
        # 3. Format Response
        return [{
            "id": e.id,
            "day": e.day_of_week,
            "slot": e.time_slot,
            "course": e.course_instance.course_id if e.course_instance else "N/A",
            "room": e.room.name if e.room else "N/A",
            "professor": e.instructor.name if e.instructor else "N/A",
            "group": e.student_grp.name if e.student_grp else "N/A",
            "type": e.course_instance.session_type if e.course_instance else "lecture"
        } for e in entries]
