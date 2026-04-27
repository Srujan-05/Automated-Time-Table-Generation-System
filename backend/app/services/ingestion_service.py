import pandas as pd
import json
import re
from ..models import db, Professor, Room, StudentGroup, CourseRequirement

class IngestionService:
    @staticmethod
    def process_faculties(data):
        count = 0
        for item in data:
            if not Professor.query.filter_by(name=item['name']).first():
                # Correctly generate dummy email by stripping "Dr. " prefix
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
        count = 0
        for item in data:
            if not Room.query.filter_by(name=item['name']).first():
                room = Room(
                    name=item['name'], 
                    is_lab=item.get('is_lab', False), 
                    capacity=item.get('capacity', 100)
                )
                db.session.add(room)
                count += 1
        db.session.commit()
        return count

    @staticmethod
    def process_courses(data):
        count = 0
        for item in data:
            # Resolve Professor
            prof = Professor.query.filter_by(name=item['professor']).first()
            if not prof: continue
            
            # Resolve Group
            group = StudentGroup.query.filter_by(name=item['student_group']).first()
            if not group:
                group = StudentGroup(name=item['student_group'], size=80)
                db.session.add(group)
                db.session.flush()

            req = CourseRequirement(
                course_code=item['course_code'],
                session_type=item['session_type'],
                professor_id=prof.id,
                student_group_id=group.id,
                slots_required=item.get('slots_required', 1),
                slots_continuous=item.get('slots_continuous', False),
                preference_bin=item.get('preference_bin', 1)
            )
            db.session.add(req)
            count += 1
        db.session.commit()
        return count

    @staticmethod
    def seed_initial_data(seed_json_path):
        with open(seed_json_path, 'r') as f:
            data = json.load(f)
        
        f_count = IngestionService.process_faculties(data['faculties'])
        r_count = IngestionService.process_rooms(data['rooms'])
        
        # Student groups
        for g in data['student_groups']:
            if not StudentGroup.query.filter_by(name=g['name']).first():
                db.session.add(StudentGroup(name=g['name'], size=g['size']))
        db.session.commit()
        
        c_count = IngestionService.process_courses(data['course_requirements'])
        return f_count, r_count, c_count
