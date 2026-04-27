"""
Parallel evaluation mixin for both SOEA and MOEA.
"""

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

# ----------------------------------------------------------------------
# Standalone fitness functions – they do NOT need a GASearch object,
# they only use data that is already inside the timetable.
# ----------------------------------------------------------------------

def _compute_fitness_vector(tt, pref_bins):
    """
    Compute the three objective values for a single timetable.
    Returns (ptp, rtr, ctrr) as a tuple.
    """
    # -- PTP --
    ptp = 0
    for day in tt:
        for slot, courses in tt[day].items():
            if slot in pref_bins:
                for course in courses:
                    ptp += abs(pref_bins[slot] - course.preference_bin)

    # -- RTR --
    rtr = 0
    for day in tt:
        slots = sorted(tt[day].keys())
        for i in range(len(slots) - 1):
            curr_slot = slots[i]
            next_slot = slots[i+1]
            curr_courses = tt[day][curr_slot]
            next_courses = tt[day][next_slot]

            # map student groups (direct) to rooms
            curr_grp_room = {}
            for c in curr_courses:
                if c.student_grp not in curr_grp_room:
                    curr_grp_room[c.student_grp] = c.room
            next_grp_room = {}
            for c in next_courses:
                if c.student_grp not in next_grp_room:
                    next_grp_room[c.student_grp] = c.room

            for grp, rm in curr_grp_room.items():
                match = None
                if grp in next_grp_room:
                    match = grp
                elif hasattr(grp, 'super_groups'):
                    for sg in grp.super_groups:
                        if sg in next_grp_room:
                            match = sg
                            break
                if match:
                    rm2 = next_grp_room[match]
                    rtr += abs(rm.x - rm2.x) + abs(rm.y - rm2.y) + abs(rm.z - rm2.z)

    # -- CTRR --
    ctrr = 0
    course_sessions = {}
    for day in tt:
        for slot, courses in tt[day].items():
            for c in courses:
                key = (c.course_id, c.session_type)
                course_sessions.setdefault(key, []).append((slot, c.room))
    for key, sessions in course_sessions.items():
        if len(sessions) > 1:
            ref_slot, ref_room = sessions[0]
            for slot, room in sessions[1:]:
                if slot != ref_slot:
                    ctrr += 1
                if room != ref_room:
                    ctrr += 1

    return (ptp, rtr, ctrr)


def _compute_fitness_scalar(tt, pref_bins, weights):
    """Weighted‑sum scalar fitness for SOEA."""
    ptp, rtr, ctrr = _compute_fitness_vector(tt, pref_bins)
    return weights[0] * ptp + weights[1] * rtr + weights[2] * ctrr


# ----------------------------------------------------------------------
# Mixin class to add parallel evaluation capability
# ----------------------------------------------------------------------

class ParallelEvaluationMixin:
    """
    Adds evaluate_population_parallel() that uses multiprocessing.
    Must be mixed into a class that has:
      - self.preference_bins
      - self.objective_function_weights (only needed for SOEA)
      - self.logger (optional, for logging)
    """

    def evaluate_population_parallel(self, population, n_workers=None):
        """
        Evaluate fitness for every individual in *population* using
        multiple processes.
        Returns a list of fitness values (scalar for SOEA, tuple for MOEA).
        """
        if n_workers is None:
            n_workers = min(os.cpu_count() or 4, len(population))

        # Determine if we are in a multi‑objective context
        multi_objective = hasattr(self, 'fitness_vector')

        if multi_objective:
            worker_func = _compute_fitness_vector
            extra_args = (self.preference_bins,)
        else:
            worker_func = _compute_fitness_scalar
            extra_args = (self.preference_bins, self.objective_function_weights)

        results = [None] * len(population)
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            future_to_idx = {}
            for idx, ind in enumerate(population):
                future = executor.submit(worker_func, ind, *extra_args)
                future_to_idx[future] = idx

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    self.logger.error(f"Error evaluating individual {idx}: {e}")
                    # Provide a fallback large penalty so the individual is not preferred
                    if multi_objective:
                        results[idx] = (float('inf'), float('inf'), float('inf'))
                    else:
                        results[idx] = float('inf')

        return results