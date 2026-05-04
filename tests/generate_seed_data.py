#!/usr/bin/env python3
"""
Comprehensive Seed Data Generator for Multi-Branch B.Tech Timetable
Generates 4 years × 11 branches with branch-specific lab restrictions.
"""

import json
import random
from typing import List, Dict, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

BRANCHES = {
    "CSE": {"code": "CS", "name": "Computer Science & Engineering", "color": "blue"},
    "AI": {"code": "AI", "name": "Artificial Intelligence", "color": "cyan"},
    "ME": {"code": "ME", "name": "Mechanical Engineering", "color": "orange"},
    "CEC": {"code": "CEC", "name": "Civil Engineering", "color": "brown"},
    "CAM": {"code": "CAM", "name": "Computer Science & Applied Mathematics", "color": "indigo"},
    "ECE": {"code": "ECE", "name": "Electronics & Communication Engineering", "color": "red"},
    "ECM": {"code": "ECM", "name": "Electronics & Computer Science", "color": "magenta"},
}

YEARS = [1, 2]  # Reduced from 4 to 2 years for smaller dataset
SECTIONS_PER_BRANCH = 1  # Reduced from 2 to 1 section per branch
STUDENTS_PER_SECTION = 25  # Reduced from 35 to 25

# ============================================================================
# FACULTY GENERATION
# ============================================================================

FACULTY_NAMES = {
    "CSE": [
        "Dr. Rajesh Kumar", "Dr. Priya Sharma", "Dr. Amit Patel", "Dr. Neha Gupta",
        "Dr. Vikram Singh", "Prof. Deepak Verma", "Dr. Anjali Rao", "Prof. Sanjay Mishra",
        "Dr. Kavya Nair", "Prof. Arjun Desai",
    ],
    "AI": [
        "Dr. Akshay Joshi", "Dr. Pooja Bhat", "Dr. Rohan Kapoor", "Prof. Maya Reddy",
        "Dr. Nitin Sharma", "Prof. Seema Pandey", "Dr. Rahul Singh", "Prof. Divya Kulkarni",
        "Dr. Aditya Malhotra", "Prof. Simran Kaur",
    ],
    "ME": [
        "Dr. Venkat Naidu", "Prof. Priya Deshmukh", "Dr. Arjun Pillai", "Prof. Shreya Iyer",
        "Dr. Manish Gupta", "Prof. Isha Sharma", "Dr. Rajiv Kumar", "Prof. Meera Nambiar",
        "Dr. Sanjay Rao", "Prof. Ananya Singh",
    ],
    "CEC": [
        "Dr. Karthik Murthy", "Prof. Harshita Jain", "Dr. Suresh Kumar", "Prof. Divya Rai",
        "Dr. Ajay Patel", "Prof. Nisha Gupta", "Dr. Ramesh Sinha", "Prof. Anjana Rao",
        "Dr. Saurav Dutta", "Prof. Tejas Kulkarni",
    ],
    "CAM": [
        "Dr. Shalini Verma", "Prof. Ravi Tiwari", "Dr. Pankaj Sharma", "Prof. Meera Singh",
        "Dr. Arjun Desai", "Prof. Neha Iyer", "Dr. Vikram Kumar", "Prof. Divya Rao",
        "Dr. Sandeep Patel", "Prof. Priya Nair",
    ],
    "ECE": [
        "Dr. Mohan Rao", "Prof. Sneha Patel", "Dr. Bhargav Kumar", "Prof. Ananya Ghosh",
        "Dr. Vinay Sharma", "Prof. Kavya Singh", "Dr. Suresh Reddy", "Prof. Pooja Iyer",
        "Dr. Nikhil Gupta", "Prof. Ritika Sharma",
    ],
    "ECM": [
        "Dr. Rajesh Singh", "Prof. Anjali Desai", "Dr. Vikram Patel", "Prof. Neha Verma",
        "Dr. Sanjay Kumar", "Prof. Priya Gupta", "Dr. Arjun Rao", "Prof. Divya Singh",
        "Dr. Harsh Nair", "Prof. Isha Patel",
    ],
    "General": [
        "Dr. Harish Varma", "Prof. Jaya Nair", "Dr. Srinivas Rao", "Prof. Sangeeta Kulkarni",
        "Dr. Aravind Kumar", "Prof. Priya Menon", "Dr. Gopal Singh", "Prof. Divya Patel",
        "Dr. Vikram Sinha", "Prof. Anu Gupta", "Dr. Rajkumar Verma", "Prof. Sandhya Rao",
        "Dr. Ashok Reddy", "Prof. Meena Singh", "Dr. Rohit Kumar", "Prof. Neha Iyer",
        "Dr. Suresh Patel", "Prof. Anjali Mishra", "Dr. Gaurav Sharma", "Prof. Isha Nair",
    ],
}

