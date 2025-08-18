# Search Service

Python FastAPI service providing search and matching over profiles and assets.

## Responsibilities
- Index and query entities; surface candidate matches.
- Integrate with metadata and profile services to improve rankings.

## Commands (run in repo root or service context)
- Local: `cd src/services/search_service && uvicorn main:app --reload --port 5002`
- Docker: part of `docker compose up`.

## Configuration
- Env via root `.env` and service `.env.example`.
- May use RabbitMQ for async tasks and caching as appropriate.

## Notes
- Utilities under `utils/` include Uploader and analyzers. Add endpoint smoke tests as you introduce routes.
