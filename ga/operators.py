
import random
import copy

class OperatorsMixin:
    def _is_lab_course(self, course):
        """Check if course is a lab session"""
        return hasattr(course, 'session_type') and course.session_type == 'lab'
    
    def _get_lab_pair_slots(self, course, time_table):
        """Get all slots for a lab course on the same day, if continuous"""
        if not self._is_lab_course(course):
            return []
        if not getattr(course, 'slots_continuous', False):
            return []
        
        lab_slots = []
        for day in time_table:
            for slot in time_table[day]:
                for c in time_table[day][slot]:
                    if (c.course_id == course.course_id and 
                        self._is_lab_course(c)):
                        lab_slots.append((day, slot))
        return lab_slots
    
    def mutate(self, time_table):
        mutated = copy.deepcopy(time_table)
        operator = random.choice(['swap', 'relocate', 'room_change'])
        self.logger.debug(f"[MUTATE] Operator chosen: {operator}")
        
        if operator == 'swap':
            self._mutate_swap(mutated)
        elif operator == 'relocate':
            self._mutate_relocate(mutated)
        else:
            self._mutate_room_change(mutated)
        
        # Check constraints after mutation
        if not self.check_constraints(mutated, verbose=False):
            self.logger.debug("[MUTATE] Resulting timetable invalid → reverting to original")
            mutated = time_table
        else:
            # Quick check if it actually changed (only log if verbose)
            changed = (self._serialise_timetable(mutated) != self._serialise_timetable(time_table))
            if changed:
                self.logger.debug("[MUTATE] Mutation accepted (valid & changed)")
            else:
                self.logger.debug("[MUTATE] Mutation left timetable unchanged (but valid)")
        return mutated

    def _serialise_timetable(self, tt):
        """Helper to compare timetables quickly."""
        return str([
            (day, slot, [(c.course_id, c.session_type, c.room.name) for c in slist])
            for day, slots in tt.items()
            for slot, slist in slots.items()
        ])

    def _mutate_swap(self, tt):
        slots = [(d, s) for d in tt for s in tt[d] if tt[d][s]]
        if len(slots) < 2:
            self.logger.debug("  [SWAP] Not enough occupied slots (<2)")
            return
        (d1, s1), (d2, s2) = random.sample(slots, 2)
        i1 = random.randrange(len(tt[d1][s1]))
        i2 = random.randrange(len(tt[d2][s2]))
        
        # Don't swap lab courses (would break continuity)
        if self._is_lab_course(tt[d1][s1][i1]) or self._is_lab_course(tt[d2][s2][i2]):
            self.logger.debug(f"  [SWAP] Skipped - cannot swap lab courses (breaks continuity)")
            return
        
        self.logger.debug(f"  [SWAP] Swapping {tt[d1][s1][i1].course_id}-{tt[d1][s1][i1].session_type} "
                          f"({d1} s{s1}) <-> {tt[d2][s2][i2].course_id}-{tt[d2][s2][i2].session_type} "
                          f"({d2} s{s2})")
        tt[d1][s1][i1], tt[d2][s2][i2] = tt[d2][s2][i2], tt[d1][s1][i1]

    def _mutate_relocate(self, tt):
        occupied = [(d, s, i) for d in tt for s in tt[d] for i in range(len(tt[d][s]))]
        if not occupied:
            self.logger.debug("  [RELOCATE] No courses to move")
            return
        d, s, idx = random.choice(occupied)
        course = tt[d][s][idx]
        
        # For lab courses, move all instances together to maintain continuity
        if self._is_lab_course(course):
            lab_slots = self._get_lab_pair_slots(course, tt)
            if len(lab_slots) <= 1:
                self.logger.debug(f"  [RELOCATE] Skipped - lab {course.course_id} only has 1 slot")
                return
            
            # Choose new day and slot for all lab instances
            d2 = random.choice(list(tt.keys()))
            s2 = random.choice(list(tt[d2].keys()))
            suitable_rooms = self._get_available_rooms(course)
            if not suitable_rooms:
                self.logger.debug(f"  [RELOCATE] No suitable rooms for this lab course → aborting")
                return
            
            # Move all lab instances to new location with same room
            shuffled_suitable_rooms = list(suitable_rooms)
            random.shuffle(shuffled_suitable_rooms)
            new_room = shuffled_suitable_rooms[0]
            
            # Remove from old slots
            for old_day, old_slot in lab_slots:
                tt[old_day][old_slot] = [c for c in tt[old_day][old_slot] 
                                         if not (c.course_id == course.course_id and self._is_lab_course(c))]
            
            # Add to new slot with same room - CREATE SINGLE COPY FOR ALL SLOTS
            lab_copy = copy.copy(course)
            lab_copy.room = new_room
            for i in range(len(lab_slots)):  # Add SAME copy to all slots
                tt[d2][s2].append(lab_copy)
            
            self.logger.debug(f"  [RELOCATE] Moving lab {course.course_id} (all instances) from {d} to {d2} s{s2}, room {new_room.name}")
            return
        
        # Normal (non-lab) course relocation
        tt[d][s].pop(idx)
        self.logger.debug(f"  [RELOCATE] Moving {course.course_id}-{course.session_type} from {d} s{s}")

        # Choose new day and slot
        d2 = random.choice(list(tt.keys()))
        s2 = random.choice(list(tt[d2].keys()))
        suitable_rooms = self._get_available_rooms(course)
        if not suitable_rooms:
            self.logger.debug(f"  [RELOCATE] No suitable rooms for this course → aborting")
            tt[d][s].insert(idx, course)
            return
        shuffled_suitable_rooms = list(suitable_rooms)
        random.shuffle(shuffled_suitable_rooms)
        room = shuffled_suitable_rooms[0]
        self.logger.debug(f"  [RELOCATE] Placing in {d2} s{s2}, room {room.name}")
        course.room = room
        tt[d2][s2].append(course)

    def _mutate_room_change(self, tt):
        all_courses = [(d, s, i) for d in tt for s in tt[d] for i in range(len(tt[d][s]))]
        if not all_courses:
            self.logger.debug("  [ROOM CHANGE] No courses available")
            return
        d, s, idx = random.choice(all_courses)
        course = tt[d][s][idx]
        self.logger.debug(f"  [ROOM CHANGE] Trying to change room for {course.course_id}-{course.session_type} "
                          f"currently in {course.room.name}")
        
        # For lab courses, change room for ALL instances (to keep them in same room)
        if self._is_lab_course(course):
            rooms = self._get_available_rooms(course)
            rooms = [r for r in rooms if r != course.room]
            if not rooms:
                self.logger.debug("  [ROOM CHANGE] No alternative rooms available for lab")
                return
            shuffled_rooms = list(rooms)
            random.shuffle(shuffled_rooms)
            new_room = shuffled_rooms[0]
            
            # Change room for all instances of this lab on the same day
            for slot in tt[d]:
                for i, c in enumerate(tt[d][slot]):
                    if c.course_id == course.course_id and self._is_lab_course(c):
                        tt[d][slot][i].room = new_room
            
            self.logger.debug(f"  [ROOM CHANGE] Changed lab {course.course_id} to {new_room.name} (all instances on {d})")
            return
        
        # Normal (non-lab) room change
        rooms = self._get_available_rooms(course)
        rooms = [r for r in rooms if r != course.room]
        if not rooms:
            self.logger.debug("  [ROOM CHANGE] No alternative rooms available")
            return
        shuffled_rooms = list(rooms)
        random.shuffle(shuffled_rooms)
        new_room = shuffled_rooms[0]
        self.logger.debug(f"  [ROOM CHANGE] Changing room to {new_room.name}")
        course.room = new_room

    def select_parents(self, population, fitnesses):
        # Tournament selection: pick k random individuals, choose the one with lowest fitness.
        # Returns two parents.
        if len(population) < 2:
            raise ValueError("Population too small")
        
        def tournament():
            # Get indices of k random individuals
            k = min(3, len(population))  # tournament size 3
            indices = random.sample(range(len(population)), k)
            best_idx = min(indices, key=lambda i: fitnesses[i])
            return population[best_idx]
        
        parent1 = tournament()
        parent2 = tournament()
        return parent1, parent2
    
    def crossover(self, parent1, parent2):
        """
        Uniform crossover at the day-slot level with lab continuity preservation.
        
        Key insight: Keep all slots of a lab from the SAME parent to prevent fragmentation.
        1. For each day, identify lab courses and their slots
        2. For each lab, pick ONE parent and take all its slots from that parent
        3. For non-lab slots, randomly select from either parent
        
        Returns a new timetable (deep copy of selected parts).
        """
        import copy
        import random
        
        child = {}
        
        for day in parent1:
            child[day] = {}
            
            # Step 1: Identify all lab courses on this day and their slot ranges in both parents
            lab_slots_p1 = self._get_lab_slots_on_day(parent1, day)
            lab_slots_p2 = self._get_lab_slots_on_day(parent2, day)
            
            # Merge to get all lab course IDs on this day
            all_lab_ids = set(lab_slots_p1.keys()) | set(lab_slots_p2.keys())
            
            # Track which slots are assigned from labs
            lab_assigned_slots = set()
            
            # Step 2: For each lab, pick ONE parent and take all its slots
            for lab_id in all_lab_ids:
                pick_parent = random.choice([parent1, parent2])
                
                # Get lab slots from the picked parent
                if pick_parent == parent1:
                    slots_to_copy = lab_slots_p1.get(lab_id, [])
                    parent_to_copy = parent1
                else:
                    slots_to_copy = lab_slots_p2.get(lab_id, [])
                    parent_to_copy = parent2
                
                # Copy all slots for this lab from the chosen parent
                for slot in slots_to_copy:
                    if slot in child[day]:
                        # Slot already assigned, extend the list
                        child[day][slot].extend(copy.deepcopy(parent_to_copy[day][slot]))
                    else:
                        # New slot, copy it
                        child[day][slot] = copy.deepcopy(parent_to_copy[day][slot])
                    lab_assigned_slots.add(slot)
            
            # Step 3: For remaining non-lab slots, randomly select from either parent
            for slot in parent1[day].keys():
                if slot not in lab_assigned_slots:
                    # This slot doesn't contain labs, randomly pick from parent
                    if random.random() < 0.5:
                        child[day][slot] = copy.deepcopy(parent1[day][slot])
                    else:
                        child[day][slot] = copy.deepcopy(parent2[day][slot])
        
        # Step 4: Validation - ensure lab integrity after crossover
        if not self._validate_crossover_lab_integrity(child):
            self.logger.debug("[CROSSOVER] Lab integrity check failed, attempting repair")
        
        return child
    
    def _validate_crossover_lab_integrity(self, child):
        """
        Verify that all lab slots on the same day for the same batch use the same object reference.
        If fragmented, returns False (caller can handle).
        """
        for day in child:
            lab_instances = {}  # (course_id, grp_name) -> [objects]
            
            for slot in child[day]:
                for course in child[day][slot]:
                    if course.session_type == 'lab':
                        grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                        key = (course.course_id, grp_name)
                        if key not in lab_instances:
                            lab_instances[key] = []
                        lab_instances[key].append((slot, course))
            
            # Check each lab course for object fragmentation
            for (course_id, grp_name), instances in lab_instances.items():
                if len(instances) > 1:
                    # Check if all instances are the same object (good) or different (bad)
                    first_obj = instances[0][1]
                    for slot, course in instances[1:]:
                        if course is not first_obj:
                            return False  # Objects are different - fragmentation detected
        
        return True