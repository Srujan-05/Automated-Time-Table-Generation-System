# System Technical Documentation

## 1. Overview
This document outlines the architecture, data structures, and algorithmic logic for the Automated Timetable Generation System.

---

## 2. Backend Architecture (Service Layer)

The system follows a **Service-Oriented Design** to decouple API routing from business logic.

### SchedulingService (`app/services/scheduling_service.py`)
- **Logic**: Orchestrates the Genetic Algorithm.
- **Workflow**:
    1.  Fetches active `CourseInstance`, `Professor`, and `Room` records.
    2.  Maps DB models to internal GA classes (`Instructor`, `GARoom`, `GAInstance`).
    3.  Runs `GASearch.run()` to find an optimal configuration.
    4.  Wipes existing `TimetableEntry` and persists the new schedule.
- **Feedback**: Returns the final fitness score (lower is better).

### IngestionService (`app/services/ingestion_service.py`)
- **Logic**: Handles bulk data imports and normalization.
- **Course Expansion**: Automatically splits multi-slot requirements into multiple 1-slot `CourseInstance` records if `slots_continuous` is False. This allows the GA to distribute classes across different days.
- **Robustness**: Automatically creates parent `Course`, `Professor`, and `StudentGroup` records during ingestion if they don't exist.

### Auth & Preference Services
- **AuthService**: Manages JWT-based login and auto-links users to faculty profiles via email domain.
- **PreferenceService**: Manages the "Time Bin" preferences for instructors, allowing them to shift their availability between Morning, Noon, and Evening windows.

---

## 3. Genetic Algorithm (GA) Engine

### GASearch Class
The GA operates on a population of candidate timetables, using evolutionary strategies to minimize conflicts and maximize preference satisfaction.

#### Constraints Handled:
1.  **Hard Constraints**: 
    - No professor overlaps.
    - No student group overlaps.
    - No room overlaps.
    - Room capacity must fit group size.
2.  **Soft Constraints (Objective Functions)**:
    - **Course Time Preference (CTP)**: Penalizes placement outside the preferred time bin.
    - **Room-to-Room (RTR)**: Minimizes physical travel distance between consecutive classes.
    - **Stability**: Prefers consistent slot placement for the same course across different days.

### `run()` Method Parameters
- `convergence_threshold`: (float) Stops early if improvement is less than this value.
- `min_generations`: (int) Guarantees a minimum number of iterations before convergence check.
- `population_size`: (int) Number of candidate schedules to evolve simultaneously.

---

## 4. Configuration & Path Resolution

The system uses a custom **Pathlib-based Resolution** strategy in `app/core/config.py` to ensure zero path-related failures.

- **SQLite Stability**: Automatically converts relative `.env` paths to absolute POSIX paths. This prevents "unable to open database file" errors on Windows.
- **Platform Agnostic**: Uses `Path.resolve().as_posix()` to ensure forward-slashes are used for database URIs, matching SQLAlchemy's cross-platform expectations.

---

## 5. API Reference Summary

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/auth/signin` | POST | ALL | Authenticates and returns JWT + role. |
| `/api/timetable` | GET | ALL | Returns active schedule filtered by user role. |
| `/api/timetable/stats` | GET | ALL | Compiles dashboard metrics and recent activity. |
| `/api/timetable/generate`| POST | ADMIN | Triggers GA engine to rebuild the schedule. |
| `/api/ingestion/seed` | POST | ADMIN | Resets and populates DB with institutional JSON data. |
| `/api/preferences/shift` | POST | FACULTY| Updates preferred teaching window (Morning/Noon/Evening). |

---

## 6. Data Schema Details

### CourseInstance Model
The primary scheduling unit. Unlike a "Course," an "Instance" represents a specific teaching event (e.g., "Math 101 Lecture A").
- `slots_required`: How many hours per week.
- `preference_bin`: Preferred shift (1=Morning, 2=Noon, 3=Evening).
- `instructor_id`: FK to Professor.
- `student_group_id`: FK to StudentGroup.
