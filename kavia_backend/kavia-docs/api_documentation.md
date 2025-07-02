# KAVIA Meet Backend API Documentation

This document details the REST API implemented using FastAPI for the KAVIA Meet Backend. All listed routes, parameters, bodies, and responses reflect the actual backend codebase as of this release.

**Base URL:** `/` (relative to deployed backend, e.g. `https://<host>/`)

## API Metadata

- **Title:** KAVIA Meet Backend API
- **Version:** 0.1.0
- **Description:** API for video meetings, multilingual translation, AI summaries, collaboration, authentication, and export/replay functionality.

## Tags
- **health:** Health and readiness probes
- **user:** User management and authentication _(placeholders for routes, to be implemented)_
- **meeting:** Meeting scheduling, joining, history _(placeholders for routes, to be implemented)_
- **translation:** Live and AI-powered translation _(placeholders for routes, to be implemented)_
- **chat:** Real-time chat, subtitles, and communication _(placeholders for routes, to be implemented)_

---

## Implemented Endpoints

### Health Check Endpoints

#### 1. Root Health Check

- **Route:** `GET /`
- **Tags:** `health`
- **Summary:** Backend health check
- **Description:** Basic backend health check; returns a simple online message.
  
**Response Example:**
```json
{
  "status": "ok",
  "message": "KAVIA Meet backend is alive"
}
```

---

#### 2. Database Health Check

- **Route:** `GET /health/db`
- **Tags:** `health`
- **Summary:** Check SQLite DB health
- **Description:** Executes a minimal SQL query (`SELECT 1`) to verify database connectivity.

**Response Example (Healthy):**
```json
{
  "status": "ok",
  "message": "Database connection is healthy"
}
```
**Response Example (Unhealthy):**
```json
{
  "status": "error",
  "message": "Database is unreachable"
}
```

---

## Schemas / Models

### User Models

- **UserBase**
  - `username`: str (required) — Unique username
  - `display_name`: Optional[str] — Display name
  - `language`: Optional[str] (default: "en") — Preferred language code
  - `is_active`: bool (default: true) — Active user?

- **UserCreate (inherits UserBase)**
  - `password`: str (required) — User password

- **User (inherits UserBase)**
  - `id`: int
  - `email`: EmailStr

### Meeting Models

- **MeetingBase**
  - `topic`: str
  - `start_time`: datetime
  - `end_time`: Optional[datetime]
  - `host_id`: int

- **MeetingCreate (inherits MeetingBase)**
  - _no extensions_

- **Meeting (inherits MeetingBase)**
  - `id`: int
  - `code`: str

### Message Models

- **MessageBase**
  - `meeting_id`: int
  - `sender_id`: int
  - `content`: str
  - `timestamp`: datetime
  - `language`: Optional[str] (default: "en")

- **Message (inherits MessageBase)**
  - `id`: int

### Translation Models

- **TranslationRequest**
  - `text`: str
  - `source_lang`: str
  - `target_lang`: str

- **TranslationResponse**
  - `translated_text`: str

---

## Unimplemented (Scaffolded) Features

The following functionalities are referenced in documentation tags, models, or code comments but do **not** have any implemented endpoints in `main.py` as of this version:
- User sign-up, authentication, or management endpoints (e.g., `/users/`, `/users/auth/`)
- Meeting scheduling/joining endpoints (e.g., `/meetings/`)
- Chat or message-posting endpoints (e.g., `/messages/`)
- Translation endpoints (e.g., `/translate/`)
- WebSocket endpoints for conferencing, subtitles, or collaboration

These routes will be added as submodules and routers in the future.

---

## Example: Expanding API Usage

To add or use more routes, implement additional FastAPI routers and endpoints referencing the included `User`, `Meeting`, `Message`, and `Translation` models.

---

## API Structure Diagram (Mermaid)

```mermaid
graph TD
    subgraph KAVIA Meet API
        A[GET /] -- Health Probe --> B{{"status":"ok"}}
        C[GET /health/db] -- DB Health --> D{{"status":"ok"/"status":"error"}}
    end
    subgraph Models
        E[UserBase / UserCreate / User]
        F[MeetingBase / MeetingCreate / Meeting]
        G[MessageBase / Message]
        H[TranslationRequest / TranslationResponse]
    end
    %% No other endpoint links implemented yet
```

---

## Notes

- OpenAPI/Swagger docs are available at `/docs` when running the backend.
- The backend currently only exposes health check endpoints.
- For future expansion, see comments in the backend code regarding routers and new modules.

---

## References

- **Backend Code File:** `kavia_backend/src/api/main.py`
- **Requirements:** See `kavia_backend/requirements.txt` for dependencies.

