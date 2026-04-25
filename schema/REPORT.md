# Automated Timetable Generation System - Schema & Algorithm Documentation

This document outlines the workflow, data structures, and algorithmic setup developed for the Automated Timetable Generation System. It serves as a comprehensive overview of the backend and genetic algorithm (GA) implementation, functioning as a clean readme for version control and team onboarding.

## 1. Input Data Source
* **`schema/all_years.md`**: The raw curriculum data source containing course schedules for 2nd and 3rd year students. It includes course codes (e.g., MA2103, CS2104), instructor names, student groups (CS1-4, AI1-3, ECE, ECM, CB, BT, CE, ME, MT, NT), and implied session types (Lecture, Tutorial, Lab). We used this document to extract real-world constraints, resulting in a comprehensive dataset of 53 professors, 34 rooms, 15 student groups, and 74 unique course requirements.

## 2. Database & Infrastructure Setup
We established a PostgreSQL database (`timetable_db`) to store and manage the requirements and generated schedules seamlessly.
* **`schema/test/.env`**: Contains local PostgreSQL credentials and configuration.
* **`schema/test/db_setup.py`**: Initializes the database schema. It creates 5 core tables—`professors`, `rooms`, `student_groups`, `course_requirements`, and `generated_schedules`. It also seeds these tables utilizing the structured data parsed out of `all_years.md`.

## 3. The `test/` Environment & Genetic Algorithm Setup
The `schema/test/` directory acts as our primary algorithmic sandbox. Below is a breakdown of the files and their system responsibilities:

* **`classes.py`**: Defines the core Python object models mapped from the database:
  * `Instructor`: Represents the professor entity.
  * `Room`: Represents physical rooms, tracking attributes like capacity, whether it's specialized as a lab, and (x, y, z) coordinates used to calculate walking distances.
  * `StudentGroup`: Denotes specific student cohorts with varying enrollment sizes.
  * `CourseInstance`: Encapsulates a distinct scheduling requirement (e.g., specific professor, specific group, duration).
* **`preprocessor.py`**: Bridges the relational data from PostgreSQL by converting rows into instantiated Python objects (defined in `classes.py`) ready to be fed into the generic algorithm environment.
* **`genetic_algorithm.py`**: The baseline implementation of the genetic algorithm utilizing a greedy initialization strategy.
* **`genetic_algorithm_improved.py`**: An enhanced algorithmic iteration designed with evolutionary operators such as crossover (swapping whole days between candidate timetables), mutation, tournament selection, and preference-aware initialization.
* **`run_ga.py` & `run_ga_improved.py`**: Execution scripts running the generation logic with varying hyperparameter setups (generations, population sizes, mutation rates).
* **`save_schedule.py`**: Persists the mathematically optimal generated timetable back mapping the structures into JSON into the `generated_schedules` table in PostgreSQL.

### Algorithm Assumptions & Constraints
While building and testing the scheduling logic, several key constraints and structural configurations were established:
* **Time Structure**: A standard 5-day academic week (Monday to Friday) was assumed, featuring exactly 10 available time slots per operating day.
* **Hard Constraints** (Any candidate timeline violating these is inherently discarded as unviable):
  1. No single professor teaches two different classes concurrently.
  2. No student group attends two different classes concurrently.
  3. No room hosts two classes at the same time.
  4. Lab courses must strictly be placed within designated (`is_lab=True`) rooms.
  5. Room capacity must strictly comfortably seat the class's `student_group` size.
  6. Courses must be scheduled matching their precise required number of blocks.
  7. Certain laboratory blocks flagged as continuous must occupy chronologically consecutive time slots.
  8. A soft maximum of 1 lecture module per day for any unique (course, student cohort) combination unless explicitly permitted.
* **Soft Objectives** (Calculated as penalty offsets applied to fitness scores during evolution):
  * *Course Time Preference (CTP)*: Matching a course against natural preferences in time-of-day (Morning/Noon/Evening slots).
  * *Room-to-Room Distance (RTR)*: Minimizing raw physical travel distance navigating campus between consecutive classes for students.
  * *Course Stability (CTRR)*: Heavily penalizing schedules where identical recurring weekly sessions for a course scatter across widely different time slots or varying rooms.

## 4. Next Steps
1. **Refine Evolutionary Operators**: Debug and tune the crossover and mutation functions in `genetic_algorithm_improved.py` to ensure the GA successfully navigates toward convergence and mathematically healthier fitness scores across advancing generations.
2. **Hyperparameter Tuning**: Test varying configurations of initial population capacities, mutation rates, and dynamic weighting on Soft Objectives to see which configuration scales most efficiently.
3. **UI Integration**: Connect the backend PostgreSQL datasets and outputs to the React/Vite frontend. The goal is to visually parse the generated JSON blobs directly into user-friendly graphical timetable grids.
4. **Advanced Scheduling Parameters**: Start factoring in granular preferences like locking hard maintenance hours, setting universally synchronized lunch breaks, or explicitly implementing algorithm controls balancing absolute faculty workload limits per-day workload distributions.

## TL;DR
- **Source Data**: Parsed university curriculum constraints from `all_years.md`.
- **Database**: Stored structured requirements (professors, rooms, courses, groups) in local PostgreSQL (`timetable_db`).
- **Engine**: Built a Python-native Genetic Algorithm to automatically generate conflict-free schedules satisfying 8 hard constraints across a 5-day, 10-slot week.
- **Output**: Writes the optimal generated schedule as JSON back to the database.
- **Next**: Tune the algorithm's evolutionary parameters for better optimization and integrate the JSON output with our React frontend.
