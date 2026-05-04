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
- **Docker:** For containerized deployment

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
uv run python generate_seed_data.py
```

#### 2.5 Verify backend setup
```bash
# Run validation checks
uv run python validate_system.py
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
VITE_API_URL=http://localhost:5000
VITE_API_BASE_PATH=/api
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
uv run python generate_seed_data.py
```

---

## 🧪 Testing & Validation

### Run System Validation
```bash
cd backend
uv run python validate_system.py
```

This validates:
- Database connectivity
- GA algorithm functionality
- API endpoints
- Seed data integrity

### Run Tests
```bash
cd backend

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_ga.py -v

# Run with coverage
uv run pytest --cov=app tests/
```

### Generate Test Timetables
```bash
cd backend
uv run python schema/run_ga.py
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
│   ├── ga/                       # Genetic algorithm
│   │   ├── constraints.py       # Constraint checking
│   │   ├── population.py        # Population initialization
│   │   ├── operators.py         # GA operators
│   │   └── fitness.py           # Fitness evaluation
│   ├── generate_seed_data.py    # Seed data generator
│   ├── pyproject.toml           # Python dependencies
│   ├── main.py                  # Flask app entry point
│   └── README.md                # Backend documentation
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
├── schema/                       # Data schema & GA testing
│   ├── genetic_algorithm.py     # GA implementation
│   └── run_ga.py                # GA test runner
│
├── tests/                        # Test files
├── migrations/                   # Database migrations
└── README.md                     # This file
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
# Flask
FLASK_ENV=development
FLASK_APP=main.py
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/timetable.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/timetable

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Email (optional, for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:5000
VITE_API_BASE_PATH=/api
VITE_DEBUG=true
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
# Check VITE_API_URL in .env matches backend URL
# Check browser console for CORS errors
```

### GA Issues

**GA taking too long:**
- Reduce population size in GA parameters
- Reduce number of generations
- Check constraint violations in logs

**Constraint violations:**
```bash
cd backend
uv run python validate_system.py --verbose
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

## 🚀 Production Deployment

### Build Frontend
```bash
cd ui
bun run build
# Creates optimized build in dist/
```

### Deploy Backend
```bash
cd backend

# Set production environment
export FLASK_ENV=production
export DATABASE_URL=postgresql://...  # Use production DB

# Run with production server (gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Using Docker (Optional)
```bash
# Build Docker images
docker-compose build

# Run services
docker-compose up
```
