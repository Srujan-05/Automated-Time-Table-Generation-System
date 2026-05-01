"""
Updated Ingestion Service to use new Course/CourseInstance schema
"""
import pandas as pd
import json
import re
from ..models import db, Professor, Room, StudentGroup, Course, CourseInstance

class IngestionService:
    @staticmethod
    def process_faculties(data):
        """Create Professor records from faculty data"""
        count = 0
        for item in data:
            if not Professor.query.filter_by(name=item['name']).first():
                # Correctly generate email or use provided
                clean_name = re.sub(r'^dr\.\s*', '', item['name'], flags=re.IGNORECASE).strip()
                email_prefix = clean_name.lower().replace(' ', '.')
                email = item.get('email', f"{email_prefix}@mahindrauniversity.edu.in")
                
                prof = Professor(name=item['name'], email=email)
                db.session.add(prof)
                count += 1
        db.session.commit()
        return count

    @staticmethod
    def process_rooms(data):
        """Create Room records from room data"""
        count = 0
        for item in data:
            if not Room.query.filter_by(name=item['name']).first():
                room = Room(
                    name=item['name'], 
                    is_lab=item.get('is_lab', False), 
                    capacity=item.get('capacity', 100),
                    x=item.get('x', 0.0),
                    y=item.get('y', 0.0),
                    z=item.get('z', 0.0)
                )
                db.session.add(room)
                count += 1
        db.session.commit()
        return count

    @staticmethod
    def process_courses(data):
        """
        Create Course and CourseInstance records from course data
        
        Data format expected:
        {
            'course_code': 'CS201',
            'course_name': 'Programming',
            'total_credits': 4,
            'session_type': 'lecture',
            'professor': 'Prof Kumar',
            'student_group': 'CSE-2025',
            'slots_required': 1,
            'slots_continuous': False,
            'preference_bin': 1,
            'room': 'Room 101',
            'parallelizable_id': None,
            'lecture_consecutive': False
        }
        """
        count = 0
        courses_created = {}  # Track created Course records
        
        for item in data:
            course_code = item.get('course_code')
            
            # Step 1: Create Course if not exists
            if course_code not in courses_created and not Course.query.filter_by(course_id=course_code).first():
                course = Course(
                    course_id=course_code,
                    name=item.get('course_name', course_code),
                    total_credits=item.get('total_credits', 3),
                    lectures_per_week=item.get('lectures_per_week', 0),
                    tutorials_per_week=item.get('tutorials_per_week', 0),
                    practicals_per_week=item.get('practicals_per_week', 0)
                )
                db.session.add(course)
                db.session.flush()
                courses_created[course_code] = course.id
            
            # Step 2: Resolve references (Professor, Room, StudentGroup)
            prof = Professor.query.filter_by(name=item.get('professor')).first()
            if not prof:
                continue
            
            room = Room.query.filter_by(name=item.get('room')).first()
            if not room:
                # Use first available room or create default
                room = Room.query.first()
                if not room:
                    continue
            
            group = StudentGroup.query.filter_by(name=item.get('student_group')).first()
            if not group:
                # Create StudentGroup if doesn't exist
                group = StudentGroup(name=item.get('student_group'), size=item.get('group_size', 80))
                db.session.add(group)
                db.session.flush()
            
            # Step 3: Create CourseInstance
            instance = CourseInstance(
                course_id=course_code,
                session_type=item.get('session_type', 'lecture').lower(),
                instructor_id=prof.id,
                room_id=room.id,
                student_group_id=group.id,
                slots_required=item.get('slots_required', 1),
                slots_continuous=item.get('slots_continuous', False),
                preference_bin=item.get('preference_bin', 1),
                lecture_consecutive=item.get('lecture_consecutive', False),
                parallelizable_id=item.get('parallelizable_id'),
                course_credits=item.get('course_credits')
            )
            db.session.add(instance)
            count += 1
        
        db.session.commit()
        return count

    @staticmethod
    def seed_initial_data(seed_json_path):
        """
        Load initial seed data from JSON file
        Expected structure:
        {
            'faculties': [...],
            'rooms': [...],
            'courses': [...],
            'student_groups': [...]
        }
        """
        with open(seed_json_path, 'r') as f:
            data = json.load(f)
        
        # Process faculties
        f_count = IngestionService.process_faculties(data.get('faculties', []))
        
        # Process rooms
        r_count = IngestionService.process_rooms(data.get('rooms', []))
        
        # Process student groups
        for g in data.get('student_groups', []):
            if not StudentGroup.query.filter_by(name=g['name']).first():
                sg = StudentGroup(
                    name=g['name'], 
                    size=g.get('size', 80),
                    level=g.get('level', 'batch')
                )
                db.session.add(sg)
        db.session.commit()
        
        # Process courses (which creates both Course and CourseInstance)
        c_count = IngestionService.process_courses(data.get('courses', []))
        
        return {
            'faculties': f_count,
            'rooms': r_count,
            'courses': c_count,
            'student_groups': len(data.get('student_groups', []))
        }
