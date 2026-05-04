"""
Scheduling Service: Orchestrates the Genetic Algorithm engine for timetable generation.
"""
import sys
from pathlib import Path
from ..models import db, Professor, Room, StudentGroup, CourseInstance, Schedule, TimetableEntry, ActivityLog

# Add root to sys.path to import ga and schema modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ga.algorithm import GASearch
from schema.classes import Instructor, Room as GARoom, StudentGroup as GAStudentGroup, CourseInstance as GAInstance

class SchedulingService:
    @staticmethod
    def generate_optimized_schedule(config=None):
        """Fetches data, runs the GA engine, and persists the best result."""
        config = config or {}
        
        # Dynamic Parameters from UI
        time_slots = int(config.get('slots', 10))
        population_size = int(config.get('population_size', 50))
        max_gens = int(config.get('max_generations', 100))
        min_gens = int(config.get('min_generations', 10))
        schedule_name = config.get('name', f"Schedule ({time_slots} slots)")

        db.session.add(ActivityLog(category='NOTIFICATION', title='GA Start', message=f'Generation started with {time_slots} slots.'))
        db.session.commit()

        # 1. Gather all required scheduling entities
        all_professors = Professor.query.all()
        all_rooms = Room.query.all()
        all_groups = StudentGroup.query.all()
        all_instances = CourseInstance.query.all()

        if not all_instances:
            raise ValueError("No course instances found in database.")

        # 2. Map Database Models to GA-compatible Objects
        instructors_map = {p.id: Instructor(p.id, p.name) for p in all_professors}
        ga_rooms = [GARoom(r.id, r.name, r.is_lab, r.capacity, r.x, r.y, r.z, r.allowed_batches) for r in all_rooms]
        
        # Map groups including their hierarchy for constraint checking
        groups_map = {}
        for g in all_groups:
            ga_g = GAStudentGroup(g.name, g.size)
            ga_g.id = g.id # Keep DB ID for mapping
            groups_map[g.id] = ga_g
        
        # Map batch names to student group objects
        groups_map_by_name = {g.name: groups_map[g.id] for g in all_groups}
        
        # Convert allowed_batches from batch names to student group objects
        for room in ga_rooms:
            if room.allowed_batches:
                room.allowed_batches = [groups_map_by_name[batch_name] for batch_name in room.allowed_batches 
                                       if batch_name in groups_map_by_name]

        ga_course_instances = []
        for instance in all_instances:
            ga_instance = GAInstance(
                instance_id=instance.id,
                course_id=instance.course_id,
                session_type=instance.session_type.lower(),
                instructor=instructors_map[instance.instructor_id],
                student_grp=groups_map[instance.student_group_id],
                slots_req=instance.slots_required,
                slots_continuous=instance.slots_continuous,
                preference_bin=instance.preference_bin,
                lecture_consecutive=instance.lecture_consecutive,
                parallelizable_id=instance.parallelizable_id
            )
            ga_instance.db_record_id = instance.id
            ga_course_instances.append(ga_instance)

        # 3. Configure and Initialize GA Engine
        time_slot_bins = {i: (1 if i <= (time_slots//3) else 2 if i <= (2*time_slots//3) else 3) for i in range(1, time_slots + 1)}
        ga_engine = GASearch(
            time_slots=time_slots,
            courses=ga_course_instances,
            preference_bins=time_slot_bins,
            objective_function_weights=[1.0, 1.0, 1.0],
            rooms=ga_rooms,
            population_size=population_size, 
            generations=max_gens
        )

        # 4. Execute Evolutionary Search
        try:
            best_timetable, best_fitness = ga_engine.run(
                convergence_threshold=0.1, 
                min_generations=min_gens
            )
            print(f"\nFull Timetable:")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # Weekdays only
            for day in days:
                print(f"\n{day}:")
                day_slots = best_timetable[day]
                for slot in sorted(day_slots.keys()):
                    courses_in_slot = day_slots[slot]
                    if courses_in_slot:
                        course_names = [f"{c.course_id}-{c.session_type}({c.student_grp.name})" for c in
                                        courses_in_slot]
                        print(f"  Slot {slot}: {course_names}")
                    else:
                        print(f"  Slot {slot}: [empty]")
        except Exception as e:
            db.session.add(ActivityLog(category='NOTIFICATION', title='GA Failed', message=f'Engine Error: {str(e)}'))
            db.session.commit()
            raise RuntimeError(f"GA Engine failed: {str(e)}")

        if not best_timetable:
            raise RuntimeError("GA engine failed to find a valid solution.")

        # 5. Persist the Resulting Schedule
        Schedule.query.update({Schedule.is_active: False})
        new_schedule_record = Schedule(name=schedule_name, fitness_score=best_fitness, is_active=True)
        db.session.add(new_schedule_record)
        db.session.flush()

        for day, slots in best_timetable.items():
            for slot_idx, courses in slots.items():
                for course in courses:
                    db_id = getattr(course, 'db_record_id', None)
                    if not db_id: continue

                    entry = TimetableEntry(
                        schedule_id=new_schedule_record.id,
                        day_of_week=day,
                        time_slot=slot_idx,
                        course_instance_id=db_id,
                        room_id=course.room.id if course.room else None,
                        instructor_id=course.instructor.id,
                        student_group_id=course.student_grp.id
                    )
                    db.session.add(entry)
        
        db.session.add(ActivityLog(category='CHANGE', title='Schedule Generated', message=f'Fitness Score: {best_fitness:.2f}.'))
        db.session.commit()
        return new_schedule_record
