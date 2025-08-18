# Profile Service

Python FastAPI service for participant profiles and templates.

## Responsibilities
- Manage profile entities and profile templates used for matching.
- Exposes routes under `/profile/api/*` (FastAPI `root_path` is `/profile`).

## Commands (run in repo root or service context)
- Local: `cd src/services/profile_service && uvicorn main:app --reload --port 5000`
- Docker: part of `docker compose up`.

## Configuration
- Uses root `.env`; see `src/services/profile_service/.env.example` when present.

## Notes
- Middleware allows CORS for local development.
- Extend Pydantic models to include domain-specific fields and maintain schema consistency with other services.
