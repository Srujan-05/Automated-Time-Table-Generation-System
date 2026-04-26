import random
import copy

class OperatorsMixin:
    def mutate(self, time_table):
        mutated = copy.deepcopy(time_table)
        operator = random.choice(['swap', 'relocate', 'room_change'])
        if operator == 'swap':
            self._mutate_swap(mutated)
        elif operator == 'relocate':
            self._mutate_relocate(mutated)
        else:
            self._mutate_room_change(mutated)
        # optional feasibility fix
        if not self.check_constraints(mutated, verbose=False):
            mutated = time_table  # revert
        return mutated

    def _mutate_swap(self, tt):
        # pick two occupied slots and swap courses
        slots = [(d,s) for d in tt for s in tt[d] if tt[d][s]]
        if len(slots) < 2: return
        (d1, s1), (d2, s2) = random.sample(slots, 2)
        i1, i2 = random.randrange(len(tt[d1][s1])), random.randrange(len(tt[d2][s2]))
        tt[d1][s1][i1], tt[d2][s2][i2] = tt[d2][s2][i2], tt[d1][s1][i1]
        # rooms stay with the course object itself

    def _mutate_relocate(self, tt):
        # move a course to a new empty/invisible slot
        occupied = [(d,s,i) for d in tt for s in tt[d] for i in range(len(tt[d][s]))]
        if not occupied: return
        d, s, idx = random.choice(occupied)
        course = tt[d][s].pop(idx)
        # choose a random day and slot (room pre‑selected)
        d2 = random.choice(list(tt.keys()))
        s2 = random.choice(list(tt[d2].keys()))
        suitable_rooms = self._get_available_rooms(course)
        if not suitable_rooms:  # fallback: put it back
            tt[d][s].insert(idx, course)
            return
        room = random.choice(suitable_rooms)
        course.room = room
        tt[d2][s2].append(course)

    def _mutate_room_change(self, tt):
        # change room for a single course
        all_courses = [(d,s,i) for d in tt for s in tt[d] for i in range(len(tt[d][s]))]
        if not all_courses: return
        d, s, idx = random.choice(all_courses)
        course = tt[d][s][idx]
        rooms = self._get_available_rooms(course)
        rooms = [r for r in rooms if r != course.room]  # different room
        if rooms:
            course.room = random.choice(rooms)

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