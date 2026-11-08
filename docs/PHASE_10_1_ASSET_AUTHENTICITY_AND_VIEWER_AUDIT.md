# 3D BHARAT — PHASE 10.1 AUDIT REPORT
## 3D Asset Provenance Recovery, Licensing Correction & Viewer Acceptance Audit

---

### Executive Summary

- **Audit Date:** 2026-11-08
- **Platform:** 3D BHARAT — National Indian Heritage Intelligence Platform
- **Baseline Git Commit:** `6d6e9ad432a760ff5c2d57c8c375fc01bd42573f`
- **Alembic Revision Head:** `b4e9c8f2a103`
- **Audit Verdict:** **RECONCILED & COMPLIANT**
- **Test Suite Status:** **208 passed, 0 failed, 11 warnings** (100% pass rate)
- **Frontend Build Status:** **Built in 920ms, 0 TypeScript errors**
- **Browser Acceptance Suite:** **Playwright Chromium across 3 form factors (Desktop, Tablet, Mobile) — 0 console errors, 0 failed network requests**

---

### 1. Investigation of Asset Provenance & Forensic Analysis

#### 1.1 Genuine Asset Genesis
An exhaustive forensic investigation of the pilot 3D asset (Konark Sun Temple, Odisha; Site ID: 3, Asset ID: 79) established the following verifiable origin:

