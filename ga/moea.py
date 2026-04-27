import copy
import random
from .algorithm import GASearch   # inherits from PopulationMixin, ConstraintsMixin, FitnessMixin, OperatorsMixin
from .dominance import non_dominated_sort, crowding_distance

class MOEAGASearch(GASearch):
    """
    Multi-Objective Evolutionary Algorithm using NSGA-II.
    Inherits all constraint handling, population initialisation,
    mutation, and crossover from the SOEA mixins.
    """

    def fitness_vector(self, time_table):
        """Return a tuple of three objectives (all to be minimised)."""
        return (self._ptp_objective_function(time_table),
                self._rtr_objective_function(time_table),
                self._ctrr_objective_function(time_table))

    def evaluate_population(self, population):
        """Return list of fitness vectors."""
        return [self.fitness_vector(ind) for ind in population]

    def select_parents(self, population, fitness_vectors):
        """
        Binary tournament selection based on:
          - lower Pareto rank (closer to front 0)
          - higher crowding distance if ranks are equal
        """
        if len(population) < 2:
            raise ValueError("Population too small for selection")

        # Compute fronts and assign rank and crowding
        fronts = non_dominated_sort(fitness_vectors)
        rank = {idx: r for r, front in enumerate(fronts) for idx in front}
        crowding = {}
        for front in fronts:
            crowding.update(crowding_distance(fitness_vectors, front))

        def tournament():
            k = min(3, len(population))
            contestants = random.sample(range(len(population)), k)
            best = contestants[0]
            for c in contestants[1:]:
                if rank[c] < rank[best] or (rank[c] == rank[best] and crowding[c] > crowding[best]):
                    best = c
            return population[best]

        p1 = tournament()
        p2 = tournament()
        return p1, p2

    def run(self, generations=None):
        """
        Execute NSGA-II and return the final Pareto front.
        """
        if generations is None:
            generations = self.generations

        self.logger.info("[MOEA] Creating initial population...")
        population = self.create_population()          # uses smart init from PopulationMixin
        fitness_vectors = self.evaluate_population_parallel(population)

        for gen in range(generations):
            self.logger.info(f"[MOEA] Generation {gen+1}/{generations}")

            # --- Create offspring ---
            offspring = []
            while len(offspring) < self.population_size:
                # Select parents
                p1, p2 = self.select_parents(population, fitness_vectors)
                # Crossover and mutate
                child = self.crossover(p1, p2)
                child = self.mutate(child)

                # Ensure feasibility (hard constraints)
                if not self.check_constraints(child):
                    # Fallback: keep one parent unchanged (deepcopy to avoid side effects)
                    child = copy.deepcopy(random.choice([p1, p2]))

                offspring.append(child)

            # Evaluate offspring
            offspring_fitness = self.evaluate_population_parallel(offspring)

            # --- Combine parents and offspring ---
            combined_pop = population + offspring
            combined_fitness = fitness_vectors + offspring_fitness

            # --- NSGA‑II selection of next generation ---
            fronts = non_dominated_sort(combined_fitness)
            next_pop = []
            next_fitness = []

            for front in fronts:
                if len(next_pop) + len(front) <= self.population_size:
                    # Add all individuals of this front
                    for idx in front:
                        next_pop.append(combined_pop[idx])
                        next_fitness.append(combined_fitness[idx])
                else:
                    # Add the best individuals from this front based on crowding distance
                    # We need to compute crowding only for the current front
                    front_crowding = crowding_distance(combined_fitness, front)
                    sorted_front = sorted(front, key=lambda idx: front_crowding[idx], reverse=True)
                    remaining = self.population_size - len(next_pop)
                    for idx in sorted_front[:remaining]:
                        next_pop.append(combined_pop[idx])
                        next_fitness.append(combined_fitness[idx])
                    break   # stop after filling the slots

            population = next_pop
            fitness_vectors = next_fitness

        # --- Final Pareto front (first front of final population) ---
        fronts = non_dominated_sort(fitness_vectors)
        pareto_set = [population[i] for i in fronts[0]]
        pareto_fitness = [fitness_vectors[i] for i in fronts[0]]

        self.logger.info(f"[MOEA] Run complete. Pareto front size: {len(pareto_set)}")
        return pareto_set, pareto_fitness