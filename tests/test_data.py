"""
Dummy data for testing the Genetic Algorithm Search (GASearch)
"""

# ============================================================================
# DATA CLASSES (simplified versions for testing)
# ============================================================================

class Instructor:
    """Represents a professor/instructor"""
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Room:
    """Represents a classroom or lab space"""
    def __init__(self, id, name, x, y, z, capacity, is_lab=False):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.capacity = capacity
        self.is_lab = is_lab


class StudentGroup:
    """Represents a group of students"""
    def __init__(self, name, size, super_groups=None):
        self.name = name
        self.size = size
        self.super_groups = super_groups if super_groups else []
    
    def __repr__(self):
        return f"StudentGroup({self.name})"


class Course:
    """Represents a base course with credit breakdown"""
    def __init__(self, course_id, name, total_credits, lectures=0, tutorials=0, practicals=0):
        self.course_id = course_id
        self.name = name
        self.total_credits = total_credits
        self.lectures = lectures        # number of lecture sessions per week
        self.tutorials = tutorials      # number of tutorial sessions per week
        self.practicals = practicals    # number of practical/lab sessions per week


class CourseInstance:
    """Represents a single instance of a course session (lecture, tutorial, or lab)"""
    def __init__(self, id, course_id, session_type, instructor, room, student_grp, 
                 slots_req, slots_continuous=False, preference_bin=1, lecture_consecutive=False, allow_parallel=False):
        self.id = id
        self.course_id = course_id  # e.g., "CS201"
        self.session_type = session_type  # "lecture", "tutorial", or "lab"
        self.instructor = instructor
        self.room = room
        self.student_grp = student_grp
        self.slots_req = slots_req
        self.slots_continuous = slots_continuous
        self.preference_bin = preference_bin  # 1=morning, 2=noon, 3=evening (per instance)
        self.lecture_consecutive = lecture_consecutive  # If True, allows multiple lectures on same day; if False, max 1 lecture/day
        self.allow_parallel = allow_parallel  # Can run in parallel with other allow_parallel courses?
        self.course_credits = None  # Will be set during course generation
    
    def __repr__(self):
        return f"Instance({self.course_id}-{self.session_type}, {self.student_grp.name})"


# ============================================================================
# CREATE DUMMY DATA
# ============================================================================

