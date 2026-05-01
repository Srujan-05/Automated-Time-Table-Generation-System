"""
Updated GA Service to use new CourseInstance schema
"""
import sys
import copy
from pathlib import Path
from ..models import db, Professor, Room, StudentGroup, CourseInstance, Schedule, TimetableEntry, ActivityLog

# Add root to sys.path to import ga and schema
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from ga.algorithm import GASearch
from schema.classes import Instructor, Room as GARoom, StudentGroup as GAStudentGroup, CourseInstance as GAInstance

class GAService:
    @staticmethod
    def run_ga_generation(name="Automated Schedule"):
        """
        Run the Genetic Algorithm to generate a timetable using the new CourseInstance schema
        """
        # 0. Log start
        log_start = ActivityLog(category='NOTIFICATION', title='GA Start', message='Timetable generation process started.')
        db.session.add(log_start)
        db.session.commit()

        # 1. Fetch data from DB (new schema)
        db_professors = Professor.query.all()
        db_rooms = Room.query.all()
        db_groups = StudentGroup.query.all()
        db_instances = CourseInstance.query.all()

        if not db_instances:
            raise ValueError("No course instances found in database.")

        # 2. Map to GA objects
        instructors_map = {p.id: Instructor(p.id, p.name) for p in db_professors}
        rooms_list = [GARoom(r.id, r.name, r.is_lab, r.capacity, r.x, r.y, r.z) for r in db_rooms]
        groups_map = {g.id: GAStudentGroup(g.name, g.size) for g in db_groups}
        
        ga_courses = []
        for instance in db_instances:
            ga_instance = GAInstance(
                id=instance.id,
                course_id=instance.course_id,
                session_type=instance.session_type.lower(),
                instructor=instructors_map[instance.instructor_id],
                room=next((r for r in rooms_list if r.id == instance.room_id), None),
                student_grp=groups_map[instance.student_group_id],
                slots_req=instance.slots_required,
                slots_continuous=instance.slots_continuous,
                preference_bin=instance.preference_bin,
                lecture_consecutive=instance.lecture_consecutive,
                parallelizable_id=instance.parallelizable_id
            )
            # Tag the instance so we can identify it later
            ga_instance.db_instance_id = instance.id
            ga_courses.append(ga_instance)

        # 3. Initialize GA
        pref_bins = {i: (1 if i <= 3 else 2 if i <= 6 else 3) for i in range(1, 10)}
        
        ga = GASearch(
            time_slots=9,  # Example: 9 slots per day
            courses=ga_courses,
            preference_bins=pref_bins,
            objective_function_weights=[1.0, 1.0, 1.0],
            rooms=rooms_list,
            population_size=50, 
            generations=100
        )

        # 4. Run GA
        try:
            # Monkeypatch copy.copy to preserve CourseInstance references
            original_copy = copy.copy
            def robust_copy(obj):
                if isinstance(obj, GAInstance):
                    return obj  # Return same ref to keep same id(obj)
                return original_copy(obj)
            
            copy.copy = robust_copy
            try:
                population = ga.create_population()
            finally:
                copy.copy = original_copy  # ALWAYS restore

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
                    instance_id = getattr(course, 'db_instance_id', None)
                    instance = CourseInstance.query.get(instance_id) if instance_id else None
                    
                    if not instance:
                        continue

                    entry = TimetableEntry(
                        schedule_id=new_schedule.id,
                        day_of_week=day,
                        time_slot=slot_idx,
                        course_instance_id=instance.id,
                        room_id=instance.room_id,
                        instructor_id=instance.instructor_id,
                        student_group_id=instance.student_group_id
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
