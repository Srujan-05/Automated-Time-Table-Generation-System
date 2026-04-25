import logging
import random
import copy

class GASearchImproved:
    """
    Improved Genetic Algorithm with:
    - Real crossover operators
    - Mutation operations
    - Tournament selection
    - Preference-aware initialization
    - Multi-generational evolution
    """
    
    def __init__(self, time_slots, courses, preference_bins, objective_function_weights, rooms, 
                 population_size=20, generations=100, mutation_rate=0.1):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Convert time_slots if needed
        self.time_slots = time_slots
        if isinstance(time_slots, int):
            self.time_slots = {
                'Monday': time_slots,
                'Tuesday': time_slots,
                'Wednesday': time_slots,
                'Thursday': time_slots,
                'Friday': time_slots
            }
        
        self.courses = courses
        self.preference_bins = preference_bins
        self.objective_function_weights = objective_function_weights
        self.rooms = rooms
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.best_fitness_history = []

    def create_population(self):
        """Create initial population with preference-aware initialization"""
        self.logger.info(f"\n[POPULATION] Starting population creation (target size: {self.population_size})")
        population = []
        failed_attempts = 0
        max_failed_attempts = 5
        
        while len(population) < self.population_size:
            self.logger.info(f"\n[POPULATION] Attempt {len(population) + 1 + failed_attempts}/{self.population_size + failed_attempts}")
            time_table = self._generate_preference_aware_timetable()
            
            if time_table:
                constraint_check = self.check_constraints(time_table, verbose=True)
            else:
                constraint_check = False
            
            if constraint_check:
                population.append(time_table)
                failed_attempts = 0
                self.logger.info(f"[POPULATION] ✓ Candidate {len(population)}/{self.population_size} created")
            else:
                failed_attempts += 1
                self.logger.info(f"[POPULATION] ✗ FAILED (attempt #{failed_attempts})")
                if failed_attempts >= max_failed_attempts:
                    break
        
        self.logger.info(f"\n[POPULATION] Population creation complete: {len(population)} candidates")
        return population
    
    def _generate_preference_aware_timetable(self):
        """Generate timetable - use proven greedy logic from basic GA"""
        import random
        import copy
        
        self.logger.info("    [INIT] Initializing timetable...")
        
        # Initialize timetable
        time_table = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for day in days:
            time_table[day] = {}
            day_slots = self.time_slots.get(day, 10)
            for slot in range(1, day_slots + 1):
                time_table[day][slot] = []
        
        # Simple greedy: sort by slots needed, then randomize
        session_type_priority = {
            'lab': random.randint(0, 2),
            'lecture': random.randint(0, 2),
            'tutorial': random.randint(0, 2)
        }
        
        courses_to_schedule = sorted(
            self.courses,
            key=lambda c: (
                session_type_priority.get(c.session_type, 3),
                -c.slots_req,
                -(c.student_grp.size if hasattr(c.student_grp, 'size') else 0),
                random.random()
            )
        )
        
        scheduled = 0
        failed_courses = []
        
        for course in courses_to_schedule:
            assigned_count = 0
            available_rooms = self._get_available_rooms(course)
            
            if not available_rooms:
                failed_courses.append(course)
                continue
            
            shuffled_days = list(days)
            random.shuffle(shuffled_days)
            
            if course.slots_continuous:
                assigned_count = self._assign_continuous_slots_simple(course, time_table, shuffled_days, available_rooms)
            else:
                assigned_count = self._assign_non_continuous_slots_simple(course, time_table, shuffled_days, available_rooms)
            
            if assigned_count == course.slots_req:
                scheduled += 1
            else:
                failed_courses.append(course)
        
        self.logger.info(f"    [INIT] Scheduling complete: {scheduled}/{len(courses_to_schedule)} courses fully scheduled")
        
        if failed_courses:
            return None
        
        return time_table
    
    def _assign_continuous_slots_simple(self, course, time_table, days, available_rooms):
        """Simple continuous slot assignment"""
        import random
        import copy
        
        assigned_count = 0
        
        for day in days:
            if assigned_count >= course.slots_req:
                break
            
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
                            break
                    if course_already_on_day:
                        break
                
                if course_already_on_day:
                    continue
            
            day_slots = self.time_slots.get(day, 10)
            for start_slot in range(1, day_slots - course.slots_req + 2):
                if assigned_count >= course.slots_req:
                    break
                
                slots_to_use = list(range(start_slot, start_slot + course.slots_req))
                slots_available = True
                
                for slot in slots_to_use:
                    if len(time_table[day][slot]) > 0:
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
                    assigned_room = random.choice(available_rooms)
                    # Create a copy for this day to hold the room assignment
                    course_copy = copy.copy(course)
                    course_copy.room = assigned_room
                    course_copy._orig_id = getattr(course, '_orig_id', id(course))
                    
                    for slot in slots_to_use:
                        time_table[day][slot].append(course_copy)
                    assigned_count = course.slots_req
                    break
        
        return assigned_count
    
    def _assign_non_continuous_slots_simple(self, course, time_table, days, available_rooms):
        """Simple non-continuous slot assignment - one slot per day for lectures"""
        import random
        import copy
        
        assigned_count = 0
        
        for day in days:
            if assigned_count >= course.slots_req:
                break
            
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
                            break
                    if course_already_on_day:
                        break
                
                if course_already_on_day:
                    continue  # Skip this day, lecture already scheduled
            
            day_slots = self.time_slots.get(day, 10)
            day_assigned = False  # Track if we assigned anything on this day for lectures
            
            for slot in range(1, day_slots + 1):
                if assigned_count >= course.slots_req:
                    break
                
                slot_available = False
                assigned_room = None
                
                if len(time_table[day][slot]) == 0:
                    slot_available = True
                    assigned_room = random.choice(available_rooms)
                else:
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
                    # Create a fresh copy for this slot
                    course_copy = copy.copy(course)
                    course_copy.room = assigned_room
                    course_copy._orig_id = getattr(course, '_orig_id', id(course))
                    time_table[day][slot].append(course_copy)
                    assigned_count += 1
                    
                    # For lectures, only assign one slot per day
                    if course.session_type == 'lecture':
                        day_assigned = True
                        break  # Move to next day
        
        return assigned_count

    def _get_available_rooms(self, course):
        available_rooms = []
        
        for room in self.rooms:
            if course.session_type == 'lab':
                if not hasattr(room, 'is_lab') or not room.is_lab:
                    continue
            
            if hasattr(course.student_grp, 'size') and hasattr(room, 'capacity'):
                if room.capacity < course.student_grp.size:
                    continue
            
            available_rooms.append(room)
        
        return available_rooms
    
    def _can_add_course(self, new_course, assigned_room, existing_course):
        # Professor conflict
        if new_course.instructor.id == existing_course.instructor.id:
            return False
        
        # Room conflict
        if assigned_room.id == existing_course.room.id:
            return False
        
        # Student group conflicts
        new_grp_name = new_course.student_grp.name if hasattr(new_course.student_grp, 'name') else str(new_course.student_grp)
        existing_grp_name = existing_course.student_grp.name if hasattr(existing_course.student_grp, 'name') else str(existing_course.student_grp)
        
        if new_grp_name == existing_grp_name:
            return False
        
        if hasattr(new_course.student_grp, 'super_groups') and hasattr(existing_course.student_grp, 'super_groups'):
            new_super_names = [s.name if hasattr(s, 'name') else str(s) for s in new_course.student_grp.super_groups]
            existing_super_names = [s.name if hasattr(s, 'name') else str(s) for s in existing_course.student_grp.super_groups]
            if existing_grp_name in new_super_names or new_grp_name in existing_super_names:
                return False
            if set(new_super_names) & set(existing_super_names):
                return False
        
        return True

    def check_constraints(self, time_table, verbose=False):
        """Check all hard constraints"""
        for day in time_table:
            for time_slot in time_table[day]:
                courses = time_table[day][time_slot]
                
                # Professor collisions
                professor_ids = []
                for course in courses:
                    if course.instructor.id in professor_ids:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Professor conflict")
                        return False
                    professor_ids.append(course.instructor.id)
                
                # Student group collisions
                student_grp_names = []
                for course in courses:
                    grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                    if grp_name in student_grp_names:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Student group conflict ({grp_name})")
                        return False
                    student_grp_names.append(grp_name)
                
                # Room collisions
                room_ids = []
                for course in courses:
                    if course.room.id in room_ids:
                        if verbose:
                            self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Room conflict")
                        return False
                    room_ids.append(course.room.id)
                
                # Lab room constraint
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            if verbose:
                                self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Lab in non-lab room")
                            return False
                
                # Room capacity
                for course in courses:
                    if hasattr(course.student_grp, 'size') and hasattr(course.room, 'capacity'):
                        if course.room.capacity < course.student_grp.size:
                            if verbose:
                                self.logger.info(f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: Room too small")
                            return False
        
        # Lectures per day constraint
        for day in time_table:
            lectures_per_day = {}
            seen_lecture_instances = set()  # Track unique course instances
            
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                        # Use instance ID to deduplicate (same course object might appear in multiple slots)
                        instance_key = (course.course_id, grp_name, id(course))
                        
                        if instance_key not in seen_lecture_instances:
                            seen_lecture_instances.add(instance_key)
                            course_key = (course.course_id, grp_name)
                            if course_key not in lectures_per_day:
                                lectures_per_day[course_key] = {'count': 0, 'lecture_consecutive': getattr(course, 'lecture_consecutive', False)}
                            lectures_per_day[course_key]['count'] += 1
                            
                            if not lectures_per_day[course_key]['lecture_consecutive']:
                                if lectures_per_day[course_key]['count'] > 1:
                                    if verbose:
                                        self.logger.info(f"    [CONSTRAINT FAIL] {day}: Multiple lectures for {course_key}")
                                    return False
        
        # Slot requirements
        course_slot_count = {}
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    # Use _orig_id if available, otherwise use the course's id attribute, otherwise use Python id()
                    course_id = getattr(course, '_orig_id', getattr(course, 'id', id(course)))
                    course_slot_count[course_id] = course_slot_count.get(course_id, 0) + 1
        
        for course in self.courses:
            course_id = getattr(course, '_orig_id', getattr(course, 'id', id(course)))
            if course_slot_count.get(course_id, 0) != course.slots_req:
                if verbose:
                    self.logger.info(f"    [CONSTRAINT FAIL] {course.course_id}: Wrong slot count (have {course_slot_count.get(course_id, 0)}, need {course.slots_req})")
                return False
        
        return True

    def fitness(self, time_table):
        """Calculate fitness with improved weighting"""
        ptp_penalty = self._ptp_objective_function(time_table)
        rtr_penalty = self._rtr_objective_function(time_table)
        stability_penalty = self._ctrr_objective_function(time_table)
        
        # IMPROVED: Reduce stability weight, focus on preference + distance
        total_penalty = (
            self.objective_function_weights[0] * ptp_penalty +
            self.objective_function_weights[1] * rtr_penalty +
            self.objective_function_weights[2] * stability_penalty
        )
        
        return total_penalty

    def _ptp_objective_function(self, time_table):
        """Course Time Preference penalty"""
        penalty = 0
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    if time_slot in self.preference_bins:
                        penalty += abs(self.preference_bins[time_slot] - course.preference_bin)
        return penalty
    
    def _rtr_objective_function(self, time_table):
        """Room-to-Room Distance penalty"""
        penalty = 0
        for day in time_table:
            time_slots = sorted(time_table[day].keys())
            
            for i in range(len(time_slots) - 1):
                current_slot = time_slots[i]
                next_slot = time_slots[i + 1]
                
                current_courses = time_table[day][current_slot]
                next_courses = time_table[day][next_slot]
                
                current_grp_rooms = {}
                for course in current_courses:
                    if course.student_grp not in current_grp_rooms:
                        current_grp_rooms[course.student_grp] = course.room
                
                next_grp_rooms = {}
                for course in next_courses:
                    if course.student_grp not in next_grp_rooms:
                        next_grp_rooms[course.student_grp] = course.room
                
                for curr_grp, curr_room in current_grp_rooms.items():
                    next_grp_match = None
                    
                    if curr_grp in next_grp_rooms:
                        next_grp_match = curr_grp
                    elif hasattr(curr_grp, 'super_groups'):
                        for super_grp in curr_grp.super_groups:
                            if super_grp in next_grp_rooms:
                                next_grp_match = super_grp
                                break
                    
                    if next_grp_match:
                        next_room = next_grp_rooms[next_grp_match]
                        distance = abs(curr_room.x - next_room.x) + abs(curr_room.y - next_room.y) + abs(curr_room.z - next_room.z)
                        penalty += distance
        
        return penalty

    def _ctrr_objective_function(self, time_table):
        """Course Stability penalty"""
        penalty = 0
        course_sessions = {}
        
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_key = (course.course_id, course.session_type)
                    
                    if course_key not in course_sessions:
                        course_sessions[course_key] = []
                    
                    course_sessions[course_key].append((time_slot, course.room))
        
        for course_key, sessions in course_sessions.items():
            if len(sessions) > 1:
                reference_slot, reference_room = sessions[0]
                
                for slot, room in sessions[1:]:
                    if slot != reference_slot:
                        penalty += 2  # Higher penalty for different slots
                    if room != reference_room:
                        penalty += 1
        
        return penalty

    def select_parents(self, population, fitness_scores, tournament_size=3):
        """Tournament selection"""
        selected = []
        for _ in range(len(population)):
            tournament_idx = random.sample(range(len(population)), tournament_size)
            best_tournament_idx = min(tournament_idx, key=lambda i: fitness_scores[i])
            selected.append(population[best_tournament_idx])
        return selected

    def crossover(self, parent1, parent2):
        """Single-point crossover: swap courses between two days"""
        import copy
        
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        days = list(parent1.keys())
        crossover_day_idx = random.randint(0, len(days) - 1)
        crossover_day = days[crossover_day_idx]
        
        # Swap all courses on crossover day
        child1[crossover_day], child2[crossover_day] = child2[crossover_day], child1[crossover_day]
        
        return child1, child2

    def mutate(self, time_table):
        """Mutation: move random course to different slot"""
        import copy
        import random
        
        mutated = copy.deepcopy(time_table)
        
        if random.random() > self.mutation_rate:
            return mutated
        
        days = list(mutated.keys())
        
        # Try to find and move a course
        for _ in range(5):  # Try 5 times
            random_day = random.choice(days)
            slots_in_day = list(mutated[random_day].keys())
            
            # Find non-empty slot
            non_empty_slots = [s for s in slots_in_day if len(mutated[random_day][s]) > 0]
            if not non_empty_slots:
                continue
            
            source_slot = random.choice(non_empty_slots)
            if not mutated[random_day][source_slot]:
                continue
            
            course = random.choice(mutated[random_day][source_slot])
            
            # Try to move to different day/slot
            target_day = random.choice(days)
            target_slot = random.choice(slots_in_day)
            
            # Check if move is valid (no conflicts)
            # For simplicity, just try moving
            try:
                mutated[random_day][source_slot].remove(course)
                
                # Check constraints
                test_copy = copy.deepcopy(mutated)
                test_copy[target_day][target_slot].append(course)
                
                if self.check_constraints(test_copy, verbose=False):
                    mutated = test_copy
                    return mutated
                else:
                    # Revert
                    mutated[random_day][source_slot].append(course)
            except:
                continue
        
        return mutated

    def run(self):
        """Main GA loop with multi-generational evolution"""
        self.logger.info(f"\n[GA] Starting Improved Genetic Algorithm")
        self.logger.info(f"[GA] Population size: {self.population_size}")
        self.logger.info(f"[GA] Generations: {self.generations}")
        self.logger.info(f"[GA] Mutation rate: {self.mutation_rate}")
        
        population = self.create_population()
        
        if not population:
            self.logger.info("[GA] ❌ Failed to create valid population")
            return None
        
        best_overall = None
        best_overall_fitness = float('inf')
        
        for generation in range(self.generations):
            self.logger.info(f"\n[GA] Generation {generation + 1}/{self.generations}")
            
            # Evaluate fitness
            fitness_scores = [self.fitness(tt) for tt in population]
            
            # Track best
            gen_best_idx = fitness_scores.index(min(fitness_scores))
            gen_best_fitness = fitness_scores[gen_best_idx]
            
            self.logger.info(f"[GA] Generation Best: {gen_best_fitness:.2f} | Avg: {sum(fitness_scores)/len(fitness_scores):.2f}")
            self.best_fitness_history.append(gen_best_fitness)
            
            if gen_best_fitness < best_overall_fitness:
                best_overall_fitness = gen_best_fitness
                best_overall = population[gen_best_idx]
            
            # Selection
            parents = self.select_parents(population, fitness_scores)
            
            # Crossover
            offspring = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1, child2 = self.crossover(parents[i], parents[i + 1])
                    offspring.extend([child1, child2])
                else:
                    offspring.append(parents[i])
            
            # Mutation
            offspring = [self.mutate(child) for child in offspring]
            
            # Validate offspring
            valid_offspring = []
            for child in offspring:
                if self.check_constraints(child, verbose=False):
                    valid_offspring.append(child)
            
            # Replace worst candidates
            if valid_offspring:
                sorted_indices = sorted(range(len(population)), key=lambda i: fitness_scores[i], reverse=True)
                replace_count = min(len(valid_offspring), len(sorted_indices) // 2)
                
                for i in range(replace_count):
                    population[sorted_indices[i]] = valid_offspring[i]
        
        self.logger.info(f"\n[GA] ✅ Evolution complete!")
        self.logger.info(f"[GA] Best fitness found: {best_overall_fitness:.2f}")
        
        return best_overall