# ============================================================================
# ROOM GENERATION
# ============================================================================

def generate_rooms() -> List[Dict[str, Any]]:
    """Generate all rooms with branch-specific lab restrictions."""
    rooms = []
    room_id = 1

    # Regular Classrooms (18 CRs, 120 capacity)
    for i in range(1, 19):
        rooms.append({
            "id": room_id,
            "name": f"CR{i}",
            "capacity": 120,
            "is_lab": False,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": 0,
            "allowed_batches": None,  # Available to all
            "allowed_departments": None,  # Available to all departments
        })
        room_id += 1

    # Lecture Halls (15 LHs, 300 capacity) - INCREASED FROM 8
    for i in range(1, 16):
        rooms.append({
            "id": room_id,
            "name": f"LH{i}",
            "capacity": 300,
            "is_lab": False,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": 1,
            "allowed_batches": None,
            "allowed_departments": None,  # Available to all departments
        })
        room_id += 1

    # Auditorium (1, 1200 capacity)
    rooms.append({
        "id": room_id,
        "name": "AUD1",
        "capacity": 1200,
        "is_lab": False,
        "x": 50,
        "y": 50,
        "z": 2,
        "allowed_batches": None,
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    # Small Classrooms (6 SCRs, 60 capacity)
    for i in range(1, 7):
        rooms.append({
            "id": room_id,
            "name": f"SCR{i}",
            "capacity": 60,
            "is_lab": False,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": 0,
            "allowed_batches": None,
            "allowed_departments": None,  # Available to all departments
        })
        room_id += 1

    # ========================================================================
    # BRANCH-SPECIFIC LABS (14 labs, two per branch)
    # ========================================================================

    # Lab mapping: actual batch names as generated (section format: {code}{section}-Yr{year})
    lab_mapping = {
        "CSE": ["CS1-Yr1", "CS1-Yr2"],
        "AI": ["AI1-Yr1", "AI1-Yr2"],
        "ME": ["ME1-Yr1", "ME1-Yr2"],
        "CEC": ["CEC1-Yr1", "CEC1-Yr2"],
        "ECE": ["ECE1-Yr1", "ECE1-Yr2"],
        "ECM": ["ECM1-Yr1", "ECM1-Yr2"],
        "CAM": ["CAM1-Yr1", "CAM1-Yr2"],
    }

    # Create 2 labs per branch for better distribution
    for branch_short, branch_code in [("CSE", "CS"), ("AI", "AI"), ("ME", "ME"), ("CEC", "CEC"),
                                       ("ECE", "ECE"), ("ECM", "ECM"), ("CAM", "CAM")]:
        for lab_num in range(1, 3):  # 2 labs per branch
            rooms.append({
                "id": room_id,
                "name": f"{branch_short}_Lab{lab_num}",
                "capacity": 100,
                "is_lab": True,
                "x": random.uniform(0, 100),
                "y": random.uniform(0, 100),
                "z": 1,
                "allowed_batches": lab_mapping[branch_short],
                "allowed_departments": [branch_short],  # Restricted to this department
            })
            room_id += 1

    # ========================================================================
    # SHARED LABS (5 labs with cross-branch access)
    # ========================================================================
    # All shared labs use the same coordinates for consistency
    shared_lab_x = 75.0
    shared_lab_y = 75.0
    shared_lab_z = 1

    # Shared Lab 1: All branches - General purpose
    rooms.append({
        "id": room_id,
        "name": "SharedLab1",
        "capacity": 100,
        "is_lab": True,
        "x": shared_lab_x,
        "y": shared_lab_y,
        "z": shared_lab_z,
        "allowed_batches": None,  # Available to all
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    # Shared Lab 2: All branches - Additional general purpose lab
    rooms.append({
        "id": room_id,
        "name": "SharedLab2",
        "capacity": 100,
        "is_lab": True,
        "x": shared_lab_x,
        "y": shared_lab_y,
        "z": shared_lab_z,
        "allowed_batches": None,  # Available to all
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    # Shared Lab 3: All branches - Additional general purpose lab
    rooms.append({
        "id": room_id,
        "name": "SharedLab3",
        "capacity": 100,
        "is_lab": True,
        "x": shared_lab_x,
        "y": shared_lab_y,
        "z": shared_lab_z,
        "allowed_batches": None,  # Available to all
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    # Shared Lab 4: All branches - Additional general purpose lab
    rooms.append({
        "id": room_id,
        "name": "SharedLab4",
        "capacity": 100,
        "is_lab": True,
        "x": shared_lab_x,
        "y": shared_lab_y,
        "z": shared_lab_z,
        "allowed_batches": None,  # Available to all
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    # Shared Lab 5: All branches - Additional capacity
    rooms.append({
        "id": room_id,
        "name": "SharedLab5",
        "capacity": 100,
        "is_lab": True,
        "x": shared_lab_x,
        "y": shared_lab_y,
        "z": shared_lab_z,
        "allowed_batches": None,  # Available to all
        "allowed_departments": None,  # Available to all departments
    })
    room_id += 1

    return rooms


# ============================================================================
# FACULTY GENERATION
# ============================================================================

def generate_faculty() -> List[Dict[str, str]]:
    """Generate ~100 faculty members."""
    faculty = []
    faculty_id = 1

    # Add specialized faculty by department
    for dept, names in FACULTY_NAMES.items():
        for name in names:
            faculty.append({
                "id": faculty_id,
                "name": name,
                "email": f"{name.lower().replace(' ', '.').replace('dr.', '').replace('prof.', '')}{faculty_id}@university.edu",
                "department": dept if dept != "General" else "Other",
            })
            faculty_id += 1

    return faculty


# ============================================================================
# STUDENT GROUPS GENERATION (WITH HIERARCHY)
# ============================================================================

def generate_student_groups() -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Generate student groups with hierarchy:
    Year (top level) → Branch → Section
    E.g., Year 1 → CSE → CS1
    """
    groups = []
    group_id = 1
    group_id_map = {}  # name -> id mapping

    # ========================================================================
    # CREATE TOP-LEVEL YEAR GROUPS
    # ========================================================================
    year_groups = {}
    for year in YEARS:
        year_name = f"Year {year}"
        groups.append({
            "id": group_id,
            "name": year_name,
            "size": len(BRANCHES) * SECTIONS_PER_BRANCH * STUDENTS_PER_SECTION,  # ~840 per year
            "level": "year",
            "parents": [],
        })
        year_groups[year] = group_id
        group_id_map[year_name] = group_id
        group_id += 1

    # ========================================================================
    # CREATE BRANCH-LEVEL GROUPS
    # ========================================================================
    branch_groups = {}
    for year in YEARS:
        for branch_short, branch_info in BRANCHES.items():
            branch_name = f"{branch_short}-Yr{year}"
            groups.append({
                "id": group_id,
                "name": branch_name,
                "size": SECTIONS_PER_BRANCH * STUDENTS_PER_SECTION,  # ~70 per branch
                "level": "branch",
                "parents": [f"Year {year}"],
            })
            branch_groups[(year, branch_short)] = group_id
            group_id_map[branch_name] = group_id
            group_id += 1

    # ========================================================================
    # CREATE SECTION-LEVEL GROUPS (ACTUAL BATCHES)
    # ========================================================================
    section_groups = {}
    for year in YEARS:
        for branch_short, branch_info in BRANCHES.items():
            branch_code = branch_info["code"]
            for section in range(1, SECTIONS_PER_BRANCH + 1):
                section_name = f"{branch_code}{section}-Yr{year}"
                branch_display_name = f"{branch_short}-Yr{year}"
                groups.append({
                    "id": group_id,
                    "name": section_name,
                    "size": STUDENTS_PER_SECTION,  # ~35 per section
                    "level": "section",
                    "parents": [branch_display_name],
                })
                section_groups[(year, branch_short, section)] = group_id
                group_id_map[section_name] = group_id
                group_id += 1

    return groups, group_id_map


# ============================================================================
# COURSE GENERATION
# ============================================================================

# Format: {"code": "...", "name": "...", "credits": 3, "has_lab": True/False}
CORE_COURSES = {
    1: {  # Year 1 - Foundational (Semester 1)
        "general": [
            {"code": "MA1101", "name": "Mathematics I - Calculus and Linear Algebra", "credits": 3, "has_lab": False},
            {"code": "PHY1101", "name": "Physics I - Mechanics and Thermodynamics", "credits": 3, "has_lab": True},
            {"code": "CHM1101", "name": "Chemistry I - Physical and Inorganic Chemistry", "credits": 3, "has_lab": False},
            {"code": "ES1101", "name": "Engineering Drawing and CAD", "credits": 2, "has_lab": False},
            {"code": "CS1101", "name": "Introduction to Programming", "credits": 3, "has_lab": True},
            {"code": "ENG1101", "name": "English and Technical Communication", "credits": 2, "has_lab": False},
        ],
        "branch_specific": {
            "CSE": [{"code": "CS1102", "name": "Discrete Mathematics and Logic", "credits": 3, "has_lab": False}],
            "AI": [{"code": "AI1102", "name": "Foundations of Artificial Intelligence", "credits": 3, "has_lab": False}],
            "ME": [{"code": "ME1102", "name": "Engineering Mechanics", "credits": 3, "has_lab": False}],
            "CEC": [{"code": "CEC1102", "name": "Surveying and Mapping Basics", "credits": 3, "has_lab": False}],
            "ECE": [{"code": "ECE1102", "name": "Circuit Analysis and Networks", "credits": 3, "has_lab": False}],
            "ECM": [{"code": "ECM1102", "name": "Digital Logic and Design", "credits": 3, "has_lab": False}],
            "CAM": [{"code": "CAM1102", "name": "Computational Mathematics", "credits": 3, "has_lab": False}],
        },
    },
    2: {  # Year 2 - Advanced (Semester 1)
        "branch_specific": {
            "CSE": [
                {"code": "CS2101", "name": "Data Structures and Algorithms", "credits": 3, "has_lab": False},
                {"code": "CS2102", "name": "Digital Architecture and Design", "credits": 3, "has_lab": False},
                {"code": "CS2103", "name": "Discrete Mathematics and Computation", "credits": 3, "has_lab": False},
            ],
            "AI": [
                {"code": "AI2101", "name": "Machine Learning Fundamentals", "credits": 3, "has_lab": False},
                {"code": "AI2102", "name": "Probability and Statistics for AI", "credits": 3, "has_lab": False},
                {"code": "AI2103", "name": "Data Structures and Algorithms", "credits": 3, "has_lab": False},
            ],
            "ME": [
                {"code": "ME2101", "name": "Mechanics of Materials", "credits": 3, "has_lab": False},
                {"code": "ME2102", "name": "Thermodynamics I", "credits": 3, "has_lab": False},
                {"code": "ME2103", "name": "Manufacturing Processes and Workshop", "credits": 3, "has_lab": True},
            ],
            "CEC": [
                {"code": "CEC2101", "name": "Structural Analysis I", "credits": 3, "has_lab": False},
                {"code": "CEC2102", "name": "Surveying I - Instruments and Methods", "credits": 3, "has_lab": False},
                {"code": "CEC2103", "name": "Soil Mechanics I", "credits": 3, "has_lab": False},
            ],
            "ECE": [
                {"code": "ECE2101", "name": "Electronic Devices and Circuits", "credits": 3, "has_lab": False},
                {"code": "ECE2102", "name": "Signals and Systems", "credits": 3, "has_lab": False},
                {"code": "ECE2103", "name": "Digital Electronics", "credits": 3, "has_lab": False},
            ],
            "ECM": [
                {"code": "ECM2101", "name": "Microprocessors and Embedded Systems", "credits": 3, "has_lab": False},
                {"code": "ECM2102", "name": "Digital VLSI Design", "credits": 3, "has_lab": False},
                {"code": "ECM2103", "name": "Signals and Systems", "credits": 3, "has_lab": False},
            ],
            "CAM": [
                {"code": "CAM2101", "name": "Numerical Analysis and Methods", "credits": 3, "has_lab": False},
                {"code": "CAM2102", "name": "Optimization Techniques", "credits": 3, "has_lab": False},
                {"code": "CAM2103", "name": "Data Structures and Algorithms", "credits": 3, "has_lab": False},
            ],
        },
    },
}


def assign_room_for_course(session_type: str, branch_short: str, all_rooms: List[Dict]) -> str:
    """
    Assign an appropriate room based on session type and branch.
    Labs get branch-specific labs, lectures get halls, tutorials get classrooms.
    """
    if session_type == "lab":
        # Try to assign branch-specific lab first (Lab1 or Lab2)
        branch_labs = [r['name'] for r in all_rooms if r['name'].startswith(f"{branch_short}_Lab")]
        if branch_labs:
            return random.choice(branch_labs)
        # Fall back to shared lab
        shared_labs = [r['name'] for r in all_rooms if r['name'].startswith("SharedLab")]
        return random.choice(shared_labs) if shared_labs else "SharedLab1"
    elif session_type == "lecture":
        # Assign lecture halls or regular classrooms
        lecture_halls = [r['name'] for r in all_rooms if 'LH' in r['name']]
        return random.choice(lecture_halls) if lecture_halls else "CR1"
    else:  # tutorial
        # Assign small classrooms or regular classrooms
        classrooms = [r['name'] for r in all_rooms if r['name'].startswith('CR')]
        return random.choice(classrooms) if classrooms else "CR1"


def generate_courses(group_id_map: Dict[str, int], all_rooms: List[Dict]) -> List[Dict[str, Any]]:
    """Generate all course instances for all years and branches.
    
    Session types created:
    - lecture: Always created
    - tutorial: Always created
    - lab: Only created if course has_lab is True
    """
    courses = []
    course_instance_id = 1
    faculty_list = generate_faculty()
    faculty_count = len(faculty_list)

    for year in YEARS:
        for branch_short, branch_info in BRANCHES.items():
            for section in range(1, SECTIONS_PER_BRANCH + 1):
                section_name = f"{branch_info['code']}{section}-Yr{year}"
                student_group_id = group_id_map[section_name]

                # ============================================================
                # ADD GENERAL COURSES (common to all batches)
                # ============================================================
                general_courses = CORE_COURSES[year].get("general", [])
                for course in general_courses:
                    # Determine which session types to create
                    has_lab = course.get("has_lab", True)  # Default to True for backward compatibility
                    session_types = ["lecture", "tutorial"]
                    if has_lab:
                        session_types.append("lab")
                    
                    for session_type in session_types:
                        faculty_idx = (course_instance_id % faculty_count)
                        professor_name = faculty_list[faculty_idx]["name"]
                        room_name = assign_room_for_course(session_type, branch_short, all_rooms)

                        # Determine slots and room type
                        if session_type == "lecture":
                            slots = 2
                            room_type = "lecture"
                        elif session_type == "tutorial":
                            slots = 1
                            room_type = "tutorial"
                        else:  # lab
                            slots = 2
                            room_type = "lab"

                        courses.append({
                            "id": course_instance_id,
                            "course_code": course["code"],
                            "course_name": course["name"],
                            "professor": professor_name,
                            "room": room_name,
                            "session_type": session_type,
                            "slots_required": slots,
                            "slots_continuous": True if session_type == "lab" else False,
                            "preference_bin": 1 if year <= 2 else (1 + (section_name[0:1] == "E")),  # Spread Y3-Y4
                            "total_credits": course["credits"],
                            "lecture_consecutive": True if session_type == "lecture" else False,
                            "student_group": section_name,
                            "department_name": "General",  # General courses taught by all departments
                            "hierarchy": {
                                "parents": [f"{branch_short}-Yr{year}", f"Year {year}"]
                            },
                        })
                        course_instance_id += 1

                # ============================================================
                # ADD BRANCH-SPECIFIC CORE COURSES
                # ============================================================
                branch_courses = CORE_COURSES[year].get("branch_specific", {}).get(branch_short, [])
                for course in branch_courses:
                    # Determine which session types to create
                    has_lab = course.get("has_lab", True)  # Default to True for backward compatibility
                    session_types = ["lecture", "tutorial"]
                    if has_lab:
                        session_types.append("lab")
                    
                    for session_type in session_types:
                        faculty_idx = (course_instance_id % faculty_count)
                        professor_name = faculty_list[faculty_idx]["name"]
                        room_name = assign_room_for_course(session_type, branch_short, all_rooms)

                        if session_type == "lecture":
                            slots = 2
                            room_type = "lecture"
                        elif session_type == "tutorial":
                            slots = 1
                            room_type = "tutorial"
                        else:
                            slots = 2
                            room_type = "lab"

                        courses.append({
                            "id": course_instance_id,
                            "course_code": course["code"],
                            "course_name": course["name"],
                            "professor": professor_name,
                            "room": room_name,
                            "session_type": session_type,
                            "slots_required": slots,
                            "slots_continuous": True if session_type == "lab" else False,
                            "preference_bin": 1 if year <= 2 else (1 + (section_name[0:1] == "E")),
                            "total_credits": course["credits"],
                            "lecture_consecutive": True if session_type == "lecture" else False,
                            "student_group": section_name,
                            "department_name": branch_short,  # Branch-specific courses belong to this department
                            "hierarchy": {
                                "parents": [f"{branch_short}-Yr{year}", f"Year {year}"]
                            },
                        })
                        course_instance_id += 1

    return courses


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_seed_data() -> Dict[str, Any]:
    """Generate complete seed data."""
    print("Generating student groups...")
    groups, group_id_map = generate_student_groups()

    print("Generating faculty...")
    faculty = generate_faculty()

    print("Generating rooms with lab restrictions...")
    rooms = generate_rooms()

    print("Generating courses...")
    courses = generate_courses(group_id_map, rooms)

    seed_data = {
        "professors": faculty,
        "rooms": rooms,
        "student_groups": groups,
        "courses": courses,
    }

    return seed_data


if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE MULTI-BRANCH SEED DATA GENERATOR")
    print("=" * 80)

    seed_data = generate_seed_data()

    # Summary Statistics
    print("\n" + "=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)
    print(f"✓ Professors: {len(seed_data['professors'])}")
    
    # Calculate room breakdown
    total_rooms = len(seed_data['rooms'])
    lab_rooms = len([r for r in seed_data['rooms'] if r['is_lab']])
    regular_rooms = total_rooms - lab_rooms
    print(f"✓ Rooms: {total_rooms} (Regular: {regular_rooms}, Labs: {lab_rooms})")
    
    print(f"✓ Student Groups: {len(seed_data['student_groups'])}")
    print(f"  - Year groups: 2")
    print(f"  - Branch groups: 14 (7 branches × 2 years)")
    print(f"  - Section groups: 14 (7 branches × 2 years × 1 section)")
    print(f"✓ Course Instances: {len(seed_data['courses'])}")

    # Lab verification
    branch_labs = [r for r in seed_data['rooms'] if r['is_lab'] and any(b in r['name'] for b in ['CSE_Lab', 'AI_Lab', 'ME_Lab', 'CEC_Lab', 'ECE_Lab', 'ECM_Lab', 'CAM_Lab'])]
    shared_labs = [r for r in seed_data['rooms'] if r['is_lab'] and r['name'].startswith('SharedLab')]
    
    print(f"\nBranch-Specific Labs: {len(branch_labs)}")
    for lab in branch_labs:
        print(f"  - {lab['name']}: {lab['allowed_batches']}")
    
    print(f"\nShared Labs: {len(shared_labs)}")
    for lab in shared_labs:
        print(f"  - {lab['name']}: {lab['allowed_batches']}")

    # Write to file
    output_path = "/Users/venkatanagasaisrujantallam/PyCharm Projects/Automated Time Table Gen/backend/instance/seed_data.json"
    with open(output_path, 'w') as f:
        json.dump(seed_data, f, indent=2)

    print(f"\n✓ Seed data written to: {output_path}")
    print("=" * 80)
