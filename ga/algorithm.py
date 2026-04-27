import logging

from .population import PopulationMixin
from .constraints import ConstraintsMixin
from .fitness import FitnessMixin
from .operators import OperatorsMixin
from .parallel import ParallelEvaluationMixin

class GASearch(PopulationMixin, ConstraintsMixin, FitnessMixin, OperatorsMixin, ParallelEvaluationMixin):
    def __init__(self, time_slots, courses, preference_bins,
                 objective_function_weights, rooms,
                 population_size=20, generations=100, mutation_rate=0.1):
        # ---------- logging setup ----------
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # ---------- normalize time_slots ----------
        self.time_slots = time_slots
        if isinstance(time_slots, int):
            self.time_slots = {
                'Monday': time_slots,
                'Tuesday': time_slots,
                'Wednesday': time_slots,
                'Thursday': time_slots,
                'Friday': time_slots
            }

        # ---------- store parameters ----------
        self.courses = courses
        self.preference_bins = preference_bins
        self.objective_function_weights = objective_function_weights
        self.rooms = rooms
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate