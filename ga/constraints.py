class ConstraintsMixin:
    def _ancestors(self, group):
        """Return a set of name strings of the group and all its super_groups (recursively)."""
        names = set()
        stack = [group]
        while stack:
            g = stack.pop()
            name = g.name if hasattr(g, 'name') else str(g)
            if name not in names:
                names.add(name)
                if hasattr(g, 'super_groups'):
                    for sg in g.super_groups:
                        stack.append(sg)
        return names

    def check_constraints(self, time_table, verbose=False):
        for day in time_table:
            for time_slot in time_table[day]:
                courses = time_table[day][time_slot]

                # 1. professor collisions
                professor_ids = []
                for course in courses:
                    if course.instructor.id in professor_ids:
                        if verbose:
                            self.logger.info(
                                f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                f"Professor conflict (Prof {course.instructor.id})"
                            )
                        return False
                    professor_ids.append(course.instructor.id)

                # 2. student group + ancestor conflicts (with allow_parallel exemption)
                ancestor_sets = [self._ancestors(c.student_grp) for c in courses]
                allow_parallel_flags = [getattr(c, 'allow_parallel', False) for c in courses]

                for i in range(len(ancestor_sets)):
                    for j in range(i + 1, len(ancestor_sets)):
                        # If both courses explicitly allow parallel scheduling, skip ancestor conflict
                        if allow_parallel_flags[i] and allow_parallel_flags[j]:
                            continue
                        if ancestor_sets[i] & ancestor_sets[j]:
                            if verbose:
                                grp_i = courses[i].student_grp.name if hasattr(courses[i].student_grp, 'name') else str(courses[i].student_grp)
                                grp_j = courses[j].student_grp.name if hasattr(courses[j].student_grp, 'name') else str(courses[j].student_grp)
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"Student group conflict between {grp_i} and {grp_j}"
                                )
                            return False

                # 3. room collisions
                room_ids = []
                for course in courses:
                    if course.room.id in room_ids:
                        if verbose:
                            self.logger.info(
                                f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                f"Room conflict (Room {course.room.id})"
                            )
                        return False
                    room_ids.append(course.room.id)

                # 4. lab room constraint
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            if verbose:
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"{course.course_id}-lab in non‑lab room ({course.room.name})"
                                )
                            return False

                # 5. room capacity
                for course in courses:
                    if hasattr(course.student_grp, 'size') and hasattr(course.room, 'capacity'):
                        if course.room.capacity < course.student_grp.size:
                            if verbose:
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"Room too small – {course.course_id} in {course.room.name} "
                                    f"(capacity {course.room.capacity}, need {course.student_grp.size})"
                                )
                            return False

            # 6. lectures per day (unless lecture_consecutive=True)
            lectures_per_day = {}
            seen_instances = set()
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        instance_id = course.id if hasattr(course, 'id') else id(course)
                        if instance_id not in seen_instances:
                            seen_instances.add(instance_id)
                            key = (course.course_id, grp_name)
                            if key not in lectures_per_day:
                                lectures_per_day[key] = {
                                    'count': 0,
                                    'lecture_consecutive': getattr(course, 'lecture_consecutive', False)
                                }
                            lectures_per_day[key]['count'] += 1
                            if not lectures_per_day[key]['lecture_consecutive']:
                                if lectures_per_day[key]['count'] > 1:
                                    if verbose:
                                        self.logger.info(
                                            f"    [CONSTRAINT FAIL] {day}: Multiple lectures for "
                                            f"{course.course_id} in {grp_name} (lecture_consecutive=False)"
                                        )
                                    return False

            # 7. continuous slots
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.slots_continuous:
                        course_slots = []
                        for slot in time_table[day]:
                            if course in time_table[day][slot]:
                                course_slots.append(slot)
                        course_slots.sort()
                        if len(course_slots) > 1:
                            for i in range(len(course_slots) - 1):
                                if course_slots[i+1] != course_slots[i] + 1:
                                    if verbose:
                                        self.logger.info(
                                            f"    [CONSTRAINT FAIL] {day}: Non‑consecutive slots for "
                                            f"{course.course_id}-{course.session_type} (slots {course_slots})"
                                        )
                                    return False

        # 8. each course scheduled exactly slots_req times
        course_slot_count = {}
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_id = course.id if hasattr(course, 'id') else id(course)
                    course_slot_count[course_id] = course_slot_count.get(course_id, 0) + 1

        for course in self.courses:
            course_id = course.id if hasattr(course, 'id') else id(course)
            if course_id in course_slot_count:
                if course_slot_count[course_id] != course.slots_req:
                    if verbose:
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        self.logger.info(
                            f"    [CONSTRAINT FAIL] {course.course_id}-{course.session_type}({grp_name}): "
                            f"scheduled {course_slot_count[course_id]} slots, needs {course.slots_req}"
                        )
                    return False
            else:
                if verbose:
                    grp_name = (course.student_grp.name
                                if hasattr(course.student_grp, 'name')
                                else str(course.student_grp))
                    self.logger.info(
                        f"    [CONSTRAINT FAIL] {course.course_id}-{course.session_type}({grp_name}): "
                        f"not scheduled at all"
                    )
                return False

        return True

    def _can_add_course(self, new_course, assigned_room, existing_course):
        if new_course.instructor.id == existing_course.instructor.id:
            return False
        if assigned_room.id == existing_course.room.id:
            return False

        # Student group conflict: ancestor intersection, with allow_parallel exemption
        new_ancestors = self._ancestors(new_course.student_grp)
        existing_ancestors = self._ancestors(existing_course.student_grp)
        if new_ancestors & existing_ancestors:
            # If both explicitly allow parallel scheduling, ignore ancestor conflict
            if not (getattr(new_course, 'allow_parallel', False) and getattr(existing_course, 'allow_parallel', False)):
                return False

        return True

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