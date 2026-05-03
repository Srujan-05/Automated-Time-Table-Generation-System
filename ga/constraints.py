class ConstraintsMixin:
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

                # 2a. parallelizable_id constraint: different IDs cannot coexist in same slot
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
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"Parallelizable conflict: {grp_i} (id={id_i}) and {grp_j} (id={id_j}) cannot coexist"
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

                # 4b. non-lab room constraint (lectures and tutorials must use non-lab rooms)
                for course in courses:
                    if course.session_type in ['lecture', 'tutorial']:
                        if hasattr(course.room, 'is_lab') and course.room.is_lab:
                            if verbose:
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"{course.course_id}-{course.session_type} in lab room ({course.room.name})"
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

                # 5b. allowed_batches constraint (room batch restrictions)
                for course in courses:
                    room_allowed_batches = getattr(course.room, 'allowed_batches', None)
                    if room_allowed_batches is not None:
                        # If room has restrictions, check if student group is allowed
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        if grp_name not in room_allowed_batches:
                            if verbose:
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"{grp_name} not allowed in room {course.room.name} "
                                    f"(allowed: {room_allowed_batches})"
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
        # Check if new_course can be added to a slot with existing_course
        # Return False if they conflict
        
        # Room type constraint: labs only for lab sessions, non-labs only for lectures/tutorials
        if new_course.session_type == 'lab':
            if not hasattr(assigned_room, 'is_lab') or not assigned_room.is_lab:
                return False
        elif new_course.session_type in ['lecture', 'tutorial']:
            if hasattr(assigned_room, 'is_lab') and assigned_room.is_lab:
                return False
        
        # Room allowed_batches constraint: check if student group is allowed in this room
        room_allowed_batches = getattr(assigned_room, 'allowed_batches', None)
        if room_allowed_batches is not None:
            grp_name = new_course.student_grp.name if hasattr(new_course.student_grp, 'name') else str(new_course.student_grp)
            if grp_name not in room_allowed_batches:
                return False
        
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
        # If both courses have same parallelizable_id, they can coexist even with shared super groups
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

    def _get_available_rooms(self, course):
        available_rooms = []
        for room in self.rooms:
            # For lab sessions: only use lab rooms
            if course.session_type == 'lab':
                if not hasattr(room, 'is_lab') or not room.is_lab:
                    continue
            # For lectures and tutorials: only use non-lab rooms
            elif course.session_type in ['lecture', 'tutorial']:
                if hasattr(room, 'is_lab') and room.is_lab:
                    continue
            
            # Check room capacity
            if hasattr(course.student_grp, 'size') and hasattr(room, 'capacity'):
                if room.capacity < course.student_grp.size:
                    continue
            
            # Check allowed_batches constraint
            room_allowed_batches = getattr(room, 'allowed_batches', None)
            if room_allowed_batches is not None:
                grp_name = course.student_grp.name if hasattr(course.student_grp, 'name') else str(course.student_grp)
                if grp_name not in room_allowed_batches:
                    continue
            
            available_rooms.append(room)
        return available_rooms