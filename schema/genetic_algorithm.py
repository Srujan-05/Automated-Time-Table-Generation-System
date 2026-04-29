import logging

class GASearch:
    def __init__(self, time_slots, courses, preference_bins, objective_function_weights, rooms, population_size=20, generations=100, mutation_rate=0.1):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # time_slots can be either an integer (legacy, all days same) or a dict (day-specific)
        self.time_slots = time_slots
        if isinstance(time_slots, int):
            # Convert single integer to dict with same slots for all days
            self.time_slots = {
                'Monday': time_slots,
                'Tuesday': time_slots,
                'Wednesday': time_slots,
                'Thursday': time_slots,
                'Friday': time_slots
            }
        # else: time_slots is already a dict with day-specific counts
        
        self.courses = courses
        self.preference_bins = preference_bins
        self.objective_function_weights = objective_function_weights
        self.rooms = rooms
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def create_population(self):
        # Create an initial population of valid timetables using smart initialization
        self.logger.info(f"\n[POPULATION] Starting population creation (target size: {self.population_size})")
        population = []
        failed_attempts = 0
        max_failed_attempts = 5  # Stop after 5 consecutive failures
        
        while len(population) < self.population_size:
            self.logger.info(f"\n[POPULATION] Attempt {len(population) + 1 + failed_attempts}/{self.population_size + failed_attempts}")
            time_table = self._generate_smart_timetable()
            
            # Check constraints with verbose output
            if time_table:
                constraint_check = self.check_constraints(time_table, verbose=True)
            else:
                constraint_check = False
            
            # Only add if it satisfies all constraints
            if constraint_check:
                population.append(time_table)
                failed_attempts = 0
                self.logger.info(f"[POPULATION] ✓ Candidate {len(population)}/{self.population_size} created successfully")
            else:
                failed_attempts += 1
                self.logger.info(f"[POPULATION] ✗ FAILED - Candidate violates constraints (attempt #{failed_attempts})")
                if failed_attempts >= max_failed_attempts:
                    self.logger.info(f"[POPULATION] ⚠ Reached max failed attempts ({max_failed_attempts}), stopping")
                    break
        
        self.logger.info(f"\n[POPULATION] Population creation complete: {len(population)} candidates")
        return population
    
    def _generate_smart_timetable(self):
        # Generate a timetable using greedy/smart initialization with logging
        import random
        import copy
        
        self.logger.info("    [INIT] Initializing timetable structure...")
        
        # Initialize timetable: {day: {slot: [courses]}}
        time_table = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # Weekdays only
        
        for day in days:
            time_table[day] = {}
            # Use day-specific time slot count
            day_slots = self.time_slots.get(day, 9)  # Default to 9 if not specified
            for slot in range(1, day_slots + 1):
                time_table[day][slot] = []
        
        # Sort courses by difficulty (harder courses first) + add small randomness for variation
        # Randomize session type priorities for diversity: some candidates prioritize labs first,
        # others prioritize lectures or tutorials first
        session_type_priority = {
            'lab': random.randint(0, 2),
            'lecture': random.randint(0, 2),
            'tutorial': random.randint(0, 2)
        }
        
        courses_to_schedule = sorted(
            self.courses,
            key=lambda c: (
                session_type_priority.get(c.session_type, 3),  # Randomized session type priority
                -c.slots_req,  # More slots needed = schedule first
                -(c.student_grp.size if hasattr(c.student_grp, 'size') else 0),  # Larger groups = schedule first
                random.random()  # Add randomness for variation between candidates
            )
        )
        
        self.logger.info(f"    [INIT] Scheduling {len(courses_to_schedule)} courses in priority order")
        self.logger.info(f"    [INIT] Session type priorities (randomized): labs={session_type_priority['lab']}, lectures={session_type_priority['lecture']}, tutorials={session_type_priority['tutorial']}")
        
        # Track scheduling statistics
        scheduled = 0
        failed_courses = []
        
        # Try to assign each course
        for course_idx, course in enumerate(courses_to_schedule):
            self.logger.info(f"    [COURSE {course_idx + 1}/{len(courses_to_schedule)}] {course.course_id}-{course.session_type} "
                  f"({course.student_grp.name if hasattr(course.student_grp, 'name') else 'Unknown'}) - "
                  f"slots needed: {course.slots_req}")
            
            assigned_count = 0
            available_rooms = self._get_available_rooms(course)
            
            if not available_rooms:
                # Debug: check why rooms failed
                if course.session_type == 'lab':
                    matching_labs = [r for r in self.rooms if hasattr(r, 'is_lab') and r.is_lab]
                    self.logger.info(f"      [FAIL] No suitable lab rooms (type check: {len(matching_labs)} labs exist)")
                    if hasattr(course.student_grp, 'size'):
                        self.logger.info(f"             Student group size: {course.student_grp.size}, "
                              f"room capacities: {[r.capacity for r in matching_labs if hasattr(r, 'capacity')]}")
                else:
                    self.logger.info(f"      [FAIL] No suitable rooms available")
                failed_courses.append(course)
                continue
            
            self.logger.info(f"      [ROOMS] {len(available_rooms)} suitable room(s) available")
            
            # Randomize day order for variation
            shuffled_days = list(days)
            random.shuffle(shuffled_days)
            
            if course.slots_continuous:
                # Need consecutive slots on the same day
                assigned_count = self._assign_continuous_slots(course, time_table, shuffled_days, available_rooms)
            else:
                # Non-continuous: find individual slots across different days
                assigned_count = self._assign_non_continuous_slots(course, time_table, shuffled_days, available_rooms)
            
            if assigned_count == course.slots_req:
                scheduled += 1
                self.logger.info(f"      [SUCCESS] Scheduled all {assigned_count}/{course.slots_req} slots")
            else:
                self.logger.info(f"      [PARTIAL] Only scheduled {assigned_count}/{course.slots_req} slots")
                failed_courses.append(course)
        
        self.logger.info(f"    [INIT] Scheduling complete: {scheduled}/{len(courses_to_schedule)} courses fully scheduled")
        
        if failed_courses:
            self.logger.info(f"    [INIT] ⚠ {len(failed_courses)} courses had scheduling issues")
            return None  # Return None if couldn't schedule all courses
        
        return time_table
    
    def _assign_continuous_slots(self, course, time_table, days, available_rooms):
        """Assign slots for continuous course (must be consecutive)"""
        import random
        import copy
        
        assigned_count = 0
        
        # Try different days and times systematically
        for day in days:
            if assigned_count >= course.slots_req:
                break
            
            # Check if this is a lecture and already scheduled for this course-student group on this day
            if course.session_type == 'lecture':
                student_grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                course_already_on_day = False
                for slot in time_table[day].keys():
                    for existing_course in time_table[day][slot]:
                        existing_grp_name = existing_course.student_grp.name if hasattr(existing_course.student_grp, 'name') else str(existing_course.student_grp)
                        if (existing_course.course_id == course.course_id and 
                            existing_course.session_type == 'lecture' and
                            existing_grp_name == student_grp_name):
                            course_already_on_day = True
                            self.logger.info(f"        [SKIP] Day {day}: {course.course_id}-lecture for {student_grp_name} already scheduled")
                            break
                    if course_already_on_day:
                        break
                
                if course_already_on_day:
                    continue  # Skip this day for lecture
                
            # Get day-specific slot count for calculating valid start slots
            day_slots = self.time_slots.get(day, 9)
            for start_slot in range(1, day_slots - course.slots_req + 2):
                if assigned_count >= course.slots_req:
                    break
                
                slots_to_use = list(range(start_slot, start_slot + course.slots_req))
                
                # Check if all slots are available
                slots_available = True
                for slot in slots_to_use:
                    if len(time_table[day][slot]) > 0:
                        # Check for conflicts
                        for existing_course in time_table[day][slot]:
                            for room in available_rooms:
                                if not self._can_add_course(course, room, existing_course):
                                    slots_available = False
                                    break
                            if not slots_available:
                                break
                    if not slots_available:
                        break
                
                if slots_available:
                    # Assign to an available room
                    assigned_room = random.choice(available_rooms)
                    course_with_room = copy.copy(course)  # Shallow copy to preserve object references
                    course_with_room.room = assigned_room
                    
                    for slot in slots_to_use:
                        time_table[day][slot].append(course_with_room)
                    assigned_count = course.slots_req
                    self.logger.info(f"        [ASSIGN] Assigned {day} slots {start_slot}-{start_slot + course.slots_req - 1} (room: {assigned_room.name})")
                    break
        
        return assigned_count
    
    def _assign_non_continuous_slots(self, course, time_table, days, available_rooms):
        """Assign slots for non-continuous course"""
        import random
        import copy
        
        assigned_count = 0
        
        # Try to find slots systematically across all days and slots
        for day in days:
            if assigned_count >= course.slots_req:
                break

            lecture_assigned_today = False
            
            # Check if this is a lecture and already scheduled for this course-student group on this day
            if course.session_type == 'lecture':
                student_grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                course_already_on_day = False
                for slot in time_table[day].keys():
                    for existing_course in time_table[day][slot]:
                        existing_grp_name = existing_course.student_grp.name if hasattr(existing_course.student_grp, 'name') else str(existing_course.student_grp)
                        if (existing_course.course_id == course.course_id and 
                            existing_course.session_type == 'lecture' and
                            existing_grp_name == student_grp_name):
                            course_already_on_day = True
                            self.logger.info(f"        [SKIP] Day {day}: {course.course_id}-lecture for {student_grp_name} already scheduled")
                            break
                    if course_already_on_day:
                        break
                
                if course_already_on_day:
                    continue  # Skip this day for lecture
                
            # Get day-specific slot count for iterating through slots
            day_slots = self.time_slots.get(day, 9)
            for slot in range(1, day_slots + 1):
                if assigned_count >= course.slots_req:
                    break
                
                # Check if slot is available
                slot_available = False
                assigned_room = None
                
                if len(time_table[day][slot]) == 0:
                    slot_available = True
                    assigned_room = random.choice(available_rooms)
                else:
                    # Check if we can add this course with existing courses
                    for room in available_rooms:
                        can_add = True
                        for existing_course in time_table[day][slot]:
                            if not self._can_add_course(course, room, existing_course):
                                can_add = False
                                break
                        if can_add:
                            slot_available = True
                            assigned_room = room
                            break
                
                if slot_available and assigned_room:
                    course_with_room = copy.copy(course)  # Shallow copy to preserve object references
                    course_with_room.room = assigned_room
                    time_table[day][slot].append(course_with_room)
                    assigned_count += 1
                    self.logger.info(f"        [ASSIGN] Slot {assigned_count}/{course.slots_req}: {day} slot {slot} (room: {assigned_room.name})")
                    if course.session_type == 'lecture':
                        # Keep lecture instances distributed: at most one slot/day for same course-group.
                        lecture_assigned_today = True
                        break

            if lecture_assigned_today:
                continue
        
        return assigned_count
    
    def _generate_random_timetable(self):
        # [DEPRECATED] Use _generate_smart_timetable instead
        # Kept for backwards compatibility
        return self._generate_smart_timetable()
    
    def _get_available_rooms(self, course):
        # Get list of rooms suitable for the given course
        available_rooms = []
        
        for room in self.rooms:
            # Check room type constraint (lab courses need lab rooms)
            if course.session_type == 'lab':
                if not hasattr(room, 'is_lab') or not room.is_lab:
                    continue  # Lab course needs lab room
            
            # Check room capacity constraint
            if hasattr(course.student_grp, 'size') and hasattr(room, 'capacity'):
                if room.capacity < course.student_grp.size:
                    continue  # Room too small
            
            available_rooms.append(room)
        
        return available_rooms
    
    def _can_add_course(self, new_course, assigned_room, existing_course):
        # Check if new_course can be added to a slot with existing_course
        # Return False if they conflict
        
        # Professor conflict
        if new_course.instructor.id == existing_course.instructor.id:
            return False
        
        # Room conflict
        if assigned_room.id == existing_course.room.id:
            return False
        
        # Parallelizable_id constraint: different non-None IDs cannot coexist
        new_p_id = getattr(new_course, 'parallelizable_id', None)
        existing_p_id = getattr(existing_course, 'parallelizable_id', None)
        if new_p_id is not None and existing_p_id is not None and new_p_id != existing_p_id:
            return False
        
        # Student group conflict (direct) - use NAME comparison, not object identity
        # But if both courses have same parallelizable_id, they can coexist even with shared ancestors
        new_grp_name = new_course.student_grp.name if hasattr(new_course.student_grp, 'name') else str(new_course.student_grp)
        existing_grp_name = existing_course.student_grp.name if hasattr(existing_course.student_grp, 'name') else str(existing_course.student_grp)
        if new_grp_name == existing_grp_name:
            return False
        
        # Student group conflict (super groups) - use NAME comparison
        # Skip if both have same parallelizable_id (same elective group)
        if new_p_id == existing_p_id:
            return True  # Same group, can coexist
        
        if hasattr(new_course.student_grp, 'super_groups') and hasattr(existing_course.student_grp, 'super_groups'):
            new_super_names = [s.name if hasattr(s, 'name') else str(s) for s in new_course.student_grp.super_groups]
            existing_super_names = [s.name if hasattr(s, 'name') else str(s) for s in existing_course.student_grp.super_groups]
            if existing_grp_name in new_super_names:
                return False
            if new_grp_name in existing_super_names:
                return False
            # Check for shared super groups
            if set(new_super_names) & set(existing_super_names):
                return False
        elif hasattr(new_course.student_grp, 'super_groups'):
            new_super_names = [s.name if hasattr(s, 'name') else str(s) for s in new_course.student_grp.super_groups]
            if existing_grp_name in new_super_names:
                return False
        elif hasattr(existing_course.student_grp, 'super_groups'):
            existing_super_names = [s.name if hasattr(s, 'name') else str(s) for s in existing_course.student_grp.super_groups]
            if new_grp_name in existing_super_names:
                return False
        
        return True

    def fitness(self, time_table):
        # Evaluate the fitness of an individual using weighted sum of objective functions
        ptp_penalty = self._ptp_objective_function(time_table)
        rtr_penalty = self._rtr_objective_function(time_table)
        stability_penalty = self._ctrr_objective_function(time_table)
        
        # Calculate weighted sum (lower is better)
        total_penalty = (self.objective_function_weights[0] * ptp_penalty +
                        self.objective_function_weights[1] * rtr_penalty +
                        self.objective_function_weights[2] * stability_penalty)
        
        return total_penalty

    def select_parents(self):
        # Select parents based on fitness
        pass

    def crossover(self, time_table1, time_table2):
        # Perform crossover between two parents to create offspring
        pass

    def mutate(self, time_table):
        # Mutate an individual based on the mutation rate
        pass

    def check_constraints(self, time_table, verbose=False):
        # Check if the time table satisfies all constraints
        # verbose=True prints detailed error messages for debugging
        
        for day in time_table:
            for time_slot in time_table[day]:
                courses = time_table[day][time_slot]
                
                # Check for professor collisions
                professor_ids = []
                for course in courses:
                    if course.instructor.id in professor_ids:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Professor conflict (Prof {course.instructor.id})")
                        return False  # Professor conflict
                    professor_ids.append(course.instructor.id)
                
                # Check parallelizable_id constraint: different non-None IDs cannot coexist in same slot
                parallelizable_ids = [getattr(c, 'parallelizable_id', None) for c in courses]
                for i in range(len(parallelizable_ids)):
                    for j in range(i + 1, len(parallelizable_ids)):
                        id_i = parallelizable_ids[i]
                        id_j = parallelizable_ids[j]
                        # If both have different non-None parallelizable_ids, they cannot coexist
                        if id_i is not None and id_j is not None and id_i != id_j:
                            if verbose:
                                grp_i = courses[i].student_grp.name if hasattr(courses[i].student_grp, 'name') else str(courses[i].student_grp)
                                grp_j = courses[j].student_grp.name if hasattr(courses[j].student_grp, 'name') else str(courses[j].student_grp)
                                self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Parallelizable conflict - {grp_i} (id={id_i}) and {grp_j} (id={id_j}) cannot coexist")
                            return False  # Parallelizable conflict
                
                # Check for student group collisions (direct groups) - use NAME comparison, not object identity
                student_grp_names = []
                for course in courses:
                    grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                    if grp_name in student_grp_names:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Student group conflict ({grp_name})")
                            self.logger.info(f"                      Courses in same slot: {[(c.course_id, c.session_type, c.student_grp.name) for c in courses]}")
                        return False  # Student group conflict
                    student_grp_names.append(grp_name)
                
                # Check for room collisions
                room_ids = []
                for course in courses:
                    if course.room.id in room_ids:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Room conflict (Room {course.room.id})")
                        return False  # Room conflict
                    room_ids.append(course.room.id)
                
                # Check student group ancestor conflicts (but allow if same parallelizable_id)
                for i in range(len(courses)):
                    for j in range(i + 1, len(courses)):
                        # If same parallelizable_id, allow ancestor conflicts
                        if parallelizable_ids[i] == parallelizable_ids[j]:
                            continue
                        
                        # Check ancestor conflicts
                        course_i = courses[i]
                        course_j = courses[j]
                        if hasattr(course_i.student_grp, 'super_groups') or hasattr(course_j.student_grp, 'super_groups'):
                            # Build ancestor sets
                            ancestors_i = set()
                            ancestors_i.add(course_i.student_grp.name if hasattr(course_i.student_grp, 'name') else str(course_i.student_grp))
                            if hasattr(course_i.student_grp, 'super_groups'):
                                for sg in course_i.student_grp.super_groups:
                                    ancestors_i.add(sg.name if hasattr(sg, 'name') else str(sg))
                            
                            ancestors_j = set()
                            ancestors_j.add(course_j.student_grp.name if hasattr(course_j.student_grp, 'name') else str(course_j.student_grp))
                            if hasattr(course_j.student_grp, 'super_groups'):
                                for sg in course_j.student_grp.super_groups:
                                    ancestors_j.add(sg.name if hasattr(sg, 'name') else str(sg))
                            
                            if ancestors_i & ancestors_j:
                                if verbose:
                                    grp_i = course_i.student_grp.name if hasattr(course_i.student_grp, 'name') else str(course_i.student_grp)
                                    grp_j = course_j.student_grp.name if hasattr(course_j.student_grp, 'name') else str(course_j.student_grp)
                                    self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Student ancestor conflict between {grp_i} and {grp_j}")
                                return False
                
                # Check room type constraint (lab courses must be in lab rooms)
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            if verbose:
                                self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: {course.course_id}-lab in non-lab room ({course.room.name})")
                            return False  # Lab course not in lab room
                
                # Check room capacity constraint
                for course in courses:
                    if hasattr(course.student_grp, 'size') and hasattr(course.room, 'capacity'):
                        if course.room.capacity < course.student_grp.size:
                            if verbose:
                                self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Room too small - {course.course_id} in {course.room.name} (capacity {course.room.capacity}, need {course.student_grp.size})")
                            return False  # Room too small for student group
            
            # Check constraint: lectures per day based on lecture_consecutive flag
            # - If lecture_consecutive=False (default): max 1 lecture per day per course-student group
            # - If lecture_consecutive=True: allow multiple lectures on same day
            lectures_per_day = {}
            seen_courses = set()  # Track unique course instances by id
            
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                        course_key = (course.course_id, grp_name, course.id)  # Use instance ID to track unique instances
                        
                        if course_key not in seen_courses:
                            seen_courses.add(course_key)
                            course_key_simple = (course.course_id, grp_name)
                            if course_key_simple not in lectures_per_day:
                                lectures_per_day[course_key_simple] = {'count': 0, 'lecture_consecutive': getattr(course, 'lecture_consecutive', False)}
                            lectures_per_day[course_key_simple]['count'] += 1
                            
                            # Only enforce max 1 lecture per day if lecture_consecutive=False
                            if not lectures_per_day[course_key_simple]['lecture_consecutive']:
                                if lectures_per_day[course_key_simple]['count'] > 1:
                                    if verbose:
                                        self.logger.info(f"    [CONSTRAINT FAIL] {day}: Multiple lectures for {course.course_id} in {grp_name} (lecture_consecutive=False)")
                                    return False  # More than one lecture per day for this course-group
            
            # Check continuous slots constraint for courses that require it
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.slots_continuous:
                        # Find all occurrences of this course in the day
                        course_slots = []
                        for slot in time_table[day]:
                            if course in time_table[day][slot]:
                                course_slots.append(slot)
                        
                        course_slots.sort()
                        
                        # Check if slots are consecutive
                        if len(course_slots) > 1:
                            for i in range(len(course_slots) - 1):
                                if course_slots[i + 1] != course_slots[i] + 1:
                                    if verbose:
                                        self.logger.info(f"    [CONSTRAINT FAIL] {day}: Non-consecutive slots for {course.course_id}-{course.session_type} (slots {course_slots})")
                                    return False  # Non-consecutive slots for continuous course
        
        # Check that each course is scheduled for exactly slots_req times
        course_slot_count = {}
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_id = course.id if hasattr(course, 'id') else id(course)
                    if course_id not in course_slot_count:
                        course_slot_count[course_id] = 0
                    course_slot_count[course_id] += 1
        
        for course in self.courses:
            course_id = course.id if hasattr(course, 'id') else id(course)
            if course_id in course_slot_count:
                if course_slot_count[course_id] != course.slots_req:
                    if verbose:
                        grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                        self.logger.info(f"    [CONSTRAINT FAIL] {course.course_id}-{course.session_type}({grp_name}): scheduled {course_slot_count[course_id]} slots, needs {course.slots_req}")
                    return False  # Course not scheduled for the required number of slots
            else:
                if verbose:
                    grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                    self.logger.info(f"    [CONSTRAINT FAIL] {course.course_id}-{course.session_type}({grp_name}): not scheduled at all")
                return False  # Course not scheduled at all
        
        return True  # All constraints satisfied

    def run(self):
        # Main GA loop - for now just create and return one valid population
        self.logger.info(f"\n[GA] Starting Genetic Algorithm")
        self.logger.info(f"[GA] Population size: {self.population_size}")
        self.logger.info(f"[GA] Generations: {self.generations}")
        
        population = self.create_population()
        
        if not population:
            self.logger.info("[GA] ❌ Failed to create valid population")
            return None
        
        # Evaluate fitness of population
        fitness_scores = []
        for idx, timetable in enumerate(population):
            score = self.fitness(timetable)
            fitness_scores.append(score)
            self.logger.info(f"[GA] Candidate {idx + 1} fitness: {score:.2f}")
        
        # Get best timetable
        best_idx = fitness_scores.index(min(fitness_scores))
        best_timetable = population[best_idx]
        best_fitness = fitness_scores[best_idx]
        
        self.logger.info(f"\n[GA] ✅ Best timetable fitness: {best_fitness:.2f} (Candidate {best_idx + 1})")
        
        return best_timetable

    def _ptp_objective_function(self, time_table):
        # Calculate the course time preference penalty value for a given time table
        penalty = 0
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    if time_slot in self.preference_bins:
                        penalty += abs(self.preference_bins[time_slot] - course.preference_bin)
        return penalty
    
    def _rtr_objective_function(self, time_table):
        # Calculate the room to room distance penalty value for a given time table
        penalty = 0
        for day in time_table:
            time_slots = sorted(time_table[day].keys())  # Get sorted slot numbers
            
            # For each consecutive pair of slots
            for i in range(len(time_slots) - 1):
                current_slot = time_slots[i]
                next_slot = time_slots[i + 1]
                
                # Get all courses in current and next slots
                current_courses = time_table[day][current_slot]
                next_courses = time_table[day][next_slot]
                
                # Map student groups (only direct groups) to rooms in each slot
                current_grp_rooms = {}
                for course in current_courses:
                    if course.student_grp not in current_grp_rooms:
                        current_grp_rooms[course.student_grp] = course.room
                
                next_grp_rooms = {}
                for course in next_courses:
                    if course.student_grp not in next_grp_rooms:
                        next_grp_rooms[course.student_grp] = course.room
                
                # For each student group in current slot, find a matching group in next slot
                for curr_grp, curr_room in current_grp_rooms.items():
                    next_grp_match = None
                    
                    # First check if the same group appears in next slot
                    if curr_grp in next_grp_rooms:
                        next_grp_match = curr_grp
                    # Otherwise check if any of its super groups appear in next slot
                    elif hasattr(curr_grp, 'super_groups'):
                        for super_grp in curr_grp.super_groups:
                            if super_grp in next_grp_rooms:
                                next_grp_match = super_grp
                                break
                    
                    if next_grp_match:
                        next_room = next_grp_rooms[next_grp_match]
                        # Manhattan distance
                        distance = abs(curr_room.x - next_room.x) + abs(curr_room.y - next_room.y) + abs(curr_room.z - next_room.z)
                        penalty += distance
        
        return penalty

    def _ctrr_objective_function(self, time_table):
        # Ensure courses of the same type are held in the same slot and room throughout the week
        penalty = 0
        # Dictionary to store {(course_id, session_type): [(slot, room), ...]}
        course_sessions = {}
        
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_key = (course.course_id, course.session_type)
                    
                    if course_key not in course_sessions:
                        course_sessions[course_key] = []
                    
                    course_sessions[course_key].append((time_slot, course.room))
        
        # For each course-type combination, check consistency
        for course_key, sessions in course_sessions.items():
            if len(sessions) > 1:
                # Get the first occurrence as reference
                reference_slot, reference_room = sessions[0]
                
                # Check all other occurrences
                for slot, room in sessions[1:]:
                    if slot != reference_slot:
                        penalty += 1
                    if room != reference_room:
                        penalty += 1
        
        return penalty
    
    def _course_stability_objective_function(self, time_table):
        # Alias for _ctrr_objective_function - ensures course session consistency
        return self._ctrr_objective_function(time_table)
