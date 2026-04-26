# Genetic Algorithm for Automated Timetable Generation (Single-Objective EA)

This package implements a single‑objective evolutionary algorithm (SOEA) to
solve the university course timetabling problem. The codebase is organised into
modular mixin classes, promoting maintainability and easy extension to
multi‑objective or co‑evolutionary variants.

## Directory Structure

```
ga/
├── __init__.py                # Exports the main GASearch class
├── algorithm.py               # Main class combining all mixins
├── population.py              # Population creation and smart timetable generation
├── constraints.py             # Hard constraint checking, conflict detection
├── fitness.py                 # Fitness evaluation and objective functions
├── operators.py               # Selection, crossover, mutation
├── README.md                  # This file
└── documentations/
    ├── mutation_strategy.tex  # LaTeX source for mutation strategy report
    └── mutation_strategy.pdf  # Compiled PDF
```

## Modules Overview

### `algorithm.py` – Entry Point

Defines `GASearch` by inheriting from all functional mixins.  
Responsibilities:

- Logging setup
- Parameter normalisation (e.g., converting integer time slots to day‑specific
  dictionaries)
- Storage of configuration: `time_slots`, `courses`, `preference_bins`,
  `objective_function_weights`, `rooms`, population parameters.

### `population.py` – PopulationMixin

Handles the creation of the initial population using a smart greedy heuristic.  
Core methods:

- `create_population()`  
  Generates `population_size` valid timetables, retrying on failure with a limit
  to avoid infinite loops.
- `_generate_smart_timetable()`  
  Constructs a single timetable by sorting courses (randomised priority per
  candidate) and assigning them to slots/rooms while respecting constraints.
- `_assign_continuous_slots()` / `_assign_non_continuous_slots()`  
  Helper assignment routines for courses that require consecutive or
  non‑consecutive slots.
- `_generate_random_timetable()`  
  Deprecated; kept as an alias for backwards compatibility.

### `constraints.py` – ConstraintsMixin

Ensures all hard constraints are satisfied.  
Key methods:

- `check_constraints(time_table, verbose=False)`  
  Validates a full timetable against:
  - Professor collisions
  - Student group collisions (direct and super groups)
  - Room collisions
  - Lab‑room type constraints
  - Room capacity constraints
  - Maximum lectures per day (unless `lecture_consecutive`)
  - Continuous slot requirements
  - Exact number of slots per course
- `_can_add_course(new_course, room, existing_course)`  
  Micro‑conflict checker used during initialisation.
- `_get_available_rooms(course)`  
  Returns rooms suitable for a given course (respects room type and capacity).

### `fitness.py` – FitnessMixin

Evaluates the quality of a timetable.  
Components:

- `fitness(time_table)`  
  Computes a weighted sum of three penalty objectives (minimisation):
  - **PTP** – preference time penalty (difference between scheduled slot and
    course preference)
  - **RTR** – room‑to‑room travel distance for students between consecutive
    slots
  - **CTRR** – course time/room consistency penalty (same slot/room across the
    week)
- Individual objective functions: `_ptp_objective_function`,
  `_rtr_objective_function`, `_ctrr_objective_function`.
- `_course_stability_objective_function` – Alias for `_ctrr_objective_function`.

### `operators.py` – OperatorsMixin

Implements the evolutionary loop components.

- **Tournament Selection**  
  `select_parents(population, fitnesses)`  
  Binary tournament (size `k = min(3, pop_size)`) selecting the individual with
  lower fitness (since we minimise).
- **Mutation**  
  `mutate(time_table)` – Applies one of four operators randomly:
  1. **Slot‑Swap** – Swap two courses between different slots.
  2. **Course‑Relocate** – Move a course to a new slot and assign a suitable
     room.
  3. **Room‑Change** – Change only the room of a course.
  4. **Block‑Permute** – Reshuffle the slots of a multi‑slot course, preserving
     continuity if required. After mutation, if hard constraints are violated,
     the original timetable is restored.
- **Crossover & Run**  
  `crossover()` and `run()` are stubbed; the main loop is to be implemented.

## SOEA Workflow

1. **Initialisation**

   ```python
   from ga import GASearch
   ga = GASearch(time_slots=..., courses=..., ...)
   population = ga.create_population()
   ```

2. **Fitness Evaluation**

   ```python
   fitnesses = [ga.fitness(ind) for ind in population]
   ```

3. **Generational Loop** (pseudocode)
   ```python
   for gen in range(ga.generations):
       # Selection
       parents = [ga.select_parents(population, fitnesses) for _ in range(...)]
       # Crossover & Mutation
       offspring = []
       for p1, p2 in parents:
           child = ga.crossover(p1, p2)
           child = ga.mutate(child)
           offspring.append(child)
       # Fitness evaluation of offspring
       offspring_fitnesses = [ga.fitness(ind) for ind in offspring]
       # Replacement (e.g., elitism + offspring)
       ...
   ```

All individuals are guaranteed to satisfy hard constraints at every step.

## Parallelisation Support

To accelerate computation, especially during large populations, the architecture
is designed for multiprocessing:

- **Initialisation** – `create_population` can be run in parallel by spawning
  workers that each produce one valid timetable.
- **Fitness Evaluation** – An entire generation’s fitness can be computed
  concurrently using `ProcessPoolExecutor` or similar.
- **Island Model** – Multiple GA instances can evolve independently with
  occasional migration.

Due to the mixin structure, these parallel wrappers can be added without
modifying the core logic.

## Mutation Strategy Documentation

A detailed LaTeX report on the mutation operators is available in the
`documentations/` subfolder.  
The report includes pseudocode, explanation of each operator, and how they
interact with the constraint model.

To compile the PDF:

```bash
cd ga/documentations
pdflatex mutation_strategy.tex
```

## Dependencies

- Python 3.8+
- Standard libraries: `logging`, `copy`, `random`, `os` (for parallel
  extensions), `concurrent.futures` (optional)
- No external packages required for the core SOEA.

## Extension Roadmap

This SOEA serves as a foundation for more advanced algorithms:

- **MOEA** – Replace the single‑objective fitness with a Pareto‑dominance‑based
  multi‑objective approach (e.g., NSGA‑II).
- **CCEA** – Decompose the timetable by course, evolve subpopulations
  cooperatively.

The mixin architecture allows these extensions to reuse the existing constraint
and mutation modules with minimal changes.

---

_For questions or contributions, please refer to the main project repository._
