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
    "MT": {"code": "MT", "name": "Mechatronics", "color": "purple"},
    "BT": {"code": "BT", "name": "Biotechnology", "color": "green"},
    "CB": {"code": "CB", "name": "Computational Biology", "color": "lime"},
    "CAM": {"code": "CAM", "name": "Computer Science & Applied Mathematics", "color": "indigo"},
    "ECE": {"code": "ECE", "name": "Electronics & Communication Engineering", "color": "red"},
    "ECM": {"code": "ECM", "name": "Electronics & Computer Science", "color": "magenta"},
    "NT": {"code": "NT", "name": "Nanotechnology", "color": "yellow"},
}

YEARS = [1, 2, 3, 4]
SECTIONS_PER_BRANCH = 2  # CS1, CS2 for CSE, etc. (some branches may have 1)
STUDENTS_PER_SECTION = 35

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
    "ECE": [
        "Dr. Mohan Rao", "Prof. Sneha Patel", "Dr. Bhargav Kumar", "Prof. Ananya Ghosh",
        "Dr. Vinay Sharma", "Prof. Kavya Singh", "Dr. Suresh Reddy", "Prof. Pooja Iyer",
        "Dr. Nikhil Gupta", "Prof. Ritika Sharma",
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
        })
        room_id += 1

    # Lecture Halls (8 LHs, 300 capacity)
    for i in range(1, 9):
        rooms.append({
            "id": room_id,
            "name": f"LH{i}",
            "capacity": 300,
            "is_lab": False,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": 1,
            "allowed_batches": None,
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
        })
        room_id += 1

    # ========================================================================
    # BRANCH-SPECIFIC LABS (11 labs, one per branch)
    # ========================================================================

    lab_mapping = {
        "CSE": ["CS1", "CS2"],
        "AI": ["AI1", "AI2"],
        "ME": ["ME1", "ME2"],
        "CEC": ["CEC1", "CEC2"],
        "ECE": ["ECE1", "ECE2"],
        "ECM": ["ECM1", "ECM2"],
        "MT": ["MT1", "MT2"],
        "BT": ["BT1", "BT2"],
        "CB": ["CB1", "CB2"],
        "CAM": ["CAM1", "CAM2"],
        "NT": ["NT1", "NT2"],
    }

    for branch_short, branch_code in [("CSE", "CS"), ("AI", "AI"), ("ME", "ME"), ("CEC", "CEC"),
                                       ("ECE", "ECE"), ("ECM", "ECM"), ("MT", "MT"), ("BT", "BT"),
                                       ("CB", "CB"), ("CAM", "CAM"), ("NT", "NT")]:
        rooms.append({
            "id": room_id,
            "name": f"{branch_short}_Lab",
            "capacity": 40,
            "is_lab": True,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": 1,
            "allowed_batches": lab_mapping[branch_short],
        })
        room_id += 1

    # ========================================================================
    # SHARED LABS (3 labs with cross-branch access)
    # ========================================================================

    # Shared Lab 1: All branches
    rooms.append({
        "id": room_id,
        "name": "SharedLab1",
        "capacity": 40,
        "is_lab": True,
        "x": random.uniform(0, 100),
        "y": random.uniform(0, 100),
        "z": 1,
        "allowed_batches": None,  # Available to all
    })
    room_id += 1

    # Shared Lab 2: Computation-related branches
    computation_batches = ["CS1", "CS2", "AI1", "AI2", "ECM1", "ECM2", "CB1", "CB2", "CAM1", "CAM2"]
    rooms.append({
        "id": room_id,
        "name": "SharedLab2",
        "capacity": 40,
        "is_lab": True,
        "x": random.uniform(0, 100),
        "y": random.uniform(0, 100),
        "z": 1,
        "allowed_batches": computation_batches,
    })
    room_id += 1

    # Shared Lab 3: Engineering-related branches
    engineering_batches = ["ME1", "ME2", "CEC1", "CEC2", "MT1", "MT2", "NT1", "NT2"]
    rooms.append({
        "id": room_id,
        "name": "SharedLab3",
        "capacity": 40,
        "is_lab": True,
        "x": random.uniform(0, 100),
        "y": random.uniform(0, 100),
        "z": 1,
        "allowed_batches": engineering_batches,
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

CORE_COURSES = {
    1: {  # Year 1 - Foundational (common to all branches)
        "general": [
            {"code": "MA1101", "name": "Calculus & Linear Algebra", "credits": 3},
            {"code": "PHY1101", "name": "Physics I", "credits": 3},
            {"code": "CHM1101", "name": "Chemistry I", "credits": 3},
            {"code": "ES1101", "name": "Engineering Drawing", "credits": 2},
            {"code": "CS1101", "name": "Introduction to Programming", "credits": 3},
            {"code": "ENG1101", "name": "Technical Communication", "credits": 2},
        ],
        "branch_specific": {
            "CSE": [{"code": "CS1102", "name": "Discrete Mathematics", "credits": 3}],
            "AI": [{"code": "AI1102", "name": "Logic & Reasoning", "credits": 3}],
            "ME": [{"code": "ME1102", "name": "Engineering Mechanics", "credits": 3}],
            "CEC": [{"code": "CEC1102", "name": "Surveying Basics", "credits": 3}],
            "ECE": [{"code": "ECE1102", "name": "Circuit Theory", "credits": 3}],
            "ECM": [{"code": "ECM1102", "name": "Digital Logic", "credits": 3}],
            "MT": [{"code": "MT1102", "name": "Robotics Fundamentals", "credits": 3}],
            "BT": [{"code": "BT1102", "name": "Molecular Biology", "credits": 3}],
            "CB": [{"code": "CB1102", "name": "Bioinformatics Basics", "credits": 3}],
            "CAM": [{"code": "CAM1102", "name": "Computational Methods", "credits": 3}],
            "NT": [{"code": "NT1102", "name": "Nanotechnology Intro", "credits": 3}],
        },
    },
    2: {  # Year 2 - Deepening
        "general": [
            {"code": "MA2101", "name": "Differential Equations", "credits": 3},
            {"code": "PHY2101", "name": "Physics II", "credits": 3},
        ],
        "branch_specific": {
            "CSE": [
                {"code": "CS2101", "name": "Data Structures", "credits": 3},
                {"code": "CS2102", "name": "Operating Systems", "credits": 3},
                {"code": "CS2103", "name": "Database Systems", "credits": 3},
            ],
            "AI": [
                {"code": "AI2101", "name": "Machine Learning", "credits": 3},
                {"code": "AI2102", "name": "Neural Networks", "credits": 3},
                {"code": "AI2103", "name": "Probability & Statistics", "credits": 3},
            ],
            "ME": [
                {"code": "ME2101", "name": "Thermodynamics", "credits": 3},
                {"code": "ME2102", "name": "Fluid Mechanics", "credits": 3},
                {"code": "ME2103", "name": "Materials Science", "credits": 3},
            ],
            "CEC": [
                {"code": "CEC2101", "name": "Structural Analysis", "credits": 3},
                {"code": "CEC2102", "name": "Soil Mechanics", "credits": 3},
                {"code": "CEC2103", "name": "Water Resources", "credits": 3},
            ],
            "ECE": [
                {"code": "ECE2101", "name": "Electromagnetic Theory", "credits": 3},
                {"code": "ECE2102", "name": "Signals & Systems", "credits": 3},
                {"code": "ECE2103", "name": "Communication Systems", "credits": 3},
            ],
            "ECM": [
                {"code": "ECM2101", "name": "Microprocessors", "credits": 3},
                {"code": "ECM2102", "name": "Embedded Systems", "credits": 3},
                {"code": "ECM2103", "name": "VLSI Design", "credits": 3},
            ],
            "MT": [
                {"code": "MT2101", "name": "Control Systems", "credits": 3},
                {"code": "MT2102", "name": "Actuators & Motors", "credits": 3},
                {"code": "MT2103", "name": "Sensors & Instrumentation", "credits": 3},
            ],
            "BT": [
                {"code": "BT2101", "name": "Biochemistry", "credits": 3},
                {"code": "BT2102", "name": "Genetics", "credits": 3},
                {"code": "BT2103", "name": "Fermentation Technology", "credits": 3},
            ],
            "CB": [
                {"code": "CB2101", "name": "Genomics", "credits": 3},
                {"code": "CB2102", "name": "Proteomics", "credits": 3},
                {"code": "CB2103", "name": "Systems Biology", "credits": 3},
            ],
            "CAM": [
                {"code": "CAM2101", "name": "Numerical Analysis", "credits": 3},
                {"code": "CAM2102", "name": "Optimization", "credits": 3},
                {"code": "CAM2103", "name": "Computational Geometry", "credits": 3},
            ],
            "NT": [
                {"code": "NT2101", "name": "Nanomaterials", "credits": 3},
                {"code": "NT2102", "name": "Characterization Techniques", "credits": 3},
                {"code": "NT2103", "name": "Nanodevices", "credits": 3},
            ],
        },
    },
    3: {  # Year 3 - Core + Electives (16 electives for all)
        "general": [
            {"code": "MA3101", "name": "Probability & Statistics", "credits": 3},
        ],
        "branch_specific": {
            "CSE": [
                {"code": "CS3101", "name": "Design Patterns", "credits": 3},
                {"code": "CS3102", "name": "Software Engineering", "credits": 3},
                {"code": "CS3103", "name": "Network Security", "credits": 3},
            ],
            "AI": [
                {"code": "AI3101", "name": "Deep Learning", "credits": 3},
                {"code": "AI3102", "name": "Reinforcement Learning", "credits": 3},
                {"code": "AI3103", "name": "Computer Vision", "credits": 3},
            ],
            "ME": [
                {"code": "ME3101", "name": "Heat Transfer", "credits": 3},
                {"code": "ME3102", "name": "Machine Design", "credits": 3},
                {"code": "ME3103", "name": "Manufacturing Processes", "credits": 3},
            ],
            "CEC": [
                {"code": "CEC3101", "name": "Concrete Technology", "credits": 3},
                {"code": "CEC3102", "name": "Environmental Engineering", "credits": 3},
                {"code": "CEC3103", "name": "Transportation Engineering", "credits": 3},
            ],
            "ECE": [
                {"code": "ECE3101", "name": "Antenna Theory", "credits": 3},
                {"code": "ECE3102", "name": "Power Electronics", "credits": 3},
                {"code": "ECE3103", "name": "Digital Signal Processing", "credits": 3},
            ],
            "ECM": [
                {"code": "ECM3101", "name": "Computer Architecture", "credits": 3},
                {"code": "ECM3102", "name": "Real-Time Systems", "credits": 3},
                {"code": "ECM3103", "name": "IoT Systems", "credits": 3},
            ],
            "MT": [
                {"code": "MT3101", "name": "Robot Kinematics", "credits": 3},
                {"code": "MT3102", "name": "Industrial Automation", "credits": 3},
                {"code": "MT3103", "name": "Vision Systems", "credits": 3},
            ],
            "BT": [
                {"code": "BT3101", "name": "Recombinant DNA", "credits": 3},
                {"code": "BT3102", "name": "Bioprocess Engineering", "credits": 3},
                {"code": "BT3103", "name": "Immunology", "credits": 3},
            ],
            "CB": [
                {"code": "CB3101", "name": "RNA-Seq Analysis", "credits": 3},
                {"code": "CB3102", "name": "Structural Biology", "credits": 3},
                {"code": "CB3103", "name": "Drug Discovery", "credits": 3},
            ],
            "CAM": [
                {"code": "CAM3101", "name": "Partial Differential Equations", "credits": 3},
                {"code": "CAM3102", "name": "Scientific Computing", "credits": 3},
                {"code": "CAM3103", "name": "Advanced Algorithms", "credits": 3},
            ],
            "NT": [
                {"code": "NT3101", "name": "Quantum Dots", "credits": 3},
                {"code": "NT3102", "name": "Nanophotonics", "credits": 3},
                {"code": "NT3103", "name": "Nanocomposites", "credits": 3},
            ],
        },
    },
    4: {  # Year 4 - Specialized + Project
        "general": [
            {"code": "PROJ401", "name": "Capstone Project I", "credits": 4},
        ],
        "branch_specific": {
            "CSE": [
                {"code": "CS4101", "name": "Distributed Systems", "credits": 3},
                {"code": "CS4102", "name": "Cloud Computing", "credits": 3},
                {"code": "CS4103", "name": "Advanced Algorithms", "credits": 3},
            ],
            "AI": [
                {"code": "AI4101", "name": "Natural Language Processing", "credits": 3},
                {"code": "AI4102", "name": "Autonomous Systems", "credits": 3},
                {"code": "AI4103", "name": "AI Ethics", "credits": 3},
            ],
            "ME": [
                {"code": "ME4101", "name": "Finite Element Analysis", "credits": 3},
                {"code": "ME4102", "name": "Advanced Manufacturing", "credits": 3},
                {"code": "ME4103", "name": "Energy Systems", "credits": 3},
            ],
            "CEC": [
                {"code": "CEC4101", "name": "Bridge Engineering", "credits": 3},
                {"code": "CEC4102", "name": "Earthquake Engineering", "credits": 3},
                {"code": "CEC4103", "name": "Smart Cities", "credits": 3},
            ],
            "ECE": [
                {"code": "ECE4101", "name": "5G & Beyond", "credits": 3},
                {"code": "ECE4102", "name": "Renewable Energy", "credits": 3},
                {"code": "ECE4103", "name": "Advanced RF Design", "credits": 3},
            ],
            "ECM": [
                {"code": "ECM4101", "name": "Quantum Computing", "credits": 3},
                {"code": "ECM4102", "name": "Advanced Embedded Systems", "credits": 3},
                {"code": "ECM4103", "name": "Cyber Security", "credits": 3},
            ],
            "MT": [
                {"code": "MT4101", "name": "Humanoid Robotics", "credits": 3},
                {"code": "MT4102", "name": "Swarm Robotics", "credits": 3},
                {"code": "MT4103", "name": "Cognitive Robotics", "credits": 3},
            ],
            "BT": [
                {"code": "BT4101", "name": "Synthetic Biology", "credits": 3},
                {"code": "BT4102", "name": "Gene Therapy", "credits": 3},
                {"code": "BT4103", "name": "Personalized Medicine", "credits": 3},
            ],
            "CB": [
                {"code": "CB4101", "name": "Single Cell Genomics", "credits": 3},
                {"code": "CB4102", "name": "Network Pharmacology", "credits": 3},
                {"code": "CB4103", "name": "Precision Medicine", "credits": 3},
            ],
            "CAM": [
                {"code": "CAM4101", "name": "Machine Learning Theory", "credits": 3},
                {"code": "CAM4102", "name": "Topological Data Analysis", "credits": 3},
                {"code": "CAM4103", "name": "Quantum Algorithms", "credits": 3},
            ],
            "NT": [
                {"code": "NT4101", "name": "Carbon Nanotubes", "credits": 3},
                {"code": "NT4102", "name": "Graphene Engineering", "credits": 3},
                {"code": "NT4103", "name": "Medical Nanotechnology", "credits": 3},
            ],
        },
    },
}

# 16 Year 3 Electives (spread across 4 bins, 4 electives per bin)
ELECTIVES = {
    1: [  # Bin 1 (parallelizable_id=1)
        {"code": "ELE3101", "name": "Artificial Intelligence Fundamentals", "credits": 3, "audience": ["CSE", "AI", "ECM", "CB", "CAM"]},
        {"code": "ELE3102", "name": "Data Science Essentials", "credits": 3, "audience": ["CSE", "AI", "ECM", "CB", "CAM", "BT"]},
        {"code": "ELE3103", "name": "Cloud Architecture", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM", "CB"]},
        {"code": "ELE3104", "name": "Web Development", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM", "CB"]},
    ],
    2: [  # Bin 2 (parallelizable_id=2)
        {"code": "ELE3105", "name": "Cybersecurity Essentials", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM"]},
        {"code": "ELE3106", "name": "Blockchain & Cryptography", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM"]},
        {"code": "ELE3107", "name": "IoT Applications", "credits": 3, "audience": ["CSE", "AI", "ECM", "MT", "CAM"]},
        {"code": "ELE3108", "name": "Mobile App Development", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM"]},
    ],
    3: [  # Bin 3 (parallelizable_id=3)
        {"code": "ELE3109", "name": "Advanced Database Design", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM", "CB"]},
        {"code": "ELE3110", "name": "Computational Biology", "credits": 3, "audience": ["CSE", "AI", "CB", "BT", "CAM"]},
        {"code": "ELE3111", "name": "Renewable Energy Systems", "credits": 3, "audience": ["ME", "CEC", "ECE", "MT", "NT", "BT"]},
        {"code": "ELE3112", "name": "Virtual Reality & AR", "credits": 3, "audience": ["CSE", "AI", "ECM", "MT", "CAM"]},
    ],
    4: [  # Bin 4 (parallelizable_id=4)
        {"code": "ELE3113", "name": "Quantum Computing", "credits": 3, "audience": ["CSE", "AI", "ECM", "CAM", "MT"]},
        {"code": "ELE3114", "name": "Biomedical Engineering", "credits": 3, "audience": ["BT", "CB", "ECE", "MT"]},
        {"code": "ELE3115", "name": "Sustainable Engineering", "credits": 3, "audience": "all"},
        {"code": "ELE3116", "name": "Entrepreneurship & Innovation", "credits": 3, "audience": "all"},
    ],
}


def is_eligible_for_elective(branch: str, elective: Dict) -> bool:
    """Check if a branch can take an elective."""
    audience = elective.get("audience", "all")
    if audience == "all":
        return True
    return branch in audience


def assign_room_for_course(session_type: str, branch_short: str, all_rooms: List[Dict]) -> str:
    """
    Assign an appropriate room based on session type and branch.
    Labs get branch-specific labs, lectures get halls, tutorials get classrooms.
    """
    if session_type == "lab":
        # Try to assign branch-specific lab first
        branch_lab = next((r['name'] for r in all_rooms if r['name'] == f"{branch_short}_Lab"), None)
        if branch_lab:
            return branch_lab
        # Fall back to shared lab
        return "SharedLab1"
    elif session_type == "lecture":
        # Assign lecture halls or regular classrooms
        lecture_halls = [r['name'] for r in all_rooms if 'LH' in r['name']]
        return random.choice(lecture_halls) if lecture_halls else "CR1"
    else:  # tutorial
        # Assign small classrooms or regular classrooms
        classrooms = [r['name'] for r in all_rooms if r['name'].startswith('CR')]
        return random.choice(classrooms) if classrooms else "CR1"


def generate_courses(group_id_map: Dict[str, int], all_rooms: List[Dict]) -> List[Dict[str, Any]]:
    """Generate all course instances for all years and branches."""
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
                    for session_type in ["lecture", "tutorial", "lab"]:
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
                            "preference_bin": 1 if year <= 2 else (1 + (section_name[0:1] == "E")),  # Spread Y3-Y4
                            "total_credits": course["credits"],
                            "lecture_consecutive": True if session_type == "lecture" else False,
                            "student_group": section_name,
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
                    for session_type in ["lecture", "tutorial", "lab"]:
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
                            "preference_bin": 1 if year <= 2 else (1 + (section_name[0:1] == "E")),
                            "total_credits": course["credits"],
                            "lecture_consecutive": True if session_type == "lecture" else False,
                            "student_group": section_name,
                            "hierarchy": {
                                "parents": [f"{branch_short}-Yr{year}", f"Year {year}"]
                            },
                        })
                        course_instance_id += 1

                # ============================================================
                # ADD ELECTIVES FOR YEAR 3 ONLY
                # ============================================================
                if year == 3:
                    for bin_id, elective_list in ELECTIVES.items():
                        for elective in elective_list:
                            if is_eligible_for_elective(branch_short, elective):
                                for session_type in ["lecture", "lab"]:
                                    faculty_idx = (course_instance_id % faculty_count)
                                    professor_name = faculty_list[faculty_idx]["name"]
                                    room_name = assign_room_for_course(session_type, branch_short, all_rooms)

                                    if session_type == "lecture":
                                        slots = 1
                                    else:
                                        slots = 1

                                    courses.append({
                                        "id": course_instance_id,
                                        "course_code": elective["code"],
                                        "course_name": elective["name"],
                                        "professor": professor_name,
                                        "room": room_name,
                                        "session_type": session_type,
                                        "slots_required": slots,
                                        "preference_bin": 2,  # Noon for electives
                                        "total_credits": elective["credits"],
                                        "lecture_consecutive": False,
                                        "parallelizable_id": bin_id,  # KEY: Electives in same bin can coexist
                                        "student_group": section_name,
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
        "groups": groups,
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
    print(f"✓ Rooms: {len(seed_data['rooms'])} (Regular: 33, Labs: 14)")
    print(f"✓ Student Groups: {len(seed_data['groups'])}")
    print(f"  - Year groups: 4")
    print(f"  - Branch groups: 44 (11 branches × 4 years)")
    print(f"  - Section groups: 88 (44 branches × 2 sections)")
    print(f"✓ Course Instances: {len(seed_data['courses'])}")

    # Year 3 electives verification
    year3_electives = [c for c in seed_data['courses'] if 'ELE3' in c.get('course_code', '')]
    print(f"\nYear 3 Electives: {len(year3_electives)} instances")
    print(f"  - Unique elective codes: {len(set(c['course_code'] for c in year3_electives))}")

    # Lab verification
    branch_labs = [r for r in seed_data['rooms'] if r['is_lab'] and r['name'] != 'SharedLab1' and r['name'] != 'SharedLab2' and r['name'] != 'SharedLab3']
    print(f"\nBranch-Specific Labs: {len(branch_labs)}")
    for lab in branch_labs:
        print(f"  - {lab['name']}: {lab['allowed_batches']}")

    # Write to file
    output_path = "/Users/venkatanagasaisrujantallam/PyCharm Projects/Automated Time Table Gen/backend/instance/seed_data_copy.json"
    with open(output_path, 'w') as f:
        json.dump(seed_data, f, indent=2)

    print(f"\n✓ Seed data written to: {output_path}")
    print("=" * 80)
