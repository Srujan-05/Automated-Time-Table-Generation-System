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
        # Create an initial random population
        pass

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
        pass

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