# Timetable System Frontend (React)

A premium, responsive dashboard interface for the Automated Time Table Generation System, built with React, Vite, and Tailwind CSS.

## Setup Instructions

### 1. Prerequisites
- Node.js 18 or higher
- **Bun** (Recommended for performance)

### 2. Installation
Navigate to this directory and install dependencies:
```bash
bun install
```

### 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Ensure `VITE_API_BASE_URL` points to your running backend (default: `http://localhost:5000/api`).

### 4. Running the Development Server
```bash
bun dev
```
The UI will be available at `http://localhost:5173`.

## Core Features
- **Intelligent Dashboard:** Dynamic stats that change based on your role (Admin, Faculty, or Student).
- **Interactive Timetable:** Click any session to see full details in a themed popup.
- **Calendar Integration:** Export your schedule as an `.ics` file for Google/Outlook calendars.
- **Pro Printing:** Perfectly scaled A4 landscape PDF export.
- **Role-Based Views:**
  - **Admins:** Global control, GA engine management, and data seeding.
  - **Faculty:** Teaching window preference management.
  - **Students:** Group-scoped schedules and enrollment metrics.

## Tech Stack
- **React 18 & Vite**
- **TypeScript** (Soundly typed)
- **Tailwind CSS & Framer Motion**
- **Radix UI** (via Shadcn)
- **Phosphor Icons**
