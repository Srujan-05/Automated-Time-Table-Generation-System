"""
Database Setup Script

This script:
1. Connects to PostgreSQL
2. Creates all necessary tables for raw inputs and GA outputs
3. Seeds sample data extracted from all_years.md

Run this ONCE after creating timetable_db in pgAdmin
"""

import psycopg2
from psycopg2 import Error
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"[INIT] Loading environment from: {env_path}")

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
        print("\nMake sure you:")
        print("  1. Have PostgreSQL running")
        print("  2. Created timetable_db in pgAdmin")
        print("  3. Filled in .env with correct password")
        exit(1)


def create_tables(conn):
    """Create all raw input and output tables"""
    cursor = conn.cursor()
    
    print("[1/3] Creating raw input tables...")
    
    try:
        # Professors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS professors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        # Rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                is_lab BOOLEAN DEFAULT FALSE,
                capacity INT DEFAULT 100
            );
        """)
        
        # Student Groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                size INT NOT NULL
            );
        """)
        
        # Course Requirements table (RAW REQUIREMENTS - unscheduled)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_requirements (
                id SERIAL PRIMARY KEY,
                course_code VARCHAR(20) NOT NULL,
                session_type VARCHAR(20) NOT NULL,
                professor_id INT REFERENCES professors(id),
                student_group_id INT REFERENCES student_groups(id),
                slots_required INT NOT NULL,
                slots_continuous BOOLEAN DEFAULT FALSE,
                preference_bin INT DEFAULT 1
            );
        """)
        
        print("   ✓ Raw input tables created")
        
        # GA Output tables
        print("[2/3] Creating GA output table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_schedules (
                id SERIAL PRIMARY KEY,
                schedule_name VARCHAR(100),
                generation_date TIMESTAMP DEFAULT NOW(),
                fitness_score FLOAT,
                schedule_data JSONB
            );
        """)
        
        print("   ✓ GA output table created")
        
        conn.commit()
        
    except Error as e:
        print(f"   ❌ Table creation failed: {e}")
        conn.rollback()
        exit(1)


