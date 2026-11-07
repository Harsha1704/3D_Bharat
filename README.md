# 3D Bharat

3D Bharat is an AI-powered Indian heritage intelligence and digital preservation platform for discovering, mapping, and connecting India's monumental cultural heritage. It combines an interactive React map and knowledge graph explorer with a robust Python FastAPI backend managing geospatial heritage sites, cultural connections, archival media, 3D digital reconstructions, and historical sources.

## Features

- **Interactive Heritage Map:** Explore heritage sites across India with verified coordinates, category filters, and detailed architectural summaries.
- **Cultural Connections & Knowledge Graph:** Model relationships between dynasties, traditions, architectural styles, and trade routes.
- **Digital Preservation Media:** Archival photographs, historical documents, audio guides, and documentary footage linked to heritage sites with SHA-256 verification.
- **3D Digital Assets:** GLB, glTF, OBJ, PLY point clouds, and Gaussian Splat preservation models with coordinate reference systems and companion file tracking.
- **Historical Provenance & Sources:** Strict demarcation between verified historical facts, community submissions, and AI-derived suggestions.
- **Complete Heritage Discovery APIs:** Geographical bounding-box viewports, eager-loaded comprehensive monument dossiers, related-site graph & structured discovery, and multi-field text search.
- **Geospatial & Semantic Intelligence:** Sub-millisecond Haversine proximity queries and hybrid category/period/vector recommendations with in-memory embedding caching.

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, React Leaflet, Leaflet, Lucide React
- **Backend:** Python FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, Psycopg 3
- **Database:** PostgreSQL 17 (with native spherical distance optimization)
- **Digital Preservation Storage:** Secure local storage abstraction with content-sniffing and path traversal protection (object storage ready)

## Project Structure

```text
.
├── frontend/                     # React + TypeScript + Vite web application
│   ├── src/components/           # HeritageMap and UI explorer components
│   └── src/api.ts                # Frontend API client
├── backend/                      # FastAPI application and database migrations
│   ├── alembic/                  # Alembic migration revisions
│   ├── app/
│   │   ├── api/v1/               # Versioned REST API endpoints
│   │   ├── core/                 # Config, security, centralized DB session
│   │   ├── models/               # SQLAlchemy ORM declarative models
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   └── services/             # Domain logic, storage abstraction, graph engine
│   ├── storage/uploads/          # Local asset preservation storage (gitignored)
│   └── tests/                    # Automated pytest test suites (107 tests)
└── README.md
```

## Getting Started

### 1. Database Setup

Create a PostgreSQL 17 database named `3d_bharat`:

```sql
CREATE DATABASE 3d_bharat;
```

### 2. Configure Backend Environment

Copy `.env.example` to `backend/.env` (never commit `.env`):

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/3d_bharat
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
STORAGE_LOCAL_ROOT=storage/uploads
MAX_MEDIA_FILE_SIZE_BYTES=52428800    # 50 MB
MAX_3D_FILE_SIZE_BYTES=209715200      # 200 MB
```

### 3. Run Backend Service

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API starts at `http://127.0.0.1:8000`. Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### 4. Run Frontend

```cmd
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to explore the interactive application.

---

## API Overview (`/api/v1`)

| Domain | Method & Endpoint | Description |
| --- | --- | --- |
| **Discovery** | `GET /heritage-sites/search` | Multi-field search (name, dynasty, architecture, state, tags) with stable sorting & pagination |
| **Discovery** | `GET /heritage-sites/bbox` | Bounding-box viewport search with coordinate validation (`min_lat`, `min_lon`, `max_lat`, `max_lon`) |
| **Discovery** | `GET /heritage-sites/nearby` | Geodesic radius search using spherical distance calculation |
| **Discovery** | `GET /heritage-sites/{id}/details` | Comprehensive eager-loaded site dossier (sources, media with safe URLs, 3D assets, connections) |
| **Discovery** | `GET /heritage-sites/{id}/related` | Related heritage distinguishing documented archival links, structured relations, and AI suggestions |
| **Sites** | `GET /heritage-sites` | Paginated listing with basic pagination |
| **Sites** | `GET /heritage-sites/{id}` | Single heritage site by ID |
| **Sites** | `GET /heritage-sites/{id}/recommendations` | Hybrid semantic & structural recommendations |
| **Connections** | `GET /heritage-connections/site/{id}` | Connections linking a heritage site |
| **Graph** | `GET /heritage-graph` | Complete frontend-ready graph (nodes & edges) |
| **Sources** | `POST /heritage-sites/{id}/sources` | Register academic citation or archival source |
| **Sources** | `GET /heritage-sites/{id}/sources` | List sources and provenance citations |
| **Media** | `GET /heritage-media` | Global discovery of preservation media assets across all heritage sites |
| **Media** | `POST /heritage-sites/{id}/media` | Register media metadata |
| **Media** | `POST /heritage-sites/{id}/media/upload` | Multipart file upload with SHA-256 verification |
| **Media** | `GET /heritage-media/{id}/file` | Stream media asset safely |
| **3D Assets** | `GET /heritage-3d-assets` | Global discovery of 3D models and digital reconstructions across sites |
| **3D Assets** | `POST /heritage-sites/{id}/3d-assets` | Register 3D reconstruction metadata |
| **3D Assets** | `POST /heritage-sites/{id}/3d-assets/upload` | Multipart upload for GLB, glTF, OBJ, PLY, Splats |
| **3D Assets** | `GET /heritage-3d-assets/{id}/file` | Stream 3D model asset |
| **System** | `GET /health` | Healthcheck monitoring database connectivity |

---

## Storage & Digital Preservation Architecture

- **Path Traversal Protection:** Input filenames are sanitized; absolute paths are constrained to the storage root.
- **Allowed Formats:**
  - *Media:* `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.pdf`, `.mp3`, `.wav`, `.ogg`, `.mp4`
  - *3D Models:* `.glb`, `.gltf`, `.obj`, `.mtl`, `.ply`, `.splat`
- **Content Sniffing:** Verifies binary magic headers (JPEG, PNG, PDF, GLB, RIFF, OGG, PLY) to prevent malicious extension spoofing.
- **Integrity:** SHA-256 checksums are calculated during streaming and verified.
- **Failure Recovery:** Partial files are automatically unlinked if an upload or database transaction fails.
- **Security Note on Authentication:** As this platform currently does not include user session/role authentication, write and upload endpoints should be placed behind an API gateway or reverse proxy in production environments.

---

## Testing

Run the full automated backend test suite:

```cmd
cd backend
.venv\Scripts\pytest.exe backend/tests -v
```

Test coverage includes 107 passing tests:
- Bounding-box geographical viewport search and boundary coordinate validations
- Comprehensive site details eager loading (sources, media, 3D assets, connections) without N+1 queries
- Clear demarcation between documented archival links, structured relations, and exploratory AI suggestions
- Global discovery endpoints for preservation media and 3D digital reconstructions with safe file URLs
- Unit tests for storage abstraction, content sniffing, and path traversal guards
- CRUD, pagination, and error responses (400, 404, 409, 422) for sources, media, and 3D assets
- Mathematical edge-case validation for Haversine geodesic calculations
- Database CHECK constraints, transaction rollbacks, and session lifecycle
- Regression tests for existing heritage sites, connections, and knowledge graph
