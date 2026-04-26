# Automated Timetable System - Technical Documentation

This document serves as the authoritative guide for the backend logic, algorithm integration, and API specifications.

---

## 🛠️ 1. Infrastructure & Environment

### A. Dependency Management
- **Tool**: `uv` (Next-generation Python package manager).
- **Project Configuration**: `pyproject.toml` defines core dependencies and Python version (>=3.12).
- **Database Driver**: `psycopg2-binary` for Cloud PostgreSQL (Supabase) integration.

### B. Database Strategy
- **Dual Support**: Toggled via `DB_TYPE` (`sqlite` | `postgres`).
- **Schema Management**: Controlled via `flask-migrate`.
- **Security**: `password_hash` column is `VARCHAR(255)` to support modern `scrypt` hashing produced by Werkzeug 3.0+.

---

## 🔐 2. Authentication & RBAC Logic

### A. Implicit Role Detection
Roles are determined at signup based on the Mahindra University email prefix:
- **Admin**: Hardcoded list in `config.py` (e.g., `se23ucse020`).
- **Student**: Email contains numeric identifiers (e.g., `se23ucse010`).
- **Faculty**: Email contains alphabetical characters only.

### B. Dynamic Student Group Mapping
Student emails are deterministically mapped to class groups:
- **Logic**: Branch Code + `ceil(ID / 80)`.
- **Example**: `se23ucse150` -> Branch: `CS`, ID: `150`. `150/80 = 1.875` -> **CS2**.

### C. Faculty Linking
During signup, the system normalizes the professor's email to match pre-ingested faculty records, ensuring their account is correctly linked to their assigned courses.

---

## 🧬 3. Genetic Algorithm (GA) Integration

### A. Core Dependency
The backend imports the optimization engine directly from the root directories:
- `/ga`: Core algorithm logic.
- `/schema/classes.py`: Shared data models (Instructor, Room, CourseInstance).

### B. The Object Identity "Monkeypatch"
The `ga/constraints.py` logic uses `id(course)` to track slot counts. However, the greedy initializer in `ga/population.py` creates object copies. 
- **Solution**: `GAService` performs a temporary monkeypatch of `copy.copy` during the `create_population()` phase. 
- **Effect**: It returns the original object reference for `CourseInstance` types, preserving their memory ID and satisfying **Constraint #9** (Total slots count) without modifying the source algorithm.

---

## 📂 4. Data Ingestion Logic

### A. Seed System (`/api/ingestion/seed`)
- **Action**: Drops all tables and recreates them.
- **Source**: `backend/instance/seed_data.json`.
- **Automation**: Populates Professors, Rooms, Groups, and Course Requirements in a single atomic transaction.

### B. Template Management
- **Endpoint**: `GET /api/ingestion/templates`.
- **Logic**: Dynamically bundles `courses.csv`, `faculties.csv`, and `rooms.csv` from the `instance/` folder into a single ZIP file for user download.

---

## 📊 5. API Reference (Core)

### Dashboard Statistics (`GET /api/timetable/stats`)
Returns role-aware data payloads:
- **Admin**: `{ "primary": "Total Courses", "secondary": "Active Faculty", "tertiary": "Total Rooms" }`
- **Faculty**: `{ "primary": "My Courses", "secondary": "Weekly Hours", "quaternary": "My Preference" }`
- **Student**: `{ "primary": "Enrolled Courses", "secondary": "Active Rooms", "tertiary": "Total Professors" }`

### Timetable Retrieval (`GET /api/timetable`)
- **Logic**: Filters globally for **Active** schedules only.
- **Student Filter**: Automatically scoped to their mapped group (e.g., "CS1").
- **Faculty Filter**: Scoped to courses where the user is the assigned instructor.

### Preference Management (`POST /api/preferences/shift`)
- **Payload**: `{ "bin_id": 1|2|3 }` (1: Morning, 2: Afternoon, 3: Flexible).
- **Admin Override**: Admins can append `professor_id` to the payload to manage preferences for any faculty member.

---

## 🗄️ 6. Activity Logging
The `activity_logs` table tracks:
1.  **NOTIFICATION**: GA Start/Stop, critical system failures.
2.  **CHANGE**: Schedule generation success (with fitness score), preference updates.
These events are dynamically surfaced on the Admin Dashboard "Notifications" panel.
