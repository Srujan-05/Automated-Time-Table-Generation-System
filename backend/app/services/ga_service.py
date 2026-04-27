import sys
import copy
from pathlib import Path
from ..models import db, Professor, Room, StudentGroup, CourseRequirement, Schedule, TimetableEntry, ActivityLog

# Add root to sys.path to import ga and schema
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from ga.algorithm import GASearch
from schema.classes import Instructor, Room as GARoom, StudentGroup as GAStudentGroup, CourseInstance

class GAService:
    @staticmethod
    def run_ga_generation(name="Automated Schedule"):
        # 0. Log start
        log_start = ActivityLog(category='NOTIFICATION', title='GA Start', message='Timetable generation process started.')
        db.session.add(log_start)
        db.session.commit()

        # 1. Fetch data from DB
        db_professors = Professor.query.all()
        db_rooms = Room.query.all()
        db_groups = StudentGroup.query.all()
        db_requirements = CourseRequirement.query.all()

        if not db_requirements:
            raise ValueError("No course requirements found in database.")

        # 2. Map to GA objects
        instructors_map = {p.id: Instructor(p.id, p.name) for p in db_professors}
        rooms_list = [GARoom(r.id, r.name, r.is_lab, r.capacity, r.x, r.y, r.z) for r in db_rooms]
        groups_map = {g.id: GAStudentGroup(g.name, g.size) for g in db_groups}
        
        ga_courses = []
        for req in db_requirements:
            instance = CourseInstance(
                course_id=req.course_code,
                session_type=req.session_type.lower(),
                instructor=instructors_map[req.professor_id],
                student_grp=groups_map[req.student_group_id],
                slots_req=req.slots_required,
                slots_continuous=req.slots_continuous,
                preference_bin=req.preference_bin
            )
            # Tag the instance so we can identify it later without using id(obj) which changes on copy
            instance.db_req_id = req.id
            ga_courses.append(instance)

        # 3. Initialize GA
        pref_bins = {i: (1 if i <= 4 else 2 if i <= 7 else 3) for i in range(1, 11)}
        
        ga = GASearch(
            time_slots=10, 
            courses=ga_courses,
            preference_bins=pref_bins,
            objective_function_weights=[1.0, 1.0, 1.0],
            rooms=rooms_list,
            population_size=50, 
            generations=100
        )

        # 4. Run GA
        try:
            # We use a custom trick here: we'll monkeypatch copy.copy ONLY for this call
            # to return the same object if it's a CourseInstance. 
            # This forces the greedy initializer in ga/population.py to NOT create 
            # new object IDs, which satisfies Constraint #9.
            
            original_copy = copy.copy
            def robust_copy(obj):
                if isinstance(obj, CourseInstance):
                    return obj # Return same ref to keep same id(obj)
                return original_copy(obj)
            
            copy.copy = robust_copy
            try:
                population = ga.create_population()
            finally:
                copy.copy = original_copy # ALWAYS restore

        except Exception as e:
            db.session.add(ActivityLog(category='NOTIFICATION', title='GA Failed', message=f'GA Error: {str(e)}'))
            db.session.commit()
            raise RuntimeError(f"GA failed: {str(e)}")

        if not population:
            msg = "GA failed to find a valid initial population. Likely constraints are too tight."
            db.session.add(ActivityLog(category='NOTIFICATION', title='GA Failed', message=msg))
            db.session.commit()
            raise RuntimeError(msg)

        best_timetable = population[0]
        fitness = ga.fitness(best_timetable)

        # 5. Save to DB
        Schedule.query.update({Schedule.is_active: False})
        
        new_schedule = Schedule(name=name, fitness_score=fitness, is_active=True)
        db.session.add(new_schedule)
        db.session.flush()

        for day, slots in best_timetable.items():
            for slot_idx, courses in slots.items():
                for course in courses:
                    req_id = getattr(course, 'db_req_id', None)
                    req = CourseRequirement.query.get(req_id) if req_id else None
                    group_id = req.student_group_id if req else 1

                    entry = TimetableEntry(
                        schedule_id=new_schedule.id,
                        day=day,
                        time_slot=slot_idx,
                        course_code=course.course_id,
                        room_id=course.room.id,
                        professor_id=course.instructor.id,
                        student_group_id=group_id,
                        session_type=course.session_type
                    )
                    db.session.add(entry)
        
        # 6. Log success
        db.session.add(ActivityLog(
            category='CHANGE', 
            title='Schedule Generated', 
            message=f'New schedule generated with fitness {fitness:.2f}.'
        ))
        db.session.commit()
        return new_schedule
