# Automated Time Table Generation System

A modern, Genetic Algorithm-powered timetable scheduler designed for Mahindra University. It features a robust Flask backend (Python 3.12+) and a premium React (Vite) frontend with role-based access control.

## 🎯 Key Features

- **GA Optimization:** Advanced genetic algorithm for conflict-free scheduling with department-based room allocation
- **Dynamic RBAC:** Automatic role detection (Admin/Faculty/Student) from university emails
- **Role-Based Hubs:** Tailored dashboards showing relevant academic and system metrics
- **Dual Database:** Seamlessly switch between SQLite and Cloud PostgreSQL (Supabase)
- **Pro Exports:** One-click PDF generation and `.ics` calendar synchronization
- **Admin Tools:** ZIP-based template management and atomic database seeding
- **Department Constraints:** Room allocation respects department restrictions

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- **Python:** 3.12 or higher
- **Node.js:** 18.x or higher
- **Git:** For cloning the repository
- **macOS/Linux/Windows:** Any OS with Python 3.12+ support

### Package Managers
- **Backend:** `uv` (ultra-fast Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Frontend:** `bun` (fast JavaScript runtime) - [Install bun](https://bun.sh/docs/installation) OR `npm`/`yarn`

### Optional
- **PostgreSQL:** For production database (Supabase recommended for cloud)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Automated Time Table Gen"
```

### 2. Backend Setup (Python/Flask)

#### 2.1 Navigate to backend directory
```bash
cd backend
```

#### 2.2 Install dependencies using `uv`
```bash
# Install all dependencies from pyproject.toml
uv sync

# Or if using pip
pip install -r requirements.txt
```

#### 2.3 Configure environment variables
```bash
# Create .env file in backend/ directory
cp .env.example .env  # (if provided, otherwise create manually)

# Edit .env with your configuration:
# - FLASK_ENV=development
# - FLASK_APP=main.py
# - DATABASE_URL=sqlite:///instance/timetable.db (or PostgreSQL URL)
# - SECRET_KEY=your-secret-key-here
```

#### 2.4 Initialize the database
```bash
# Run migrations
uv run flask db upgrade

# Generate seed data (optional, for testing)
# From backend directory:
uv run python ../tests/generate_seed_data.py
# OR from project root:
python tests/generate_seed_data.py
```

### 3. Frontend Setup (React/Vite)

#### 3.1 Navigate to ui directory
```bash
cd ../ui
```

#### 3.2 Install dependencies using `bun`
```bash
# Using bun (recommended for speed)
bun install

# OR using npm
npm install

# OR using yarn
yarn install
```

#### 3.3 Configure environment variables
```bash
# Create .env file in ui/ directory
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5000/api
EOF
```

#### 3.4 Build the frontend (optional, for production)
```bash
bun run build
# OR npm run build
```

---

## ▶️ Running the Application

### Start Backend Server

```bash
cd backend

# Using uv
uv run flask run --port 5000

# OR using Python directly (if dependencies installed via pip)
python -m flask run --port 5000
```

**Expected Output:**
```
 * Serving Flask app 'main'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Start Frontend Development Server

In a **new terminal**:

```bash
cd ui

# Using bun (recommended)
bun dev

# OR using npm
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000/api

---

## 🔧 Database Management

### Initialize Fresh Database
```bash
cd backend

# Drop existing database (development only!)
# Remove instance/timetable.db file or PostgreSQL database

# Run migrations
uv run flask db upgrade

# Seed initial data
uv run python generate_seed_data.py
```

### Database Migrations (after model changes)
```bash
cd backend

# Create new migration
uv run flask db migrate -m "description of changes"

# Apply migration
uv run flask db upgrade

# Rollback migration
uv run flask db downgrade
```

### Connect to Cloud Database (PostgreSQL/Supabase)
Edit `backend/.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/database_name
```

Then run migrations:
```bash
cd backend
uv run flask db upgrade
uv run python ../tests/generate_seed_data.py
```

---

## 🧪 Testing & Validation

### Run Tests
```bash
cd tests

# Run simple test
python simple_test.py

# Run full test suite
python run_test.py
```

### Generate Test Timetables (GA Testing)
```bash
cd schema/test
python run_ga.py
```

---

## 🗂️ Project Structure

```
Automated Time Table Gen/
├── backend/                      # Flask API
│   ├── app/
│   │   ├── models.py            # Database models
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── extensions.py        # Flask extensions
│   ├── migrations/              # Database migrations
│   ├── instance/                # Database & instance files
│   ├── main.py                  # Flask app entry point
│   ├── nuke_db.py               # Database reset utility
│   ├── pyproject.toml           # Python dependencies
│   ├── requirements.txt         # Python requirements (legacy)
│   ├── .env.example             # Environment variables template
│   └── README.md                # Backend documentation
│
├── ga/                           # Genetic algorithm (core)
│   ├── constraints.py           # Constraint checking
│   ├── population.py            # Population initialization
│   ├── operators.py             # GA operators (crossover, mutation)
│   ├── fitness.py               # Fitness evaluation
│   └── README.md                # GA documentation
│
├── ui/                           # React/Vite frontend
│   ├── src/
│   │   ├── pages/               # Page components
│   │   ├── components/          # Reusable components
│   │   ├── hooks/               # Custom React hooks
│   │   └── lib/                 # Utilities & API client
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── vite.config.ts           # Vite config
│   └── README.md                # Frontend documentation
│
├── schema/                       # Data schema & experimental GA
│   ├── genetic_algorithm.py     # GA implementation (legacy)
│   ├── genetic_algorithm_improved.py # Improved GA version
│   ├── test/
│   │   ├── run_ga.py            # GA test runner
│   │   └── ga_verbose_output.txt # Test output logs
│   ├── raw_data/                # Sample data files
│   └── README.md                # Schema documentation
│
├── tests/                        # Test files & utilities
│   ├── run_test.py              # Main test runner
│   ├── simple_test.py           # Simple tests
│   ├── test_data.py             # Test data generation
│   └── generate_seed_data.py    # Seed data generator
│
├── migrations/                   # Alembic database migrations
├── .venv/                        # Python virtual environment
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
# Flask
FLASK_ENV=development
FLASK_APP=main.py
SECRET_KEY=your-super-secret-key-here

# Database Selection: 'sqlite' or 'postgres'
DB_TYPE=sqlite

# SQLite URL (Used if DB_TYPE=sqlite)
SQLITE_URL=sqlite:///instance/timetable.db

# PostgreSQL URL (Used if DB_TYPE=postgres)
DATABASE_URL=postgresql://user:password@localhost:5432/timetable

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:5000/api
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 5000 already in use:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (macOS/Linux)
kill -9 <PID>

# OR use different port
flask run --port 5001
```

**Database connection error:**
```bash
# Check DATABASE_URL in .env
# Ensure database file exists or PostgreSQL is running
# Reinitialize: rm instance/timetable.db && flask db upgrade
```

**Module not found errors:**
```bash
# Reinstall dependencies
uv sync --reinstall
# OR
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Use different port
bun dev --port 5174
# OR npm run dev -- --port 5174
```

**Node modules issues:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm bun.lockb  # or package-lock.json
bun install  # or npm install
```

**API connection errors:**
```bash
# Verify backend is running on http://localhost:5000
# Check VITE_API_BASE_URL in .env matches backend URL (http://localhost:5000/api)
# Check browser console for CORS errors
```

---

## 📚 Documentation

For detailed information, refer to:
- [Backend Logic Documentation](./backend/doc.md)
- [Backend README](./backend/README.md)
- [Frontend README](./ui/README.md)
- [GA Documentation](./schema/README.md)
- [Class Documentation](./CLASSES_DOCUMENTATION.txt)

---
