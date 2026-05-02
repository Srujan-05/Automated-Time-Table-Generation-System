import json
import re
from ..models import db, Professor, Room, StudentGroup, Course, CourseInstance

class IngestionService:
    @staticmethod
    def ingest_faculty_data(faculty_list):
        added_count = 0
        for item in faculty_list:
            if not Professor.query.filter_by(name=item['name']).first():
                clean_name = re.sub(r'^dr\.\s*', '', item['name'], flags=re.IGNORECASE).strip()
                email = item.get('email', f"{clean_name.lower().replace(' ', '.')}@mahindrauniversity.edu.in")
                db.session.add(Professor(name=item['name'], email=email))
                added_count += 1
        db.session.commit()
        return added_count

    @staticmethod
    def ingest_room_data(room_list):
        added_count = 0
        for item in room_list:
            if not Room.query.filter_by(name=item['name']).first():
                db.session.add(Room(
                    name=item['name'], 
                    is_lab=item.get('is_lab', False), 
                    capacity=item.get('capacity', 100)
                ))
                added_count += 1
        db.session.commit()
        return added_count

    @staticmethod
    def ingest_course_data(course_list):
        added_count = 0
        for item in course_list:
            code = item['course_code']
            if not Course.query.filter_by(course_id=code).first():
                db.session.add(Course(course_id=code, name=item.get('course_name', code), total_credits=item.get('total_credits', 3)))
                db.session.flush()
            
            prof = Professor.query.filter_by(name=item['professor']).first() or \
                   Professor(name=item['professor'], email=f"{item['professor'].lower().replace(' ', '.')}@mahindrauniversity.edu.in")
            if prof.id is None: db.session.add(prof); db.session.flush()

            room = Room.query.filter_by(name=item['room']).first() or Room(name=item['room'], capacity=100)
            if room.id is None: db.session.add(room); db.session.flush()

            group = StudentGroup.query.filter_by(name=item['student_group']).first() or StudentGroup(name=item['student_group'], size=80)
            if group.id is None: db.session.add(group); db.session.flush()

            db.session.add(CourseInstance(
                course_id=code,
                session_type=item.get('session_type', 'lecture').lower(),
                instructor_id=prof.id,
                room_id=room.id,
                student_group_id=group.id,
                slots_required=item.get('slots_required', 1),
                slots_continuous=item.get('slots_continuous', False),
                preference_bin=item.get('preference_bin', 1)
            ))
            added_count += 1
        
        db.session.commit()
        return added_count

    @staticmethod
    def perform_initial_seeding(seed_json_path):
        with open(seed_json_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            c_count = IngestionService.ingest_course_data(data)
        else:
            IngestionService.ingest_faculty_data(data.get('professors', []))
            IngestionService.ingest_room_data(data.get('rooms', []))
            c_count = IngestionService.ingest_course_data(data.get('courses', []))

        return {
            'professors_added': Professor.query.count(),
            'rooms_added': Room.query.count(),
            'instances_created': c_count,
            'groups_found': StudentGroup.query.count()
        }
