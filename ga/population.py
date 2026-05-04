import copy
import random

class PopulationMixin:
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
            
            # CRITICAL: Labs MUST always be assigned continuously in the same room
            if course.session_type == 'lab':
                # Force continuous assignment for labs
                assigned_count = self._assign_continuous_slots(course, time_table, shuffled_days, available_rooms)
            elif course.slots_continuous:
                # Other continuous courses
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
        
        # Validate all labs in the generated timetable follow continuity rules
        lab_validation = self._validate_lab_continuity(time_table)
        if not lab_validation:
            self.logger.info(f"    [INIT] ✗ Lab continuity validation FAILED")
            return None  # Reject timetable if labs don't follow rules
        
        self.logger.info(f"    [INIT] ✓ Lab continuity validation PASSED")
        return time_table
    
    def _get_lab_slots_on_day(self, time_table, day):
        """
        Get all lab courses and their slots on a specific day.
        
        Returns: dict mapping (course_id, grp_name) to list of slot numbers
        Example: {('PHY1101', 'CS1-Yr1'): [1, 2], ('PHY1101', 'AI1-Yr1'): [3, 4]}
        """
        lab_slots = {}
        for slot in time_table[day]:
            for course in time_table[day][slot]:
                if course.session_type == 'lab':
                    grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                    key = (course.course_id, grp_name)
                    if key not in lab_slots:
                        lab_slots[key] = []
                    if slot not in lab_slots[key]:
                        lab_slots[key].append(slot)
        
        return lab_slots
    
    def _get_lab_course_object(self, time_table, day, course_id, grp_name):
        """Get the first lab course object for given course_id and batch on day"""
        for slot in time_table[day]:
            for course in time_table[day][slot]:
                if (course.session_type == 'lab' and 
                    course.course_id == course_id):
                    course_grp = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                    if course_grp == grp_name:
                        return course
        return None
    
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
                    
                    # Validate room type constraint (labs only for labs, non-labs for lectures/tutorials)
                    if course.session_type == 'lab':
                        if not hasattr(assigned_room, 'is_lab') or not assigned_room.is_lab:
                            continue  # Skip this slot, room type mismatch
                    elif course.session_type in ['lecture', 'tutorial']:
                        if hasattr(assigned_room, 'is_lab') and assigned_room.is_lab:
                            continue  # Skip this slot, room type mismatch
                    
                    course_with_room = copy.copy(course)  # Shallow copy to preserve object references
                    course_with_room.room = assigned_room
                    
                    # Add the same course instance to all slots (ensures same room for all)
                    for slot in slots_to_use:
                        time_table[day][slot].append(course_with_room)
                    
                    # VALIDATION for labs: verify all slots use the same room
                    if course.session_type == 'lab':
                        rooms_in_slots = set()
                        for slot in slots_to_use:
                            for c in time_table[day][slot]:
                                if c.course_id == course.course_id and c.session_type == 'lab':
                                    rooms_in_slots.add(c.room.name if hasattr(c.room, 'name') else str(c.room))
                        
                        if len(rooms_in_slots) > 1:
                            self.logger.warning(f"        [WARNING] Lab {course.course_id} has multiple rooms in slots {slots_to_use}: {rooms_in_slots}")
                            # Remove the assignment and try next slot
                            for slot in slots_to_use:
                                time_table[day][slot] = [c for c in time_table[day][slot] if not (c.course_id == course.course_id and c.session_type == 'lab')]
                            continue
                        elif len(rooms_in_slots) == 1:
                            self.logger.info(f"        [ASSIGN] Assigned {day} slots {start_slot}-{start_slot + course.slots_req - 1} (room: {assigned_room.name}) [LAB VERIFIED]")
                    else:
                        self.logger.info(f"        [ASSIGN] Assigned {day} slots {start_slot}-{start_slot + course.slots_req - 1} (room: {assigned_room.name})")
                    
                    assigned_count = course.slots_req
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
                    # Validate room type constraint (labs only for labs, non-labs for lectures/tutorials)
                    if course.session_type == 'lab':
                        if not hasattr(assigned_room, 'is_lab') or not assigned_room.is_lab:
                            continue  # Skip this slot, room type mismatch
                    elif course.session_type in ['lecture', 'tutorial']:
                        if hasattr(assigned_room, 'is_lab') and assigned_room.is_lab:
                            continue  # Skip this slot, room type mismatch
                    
                    course_with_room = copy.copy(course)  # Shallow copy to preserve object references
                    course_with_room.room = assigned_room
                    time_table[day][slot].append(course_with_room)
                    assigned_count += 1
                    self.logger.info(f"        [ASSIGN] Slot {assigned_count}/{course.slots_req}: {day} slot {slot} (room: {assigned_room.name})")
        
        return assigned_count
    
    def _validate_lab_continuity(self, time_table):
        """
        Validate that all labs follow continuity rules:
        - Labs on the same day are in consecutive slots
        - Labs on the same day use the same room
        
        Returns True if valid, False if any lab violates rules
        """
        for day in time_table:
            lab_occurrences = {}  # {(course_id, student_grp): [(slot, room)]}
            
            for slot in time_table[day]:
                for course in time_table[day][slot]:
                    if course.session_type == 'lab':
                        key = (course.course_id, course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp))
                        if key not in lab_occurrences:
                            lab_occurrences[key] = []
                        room_name = course.room.name if hasattr(course.room, 'name') else str(course.room)
                        lab_occurrences[key].append((slot, room_name))
            
            # Check each lab occurrence on this day
            for (course_id, grp), occurrences in lab_occurrences.items():
                if len(occurrences) > 1:
                    slots = sorted([s for s, _ in occurrences])
                    rooms = [r for _, r in occurrences]
                    
                    # Check if all rooms are the same
                    if len(set(rooms)) > 1:
                        self.logger.error(f"    [LAB VALIDATION] ✗ {course_id} for {grp} on {day}: "
                                        f"Multiple rooms detected in slots {slots}: {set(rooms)}")
                        return False
                    
                    # Check if slots are consecutive
                    for i in range(len(slots) - 1):
                        if slots[i+1] - slots[i] != 1:
                            self.logger.error(f"    [LAB VALIDATION] ✗ {course_id} for {grp} on {day}: "
                                            f"Non-consecutive slots {slots}")
                            return False
        
        return True
    
    def _generate_random_timetable(self):
        # [DEPRECATED] Use _generate_smart_timetable instead
        # Kept for backwards compatibility
        return self._generate_smart_timetable()

    def run(self, convergence_threshold=0.1, min_generations=5, max_generations=None):
        """
        Run the genetic algorithm to find the optimal timetable.
        
        Args:
            convergence_threshold: If improvement is less than this, consider it converged
            min_generations: Minimum number of generations to run before checking convergence
            max_generations: Maximum number of generations (prevents infinite loops)
        
        Returns:
            best_timetable: The best timetable found
            best_fitness: The fitness value of the best timetable
        """
        if max_generations is None:
            max_generations = self.generations
        
        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING GENETIC ALGORITHM")
        self.logger.info("="*80)
        self.logger.info(f"Population size: {self.population_size}")
        self.logger.info(f"Max generations: {max_generations}")
        self.logger.info(f"Convergence threshold: {convergence_threshold}")
        self.logger.info(f"Min generations: {min_generations}")
        
        # Step 1: Initialize population
        self.logger.info("\n[GA] Step 1: Creating initial population...")
        population = self.create_population()
        
        if not population:
            self.logger.error("[GA] ✗ Failed to create initial population")
            return None, float('inf')
        
        # Step 2: Evaluate initial candidates
        self.logger.info(f"\n[GA] Step 2: Evaluating {len(population)} initial candidates...")
        fitnesses = [self.fitness(timetable) for timetable in population]
        best_fitness = min(fitnesses)
        best_timetable = population[fitnesses.index(best_fitness)]
        
        self.logger.info(f"[GA] Initial best fitness: {best_fitness:.2f}")
        
        # Track convergence
        previous_best_fitness = best_fitness
        generation = 0
        no_improvement_count = 0
        
        # Main GA loop
        while generation < max_generations:
            generation += 1
            self.logger.info(f"\n[GA] Generation {generation}/{max_generations}")
            
            # Step 3 & 4: Generate N new candidates through selection, crossover, and mutation
            self.logger.info(f"[GA] Generating {len(population)} new candidates...")
            new_candidates = []
            valid_count = 0
            
            attempts = 0
            max_attempts = len(population) * 3  # Try up to 3x to get N valid candidates
            
            while len(new_candidates) < len(population) and attempts < max_attempts:
                attempts += 1
                
                # Select 2 parents
                parent1, parent2 = self.select_parents(population, fitnesses)
                
                # Crossover
                child = self.crossover(parent1, parent2)
                
                # Mutation
                mutated_child = self.mutate(child)
                
                # Step 4: Check if mutated candidate satisfies constraints
                if self.check_constraints(mutated_child, verbose=False):
                    new_candidates.append(mutated_child)
                    valid_count += 1
            
            self.logger.info(f"[GA] Created {valid_count} valid candidates from {attempts} attempts")
            
            # Step 6: Combine population and new candidates, then select best N
            self.logger.info(f"[GA] Selecting best {len(population)} from {len(population) + len(new_candidates)} candidates...")
            combined_population = population + new_candidates
            combined_fitnesses = [self.fitness(timetable) for timetable in combined_population]
            
            # Sort by fitness (lower is better) and keep top N
            sorted_indices = sorted(range(len(combined_fitnesses)), key=lambda i: combined_fitnesses[i])
            population = [combined_population[i] for i in sorted_indices[:len(population)]]
            fitnesses = [combined_fitnesses[i] for i in sorted_indices[:len(population)]]
            
            # Update best solution
            current_best_fitness = min(fitnesses)
            current_best_idx = fitnesses.index(current_best_fitness)
            current_best_timetable = population[current_best_idx]
            
            # Step 7: Check convergence
            improvement = previous_best_fitness - current_best_fitness
            
            self.logger.info(f"[GA] Generation best fitness: {current_best_fitness:.2f}")
            self.logger.info(f"[GA] Improvement: {improvement:.2f}")
            
            if current_best_fitness < best_fitness:
                best_fitness = current_best_fitness
                best_timetable = current_best_timetable
                no_improvement_count = 0
                self.logger.info(f"[GA] ✓ New best found! Best fitness: {best_fitness:.2f}")
            else:
                no_improvement_count += 1
            
            # Check convergence criteria
            if generation >= min_generations:
                if improvement < convergence_threshold:
                    self.logger.info(f"[GA] Convergence detected! (improvement {improvement:.4f} < threshold {convergence_threshold})")
                    break
            
            previous_best_fitness = current_best_fitness
        
        # Final summary
        self.logger.info("\n" + "="*80)
        self.logger.info("GENETIC ALGORITHM COMPLETED")
        self.logger.info("="*80)
        self.logger.info(f"Total generations run: {generation}")
        self.logger.info(f"Best fitness achieved: {best_fitness:.2f}")
        self.logger.info("="*80)
        
        return best_timetable, best_fitness