import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstraintsMixin:
    def check_constraints(self, time_table, verbose=False):
        # (exactly the same body as in your original code)
        for day in time_table:
            for time_slot in time_table[day]:
                courses = time_table[day][time_slot]

                # 1. professor collisions
                professor_ids = []
                for course in courses:
                    if course.instructor.id in professor_ids:
                        if verbose:
                            self.logger.info(...)
                        return False
                    professor_ids.append(course.instructor.id)

                # 2. student group collisions (name comparison)
                student_grp_names = []
                for course in courses:
                    grp_name = (course.student_grp.name
                                if hasattr(course.student_grp, 'name')
                                else str(course.student_grp))
                    if grp_name in student_grp_names:
                        if verbose:
                            self.logger.info(...)
                        return False
                    student_grp_names.append(grp_name)

                # 3. super group collisions (name comparison)
                for course in courses:
                    if hasattr(course.student_grp, 'super_groups'):
                        for super_grp in course.student_grp.super_groups:
                            super_grp_name = (super_grp.name
                                              if hasattr(super_grp, 'name')
                                              else str(super_grp))
                            for other_course in courses:
                                if other_course != course:
                                    other_grp_name = (other_course.student_grp.name
                                                      if hasattr(other_course.student_grp, 'name')
                                                      else str(other_course.student_grp))
                                    if super_grp_name == other_grp_name:
                                        if verbose:
                                            self.logger.info(...)
                                        return False
                                    if hasattr(other_course.student_grp, 'super_groups'):
                                        for other_super in other_course.student_grp.super_groups:
                                            other_super_name = (other_super.name
                                                                if hasattr(other_super, 'name')
                                                                else str(other_super))
                                            if super_grp_name == other_super_name:
                                                if verbose:
                                                    self.logger.info(...)
                                                return False

                # 4. room collisions
                room_ids = []
                for course in courses:
                    if course.room.id in room_ids:
                        if verbose:
                            self.logger.info(...)
                        return False
                    room_ids.append(course.room.id)

                # 5. lab room constraint
                for course in courses:
                    if course.session_type == 'lab':
                        if not hasattr(course.room, 'is_lab') or not course.room.is_lab:
                            if verbose:
                                self.logger.info(...)
                            return False

                # 6. room capacity
                for course in courses:
                    if hasattr(course.student_grp, 'size') and hasattr(course.room, 'capacity'):
                        if course.room.capacity < course.student_grp.size:
                            if verbose:
                                self.logger.info(...)
                            return False

            # 7. lectures per day (non-consecutive only 1)
            lectures_per_day = {}
            seen_courses = set()
            for time_slot in sorted(time_table[day].keys()):
                for course in time_table[day][time_slot]:
                    if course.session_type == 'lecture':
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        course_key = (course.course_id, grp_name, id(course))
                        if course_key not in seen_courses:
                            seen_courses.add(course_key)
                            course_key_simple = (course.course_id, grp_name)
                            if course_key_simple not in lectures_per_day:
                                lectures_per_day[course_key_simple] = {
                                    'count': 0,
                                    'lecture_consecutive': getattr(course, 'lecture_consecutive', False)
                                }
                            lectures_per_day[course_key_simple]['count'] += 1
                            if not lectures_per_day[course_key_simple]['lecture_consecutive']:
                                if lectures_per_day[course_key_simple]['count'] > 1:
                                    if verbose:
                                        self.logger.info(...)
                                    return False

            # 8. continuous slots constraint
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
                                        self.logger.info(...)
                                    return False

        # 9. each course scheduled exactly slots_req times
        course_slot_count = {}
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_id = id(course)
                    course_slot_count[course_id] = course_slot_count.get(course_id, 0) + 1

        for course in self.courses:
            course_id = id(course)
            if course_id in course_slot_count:
                if course_slot_count[course_id] != course.slots_req:
                    if verbose:
                        grp_name = (course.student_grp.name
                                    if hasattr(course.student_grp, 'name')
                                    else str(course.student_grp))
                        self.logger.info(...)
                    return False
            else:
                if verbose:
                    grp_name = (course.student_grp.name
                                if hasattr(course.student_grp, 'name')
                                else str(course.student_grp))
                    self.logger.info(...)
                return False

        return True

    def _can_add_course(self, new_course, assigned_room, existing_course):
        # (copy of your original method – same body)
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
                return False
            if new_grp_name in existing_super_names:
                return False
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
        # (copy of original)
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