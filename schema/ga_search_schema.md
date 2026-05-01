# GASearch Class & run.py Schema Documentation

## Overview

This document provides a comprehensive schema for:
1. **GASearch Class Initialization** - The Genetic Algorithm engine for timetable generation
2. **run() Method** - The main GA loop that executes the optimization
3. **Data Structure Requirements** - Input objects and their formats

---

## Table of Contents

1. [GASearch Initialization](#gasearch-initialization)
2. [run() Method](#run-method)
3. [Input Data Structures](#input-data-structures)
4. [Usage Example](#usage-example)

---

## GASearch Initialization

### Class Definition

```python
from ga.algorithm import GASearch

ga = GASearch(
    time_slots,                    # Time slots configuration
    courses,                       # List of CourseInstance objects
    preference_bins,               # Slot-to-bin mapping
    objective_function_weights,    # Fitness weights
    rooms,                         # Available rooms
    population_size=20,            # GA parameter
    generations=100,               # GA parameter
    mutation_rate=0.1              # GA parameter
)
```

### Parameter Specifications

#### 1. **time_slots** (int or dict)

**Type:** `int` or `dict`

**Description:** Defines the number of time slots per day

**Variants:**

```python
# Option A: Integer (same slots for all days)
time_slots = 9
# Auto-converts to: {'Monday': 9, 'Tuesday': 9, 'Wednesday': 9, 'Thursday': 9, 'Friday': 9}

# Option B: Dictionary (day-specific slots)
time_slots = {
    'Monday': 9,      # 3 morning slots, 3 noon, 3 evening
    'Tuesday': 9,
    'Wednesday': 5,   # Only 2 bins available (1-3: bin1, 4-5: bin2)
    'Thursday': 9,
    'Friday': 9
}
```

**Constraints:**
- Must be positive integer(s)
- Days: 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
- Typically follows bin distribution (e.g., 9 slots = 3 bins × 3 slots)

**Example from test_data.py:**
```python
time_slots = {
    'Monday': 9,
    'Tuesday': 9,
    'Wednesday': 5,
    'Thursday': 9,
    'Friday': 9
}
```

---

#### 2. **courses** (list of CourseInstance)

**Type:** `list[CourseInstance]`

**Description:** All course sessions to be scheduled

**CourseInstance Structure:**

```python
class CourseInstance:
    def __init__(self, 
                 id,                      # int: unique identifier
                 course_id,               # str: e.g., "CS201"
                 session_type,            # str: "lecture", "tutorial", or "lab"
                 instructor,              # Instructor object
                 room,                    # Room object (can be None initially)
                 student_grp,             # StudentGroup object
                 slots_req,               # int: slots needed for this instance
                 slots_continuous=False,  # bool: consecutive slots required?
                 preference_bin=1,        # int: 1=morning, 2=noon, 3=evening
                 lecture_consecutive=False, # bool: allow multiple lectures same day?
                 parallelizable_id=None   # int or None: grouping for parallel courses
    ):
        pass
```

**Key Fields Explanation:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | int | Unique identifier | 1 |
| `course_id` | str | Course code | "CS201" |
| `session_type` | str | Type of session | "lecture", "tutorial", "lab" |
| `instructor` | Instructor | Professor teaching | prof_kumar |
| `room` | Room | Classroom/Lab | room_101 (can be None) |
| `student_grp` | StudentGroup | Student cohort | cse_2025 |
| `slots_req` | int | Weekly slots needed | 1 (for 1 lecture/week) |
| `slots_continuous` | bool | Consecutive on same day? | True (for labs) |
| `preference_bin` | int | Time preference | 1 (morning) |
| `lecture_consecutive` | bool | Multiple lectures/day OK? | False (max 1/day) |
| `parallelizable_id` | int/None | Grouping ID for electives | 101 (RL & NLP same group) |

**Example Courses from test_data.py:**

```python
# CS201 Lecture for CSE-2025 (3 lectures per week)
courses = []
for i in range(3):
    courses.append(CourseInstance(
        id=1 + i,
        course_id="CS201",
        session_type="lecture",
        instructor=prof_kumar,
        room=room_101,
        student_grp=cse_2025,
        slots_req=1,
        slots_continuous=False,
        preference_bin=1
    ))

# CS201 Tutorial (1 per week)
courses.append(CourseInstance(
    id=4,
    course_id="CS201",
    session_type="tutorial",
    instructor=prof_sharma,
    room=room_102,
    student_grp=cse_2025,
    slots_req=1,
    slots_continuous=False,
    preference_bin=1
))

# CS201 Lab (2 consecutive slots)
courses.append(CourseInstance(
    id=5,
    course_id="CS201",
    session_type="lab",
    instructor=prof_patel,
    room=lab_201,  # Must be a lab room
    student_grp=cse_2025,
    slots_req=2,
    slots_continuous=True,  # Must be consecutive
    preference_bin=2
))
```

---

#### 3. **preference_bins** (dict)

**Type:** `dict[int, int]`

**Format:** `{slot_number: bin_id}`

**Description:** Maps time slots to time-of-day bins

**Structure:**

```python
preference_bins = {
    1: 1, 2: 1, 3: 1,        # Slots 1-3 = Morning (bin 1)
    4: 2, 5: 2, 6: 2,        # Slots 4-6 = Afternoon (bin 2)
    7: 3, 8: 3, 9: 3         # Slots 7-9 = Evening (bin 3)
}
```

**Common Time Bin Mapping:**
- **Bin 1 (Morning):** 09:00 - 12:00 (typically slots 1-3)
- **Bin 2 (Afternoon):** 13:00 - 16:00 (typically slots 4-6)
- **Bin 3 (Evening):** 16:00 - 19:00 (typically slots 7-9)

**Usage:**
- Each **CourseInstance** has its own `preference_bin` (1, 2, or 3)
- Fitness function penalizes when actual slot's bin ≠ course's preference_bin
- Example: A course preferring morning (preference_bin=1) placed in slot 7 (bin 3) incurs penalty

**Example from test_data.py:**

```python
preference_bins = {
    1: 1, 2: 1, 3: 1,
    4: 2, 5: 2, 6: 2,
    7: 3, 8: 3, 9: 3
}

# For Wednesday with only 5 slots and 2 bins:
# preference_bins still maps: 1→1, 2→1, 3→1, 4→2, 5→2
# (slots 6-9 don't exist on Wednesday)
```

---

#### 4. **objective_function_weights** (list)

**Type:** `list[float]` (length 3)

**Format:** `[w_ptp, w_rtr, w_stability]`

**Description:** Weights for three penalty objectives

```python
objective_function_weights = [1.0, 0.5, 0.8]
```

**Components:**

| Index | Name | Description | Typical Weight |
|-------|------|-------------|-----------------|
| 0 | PTP/CTP | Course Time Preference penalty | 1.0 - 1.5 |
| 1 | RTR | Room-to-Room Travel distance penalty | 0.4 - 1.0 |
| 2 | Stability | Course Stability (consistency across week) | 0.2 - 1.0 |

**Fitness Calculation:**

```
fitness = w_ptp × ptp_penalty + w_rtr × rtr_penalty + w_stability × stability_penalty

# Lower fitness = better solution
```

**Weighting Strategy:**

```python
# Conservative (prioritize preferences)
weights = [1.0, 0.5, 0.8]

# Travel-focused (minimize student movement)
weights = [0.5, 2.0, 0.3]

# Stability-focused (consistent scheduling)
weights = [0.8, 0.4, 1.5]
```

**Example from test_data.py:**

```python
objective_function_weights = [1.0, 0.5, 0.8]
```

---

#### 5. **rooms** (list of Room)

**Type:** `list[Room]`

**Description:** All available classrooms and lab spaces

**Room Structure:**

```python
class Room:
    def __init__(self, 
                 id,           # int: unique ID
                 name,         # str: "Classroom 101", "Lab 201"
                 x, y, z,      # float: coordinates for distance calculation
                 capacity,     # int: max students
                 is_lab=False  # bool: True if lab, False if classroom
    ):
        pass
```

**Key Fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `id` | int | Unique identifier |
| `name` | str | Display name |
| `x, y, z` | float | 3D coordinates for distance calculation |
| `capacity` | int | Student capacity |
| `is_lab` | bool | True for labs, False for classrooms |

**Example from test_data.py:**

```python
rooms = [
    # Classrooms
    Room(id=1, name="Classroom 101", x=0, y=0, z=0, capacity=50, is_lab=False),
    Room(id=2, name="Classroom 102", x=1, y=0, z=0, capacity=50, is_lab=False),
    
    # Lab rooms
    Room(id=5, name="Lab 201", x=5, y=0, z=0, capacity=60, is_lab=True),
    Room(id=6, name="Lab 202", x=6, y=0, z=0, capacity=60, is_lab=True),
    
    # Auditorium
    Room(id=8, name="Main Auditorium", x=3, y=3, z=0, capacity=250, is_lab=False)
]
```

**Constraints:**
- Labs (is_lab=True) can only host "lab" session types
- Classrooms (is_lab=False) host "lecture" and "tutorial" sessions
- Capacity must accommodate student group size

---

#### 6. **population_size** (int, optional)

**Type:** `int`

**Default:** `20`

**Description:** Number of candidates in each generation

**Recommended Values:**
- Small problems (< 20 courses): 10-15
- Medium problems (20-100 courses): 20-40
- Large problems (> 100 courses): 40-100

**Trade-off:**
- Larger → better diversity, slower iterations
- Smaller → faster iterations, risk of premature convergence

---

#### 7. **generations** (int, optional)

**Type:** `int`

**Default:** `100`

**Description:** Maximum number of evolutionary generations

**Recommended Values:**
- Quick trials: 5-10
- Production runs: 50-200
- Complex problems: 200+

---

#### 8. **mutation_rate** (float, optional)

**Type:** `float` (0.0 to 1.0)

**Default:** `0.1`

**Description:** Probability of mutation in offspring

**Recommended Values:**
- Exploration (high): 0.2 - 0.3
- Balanced: 0.1 - 0.15
- Exploitation (low): 0.05 - 0.1

---

## run() Method

### Method Signature

```python
def run(self, convergence_threshold=0.1, min_generations=5, max_generations=None):
    """
    Run the genetic algorithm to find the optimal timetable.
    
    Args:
        convergence_threshold: If improvement < this, consider it converged (default: 0.1)
        min_generations: Minimum generations before checking convergence (default: 5)
        max_generations: Maximum generations to run (default: None → uses self.generations)
    
    Returns:
        best_timetable: Dict structure {day: {slot: [courses]}}
        best_fitness: Float, fitness value of best timetable (lower is better)
    """
```

### Execution Flow

```
1. Initialize Population
   ├─ Create `population_size` valid timetables
   └─ Log: "[POPULATION] Population creation complete: X candidates"

2. Evaluate Initial Candidates
   ├─ Calculate fitness for each candidate
   └─ Track: best_fitness, best_timetable

3. Main GA Loop (for each generation)
   ├─ Generate New Candidates
   │  ├─ Select 2 parents (tournament selection)
   │  ├─ Crossover (combine parents)
   │  ├─ Mutate (random modifications)
   │  ├─ Check constraints (validate)
   │  └─ Repeat until N valid candidates created
   │
   ├─ Evaluate New Candidates
   │  ├─ Calculate fitness for each new candidate
   │  └─ Combine with original population
   │
   ├─ Selection (Elitism)
   │  ├─ Rank all candidates by fitness
   │  ├─ Keep best population_size candidates
   │  └─ Discard rest
   │
   └─ Check Convergence
      ├─ If improvement < convergence_threshold AND generation >= min_generations
      │  └─ STOP (converged)
      └─ Else → continue to next generation

4. Return Best Solution
   └─ best_timetable, best_fitness
```

### Parameters Detailed

#### convergence_threshold
- **Type:** `float`
- **Default:** `0.1`
- **Meaning:** Improvement in fitness must exceed this to continue
- **Example:**
  ```python
  # Generation 5 fitness: 50.0
  # Generation 6 fitness: 49.95
  # Improvement: 0.05
  
  # If threshold=0.1, this improvement is too small → converge
  # If threshold=0.01, continue evolving
  ```

#### min_generations
- **Type:** `int`
- **Default:** `5`
- **Meaning:** Always run at least this many generations before checking convergence
- **Purpose:** Ensure algorithm explores enough before stopping

#### max_generations
- **Type:** `int` or `None`
- **Default:** `None` (uses self.generations from init)
- **Meaning:** Hard stop after this many generations (prevents infinite loops)

### Return Values

```python
best_timetable, best_fitness = ga.run()

# best_timetable structure:
{
    'Monday': {
        1: [course1, course2],      # Slot 1 on Monday
        2: [course3],
        3: [],
        ...
    },
    'Tuesday': { ... },
    'Wednesday': { ... },
    'Thursday': { ... },
    'Friday': { ... }
}

# best_fitness: float
# Lower values = better solutions
# Example: 42.5
```

### Example Usage

```python
# Run with defaults
best_timetable, best_fitness = ga.run()

# Run with custom convergence
best_timetable, best_fitness = ga.run(
    convergence_threshold=0.05,  # Stricter convergence
    min_generations=10,
    max_generations=200
)

# Check if solution found
if best_timetable is None:
    print("Failed to create initial population")
else:
    print(f"Best fitness: {best_fitness:.2f}")
```

---

## Input Data Structures

### Supporting Data Classes

#### Instructor

```python
class Instructor:
    def __init__(self, id, name):
        self.id = id          # int: unique ID
        self.name = name      # str: e.g., "Prof Kumar"
```

#### StudentGroup

```python
class StudentGroup:
    def __init__(self, name, size, super_groups=None):
        self.name = name              # str: e.g., "CSE-2025"
        self.size = size              # int: number of students
        self.super_groups = super_groups  # list: parent groups (hierarchy)
```

**Hierarchy Example:**
```python
class_2025 = StudentGroup(name="Class of 2025", size=200)
cse_2025 = StudentGroup(name="CSE-2025", size=50, super_groups=[class_2025])
rl_elective_2025 = StudentGroup(
    name="RL-Elective-2025", 
    size=35, 
    super_groups=[cse_2025, class_2025]
)
```

**Constraint Logic:**
- No two courses from same student group in same time slot
- No two courses from super_groups in same time slot
- Enforces scheduling consistency across hierarchy

---

## Usage Example

### Complete Initialization Example

```python
from ga.algorithm import GASearch
from tests.test_data import create_test_data

# Step 1: Get test data (or create your own)
data = create_test_data()

# Step 2: Initialize GASearch
ga = GASearch(
    time_slots=data['time_slots'],
    courses=data['courses'],
    preference_bins=data['preference_bins'],
    objective_function_weights=data['objective_function_weights'],
    rooms=data['rooms'],
    population_size=20,
    generations=100,
    mutation_rate=0.1
)

# Step 3: Run the algorithm
best_timetable, best_fitness = ga.run(
    convergence_threshold=0.1,
    min_generations=5
)

# Step 4: Process results
if best_timetable:
    print(f"✓ Solution found! Fitness: {best_fitness:.2f}")
    
    # Print schedule
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        print(f"\n{day}:")
        for slot, courses_in_slot in best_timetable[day].items():
            if courses_in_slot:
                print(f"  Slot {slot}: {[c.course_id for c in courses_in_slot]}")
else:
    print("✗ Failed to generate solution")
```

### Creating Custom Data

```python
# Define rooms
rooms = [
    Room(id=1, name="Room 101", x=0, y=0, z=0, capacity=50, is_lab=False),
    Room(id=2, name="Lab 201", x=5, y=0, z=0, capacity=60, is_lab=True)
]

# Define instructors
instructors = [
    Instructor(id=1, name="Prof A"),
    Instructor(id=2, name="Prof B")
]

# Define student groups
groups = [
    StudentGroup(name="Year-1", size=100),
    StudentGroup(name="Year-1-CSE", size=50, super_groups=[...])
]

# Define courses
courses = [
    CourseInstance(
        id=1, 
        course_id="CS101",
        session_type="lecture",
        instructor=instructors[0],
        room=rooms[0],
        student_grp=groups[1],
        slots_req=1,
        preference_bin=1
    ),
    # ... more courses
]

# Define bins and weights
preference_bins = {
    1: 1, 2: 1, 3: 1,
    4: 2, 5: 2, 6: 2,
    7: 3, 8: 3, 9: 3
}

objective_function_weights = [1.0, 0.5, 0.8]

time_slots = {
    'Monday': 9,
    'Tuesday': 9,
    'Wednesday': 5,
    'Thursday': 9,
    'Friday': 9
}

# Initialize and run
ga = GASearch(
    time_slots=time_slots,
    courses=courses,
    preference_bins=preference_bins,
    objective_function_weights=objective_function_weights,
    rooms=rooms
)

best_timetable, best_fitness = ga.run()
```

---

## Key Points Summary

### Initialization Checklist
- [ ] `time_slots`: dict with all 5 weekdays or single int
- [ ] `courses`: list of CourseInstance with all required fields
- [ ] `preference_bins`: dict mapping all slots to bins
- [ ] `objective_function_weights`: list of 3 weights
- [ ] `rooms`: list with appropriate is_lab flags
- [ ] `population_size`: reasonable for problem size
- [ ] `generations`: enough for convergence
- [ ] `mutation_rate`: appropriate for exploration/exploitation

### run() Method Checklist
- [ ] Call after successful initialization
- [ ] Returns (timetable, fitness) tuple
- [ ] timetable is dict or None on failure
- [ ] fitness is float (lower is better)
- [ ] Logs progress at each generation

### Common Issues
- **Empty population:** Courses too strict or insufficient rooms
- **High fitness:** Conflicting constraints or wrong weights
- **Slow convergence:** Increase population_size or mutation_rate
- **Early convergence:** Decrease convergence_threshold or increase mutation_rate
