# Repository Guidelines

## Project Structure & Module Organization
- Root: `docker-compose.yml`, `.env`, `docs/`.
- Frontend (Next.js): `frontend/` with `app/`, `components/`, `public/`.
- Services: `src/services/` contains microservices:
  - Python (FastAPI): `profile_service/`, `asset_service/`, `search_service/`, `llm_orchestration_service/`.
  - TypeScript (Hono/Workers): `auth_service/`, `industry_context_service/`.
- Reverse proxy: `src/services/reverse_proxy/` (Nginx).
- Shared utilities: `src/shared/`.

## Build, Test, and Development Commands
- Full stack (Docker): `docker compose up --build` — builds and starts all services.
- Frontend (from `frontend/`):
  - `pnpm dev` — run Next.js locally on `:3000`.
  - `pnpm build && pnpm start` — production build and serve.
- TypeScript services (from service dir):
  - `pnpm dev` — watch mode; `pnpm build && pnpm start` to run compiled output.
- Python services (from service dir):
  - Example: `uvicorn main:app --reload --port 5000` (profile), `--port 5002` (search).
- Tests (Python): `pytest src/services/llm_orchestration_service/tests -q`.

## Coding Style & Naming Conventions
- TypeScript: use Biome. Commands: `pnpm lint`, `pnpm lint:fix`, `pnpm format` (see `frontend/`, TS services).
- Python: follow PEP 8, 4-space indent, snake_case modules/functions, PascalCase classes.
- Filenames: kebab-case for config and scripts; snake_case for Python modules; camelCase for TS variables.
- Keep functions small; prefer explicit types in TS.

## Testing Guidelines
- Python: pytest under each service’s `tests/`. Name tests `test_*.py` and functions `test_*`.
- Fast endpoints: prefer TestClient (see `llm_orchestration_service/tests`).
- Aim for smoke tests per endpoint; add unit tests for utils.

## Commit & Pull Request Guidelines
- Commits: short, imperative subject. Observed prefixes include `UPDATE:`, `FIX:`, `CHORE:`, `DOCS:` (e.g., `UPDATE: asset service updated`).
- Group related changes; avoid WIP commits.
- PRs: clear description, linked issues, steps to test, and screenshots when UI changes.
- Include environment notes if new env vars or ports are introduced.

## Security & Configuration Tips
- Copy `.env.example` files and set required secrets locally; do not commit real secrets.
- Services expect MongoDB/Redis/RabbitMQ/S3 via `docker-compose`. Use the compose stack for parity.
