# MRPL Sovereign AI Workbench - Frontend

## Architecture
This project implements a clean separation between the existing LangGraph backend and the new React frontend. The existing Python backend files have NOT been modified.

Instead, an API adapter layer (`api/server.py`) has been created using FastAPI. It imports the existing backend logic (`app.invoke()`), handles file uploads correctly by staging them in the project root for the vision node, monitors the air-gap execution securely, and returns structured JSON responses.

The frontend is built with React, TypeScript, Tailwind CSS, and Vite.

## Folder Structure
- `/api`: The API bridge to the existing backend
- `/frontend`: The Vite React application
- `/frontend/src/api`: Axios client communicating with the adapter
- `/frontend/src/pages`: Application views (Dashboard, Analysis)
- `/frontend/src/components`: UI components

## Running the Application
Open two terminals.

**Terminal 1 (Backend API Bridge):**
```bash
cd api
..\venv\Scripts\python server.py
```
This runs on port 8000.

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
This runs on port 5173.

## Environment Variables
Create a `.env` file in the `/frontend` directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Security Considerations
The application explicitly tracks air-gap status via the `airgap_monitor.py` auditor in the backend. The UI only reflects verifiable state. We do not manufacture artificial metrics. All backend files remain authoritative.