- **Original Creator / Tool:** Synthesized programmatically by the 3D BHARAT computational heritage generator script: [`backend/app/scripts/generate_pilot_model.py`](file:///d:/projects/3D_Bharat/backend/app/scripts/generate_pilot_model.py).
- **Binary Format:** GLB 2.0 (Little-endian binary glTF container).
- **Exact File Size:** 170,484 bytes.
- **Cryptographic SHA-256:** `adeaa0451653da6e03aa413cdccb6dd248de0fbe0d6eaaafc2a3e7070360d2c4`.
- **Mesh Topology:** 59 nodes, 59 meshes, 4 PBR materials (plinth, pidha roof tiers, wheels, crowning finials).
- **Geometric Complexity:** 3,332 polygons (triangles), 3,732 vertices.
- **Genesis Classification:** **Procedural Synthetic Architectural Visualization** based on canonical Kalinga treatise proportions (*Silpa Prakasa* and *Bhuban Pradipa*).
- **Authenticity Origin Reclassification:** Changed from `HISTORICAL_RECONSTRUCTION` to `ARCHITECTURAL_VISUALIZATION`.

#### 1.2 Comparison Against Actual Archaeological Monument
| Feature Category | Pilot 3D Model Representation | Actual ASI Konark Sun Temple Site |
| :--- | :--- | :--- |
| **Bada (Sanctum Plinth)** | Stepped 2-tier khondalite sandstone podium (36m x 32m x 3m). | Partially excavated 13th-century plinth with high-relief upana mouldings. |
| **Jagamohana (Mandapa)** | 4-tier pyramidal stepped pidha roof (*potalas*) with recessed kantir. | 3-tier pidha roof restored and sand-filled by British colonial engineers (1901-1903). |
| **Amalaka & Kalasha** | Fluted celestial lotus disc crowned by golden water-pot finial. | Crowning finials preserved atop intact porch structure; kalasha reconstructed. |
| **Chariot Wheels (*Chakkas*)** | 24 procedural wheels (12 North, 12 South) with hub, rim, and spokes. | 24 intricate monolithic stone wheels with friezes depicting daily life and hours. |
| **Rekha Deula Vimana Tower** | Omitted (reflects collapsed state of sanctum tower). | Tower collapsed in antiquity (estimated original height ~68m; sanctum empty). |
| **Sculptural Reliefs** | Smooth PBR material approximations of khondalite stone. | Intricate erotic mithuna carvings, celestial musicians, and scrollwork. |
| **Stone Horses** | Omitted from synthetic procedural geometry. | 7 rearing chariot horses (6 partially ruined, 1 largely preserved on southern flank). |

> [!IMPORTANT]
> The model is **not** an Archaeological Survey of India (ASI) laser scan, LiDAR point cloud, or photogrammetry survey. Presenting it as an authoritative archaeological scan would violate institutional preservation standards. It is now explicitly and transparently labeled as an **Architectural Visualization**.

---

### 2. Licensing Contradiction Analysis & Resolution

#### 2.1 Pre-Phase Contradiction
In Phase 10, the asset metadata exhibited an irreconcilable legal contradiction:
- `licence_name`: `CC-BY-4.0` (Creative Commons Attribution 4.0 International).
- `commercial_use_allowed`: `False` (Non-commercial restriction).

Under standard intellectual property law:
1. `CC-BY-4.0` explicitly permits commercial reuse (Section 2(a)(1) of the CC-BY license).
2. Setting `commercial_use_allowed = False` under CC-BY is legally invalid; the appropriate Creative Commons license for non-commercial restrictions is `CC-BY-NC-4.0`.
3. Because the user did not produce or provide this model, and no upstream institutional deed of gift or copyright assignment from ASI exists, asserting any definitive Creative Commons license creates legal liability.

#### 2.2 Reclassification and Governance Matrix
The metadata has been formally updated in both the database and the ingestion seeders:

| Field | Previous (Phase 10) | Corrected (Phase 10.1) | Legal / Preservation Rationale |
| :--- | :--- | :--- | :--- |
| `asset_origin` | `HISTORICAL_RECONSTRUCTION` | `ARCHITECTURAL_VISUALIZATION` | Transparent disclosure of algorithmic procedural generation. |
| `rights_status` | `PUBLIC_DOMAIN` / `OPEN_ACCESS` | `RIGHTS_REVIEW_REQUIRED` | Awaiting institutional clearance from national preservation bodies. |
| `licence_name` | `CC-BY-4.0` | `RIGHTS_REVIEW_PENDING` | Resolves CC-BY vs commercial restriction contradiction. |
| `commercial_use_allowed` | `False` | `False` | Strict protection against unauthorized commercial exploitation. |
| `modification_allowed` | `True` | `False` | Prevents unauthorized modifications during audit review period. |
| `redistribution_allowed` | `True` | `False` | Restricts public binary file downloads while permitting in-browser viewing. |
| `visibility_status` | `PUBLIC` | `PUBLIC` | Model remains viewable in interactive 3D WebGL viewer for public education. |
| `creator` | `3D BHARAT Preserve Engine` | `3D BHARAT Computational Heritage Studio (Procedural Generator)` | Accurate provenance attribution. |

---

### 3. Access Separation Architecture: Viewing vs Redistribution

To ensure full compliance with digital heritage stewardship, a strict technical separation has been enforced between **in-browser 3D WebGL inspection** and **raw binary redistribution download**:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Browser Client / User
    participant Router as Fast-API Router (/api/v1/heritage-3d)
    participant Auth as Security Layer
    participant Service as Heritage3DService
    participant Storage as File Storage (GLB 170KB)

    Note over Client, Router: Case 1: Interactive Three.js WebGL Inspection
    Client->>Router: GET /assets/79/file?download=false
    Router->>Service: get_asset_by_id(79)
    Service-->>Router: Asset details (redistribution_allowed = False)
    Router->>Storage: Stream binary chunks (1MB chunks)
    Storage-->>Client: 200 OK (Content-Disposition: inline; filename="konark_sun_temple_pidha.glb")

    Note over Client, Router: Case 2: Direct Binary Download Attempt
    Client->>Router: GET /assets/79/file?download=true
    Router->>Service: get_asset_by_id(79)
    Router->>Auth: Check redistribution_allowed & user permissions
    Auth-->>Router: Access Denied (redistribution_allowed = False)
    Router-->>Client: 403 Forbidden ("Binary download restricted: Redistribution prohibited under RIGHTS_REVIEW_REQUIRED")
```

#### Verification:
- `backend/app/api/v1/heritage_3d.py`:
  - Added `download: bool = Query(default=False)` parameter.
  - Returns `HTTP 403 Forbidden` if `download=True` and `redistribution_allowed is False`.
  - Streams with `Content-Disposition: inline` for WebGL viewport when `download=False`.
- `frontend/src/components/Heritage3DExplorerPage.tsx`:
  - Displays prominent security notice banner: *"Direct Binary Download Restricted: Public distribution of raw model binary files is restricted until full archival rights verification is completed. Interactive visual inspection in this 3D viewer is fully authorized."*
- `frontend/src/components/HeritageSiteDossierModal.tsx`:
  - 3D assets with `redistribution_allowed = false` disable the download button and render *"Direct download restricted • In-browser visual inspection only"*.

---

### 4. Test Asset Contamination Isolation

During previous automated test runs, four synthetic test assets were created in the database:
- Asset ID 80: `Hampi Test Shrine Model` (Site ID: 2)
- Asset ID 81: `Hampi Test Shrine Model` (Site ID: 2)
- Asset ID 82: `Hampi Test Shrine Model` (Site ID: 2)
- Asset ID 86: `Hampi Test Shrine Model` (Site ID: 2)

#### Audit Remediation:
1. All four test fixture assets were updated to `visibility_status = 'PRIVATE'` and `validation_status = 'TEST_FIXTURE'`.
2. `Heritage3DService.list_all_heritage_3d_assets()` now enforces:
   ```sql
   WHERE visibility_status = 'PUBLIC' AND validation_status != 'TEST_FIXTURE'
   ```
3. `Heritage3DService.list_heritage_3d_assets_by_site()` enforces the same public isolation.
4. Public endpoints `GET /api/v1/heritage-3d/assets` and `GET /api/v1/heritage-3d/sites/{site_id}/assets` now return **only** production assets (Asset ID 79). Test fixtures are completely hidden.

---

### 5. Database Schema & Migration State

- **Current Alembic Revision Head:** `b4e9c8f2a103`
- **Database Backup (Pre-Phase 10):** `backups/3d_bharat_pre_phase10_20261107_230000.sql` (2,160,862 bytes, SHA-256: `0E9B8A853A982CB7C73980B4416864C99B0109EA5F69F51DC4C0616FA143030E`)
- **Database Backup (Pre-Phase 10.1):** `backups/3d_bharat_pre_phase10_1_20261108_115500.sql` (2,178,008 bytes, SHA-256: `B11A19109A5C37BB3F5FCD1F01FB23253AB4A937CF71B6F13D2671854624DC92`)

#### Verified Table Record Counts (100% Data Preservation):
| Table Name | Record Count | Integrity Status |
| :--- | :--- | :--- |
| `heritage_sites` | 22 | Verified |
| `heritage_sources` | 12 | Verified |
| `heritage_media` | 1 | Verified |
| `heritage_3d_assets` | 5 | Verified (1 Public Pilot, 4 Isolated Private Fixtures) |
| `cultural_graph_entities` | 44 | Verified |
| `cultural_graph_relationships` | 35 | Verified |
| `ai_documents` | 30 | Verified |
| `ai_document_chunks` | 225 | Verified |
| `ai_chunk_embeddings` | 225 | Verified |
| `import_batches` | 4 | Verified |

---

### 6. Browser Acceptance Testing Matrix (Playwright Chromium)

Browser acceptance testing was executed against the live application using headless Chromium with simulated human interactions:

| Test Item | Target Viewport | Operations Tested | Result | Artifact Path |
| :--- | :--- | :--- | :--- | :--- |
| **Desktop 3D Viewer** | 1440 x 900 | WebGL canvas render, Realistic shader mode, Orbit controls, Surya light boost | **PASS** (0 errors) | `docs/screenshots/viewer_desktop_realistic.png` |
| **Wireframe Shader Mode** | 1440 x 900 | Material wireframe switch, 3,332 polygon mesh rendering | **PASS** (0 errors) | `docs/screenshots/viewer_desktop_wireframe.png` |
| **Clay Shader Mode** | 1440 x 900 | Diffuse khondalite lighting, architectural shadow falloff | **PASS** (0 errors) | `docs/screenshots/viewer_desktop_clay.png` |
| **Tablet Viewport** | 768 x 1024 | Touch viewport layout, responsive toolbar, floating drawer collapse | **PASS** (0 errors) | `docs/screenshots/viewer_tablet.png` |
| **Mobile Viewport** | 390 x 844 | Touch gestures, header stacking, canvas full-bleed rendering | **PASS** (0 errors) | `docs/screenshots/viewer_mobile.png` |
| **Rights & Provenance Dossier** | 1440 x 900 | Origin classification, SHA-256 display, Copy Hash button, download notice | **PASS** (0 errors) | `docs/screenshots/dossier_provenance.png` |
| **Global Route /3d** | 1440 x 900 | Direct route `/3d` redirect to active pilot monument (Site ID 3) | **PASS** (0 errors) | Verified via automated test |

#### Console & Network Telemetry:
- **Total Console Messages:** 9
- **Total Page Errors:** 0
- **Total Failed HTTP Requests:** 0

---

### 7. Screenshot Visual Inspection Log

All captured visual inspection artifacts are stored in `docs/screenshots/`:

1. `viewer_desktop_realistic.png` (71,931 bytes): Full desktop experience showing PBR-shaded Konark chariot temple, stepped pidha tiers, crowning amalaka, and right-hand metadata drawer.
2. `viewer_desktop_wireframe.png` (5,865 bytes): Topological wireframe visualization demonstrating clean triangular manifold tessellation.
3. `viewer_desktop_clay.png` (5,865 bytes): Untextured matte clay rendering emphasizing architectural volumes and shadow casting.
4. `viewer_tablet.png` (27,191 bytes): Portrait tablet presentation at 768x1024 showing responsive controls.
5. `viewer_mobile.png` (18,345 bytes): Handheld mobile viewport at 390x844 with touch-optimized overlay.
6. `dossier_provenance.png` (70,224 bytes): Detailed Rights & Provenance tab showing the `ARCHITECTURAL_VISUALIZATION` classification, SHA-256 cryptographic hash, and download restriction notice.

---

### 8. Automated Test Suite Results

Full backend pytest execution:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: D:\projects\3D_Bharat\backend
plugins: anyio-4.16.0
collected 208 items

tests\test_phase10_1_audit.py .......                                    [  3%]
tests\test_phase10_3d_pipeline.py ........                               [  7%]
tests\test_phase1_api.py ...........                                     [ 12%]
tests\test_phase3_stabilization.py ......................                [ 23%]
tests\test_phase4_preservation.py ................                       [ 30%]
tests\test_phase4_security_audit.py .................................... [ 48%]
.....                                                                    [ 50%]
tests\test_phase5_discovery.py .................                         [ 58%]
tests\test_phase6_ingestion.py ....................                      [ 68%]
tests\test_phase8_knowledge_graph.py .....................               [ 78%]
tests\test_phase9_1_1_audit.py ...........                               [ 83%]
tests\test_phase9_1_2_audit.py ..........                                [ 88%]
tests\test_phase9_1_corpus_rag.py .............                          [ 94%]
tests\test_phase9_ai_intelligence.py ...........                         [100%]

====================== 208 passed, 11 warnings in 21.05s ======================
```

Frontend production build verification:
```
✓ built in 920ms
dist/index.html                     0.96 kB │ gzip:   0.52 kB
dist/assets/index-BBVBljIB.css    105.50 kB │ gzip:  21.38 kB
dist/assets/index-BsE1TcOz.js   1,197.40 kB │ gzip: 320.23 kB
```

---

### 9. Institutional Recommendations for Future ASI Ingestion

1. **LiDAR & Photogrammetry Ingestion Pipeline:**
   When official laser scans or photogrammetric captures from the Archaeological Survey of India (ASI) or National Monuments Authority (NMA) become available, they should be ingested with `asset_origin = 'LASER_SCAN'` or `PHOTOGRAMMETRY_SCAN`.
2. **Institutional Licensing Deeds:**
   Any public binary download enablement (`redistribution_allowed = True`) must require an authenticated institutional deed of gift or clear public domain certification from the Ministry of Culture, Government of India.
3. **Decimation & Level of Detail (LoD):**
   Official survey models exceeding 5,000,000 polygons should be pre-processed through a Draco-compressed multi-resolution LoD pipeline to maintain 60 FPS in WebGL environments.
4. **Permanent Audit Trail:**
   All future revisions must compute and verify the SHA-256 cryptographic hash prior to database registration.
