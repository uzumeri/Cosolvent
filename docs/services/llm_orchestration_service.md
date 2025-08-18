# LLM Orchestration Service

Python FastAPI service offering LLM-adjacent utilities (e.g., metadata extraction) with configuration persisted in MongoDB.

## Responsibilities
- File and image metadata extraction with LLM assistance.
- Centralize LLM providers/settings; seed default config if missing.

## Key Endpoints
- `GET /health` — service health.
- `POST /llm/metadata` — extract textual metadata from uploaded file (see tests for usage).

## Commands (run in `src/services/llm_orchestration_service`)
- Local: `uvicorn src.main:app --reload --port 8000`
- Docker: brought up via `docker compose up`.

## Configuration
- Config file `config.json` plus MongoDB-backed store; env vars set in `docker-compose.yml` (mongodb_uri/db/collection).

## Tests
- Pytest examples in `tests/` show how to stub LLM calls and validate endpoints.
