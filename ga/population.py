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
        
        return assigned_count
    
    def _generate_random_timetable(self):
        # [DEPRECATED] Use _generate_smart_timetable instead
        # Kept for backwards compatibility
        return self._generate_smart_timetable()