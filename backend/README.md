# Automated Timetable Generation System - Backend

This folder contains the Flask-based REST API and Genetic Algorithm (GA) engine for optimizing institutional timetables.

## Architecture

- **`app/core`**: System configuration, `pathlib`-based universal path resolution, and security settings.
- **`app/models`**: Database schema using SQLAlchemy. Optimized for `CourseInstance` expansion to allow granular scheduling.
- **`app/routes`**: API endpoints (Auth, Ingestion, Scheduling, Preferences).
- **`app/services`**: Business logic layer. Bridges the database models to the `ga/` algorithm.
- **`instance/`**: Local SQLite database (`timetable.db`) and `seed_data.json`.
- **`ga/`**: The core Genetic Algorithm engine (independent of the web framework).

## Installation & Setup

The backend supports both modern `uv` (recommended) and standard `python/pip` workflows.

### Option A: Using `uv` (Modern & Fast)
1. **Sync Dependencies**:
   ```powershell
   uv sync
   ```
2. **Setup Environment**:
   - Create a `.env` file (see `.env.example`).
   - Default `DB_TYPE=sqlite` is recommended for local development.
3. **Run the Server**:
   ```powershell
   uv run main.py
   ```

### Option B: Using Standard `python`
1. **Create Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the Server**:
   ```powershell
   python main.py
   ```

## Database Management

- **Seeding**: Log in as an Admin in the UI and click **"Seed Data"**. This uses the optimized `seed_data.json` which maps institutional data to the new instance-based schema.
- **PostgreSQL Support**: Change `DB_TYPE=postgres` and provide `DATABASE_URL` in your `.env` to switch from SQLite to a production-grade database.

## System Maintenance

- **Nuke & Reset Database**:
  To permanently delete all data and re-initialize clean tables, you MUST specify a target:
  ```powershell
  # Reset ONLY SQLite
  uv run python nuke_db.py --sqlite

  # Reset ONLY PostgreSQL
  uv run python nuke_db.py --postgres

  # Reset BOTH databases
  uv run python nuke_db.py --all
  ```
  *Note: The script will not run if no target parameter is provided.*

- **Dry Run Validation**:
  ```powershell
  uv run python -m compileall .
  ```
- **Documentation**: See `doc.md` for the full Genetic Algorithm schema and API implementation details.
