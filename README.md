# Automated Time Table Generation System

A modern, Genetic Algorithm-powered timetable scheduler designed for Mahindra University. It features a robust Flask backend (Python 3.12+) and a premium React (Vite) frontend with role-based access control.

## 🚀 Key Features

- **GA Optimization:** Advanced genetic algorithm for conflict-free scheduling.
- **Dynamic RBAC:** Automatic role detection (Admin/Faculty/Student) from university emails.
- **Role-Based Hubs:** Tailored dashboards showing relevant academic and system metrics.
- **Dual Database:** Seamlessly switch between SQLite and Cloud PostgreSQL (Supabase).
- **Pro Exports:** One-click PDF generation and `.ics` calendar synchronization.
- **Admin Tools:** ZIP-based template management and atomic database seeding.

---

## 🛠️ Quick Start

### 1. Backend (Flask)
```bash
cd backend
uv sync
# Configure .env
uv run flask db upgrade
uv run flask run --port 5000
```

### 2. Frontend (React)
```bash
cd ui
bun install
# Configure .env
bun dev
```

---

## 🧪 Validation & Integrity
We provide a dedicated validation tool to ensure all system components (Ingestion, DB, GA) are working correctly on your current environment:
```bash
cd backend
uv run python validate_system.py
```

---

## 📚 Documentation
For detailed logic, API schemas, and architectural patterns, please refer to:
- [Backend Logic Documentation](./backend/doc.md)
- [Backend README](./backend/README.md)
- [UI README](./ui/README.md)

## ⚖️ License
MIT
