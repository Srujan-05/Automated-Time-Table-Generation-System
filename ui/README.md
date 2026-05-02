# Timetable System Frontend (React)

A premium, responsive dashboard for the Automated Timetable Generation System, built with **React**, **Vite**, and **Tailwind CSS**.

## Installation & Development

The frontend supports **Bun** (highly recommended for speed) and standard **Node.js/npm** environments.

### Option A: Using Bun (Recommended)
1. **Install Dependencies**:
   ```bash
   bun install
   ```
2. **Setup Environment**:
   - Create `.env` from `.env.example`.
   - Ensure `VITE_API_BASE_URL=http://localhost:5000/api`.
3. **Run Dev Server**:
   ```bash
   bun dev
   ```

### Option B: Using Node.js (npm / pnpm)
1. **Install Dependencies**:
   ```bash
   npm install
   # OR
   pnpm install
   ```
2. **Run Dev Server**:
   ```bash
   npm run dev
   # OR
   pnpm dev
   ```

## Production Build
To generate a production-ready static bundle:
```bash
bun build  # or npm run build
```
The output will be in the `dist/` directory.

## System Validation
Before committing changes, run the following to ensure quality:
- **Linting**: `npm run lint`
- **Type Checking**: `npx tsc --noEmit`

## Advanced Features
- **Dynamic Role Dashboard**: Tailored metrics for Admins, Faculty, and Students.
- **Export Engine**:
  - **ICS**: Sync classes with Google/Outlook calendars.
  - **PDF**: Pro-grade A4 landscape prints.
  - **JSON**: Raw data exports for system backups.
- **GA Feedback**: Real-time toast notifications for GA convergence and fitness scores.

## Tech Stack
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Framer Motion
- **UI Components**: Radix UI (via Shadcn)
- **Icons**: Phosphor Icons
