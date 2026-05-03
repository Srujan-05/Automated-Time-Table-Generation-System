"""
Data Loader: Converts PostgreSQL database records to test_data.py class instances

This module loads data from the new database schema and reconstructs the class hierarchy
exactly as defined in test_data.py, including student group hierarchies.
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add project root to path to access test_data classes
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.test_data import (
    Instructor, Room, StudentGroup, Course, CourseInstance
)
from app.models import (
    Professor as DBProfessor,
    Room as DBRoom,
    StudentGroup as DBStudentGroup,
    Course as DBCourse,
    CourseInstance as DBCourseInstance
)


class DataLoader:
    """Load database data into test_data.py class structures"""
    
    @staticmethod
    def load_instructors(db_session: Session) -> List[Instructor]:
        """
        Load all instructors from database
        
        Returns:
            List of Instructor objects
        """
        db_instructors = db_session.query(DBProfessor).all()
        instructors = []
        
        for prof in db_instructors:
            instructor = Instructor(id=prof.id, name=prof.name)
            instructors.append(instructor)
        
        return instructors

    @staticmethod
    def load_rooms(db_session: Session) -> List[Room]:
        """
        Load all rooms from database
        
        Returns:
            List of Room objects
        """
        db_rooms = db_session.query(DBRoom).all()
        rooms = []
        
        for room in db_rooms:
            room_obj = Room(
                id=room.id,
                name=room.name,
                x=room.x,
                y=room.y,
                z=room.z,
                capacity=room.capacity,
                is_lab=room.is_lab,
                allowed_batches=room.allowed_batches
            )
            rooms.append(room_obj)
        
        return rooms

    @staticmethod
    def load_student_groups(db_session: Session) -> Dict[int, StudentGroup]:
        """
        Load all student groups with hierarchical structure from database
        
        The hierarchy is reconstructed by fetching parent_groups relationships
        
        Returns:
            Dict mapping ID to StudentGroup objects with proper hierarchy
        """
        db_groups = db_session.query(DBStudentGroup).all()
        groups_map = {}
        
        # First pass: Create all StudentGroup objects without hierarchy
        for db_group in db_groups:
            sg = StudentGroup(
                name=db_group.name,
                size=db_group.size,
                super_groups=[]  # Will populate in second pass
            )
            groups_map[db_group.id] = sg
        
        # Second pass: Establish parent-child relationships
        for db_group in db_groups:
            if db_group.parent_groups:
                sg = groups_map[db_group.id]
                # Add all parent groups to super_groups
                for parent_db_group in db_group.parent_groups:
                    if parent_db_group.id in groups_map:
                        sg.super_groups.append(groups_map[parent_db_group.id])
        
        return groups_map

    @staticmethod
    def load_courses(db_session: Session) -> List[Course]:
        """
        Load all base courses (templates) from database
        
        Returns:
            List of Course objects
        """
        db_courses = db_session.query(DBCourse).all()
        courses = []
        
        for course in db_courses:
            course_obj = Course(
                course_id=course.course_id,
                name=course.name,
                total_credits=course.total_credits,
                lectures=course.lectures_per_week,
                tutorials=course.tutorials_per_week,
                practicals=course.practicals_per_week
            )
            courses.append(course_obj)
        
        return courses

    @staticmethod
    def load_course_instances(
        db_session: Session,
        instructors_map: Dict[int, Instructor],
        rooms_map: Dict[int, Room],
        groups_map: Dict[int, StudentGroup]
    ) -> List[CourseInstance]:
        """
        Load all course instances from database
        
        Args:
            db_session: SQLAlchemy session
            instructors_map: Dict mapping instructor IDs to Instructor objects
            rooms_map: Dict mapping room IDs to Room objects
            groups_map: Dict mapping group IDs to StudentGroup objects
            
        Returns:
            List of CourseInstance objects
        """
        db_instances = db_session.query(DBCourseInstance).all()
        instances = []
        
        for db_instance in db_instances:
            # Get related objects
            instructor = instructors_map.get(db_instance.instructor_id)
            room = rooms_map.get(db_instance.room_id)
            student_grp = groups_map.get(db_instance.student_group_id)
            
            if not (instructor and room and student_grp):
                # Skip if any related object is missing
                continue
            
            instance = CourseInstance(
                id=db_instance.id,
                course_id=db_instance.course_id,
                session_type=db_instance.session_type,
                instructor=instructor,
                room=room,
                student_grp=student_grp,
                slots_req=db_instance.slots_required,
                slots_continuous=db_instance.slots_continuous,
                preference_bin=db_instance.preference_bin,
                lecture_consecutive=db_instance.lecture_consecutive,
                parallelizable_id=db_instance.parallelizable_id
            )
            # Set course_credits if available
            if db_instance.course_credits:
                instance.course_credits = db_instance.course_credits
            
            instances.append(instance)
        
        return instances

    @staticmethod
    def load_from_database(db_session: Session) -> Dict[str, Any]:
        """
        Load all data from database and reconstruct test_data.py structures
        
        This is the main entry point. Returns a dict with same structure as
        test_data.create_test_data()
        
        Args:
            db_session: SQLAlchemy session connected to the database
            
        Returns:
            Dict with keys:
                - 'instructors': List[Instructor]
                - 'rooms': List[Room]
                - 'student_groups': List[StudentGroup]
                - 'base_courses': List[Course]
                - 'courses': List[CourseInstance]
                - 'preference_bins': Dict mapping slot → bin
                - 'objective_function_weights': List of weights
                - 'time_slots': Dict mapping day → total slots
        """
        # Load individual components
        instructors = DataLoader.load_instructors(db_session)
        rooms = DataLoader.load_rooms(db_session)
        groups_map = DataLoader.load_student_groups(db_session)
        base_courses = DataLoader.load_courses(db_session)
        
        # Create maps for easier lookup
        instructors_map = {instr.id: instr for instr in instructors}
        rooms_map = {room.id: room for room in rooms}
        
        # Load course instances
        course_instances = DataLoader.load_course_instances(
            db_session,
            instructors_map,
            rooms_map,
            groups_map
        )
        
        # Return in same format as test_data.create_test_data()
        return {
            'instructors': instructors,
            'rooms': rooms,
            'student_groups': list(groups_map.values()),
            'base_courses': base_courses,
            'courses': course_instances,
            'preference_bins': {
                1: 1, 2: 1, 3: 1,      # Slots 1-3 = morning (bin 1)
                4: 2, 5: 2, 6: 2,      # Slots 4-6 = noon (bin 2)
                7: 3, 8: 3, 9: 3       # Slots 7-9 = evening (bin 3)
            },
            'objective_function_weights': [1.0, 0.5, 0.8],
            'time_slots': {
                'Monday': 9,
                'Tuesday': 9,
                'Wednesday': 5,
                'Thursday': 9,
                'Friday': 9
            }
        }


# Convenience function for Flask integration
def load_test_data_from_db(app) -> Dict[str, Any]:
    """
    Load test data from database using Flask app context
    
    Args:
        app: Flask application instance
        
    Returns:
        Dict with test data structure
        
    Example:
        from flask import current_app
        from app.data_loader import load_test_data_from_db
        
        with app.app_context():
            test_data = load_test_data_from_db(app)
    """
    from app import db
    from flask import current_app
    
    with app.app_context():
        db_session = db.session
        return DataLoader.load_from_database(db_session)


if __name__ == "__main__":
    """
    Example usage:
    
    from app import create_app, db
    from app.data_loader import DataLoader
    
    app = create_app()
    with app.app_context():
        data = DataLoader.load_from_database(db.session)
        print(f"Loaded {len(data['instructors'])} instructors")
        print(f"Loaded {len(data['rooms'])} rooms")
        print(f"Loaded {len(data['courses'])} course instances")
    """
    pass