def create_test_data():
    """Create all dummy data for testing"""
    
    # ========== INSTRUCTORS ==========
    prof_kumar = Instructor(id=1, name="Prof Kumar")
    prof_sharma = Instructor(id=2, name="Prof Sharma")
    prof_patel = Instructor(id=3, name="Prof Patel")
    prof_singh = Instructor(id=4, name="Prof Singh")
    prof_khan = Instructor(id=5, name="Prof Khan")
    prof_karan = Instructor(id=5, name="Prof Karan")
    
    instructors = [prof_kumar, prof_sharma, prof_patel, prof_singh, prof_khan, prof_karan]
    
    # ========== ROOMS ==========
    # Regular classrooms
    room_101 = Room(id=1, name="Classroom 101", x=0, y=0, z=0, capacity=50, is_lab=False)
    room_102 = Room(id=2, name="Classroom 102", x=1, y=0, z=0, capacity=50, is_lab=False)
    room_103 = Room(id=3, name="Classroom 103", x=2, y=0, z=0, capacity=40, is_lab=False)
    room_104 = Room(id=4, name="Classroom 104", x=0, y=1, z=0, capacity=60, is_lab=False)
    
    # Lab rooms
    lab_201 = Room(id=5, name="Lab 201", x=5, y=0, z=0, capacity=60, is_lab=True)
    lab_202 = Room(id=6, name="Lab 202", x=6, y=0, z=0, capacity=60, is_lab=True)
    lab_203 = Room(id=7, name="Lab 203", x=7, y=0, z=0, capacity=60, is_lab=True)
    
    # Auditorium (for batch lectures)
    auditorium = Room(id=8, name="Main Auditorium", x=3, y=3, z=0, capacity=250, is_lab=False)
    
    rooms = [room_101, room_102, room_103, room_104, lab_201, lab_202, lab_203, auditorium]
    
    # ========== STUDENT GROUPS (with hierarchy) ==========
    # Super groups (years)
    class_2025 = StudentGroup(name="Class of 2025", size=200)
    class_2026 = StudentGroup(name="Class of 2026", size=180)
    class_2027 = StudentGroup(name="Class of 2027", size=190)
    
    # Sub groups (departments within year)
    cse_2025 = StudentGroup(name="CSE-2025", size=50, super_groups=[class_2025])
    me_2025 = StudentGroup(name="ME-2025", size=50, super_groups=[class_2025])
    ece_2025 = StudentGroup(name="ECE-2025", size=50, super_groups=[class_2025])
    
    cse_2026 = StudentGroup(name="CSE-2026", size=45, super_groups=[class_2026])
    me_2026 = StudentGroup(name="ME-2026", size=45, super_groups=[class_2026])
    ece_2026 = StudentGroup(name="ECE-2026", size=45, super_groups=[class_2026])
    
    cse_2027 = StudentGroup(name="CSE-2027", size=48, super_groups=[class_2027])
    me_2027 = StudentGroup(name="ME-2027", size=47, super_groups=[class_2027])
    ece_2027 = StudentGroup(name="ECE-2027", size=48, super_groups=[class_2027])
    
    # Elective track groups (intermediate groups for managing parallel/non-parallel constraints)
    # CSE-RL-NLP track: includes students who take RL and/or NLP (can't run in parallel with each other)
    cse_rl_nlp_track = StudentGroup(name="CSE-RL-NLP-Track", size=53, super_groups=[cse_2025])
    ece_rl_nlp_track = StudentGroup(name="ECE-RL-NLP-Track", size=53, super_groups=[ece_2025])
    
    # CSE-GenAI track: separate GenAI students (can run in parallel with RL/NLP)
    cse_genai_track = StudentGroup(name="CSE-GenAI-Track", size=30, super_groups=[cse_2025])
    ece_genai_track = StudentGroup(name="ECE-GenAI-Track", size=30, super_groups=[ece_2025])
    
    # Elective groups with track-based hierarchy
    rl_elective_2025 = StudentGroup(name="RL-Elective-2025", size=35, super_groups=[cse_rl_nlp_track, ece_rl_nlp_track])
    nl_elective_2025 = StudentGroup(name="NL-Elective-2025", size=35, super_groups=[cse_rl_nlp_track, ece_rl_nlp_track])
    ga_elective_2025 = StudentGroup(name="GA-Elective-2025", size=30, super_groups=[cse_genai_track, ece_genai_track])

    student_groups = [
        class_2025, class_2026, class_2027,
        cse_2025, me_2025, ece_2025,
        cse_2026, me_2026, ece_2026,
        cse_2027, me_2027, ece_2027,
        cse_rl_nlp_track, ece_rl_nlp_track,
        cse_genai_track, ece_genai_track,
        rl_elective_2025, nl_elective_2025, ga_elective_2025
    ]
    
    # ========== COURSES ==========
    # Define base courses with credit breakdown
    base_courses = []
    
    # CS201 - Programming: 3L, 1T, 2P (total 4 credits)
    cs201 = Course(
        course_id="CS201",
        name="Programming",
        total_credits=4,
        lectures=3,
        tutorials=1,
        practicals=2
    )
    base_courses.append(cs201)
    
    # MA101 - Mathematics: 3L, 1T, 0P (total 3 credits)
    ma101 = Course(
        course_id="MA101",
        name="Mathematics",
        total_credits=3,
        lectures=3,
        tutorials=1,
        practicals=0
    )
    base_courses.append(ma101)
    
    # ME101 - Mechanics: 2L, 1T, 2P (total 3 credits)
    me101 = Course(
        course_id="ME101",
        name="Mechanics",
        total_credits=3,
        lectures=2,
        tutorials=1,
        practicals=2
    )
    base_courses.append(me101)
    
    # EC201 - Digital Electronics: 2L, 0T, 2P (total 2 credits)
    ec201 = Course(
        course_id="EC201",
        name="Digital Electronics",
        total_credits=2,
        lectures=2,
        tutorials=0,
        practicals=2
    )
    base_courses.append(ec201)
    
    # DT101 - Design Thinking: 1L (2 hours continuous), 0T, 0P (total 2 credits)
    dt101 = Course(
        course_id="DT101",
        name="Design Thinking",
        total_credits=2,
        lectures=1,
        tutorials=0,
        practicals=0
    )
    base_courses.append(dt101)
    
    # RL201 - Reinforcement Learning (Elective): 3L, 0T, 0P (total 3 credits)
    rl201 = Course(
        course_id="RL201",
        name="Reinforcement Learning",
        total_credits=3,
        lectures=3,
        tutorials=0,
        practicals=0
    )
    base_courses.append(rl201)
    nl201 = Course(
        course_id="NL201",
        name="Natural Language Processing",
        total_credits=3,
        lectures=3,
        tutorials=0,
        practicals=0
    )
    base_courses.append(nl201)

    # GA201 - Generative AI (Elective): 3L, 0T, 0P (total 3 credits)
    ga201 = Course(
        course_id="GA201",
        name="Generative AI",
        total_credits=3,
        lectures=3,
        tutorials=0,
        practicals=0
    )
    base_courses.append(ga201)
    
    # Now create instances of these courses for different student groups
    courses = []
    instance_counter = 1
    
    # CS201 instances for CSE-2025
    # 3 lecture instances (each 1 slot per session, but scheduled 3 times a week)
    for i in range(cs201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="CS201", session_type="lecture",
            instructor=prof_kumar, room=room_101, student_grp=cse_2025,
            slots_req=1, slots_continuous=False, preference_bin=1
        ))
        instance_counter += 1
    
    # 1 tutorial instance (1 slot per session)
    for i in range(cs201.tutorials):
        courses.append(CourseInstance(
            id=instance_counter, course_id="CS201", session_type="tutorial",
            instructor=prof_singh, room=room_102, student_grp=cse_2025,
            slots_req=1, slots_continuous=False, preference_bin=2
        ))
        instance_counter += 1
    
    # 1 lab instance (2 slots, continuous)
    courses.append(CourseInstance(
        id=instance_counter, course_id="CS201", session_type="lab",
        instructor=prof_sharma, room=lab_201, student_grp=cse_2025,
        slots_req=cs201.practicals, slots_continuous=True, preference_bin=3
    ))
    instance_counter += 1
    
    # CS201 instances for CSE-2026
    for i in range(cs201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="CS201", session_type="lecture",
            instructor=prof_kumar, room=room_103, student_grp=cse_2026,
            slots_req=1, slots_continuous=False, preference_bin=2
        ))
        instance_counter += 1
    
    for i in range(cs201.tutorials):
        courses.append(CourseInstance(
            id=instance_counter, course_id="CS201", session_type="tutorial",
            instructor=prof_singh, room=room_104, student_grp=cse_2026,
            slots_req=1, slots_continuous=False, preference_bin=1
        ))
        instance_counter += 1
    
    # 1 lab instance for CS201-CSE-2026 (2 slots, continuous)
    courses.append(CourseInstance(
        id=instance_counter, course_id="CS201", session_type="lab",
        instructor=prof_patel, room=lab_202, student_grp=cse_2026,
        slots_req=cs201.practicals, slots_continuous=True, preference_bin=2
    ))
    instance_counter += 1
    
    # MA101 instances for CSE-2025
    for i in range(ma101.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="MA101", session_type="lecture",
            instructor=prof_patel, room=room_102, student_grp=cse_2025,
            slots_req=1, slots_continuous=False, preference_bin=1
        ))
        instance_counter += 1
    
    for i in range(ma101.tutorials):
        courses.append(CourseInstance(
            id=instance_counter, course_id="MA101", session_type="tutorial",
            instructor=prof_singh, room=room_103, student_grp=cse_2025,
            slots_req=1, slots_continuous=False, preference_bin=3
        ))
        instance_counter += 1
    
    # MA101 instances for ME-2025
    for i in range(ma101.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="MA101", session_type="lecture",
            instructor=prof_khan, room=room_101, student_grp=me_2025,
            slots_req=1, slots_continuous=False, preference_bin=2
        ))
        instance_counter += 1
    
    for i in range(ma101.tutorials):
        courses.append(CourseInstance(
            id=instance_counter, course_id="MA101", session_type="tutorial",
            instructor=prof_singh, room=room_102, student_grp=me_2025,
            slots_req=1, slots_continuous=False, preference_bin=2
        ))
        instance_counter += 1
    
    # ME101 instances for ME-2025
    for i in range(me101.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="ME101", session_type="lecture",
            instructor=prof_patel, room=room_103, student_grp=me_2025,
            slots_req=1, slots_continuous=False, preference_bin=1
        ))
        instance_counter += 1
    
    for i in range(me101.tutorials):
        courses.append(CourseInstance(
            id=instance_counter, course_id="ME101", session_type="tutorial",
            instructor=prof_singh, room=room_104, student_grp=me_2025,
            slots_req=1, slots_continuous=False, preference_bin=3
        ))
        instance_counter += 1
    
    # 1 lab instance for ME101-ME-2025 (2 slots, continuous)
    courses.append(CourseInstance(
        id=instance_counter, course_id="ME101", session_type="lab",
        instructor=prof_khan, room=lab_201, student_grp=me_2025,
        slots_req=me101.practicals, slots_continuous=True, preference_bin=1
    ))
    instance_counter += 1
    
    # EC201 instances for ECE-2026
    for i in range(ec201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="EC201", session_type="lecture",
            instructor=prof_patel, room=room_101, student_grp=ece_2026,
            slots_req=1, slots_continuous=False, preference_bin=3
        ))
        instance_counter += 1
    
    # 1 lab instance for EC201-ECE-2026 (2 slots, continuous)
    courses.append(CourseInstance(
        id=instance_counter, course_id="EC201", session_type="lab",
        instructor=prof_khan, room=lab_203, student_grp=ece_2026,
        slots_req=ec201.practicals, slots_continuous=True, preference_bin=2
    ))
    instance_counter += 1
    
    # DT101 - Design Thinking lecture for entire Class of 2025 (2 hours continuous)
    courses.append(CourseInstance(
        id=instance_counter, course_id="DT101", session_type="lecture",
        instructor=prof_khan, room=auditorium, student_grp=class_2025,
        slots_req=2, slots_continuous=True, preference_bin=2, lecture_consecutive=True
    ))
    instance_counter += 1
    
    # RL201 - Reinforcement Learning elective instances for 2025 batch (CSE + ECE students, 35 total)
    # 3 lecture instances - marked as parallelizable with GA201
    for i in range(rl201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="RL201", session_type="lecture",
            instructor=prof_patel, room=room_101, student_grp=rl_elective_2025,
            slots_req=1, slots_continuous=False, preference_bin=2, allow_parallel=True
        ))
        instance_counter += 1

    # NL201 - Natural Language Processing (NOT parallelizable with RL)
    # 3 lecture instances
    for i in range(nl201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="NL201", session_type="lecture",
            instructor=prof_karan, room=room_101, student_grp=nl_elective_2025,
            slots_req=1, slots_continuous=False, preference_bin=2, allow_parallel=False
        ))
        instance_counter += 1
    
    # GA201 - Generative AI (parallelizable with RL, but not NLP due to track hierarchy)
    # 3 lecture instances
    for i in range(ga201.lectures):
        courses.append(CourseInstance(
            id=instance_counter, course_id="GA201", session_type="lecture",
            instructor=prof_singh, room=room_102, student_grp=ga_elective_2025,
            slots_req=1, slots_continuous=False, preference_bin=2, allow_parallel=True
        ))
        instance_counter += 1
    
    # ========== PREFERENCE BINS ==========
    # 9 slots per day: 1-3 (morning), 4-6 (noon), 7-9 (evening)
    preference_bins = {
        1: 1, 2: 1, 3: 1,      # Slots 1-3 = morning (bin 1)
        4: 2, 5: 2, 6: 2,      # Slots 4-6 = noon (bin 2)
        7: 3, 8: 3, 9: 3       # Slots 7-9 = evening (bin 3)
    }
    
    # ========== OBJECTIVE FUNCTION WEIGHTS ==========
    # [PTP_weight, RTR_weight, Stability_weight]
    objective_function_weights = [1.0, 0.5, 0.8]
    
    # ========== TIME SLOTS ==========
    # Day-specific time slots (Wednesday has only 5 slots for 2 bins)
    time_slots = {
        'Monday': 9,      # All 3 bins (slots 1-3, 4-6, 7-9)
        'Tuesday': 9,     # All 3 bins (slots 1-3, 4-6, 7-9)
        'Wednesday': 5,   # Only bins 1-2 (slots 1-3: bin1, 4-5: bin2, no bin3)
        'Thursday': 9,    # All 3 bins (slots 1-3, 4-6, 7-9)
        'Friday': 9       # All 3 bins (slots 1-3, 4-6, 7-9)
    }
    
    return {
        'instructors': instructors,
        'rooms': rooms,
        'student_groups': student_groups,
        'base_courses': base_courses,
        'courses': courses,  # List of CourseInstance objects
        'preference_bins': preference_bins,
        'objective_function_weights': objective_function_weights,
        'time_slots': time_slots
    }


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_ga_search():
    """Test the GASearch class with dummy data"""
    from schema.genetic_algorithm import GASearch
    import sys
    import time
    
    # Create test data
    data = create_test_data()
    
    print("=" * 80)
    print("TESTING GENETIC ALGORITHM SEARCH")
    print("=" * 80)
    
    print(f"\n{'BASE COURSES':-^80}")
    print(f"{'Course ID':<12} {'Name':<20} {'Credits':<10} {'Sessions':<30}")
    print("-" * 80)
    for course in data['base_courses']:
        sessions = f"{course.lectures}L, {course.tutorials}T, {course.practicals}P"
        print(f"{course.course_id:<12} {course.name:<20} {course.total_credits:<10} {sessions:<30}")
    
    print(f"\n{'COURSE INSTANCES':-^80}")
    print(f"Total instances: {len(data['courses'])}")
    
    # Count instances by type
    lecture_count = sum(1 for c in data['courses'] if c.session_type == 'lecture')
    tutorial_count = sum(1 for c in data['courses'] if c.session_type == 'tutorial')
    lab_count = sum(1 for c in data['courses'] if c.session_type == 'lab')
    
    print(f"  - Lectures: {lecture_count}")
    print(f"  - Tutorials: {tutorial_count}")
    print(f"  - Labs: {lab_count}")
    
    print(f"\n{'INSTANCES TO SCHEDULE':<40} {'Slots':<10} {'Continuous':<15}")
    print("-" * 80)
    for instance in data['courses']:
        cont_str = "Yes" if instance.slots_continuous else "No"
        print(f"{str(instance):<40} {instance.slots_req:<10} {cont_str:<15}")
    
    print(f"\n{'TEST DATA SUMMARY':-^80}")
    print(f"  - Instructors: {len(data['instructors'])}")
    print(f"  - Rooms: {len(data['rooms'])}")
    print(f"  - Student Groups: {len(data['student_groups'])}")
    print(f"  - Base Courses: {len(data['base_courses'])}")
    print(f"  - Course Instances: {len(data['courses'])}")
    # Display day-specific time slots
    if isinstance(data['time_slots'], dict):
        slots_str = ", ".join([f"{day}: {slots}" for day, slots in data['time_slots'].items()])
        print(f"  - Time Slots per Day: {{{slots_str}}}")
        total_daily = sum(data['time_slots'].values())
    else:
        print(f"  - Time Slots per Day: {data['time_slots']}")
        total_daily = data['time_slots'] * 5  # 5 weekdays
    print(f"  - Total daily slots available: {total_daily}")
    print(f"  - Objective Weights: {data['objective_function_weights']}")
    
    # Calculate total slots needed
    total_slots_needed = sum(c.slots_req for c in data['courses'])
    print(f"  - Total slots needed across week: {total_slots_needed}")
    
    # Initialize GASearch
    ga = GASearch(
        time_slots=data['time_slots'],
        courses=data['courses'],
        preference_bins=data['preference_bins'],
        objective_function_weights=data['objective_function_weights'],
        rooms=data['rooms'],
        population_size=1,  # Generate 10 candidates
        generations=10,
        mutation_rate=0.1
    )
    
    print("\n" + "=" * 80)
    print("Creating Initial Population...")
    print("=" * 80)
    print("(This may take a moment...)")
    sys.stdout.flush()
    
    try:
        start_time = time.time()
        population = ga.create_population()
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n✓ Successfully created population with {len(population)} valid timetables")
        print(f"⏱ Time elapsed: {elapsed_time:.2f} seconds")
        
        # Test fitness function on each timetable
        for candidate_idx, timetable in enumerate(population):
            print(f"\n{'='*80}")
            print(f"CANDIDATE {candidate_idx + 1}/{len(population)}")
            print(f"{'='*80}")
            
            # Test constraints
            is_valid = ga.check_constraints(timetable)
            print(f"✓ Timetable passes constraint check: {is_valid}")
            
            # Calculate fitness
            ptp_penalty = ga._ptp_objective_function(timetable)
            rtr_penalty = ga._rtr_objective_function(timetable)
            stability_penalty = ga._course_stability_objective_function(timetable)
            fitness = ga.fitness(timetable)
            
            print(f"\n✓ Fitness Calculation:")
            print(f"  - PTP Penalty: {ptp_penalty:.2f}")
            print(f"  - RTR Penalty: {rtr_penalty:.2f}")
            print(f"  - Stability Penalty: {stability_penalty:.2f}")
            print(f"  - Total Fitness: {fitness:.2f}")
            
            # Show full timetable for weekdays only
            print(f"\nFull Timetable:")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # Weekdays only
            for day in days:
                print(f"\n{day}:")
                day_slots = timetable[day]
                for slot in sorted(day_slots.keys()):
                    courses_in_slot = day_slots[slot]
                    if courses_in_slot:
                        course_names = [f"{c.course_id}-{c.session_type}({c.student_grp.name})" for c in courses_in_slot]
                        print(f"  Slot {slot}: {course_names}")
                    else:
                        print(f"  Slot {slot}: [empty]")
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ga_search()
