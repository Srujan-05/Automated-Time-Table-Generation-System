"""
Preprocessor: DB → GA Objects

This script pulls raw course requirements from PostgreSQL and 
converts them into Python objects that the GA engine expects.
"""

import psycopg2
from psycopg2 import Error
import os
from pathlib import Path
from dotenv import load_dotenv
from classes import Instructor, Room, StudentGroup, CourseInstance

# Load .env from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def get_db_connection():
    """Create and return a PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        exit(1)


def get_ga_inputs():
    """
    Pull raw data from PostgreSQL and return GA-ready objects.
    
    Returns:
        tuple: (rooms_list, courses_list, student_groups_dict)
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("[1/5] Fetching professors...")
    cursor.execute("SELECT id, name FROM professors ORDER BY id;")
    professors = {}
    for row in cursor.fetchall():
        professors[row[0]] = Instructor(row[0], row[1])
    print(f"      ✓ {len(professors)} professors loaded")
    
    print("[2/5] Fetching rooms...")
    cursor.execute("SELECT id, name, is_lab, capacity FROM rooms ORDER BY id;")
    rooms = []
    for row in cursor.fetchall():
        room = Room(row[0], row[1], is_lab=row[2], capacity=row[3])
        rooms.append(room)
    print(f"      ✓ {len(rooms)} rooms loaded")
    
    print("[3/5] Fetching student groups...")
    cursor.execute("SELECT id, name, size FROM student_groups ORDER BY id;")
    student_groups = {}
    for row in cursor.fetchall():
        student_groups[row[0]] = StudentGroup(row[1], row[2])
    print(f"      ✓ {len(student_groups)} student groups loaded")
    
    print("[4/5] Fetching course requirements (unscheduled)...")
    cursor.execute("""
        SELECT id, course_code, session_type, professor_id, student_group_id, 
               slots_required, slots_continuous, preference_bin
        FROM course_requirements
        ORDER BY id;
    """)
    
    courses = []
    for row in cursor.fetchall():
        req_id = row[0]
        course_code = row[1]
        session_type = row[2]
        instructor = professors[row[3]]
        student_group = student_groups[row[4]]
        slots_required = row[5]
        slots_continuous = row[6]
        preference_bin = row[7]

        if slots_continuous:
            # Continuous sessions (typically labs) are scheduled as one block.
            course = CourseInstance(
                course_id=course_code,
                session_type=session_type,
                instructor=instructor,
                student_grp=student_group,
                slots_req=slots_required,
                slots_continuous=True,
                preference_bin=preference_bin,
                instance_id=f"{req_id}_0"
            )
            courses.append(course)
        else:
            # Non-continuous sessions are expanded into 1-slot instances.
            for slot_idx in range(slots_required):
                course = CourseInstance(
                    course_id=course_code,
                    session_type=session_type,
                    instructor=instructor,
                    student_grp=student_group,
                    slots_req=1,
                    slots_continuous=False,
                    preference_bin=preference_bin,
                    instance_id=f"{req_id}_{slot_idx}"
                )
                courses.append(course)
    print(f"      ✓ {len(courses)} course requirements loaded")
    
    conn.close()
    
    print("[5/5] Validation...")
    
    # Sanity checks
    if not courses:
        print("      ❌ No courses loaded! Check db_setup.py was run.")
        exit(1)
    if not rooms:
        print("      ❌ No rooms loaded! Check db_setup.py was run.")
        exit(1)
    
    print("      ✓ All data validated\n")
    
    return rooms, courses, student_groups


def print_ga_inputs_summary(rooms, courses):
    """Print summary of loaded GA inputs"""
    print("="*60)
    print("GA INPUTS SUMMARY")
    print("="*60)
    
    print(f"\n📚 COURSE INSTANCES TO SCHEDULE: {len(courses)}")
    for i, course in enumerate(courses[:5], 1):  # Show first 5
        print(f"   {i}. {course.course_id}-{course.session_type} for {course.student_grp.name}")
        print(f"      Prof: {course.instructor.name}, Slots: {course.slots_req}, Continuous: {course.slots_continuous}")
    if len(courses) > 5:
        print(f"   ... and {len(courses) - 5} more")
    
    print(f"\n🏫 ROOMS AVAILABLE: {len(rooms)}")
    for i, room in enumerate(rooms[:5], 1):  # Show first 5
        room_type = "🔬 Lab" if room.is_lab else "📖 Classroom"
        print(f"   {i}. {room.name} ({room_type}, cap: {room.capacity})")
    if len(rooms) > 5:
        print(f"   ... and {len(rooms) - 5} more")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PREPROCESSOR: Loading GA Inputs from PostgreSQL")
    print("="*60 + "\n")
    
    rooms, courses, student_groups = get_ga_inputs()
    print_ga_inputs_summary(rooms, courses)

    print(f"👥 STUDENT GROUPS LOADED: {len(student_groups)}")
    
    print("✅ Preprocessor test successful!\n")
    print("Next step: python run_ga.py")
