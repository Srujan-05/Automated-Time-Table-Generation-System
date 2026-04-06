class GASearch:
    def __init__(self, time_slots, courses, preference_bins, objective_function_weights, rooms, population_size=20, generations=100, mutation_rate=0.1):
        self.time_slots = time_slots
        self.courses = courses
        self.preference_bins = preference_bins
        self.objective_function_weights = objective_function_weights
        self.rooms = rooms
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def create_population(self):
        # Create an initial random population of valid timetables
        population = []
        
        while len(population) < self.population_size:
            time_table = self._generate_random_timetable()
            
            # Only add if it satisfies all constraints
            if time_table and self.check_constraints(time_table):
                population.append(time_table)
        
        return population
    
    def _generate_random_timetable(self):
        # Generate a random timetable structure
        import random
        
        # Initialize timetable: {day: {slot: [courses]}}
        time_table = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            time_table[day] = {}
            for slot in range(1, self.time_slots + 1):
                time_table[day][slot] = []
        
        # Create a list of all courses to schedule
        courses_to_schedule = list(self.courses)
        random.shuffle(courses_to_schedule)
        
        # Try to assign each course to a valid slot
        for course in courses_to_schedule:
            assigned = False
            attempts = 0
            max_attempts = 50
            
            while not assigned and attempts < max_attempts:
                attempts += 1
                
                # Pick random day and starting slot
                day = random.choice(days)
                start_slot = random.randint(1, self.time_slots)
                
                # Check if we have enough consecutive slots for continuous requirement
                if course.slots_continuous:
                    # Need consecutive slots
                    if start_slot + course.slots_req - 1 <= self.time_slots:
                        slots_to_use = list(range(start_slot, start_slot + course.slots_req))
                    else:
                        continue  # Not enough consecutive slots from this start
                else:
                    # Can use non-consecutive slots
                    slots_to_use = [start_slot]
                
                # Check if all slots are available (no conflicts)
                slots_available = True
                for slot in slots_to_use:
                    if len(time_table[day][slot]) > 0:
                        # Check for conflicts at this slot
                        for existing_course in time_table[day][slot]:
                            # Would this create a conflict?
                            if not self._can_add_course(course, existing_course):
                                slots_available = False
                                break
                    if not slots_available:
                        break
                
                if slots_available:
                    # Assign course to all required slots
                    for slot in slots_to_use:
                        time_table[day][slot].append(course)
                    assigned = True
            
            if not assigned:
                # Failed to assign course, return None to indicate invalid timetable
                return None
        
        return time_table
    
    def _can_add_course(self, new_course, existing_course):
        # Check if new_course can be added to a slot with existing_course
        # Return False if they conflict
        
        # Professor conflict
        if new_course.instructor.id == existing_course.instructor.id:
            return False
        
        # Room conflict
        if new_course.room.id == existing_course.room.id:
            return False
        
        # Student group conflict (direct)
        if new_course.student_grp == existing_course.student_grp:
            return False
        
        # Student group conflict (super groups)
        if hasattr(new_course.student_grp, 'super_groups') and hasattr(existing_course.student_grp, 'super_groups'):
            if existing_course.student_grp in new_course.student_grp.super_groups:
                return False
            if new_course.student_grp in existing_course.student_grp.super_groups:
                return False
        elif hasattr(new_course.student_grp, 'super_groups'):
            if existing_course.student_grp in new_course.student_grp.super_groups:
                return False
        elif hasattr(existing_course.student_grp, 'super_groups'):
            if new_course.student_grp in existing_course.student_grp.super_groups:
                return False
        
        return True

    def fitness(self, time_table):
        # Evaluate the fitness of an individual using weighted sum of objective functions
        ptp_penalty = self._ptp_objective_function(time_table)
        rtr_penalty = self._rtr_objective_function(time_table)
        stability_penalty = self._course_stability_objective_function(time_table)
        
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

    def check_constraints(self, time_table):
        # Check if the time table satisfies all constraints
        
        for day in time_table:
            for time_slot in time_table[day]:
                courses = time_table[day][time_slot]
                
                # Check for professor collisions
                professor_ids = []
                for course in courses:
                    if course.instructor.id in professor_ids:
                        return False  # Professor conflict
                    professor_ids.append(course.instructor.id)
                
                # Check for student group collisions (direct groups)
                student_grps = []
                for course in courses:
                    if course.student_grp in student_grps:
                        return False  # Student group conflict
                    student_grps.append(course.student_grp)
                
                # Check for super group collisions
                for course in courses:
                    if hasattr(course.student_grp, 'super_groups'):
                        for super_grp in course.student_grp.super_groups:
                            # Check if this super group is in any other course's student group in this slot
                            for other_course in courses:
                                if other_course != course:
                                    # Check if super_grp is the student_grp of other_course
                                    if other_course.student_grp == super_grp:
                                        return False  # Super group conflict
                                    # Check if super_grp is in other_course's super groups
                                    if hasattr(other_course.student_grp, 'super_groups') and super_grp in other_course.student_grp.super_groups:
                                        return False  # Super group conflict
                
                # Check for room collisions
                room_ids = []
                for course in courses:
                    if course.room.id in room_ids:
                        return False  # Room conflict
                    room_ids.append(course.room.id)
                
                # Check room type constraint (lab courses must be in lab rooms)
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            return False  # Lab course not in lab room
                
                # Check room capacity constraint
                for course in courses:
                    if hasattr(course.student_grp, 'size') and hasattr(course.room, 'capacity'):
                        if course.room.capacity < course.student_grp.size:
                            return False  # Room too small for student group
            
            # Check constraint: only one lecture per day per course-student group combination
            lectures_per_day = {}
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        course_key = (course.course_id, course.student_grp)
                        if course_key not in lectures_per_day:
                            lectures_per_day[course_key] = 0
                        lectures_per_day[course_key] += 1
                        
                        if lectures_per_day[course_key] > 1:
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
                    return False  # Course not scheduled for the required number of slots
            else:
                return False  # Course not scheduled at all
        
        return True  # All constraints satisfied

    def run(self):
        # Main loop to run the genetic algorithm
        pass

    def _ptp_objective_function(self, time_table):
        # Calculate the professor time preference penalty value for a given time table
        
        penalty = 0
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    penalty += abs(self.preference_bins[time_slot] - course.preference)
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
                                break  # Only one super group should match in a valid timetable
                    
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