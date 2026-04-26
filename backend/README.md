# Timetable System Backend (Flask)

This is the Flask-based backend for the Automated Time Table Generation System. It handles data persistence, authentication, and the Genetic Algorithm for schedule optimization.

## Setup Instructions

### 1. Prerequisites
- Python 3.12 or higher
- `uv` (Next-generation Python package manager)

### 2. Installation
Navigate to this directory and sync dependencies:
```bash
uv sync
```

### 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Update the `DB_TYPE` (`sqlite` or `postgres`) and `DATABASE_URL` in your `.env`.

### 4. Database Initialization
The system uses `flask-migrate`. For the first run on a new database:
```bash
uv run flask db upgrade
```
*Note: This will set up all tables with the correct column lengths (e.g., VARCHAR(255) for secure hashes).*

### 5. Running the Server
```bash
uv run flask run --port 5000
```
The API will be available at `http://localhost:5000`.

## System Validation
To run a full end-to-end stress test (Reset -> Seed -> GA Run -> Verify -> Cleanse):
```bash
uv run python validate_system.py
```

## Tech Stack
- **Framework:** Flask
- **Database:** SQLAlchemy (PostgreSQL/Supabase & SQLite support)
- **Migrations:** Flask-Migrate (Alembic)
- **Tooling:** uv
- **Logic:** Custom Genetic Algorithm Integration
