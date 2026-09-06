# 3D Bharat

3D Bharat is a heritage intelligence platform for discovering, mapping, and connecting India's cultural heritage. It combines a React map experience with a FastAPI service that manages heritage sites, relationships, and graph-based recommendations.

## Features

- Browse heritage sites on an interactive Leaflet map of India.
- Search sites and find nearby places of cultural interest.
- View heritage-site details, context, and related locations.
- Model connections between sites and generate a heritage graph.
- Serve data through a documented FastAPI API.

## Tech stack

- **Frontend:** React, TypeScript, Vite, React Leaflet, Lucide
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic
- **Database:** PostgreSQL with PostGIS support

## Project structure

```text
.
├── frontend/              # React + Vite web application
│   └── src/components/    # Map and explorer interface components
├── backend/               # FastAPI application and database migrations
│   ├── app/api/v1/        # REST API routes
│   ├── app/models/        # SQLAlchemy models
│   └── alembic/           # Database migrations
└── README.md
```

## Prerequisites

- Node.js 20 or later
- Python 3.10 or later
- PostgreSQL with the PostGIS extension enabled

## Run locally

### 1. Start the database

Create a PostgreSQL database and enable PostGIS:

```sql
CREATE DATABASE 3d_bharat;
\c 3d_bharat
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. Configure and start the backend

Create `backend/.env` (this file is intentionally not committed):

```env
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/3d_bharat
```

Install the Python dependencies and run migrations:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The API starts at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL shown by Vite (normally `http://localhost:5173`). The frontend is configured to call the backend at `http://127.0.0.1:8000`.

## API overview

All versioned endpoints begin with `/api/v1`.

| Resource | Example endpoints |
| --- | --- |
| Heritage sites | `GET /heritage-sites`, `GET /heritage-sites/search`, `GET /heritage-sites/nearby` |
| Site recommendations | `GET /heritage-sites/{site_id}/recommendations` |
| Heritage connections | `POST /heritage-connections`, `GET /heritage-connections/site/{site_id}` |
| Heritage graph | `GET /heritage-graph`, `POST /heritage-graph/generate` |

Health endpoints:

```text
GET /          # Service metadata
GET /health    # Health check
```

## Available frontend commands

Run these from `frontend/`:

```powershell
npm run dev     # Start development server
npm run build   # Type-check and create a production build
npm run lint    # Run ESLint
```

## Environment and secrets

Do not commit `backend/.env` or credentials. The root `.gitignore` excludes environment files, virtual environments, generated caches, dependency folders, and build output.
