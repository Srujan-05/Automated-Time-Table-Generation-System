

class FitnessMixin:
    def fitness(self, time_table):
        ptp = self._ptp_objective_function(time_table)
        rtr = self._rtr_objective_function(time_table)
        ctrr = self._ctrr_objective_function(time_table)
        return (self.objective_function_weights[0] * ptp +
                self.objective_function_weights[1] * rtr +
                self.objective_function_weights[2] * ctrr)

    def _ptp_objective_function(self, time_table):
        penalty = 0
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    penalty += abs(self.preference_bins[time_slot] - course.preference_bin)
        return penalty

    def _rtr_objective_function(self, time_table):
        penalty = 0
        for day in time_table:
            time_slots = sorted(time_table[day].keys())
            for i in range(len(time_slots) - 1):
                current_slot = time_slots[i]
                next_slot = time_slots[i+1]
                current_courses = time_table[day][current_slot]
                next_courses = time_table[day][next_slot]

                current_grp_rooms = {}
                for c in current_courses:
                    current_grp_rooms.setdefault(c.student_grp, c.room)
                next_grp_rooms = {}
                for c in next_courses:
                    next_grp_rooms.setdefault(c.student_grp, c.room)

                for curr_grp, curr_room in current_grp_rooms.items():
                    match = None
                    if curr_grp in next_grp_rooms:
                        match = curr_grp
                    elif hasattr(curr_grp, 'super_groups'):
                        for super_grp in curr_grp.super_groups:
                            if super_grp in next_grp_rooms:
                                match = super_grp
                                break
                    if match:
                        next_room = next_grp_rooms[match]
                        distance = (abs(curr_room.x - next_room.x) +
                                    abs(curr_room.y - next_room.y) +
                                    abs(curr_room.z - next_room.z))
                        penalty += distance
        return penalty

    def _ctrr_objective_function(self, time_table):
        penalty = 0
        course_sessions = {}
        for day in time_table:
            for time_slot in time_table[day]:
                for course in time_table[day][time_slot]:
                    course_key = (course.course_id, course.session_type)
                    course_sessions.setdefault(course_key, []).append((time_slot, course.room))
        for course_key, sessions in course_sessions.items():
            if len(sessions) > 1:
                ref_slot, ref_room = sessions[0]
                for slot, room in sessions[1:]:
                    if slot != ref_slot:
                        penalty += 1
                    if room != ref_room:
                        penalty += 1
        return penalty

    def _course_stability_objective_function(self, time_table):
        return self._ctrr_objective_function(time_table)