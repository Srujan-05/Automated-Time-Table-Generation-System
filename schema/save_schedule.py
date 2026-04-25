"""
Schedule Saver: GA Output → PostgreSQL

This module saves the final GA-generated timetable to the database
for long-term storage and later retrieval.
"""

import psycopg2
from psycopg2 import Error
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

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


def save_ga_output(schedule_dict, fitness_score, schedule_name="Generated_Schedule"):
    """
    Save GA output timetable to PostgreSQL.
    
    Args:
        schedule_dict: The timetable dictionary from GA.run()
                      Format: {day: {slot: [courses]}}
        fitness_score: Fitness/penalty score of the timetable (float)
        schedule_name: Name/description of this schedule (string)
    
    Returns:
        int: The ID of the inserted schedule
    """
    
    if not schedule_dict:
        print("❌ Cannot save empty schedule!")
        return None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert timetable to JSON for storage
        schedule_json = json.dumps(schedule_dict, default=str)
        
        cursor.execute("""
            INSERT INTO generated_schedules (schedule_name, fitness_score, schedule_data)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (schedule_name, fitness_score, schedule_json))
        
        schedule_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        print(f"✅ Schedule saved to database")
        print(f"   Schedule ID: {schedule_id}")
        print(f"   Name: {schedule_name}")
        print(f"   Fitness Score: {fitness_score}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return schedule_id
        
    except Error as e:
        print(f"❌ Failed to save schedule: {e}")
        return None


def print_timetable(schedule_dict, max_courses_per_slot=3):
    """
    Pretty-print the generated timetable in readable format.
    
    Args:
        schedule_dict: The timetable dictionary
        max_courses_per_slot: Max courses to show per slot (truncate long entries)
    """
    print("\n" + "="*80)
    print("GENERATED TIMETABLE PREVIEW")
    print("="*80 + "\n")
    
    for day, slots in sorted(schedule_dict.items()):
        print(f"\n📅 {day.upper()}")
        print("-" * 80)
        
        for slot_num in sorted(slots.keys()):
            courses = slots[slot_num]
            
            if not courses:
                print(f"   Slot {slot_num:2d}: [EMPTY]")
            else:
                course_strs = []
                for course in courses[:max_courses_per_slot]:
                    # Extract info from course object
                    course_code = getattr(course, 'course_id', 'UNKNOWN')
                    session = getattr(course, 'session_type', '?')
                    prof = getattr(getattr(course, 'instructor', None), 'name', 'Prof?')
                    group = getattr(getattr(course, 'student_grp', None), 'name', 'Group?')
                    room_name = getattr(getattr(course, 'room', None), 'name', 'Room?')
                    
                    course_strs.append(f"{course_code}({session[0].upper()}) {group} [{room_name}]")
                
                courses_display = ", ".join(course_strs)
                if len(courses) > max_courses_per_slot:
                    courses_display += f" ... +{len(courses) - max_courses_per_slot} more"
                
                print(f"   Slot {slot_num:2d}: {courses_display}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("\n❌ This module should be imported, not run directly.")
    print("   Use: from save_schedule import save_ga_output, print_timetable")
