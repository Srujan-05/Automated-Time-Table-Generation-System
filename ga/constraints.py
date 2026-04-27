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

                # 2. student group collisions (direct)
                student_grp_names = []
                for course in courses:
                    grp_name = (course.student_grp.name
                                if hasattr(course.student_grp, 'name')
                                else str(course.student_grp))
                    if grp_name in student_grp_names:
                        if verbose:
                            self.logger.info(
                                f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                f"Student group conflict ({grp_name})"
                            )
                        return False
                    student_grp_names.append(grp_name)

                # 3. super group collisions
                for course in courses:
                    if hasattr(course.student_grp, 'super_groups'):
                        for super_grp in course.student_grp.super_groups:
                            super_grp_name = (super_grp.name
                                              if hasattr(super_grp, 'name')
                                              else str(super_grp))
                            for other in courses:
                                if other == course:
                                    continue
                                other_grp_name = (other.student_grp.name
                                                  if hasattr(other.student_grp, 'name')
                                                  else str(other.student_grp))
                                if super_grp_name == other_grp_name:
                                    if verbose:
                                        self.logger.info(
                                            f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                            f"Super group conflict ({super_grp_name})"
                                        )
                                    return False
                                if hasattr(other.student_grp, 'super_groups'):
                                    for other_super in other.student_grp.super_groups:
                                        other_super_name = (other_super.name
                                                            if hasattr(other_super, 'name')
                                                            else str(other_super))
                                        if super_grp_name == other_super_name:
                                            if verbose:
                                                self.logger.info(
                                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                                    f"Super group conflict ({super_grp_name})"
                                                )
                                            return False

                # 4. room collisions
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

                # 5. lab room constraint
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            if verbose:
                                self.logger.info(
                                    f"    [CONSTRAINT FAIL] {day} Slot {time_slot}: "
                                    f"{course.course_id}-lab in non‑lab room ({course.room.name})"
                                )
                            return False

                # 6. room capacity
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

            # 7. lectures per day (unless lecture_consecutive=True)
            lectures_per_day = {}
            seen_instances = set()
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        # Use course.id attribute to identify unique instances
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

            # 8. continuous slots
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

        # 9. each course scheduled exactly slots_req times
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

        new_grp_name = (new_course.student_grp.name
                        if hasattr(new_course.student_grp, 'name')
                        else str(new_course.student_grp))
        existing_grp_name = (existing_course.student_grp.name
                             if hasattr(existing_course.student_grp, 'name')
                             else str(existing_course.student_grp))
        if new_grp_name == existing_grp_name:
            return False

        if hasattr(new_course.student_grp, 'super_groups') and hasattr(existing_course.student_grp, 'super_groups'):
            new_super_names = [s.name if hasattr(s, 'name') else str(s) for s in new_course.student_grp.super_groups]
            existing_super_names = [s.name if hasattr(s, 'name') else str(s) for s in existing_course.student_grp.super_groups]
            if existing_grp_name in new_super_names:
                # If both courses explicitly allow parallel scheduling, skip this check
                if not (getattr(new_course, 'allow_parallel', False) and getattr(existing_course, 'allow_parallel', False)):
                    return False
            if new_grp_name in existing_super_names:
                # If both courses explicitly allow parallel scheduling, skip this check
                if not (getattr(new_course, 'allow_parallel', False) and getattr(existing_course, 'allow_parallel', False)):
                    return False
            if set(new_super_names) & set(existing_super_names):
                # If both courses explicitly allow parallel scheduling, skip super-group conflict
                if not (getattr(new_course, 'allow_parallel', False) and getattr(existing_course, 'allow_parallel', False)):
                    return False
        elif hasattr(new_course.student_grp, 'super_groups'):
            new_supers = [s.name if hasattr(s, 'name') else str(s) for s in new_course.student_grp.super_groups]
            if existing_grp_name in new_supers:
                return False
        elif hasattr(existing_course.student_grp, 'super_groups'):
            exist_supers = [s.name if hasattr(s, 'name') else str(s) for s in existing_course.student_grp.super_groups]
            if new_grp_name in exist_supers:
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