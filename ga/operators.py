
import random
import copy

class OperatorsMixin:
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
        course = tt[d][s].pop(idx)
        self.logger.debug(f"  [RELOCATE] Moving {course.course_id}-{course.session_type} from {d} s{s}")

        # Choose new day and slot
        d2 = random.choice(list(tt.keys()))
        s2 = random.choice(list(tt[d2].keys()))
        suitable_rooms = self._get_available_rooms(course)
        if not suitable_rooms:
            self.logger.debug(f"  [RELOCATE] No suitable rooms for this course → aborting")
            tt[d][s].insert(idx, course)
            return
        room = random.choice(suitable_rooms)
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
        rooms = self._get_available_rooms(course)
        rooms = [r for r in rooms if r != course.room]
        if not rooms:
            self.logger.debug("  [ROOM CHANGE] No alternative rooms available")
            return
        new_room = random.choice(rooms)
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