def seed_data(conn):
    """Seed sample data extracted from all_years.md"""
    cursor = conn.cursor()
    
    print("[3/3] Seeding sample data from all_years.md...")
    
    try:
        # Clear existing data (for re-runs)
        cursor.execute("DELETE FROM course_requirements;")
        cursor.execute("DELETE FROM student_groups;")
        cursor.execute("DELETE FROM professors;")
        cursor.execute("DELETE FROM rooms;")
        
        # Insert Professors (from all_years.md - 2nd & 3rd Year)
        professors_data = [
            "Dr. Rakesh",
            "Dr. Sanjukta",
            "Dr. Anagha Tobi",
            "Dr. Shabnam",
            "Dr. Murtaza",
            "Dr. Naga Deepthi",
            "Dr. Satyanarayana Akula",
            "Dr. Ravi Kishor",
            "Dr. Neha",
            "Dr. A. Pujari",
            "Dr. Pradeep",
            "Dr. Anil Annadi",
            "Dr. OmPrakash",
            "Dr. Vandna Gokhroo",
            "Dr. Ramakant",
            "Dr. Kumudham",
            "Dr. Rakhee",
            "Dr. Sherlin",
            "Dr. Balaji Prashanth",
            "Dr. Nidhi Gupta",
            "Dr. P. Chaitanya Akshara",
            "Dr. Bhanu Kiran",
            "Dr. Sayantan",
            "Dr. Sabeeha",
            "Dr. Aruna Kumar Chelluboyina",
            "Dr. Sanjeev",
            "Dr. Akankasha Singh",
            "Dr. Varun Kumar",
            "Dr. Jayaprakash",
            "Dr. Manish",
            "Dr. Bill Reynolds",
            "Dr. Mittika",
            "Dr. Runa",
            "Dr. Anil",
            "Dr. Visalakshi",
            "Dr. Yayati",
            "Dr. Veeraiah",
            "Dr. Prafulla",
            "Dr. Praveen",
            "Dr. Satyanarayan",
            "Dr. Manoj",
            "Dr. Ravi Babu",
            "Dr. Yashwanth",
            "Dr. Bharghava",
            "Dr. Subbarao",
            "Dr. Mahesh",
            "Dr. Neeraj",
            "Dr. Avinash",
            "Dr. S Bharatala",
            "Dr. S Porika",
            "Dr. Raju",
            "Dr. Ankita",
            "Dr. Santosh Thakur",
            "Dr. Palash",
            "Dr. Prasad",
            "Dr. nartakannai"
        ]
        
        for prof in professors_data:
            cursor.execute(
                "INSERT INTO professors (name) VALUES (%s) ON CONFLICT DO NOTHING;",
                (prof,)
            )
        cursor.execute("SELECT COUNT(*) FROM professors;")
        prof_count = cursor.fetchone()[0]
        print(f"   ✓ {prof_count} professors inserted")
        
        # Insert Rooms (all rooms from all_years.md - 2nd & 3rd Year)
        rooms_data = [
            ("ELT 1", False, 120),
            ("ELT 2", False, 120),
            ("ELT 3", False, 120),
            ("ELT 4", False, 120),
            ("ELT 5", False, 120),
            ("E-LT 1", False, 100),
            ("E-LT 2", False, 100),
            ("E-LT 3", False, 100),
            ("E-LT 4", False, 100),
            ("E-LT 5", False, 100),
            ("ECR 2", False, 80),
            ("ECR 3", False, 80),
            ("ECR 5", False, 80),
            ("ECR 7", False, 80),
            ("ECR 8", False, 80),
            ("ECR 9", False, 80),
            ("ECR 10", False, 80),
            ("ECR 11", False, 80),
            ("ECR 13", False, 80),
            ("ECR 15", False, 80),
            ("ETR 1", False, 70),
            ("ETR 2", False, 70),
            ("ETR 3", False, 70),
            ("ETR 4", False, 70),
            ("ETR 5", False, 70),
            ("IT2 block", True, 90),
            ("CS LAB 1", True, 70),
            ("CS LAB 2", True, 70),
            ("CS LAB 3", True, 70),
            ("Comp Lab 3", True, 65),
            ("Material Testing Lab", True, 40),
            ("Geology Lab", True, 30),
            ("Auditorium", False, 400),
            ("E-Lab", False, 150),
        ]
        
        for name, is_lab, capacity in rooms_data:
            cursor.execute(
                "INSERT INTO rooms (name, is_lab, capacity) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                (name, is_lab, capacity)
            )
        cursor.execute("SELECT COUNT(*) FROM rooms;")
        rooms_count = cursor.fetchone()[0]
        print(f"   ✓ {rooms_count} rooms inserted")
        
        # Insert Student Groups (2nd Year - 2022 Batch + additional groups)
        groups_data = [
            ("CS1", 83),
            ("CS2", 83),
            ("CS3", 83),
            ("CS4", 83),
            ("AI1", 70),
            ("AI2", 70),
            ("AI3", 70),
            ("ECE", 30),
            ("ECM", 60),
            ("CB", 15),
            ("BT", 40),
            ("CE", 10),
            ("ME", 25),
            ("MT", 25),
            ("NT", 5),
        ]
        
        for name, size in groups_data:
            cursor.execute(
                "INSERT INTO student_groups (name, size) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (name, size)
            )
        print(f"   ✓ {len(groups_data)} student groups inserted")
        
        # Insert Course Requirements (UNSCHEDULED!) - Expanded from all_years.md
        # 2nd Year CS1 courses (83 students)
        course_reqs = [
            # CS1 - Extensive courses with 4-5 slots each to force distribution
            ("MA2103", "lecture", "Dr. Rakesh", "CS1", 5, False, 1),           # Mon, Tue, Wed slots
            ("HS2102", "lecture", "Dr. Anagha Tobi", "CS1", 4, False, 1),       # Mon, Tue, Wed, Fri
            ("HS2103", "tutorial", "Dr. Kumudham", "CS1", 2, False, 2),         # Tutorial slot
            ("CS/AI2101", "lecture", "Dr. A. Pujari", "CS1", 3, False, 2),      # Wed, Thu
            ("CS/AI 2102", "lecture", "Dr. Ravi Kishor", "CS1", 4, False, 2),   # Mon, Tue, Thu, Fri
            ("CS/AI 2102", "lab", "Dr. Shabnam", "CS1", 2, True, 2),            # Tuesday lab
            ("MA2104", "lecture", "Dr. Rakhee", "CS1", 3, False, 1),            # Mon, Wed, Thu
            ("MA2105", "lecture", "Dr. Rakesh", "CS1", 2, False, 1),            # Thu, Fri
            ("EC 2102", "lecture", "Dr. Sayantan", "CS1", 4, False, 2),         # Wed, Thu, Fri + 1
            ("EC 2102", "tutorial", "Dr. Satyanarayana Akula", "CS1", 2, False, 2),  # Tue
            ("MA2106", "lecture", "Dr. Pradeep", "CS1", 3, False, 1),           # Mon
            ("PH2102", "lecture", "Dr. Murtaza", "CS1", 4, False, 3),           # Tue, Wed, Thu, Fri
            ("PH2102", "tutorial", "Dr. Vandna Gokhroo", "CS1", 2, False, 3),   # Tue
            ("CS2102", "lab", "Dr. Neha", "CS1", 2, True, 2),                   # Lab
            
            # AI1 - 70 students
            ("CS/AI 2102", "lecture", "Dr. Ravi Kishor", "AI1", 4, False, 2),
            ("CS/AI 2102", "lab", "Dr. Shabnam", "AI1", 2, True, 2),
            ("MA2103", "lecture", "Dr. Rakesh", "AI1", 5, False, 1),
            ("MA2103", "tutorial", "Dr. Rakesh", "AI1", 2, False, 1),
            ("CS/AI2101", "lecture", "Dr. A. Pujari", "AI1", 3, False, 2),
            ("PH2102", "lab", "Dr. Murtaza", "AI1", 2, True, 3),
            ("PH2102", "lecture", "Dr. Murtaza", "AI1", 3, False, 3),
            ("EC 2102", "tutorial", "Dr. Ankita", "AI1", 2, False, 2),
            ("AI 2102", "lab", "Dr. Neha", "AI1", 2, True, 2),
            ("HS2103", "tutorial", "Dr. Sherlin", "AI1", 2, False, 1),
            
            # ECE - 30 students
            ("EC 2101", "lecture", "Dr. P. Chaitanya Akshara", "ECE", 4, False, 1),
            ("EC 2101", "lab", "Dr. P. Chaitanya Akshara", "ECE", 2, True, 1),
            ("CS2104", "lecture", "Dr. OmPrakash", "ECE", 4, False, 2),
            ("CS2104", "lab", "Dr. nartakannai", "ECE", 2, True, 2),
            ("CS2104", "tutorial", "Dr. OmPrakash", "ECE", 2, False, 2),
            ("MA2103", "lecture", "Dr. Rakesh", "ECE", 4, False, 1),
            ("MA2103", "tutorial", "Dr. Rakesh", "ECE", 2, False, 1),
            ("EC2103", "lecture", "Dr. Bhanu Kiran", "ECE", 3, False, 2),
            ("EC 2102", "lecture", "Dr. Sayantan", "ECE", 4, False, 2),
            ("PH2102", "lecture", "Dr. Murtaza", "ECE", 4, False, 3),
            ("PH2102", "tutorial", "Dr. Anil Annadi", "ECE", 2, False, 3),
            ("BT 2111", "lecture", "Dr. Sabeeha", "ECE", 3, False, 1),
            ("BT 2111", "tutorial", "Dr. Sabeeha", "ECE", 2, False, 1),
            
            # ECM - 60 students  
            ("EC 2101", "lecture", "Dr. P. Chaitanya Akshara", "ECM", 4, False, 1),
            ("EC 2101", "lab", "Dr. P. Chaitanya Akshara", "ECM", 2, True, 1),
            ("EC2103", "lecture", "Dr. Bhanu Kiran", "ECM", 4, False, 2),
            ("EC 2102", "lecture", "Dr. Sayantan", "ECM", 4, False, 2),
            ("EC 3107", "lecture", "Dr. Yashwanth", "ECM", 3, False, 2),
            ("EC3101", "lecture", "Dr. Bhanu Kiran", "ECM", 3, False, 2),
            ("EC 3103", "lecture", "Dr. Bharghava", "ECM", 3, False, 2),
            ("EC 3103", "lab", "Dr. Bharghava", "ECM", 2, True, 2),
            ("EC 3109", "lecture", "Dr. Subbarao", "ECM", 4, False, 2),
            ("MA2103", "lecture", "Dr. Rakesh", "ECM", 4, False, 1),
            ("MA2103", "tutorial", "Dr. Rakesh", "ECM", 2, False, 1),
            ("PH2102", "lecture", "Dr. Murtaza", "ECM", 3, False, 3),
            ("BT 2111", "lecture", "Dr. Sabeeha", "ECM", 3, False, 1),
            
            # BT - 40 students
            ("BT 2110", "lab", "Dr. Aruna Kumar Chelluboyina", "BT", 2, True, 1),
            ("BT 2110", "lecture", "Dr. Aruna Kumar Chelluboyina", "BT", 3, False, 1),
            ("BT 2108", "lecture", "Dr. Akankasha Singh", "BT", 4, False, 1),
            ("BT 2108", "lab", "Dr. Akankasha Singh", "BT", 2, True, 1),
            ("BT 2109", "lecture", "Dr. Mittika", "BT", 3, False, 1),
            ("BT 2109", "lab", "Dr. Mittika", "BT", 2, True, 1),
            ("CS2104", "lecture", "Dr. OmPrakash", "BT", 3, False, 2),
            ("CS2104", "tutorial", "Dr. OmPrakash", "BT", 2, False, 2),
            ("HS2103", "tutorial", "Dr. Kumudham", "BT", 2, False, 1),
            
            # CE - 10 students
            ("CE 2105", "lab", "Dr. Jayaprakash", "CE", 2, True, 2),
            ("CE 2103", "lecture", "Dr. Jayaprakash", "CE", 4, False, 2),
            ("CE 2103", "tutorial", "Dr. Jayaprakash", "CE", 2, False, 2),
            ("CE 2104", "lab", "Dr. Visalakshi", "CE", 2, True, 2),
            ("HS2103", "tutorial", "Dr. Sherlin", "CE", 2, False, 1),
            
            # ME - 25 students
            ("ME 2107", "lecture", "Dr. Palash", "ME", 3, False, 2),
            ("ME 2107", "lab", "Dr. Palash", "ME", 2, True, 2),
            ("ME 2115", "lecture", "Dr. Manish", "ME", 4, False, 2),
            ("ME2116", "lecture", "Dr. Prasad", "ME", 3, False, 2),
            ("HS2103", "tutorial", "Dr. Balaji Prashanth", "ME", 2, False, 1),
            
            # MT - 25 students
            ("MT 2101", "lecture", "Dr. Ramakant", "MT", 4, False, 2),
            ("MT 2101", "tutorial", "Dr. Ramakant", "MT", 2, False, 2),
            ("HS2103", "tutorial", "Dr. Nidhi Gupta", "MT", 2, False, 1),
            
            # NT - 5 students
            ("PH2103", "lecture", "Dr. Anil", "NT", 3, False, 3),
            ("PH2103", "lab", "Dr. Anil", "NT", 2, True, 3),
            ("CH2103", "lecture", "Dr. Bill Reynolds", "NT", 3, False, 2),
            ("BT1102", "lecture", "Dr. Santosh Thakur", "NT", 2, False, 1),
            
            # CB - 15 students
            ("CB 2103", "lab", "Dr. Akankasha Singh", "CB", 2, True, 2),
            ("CS2104", "tutorial", "Dr. OmPrakash", "CB", 2, False, 2),
        ]
        
        inserted_course_rows = 0
        for course_code, session_type, prof_name, group_name, slots, continuous, pref in course_reqs:
            cursor.execute("""
                INSERT INTO course_requirements 
                (course_code, session_type, professor_id, student_group_id, slots_required, slots_continuous, preference_bin)
                SELECT %s, %s, p.id, g.id, %s, %s, %s
                FROM professors p, student_groups g
                WHERE p.name = %s AND g.name = %s
                ON CONFLICT DO NOTHING;
            """, (course_code, session_type, slots, continuous, pref, prof_name, group_name))
            inserted_course_rows += cursor.rowcount
        
        cursor.execute("SELECT COUNT(*) FROM course_requirements;")
        course_count = cursor.fetchone()[0]
        print(f"   ✓ {course_count} course requirements inserted")
        if inserted_course_rows < len(course_reqs):
            print(f"   ⚠ {len(course_reqs) - inserted_course_rows} course rows were not inserted (missing professor/group mapping or duplicate conflict)")
        
        conn.commit()
        print("\n✅ Database setup complete!\n")
        
    except Error as e:
        print(f"   ❌ Data seeding failed: {e}")
        conn.rollback()
        exit(1)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATABASE SETUP: Creating timetable_db tables & seeding data")
    print("="*60 + "\n")
    
    conn = get_db_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
    
    print("Next step: python preprocessor.py")
