# Cosolvent — Thin-Market Matching Engine (v0.1 Beta)

Cosolvent is an MIT-licensed, modular matching engine designed to help “thin” markets become “thicker.” Instead of teams reinventing market-matching primitives, Cosolvent exposes reusable services and Pydantic/Zod models you can adopt directly or extend. The system targets marketplaces where participants and listings are scarce, specialized, or distributed, enabling discovery, profiling, and high-signal matching.

## Why Cosolvent
- Thicken thin markets: bootstrap liquidity by standardizing profiles, assets, and context signals.
- Reusable primitives: adopt our schemas, queues, and services without building from scratch.
- Polyglot microservices: Python (FastAPI) and TypeScript (Hono) for flexibility and speed.

## Architecture Overview
- Frontend: Next.js app in `frontend/`.
- Services in `src/services/`:
  - `auth_service` (TS/Hono): authentication and session primitives.
  - `industry_context_service` (TS/Hono + workers): context ingestion, vectorization, jobs (Redis/BullMQ).
  - `llm_orchestration_service` (Python/FastAPI): LLM utilities (e.g., metadata extraction) with config in Postgres.
  - `profile_service` (Python/FastAPI): profile and template endpoints.
  - `asset_service` (Python/FastAPI): asset ingestion and S3 (MinIO) integration.
  - `search_service` (Python/FastAPI): search/match queries over stored profiles/assets.
  - `reverse_proxy` (Nginx): unified routing across services.
- Infra via `docker-compose.yml`: Postgres (with pgvector), Redis, RabbitMQ, MinIO (S3-compatible).

See docs for diagrams and details: docs/architecture.md and docs/services/.

## Quickstart
Prereqs: Docker & Docker Compose. For local-only service dev, Node 20+ (TS), Python 3.11+ (FastAPI), pnpm.

1) Configure environment
- Copy root `.env.example` to `.env` and fill values.
- Copy per-service `.env.example` files where present.

2) Run the full stack
```bash
docker compose up --build
```
Frontend on `http://localhost:3000`. Services as defined in `docker-compose.yml` (e.g., profiles on `:5000`, search on `:5002`).

3) Develop a single service
- Frontend: `cd frontend && pnpm install && pnpm dev`
- TS service (e.g., auth): `pnpm dev` (or `pnpm build && pnpm start`)
- Python service (e.g., profile): `uvicorn main:app --reload --port 5000`

## Data Models
- Python DTOs: Pydantic models per service (profiles, assets, match requests/results, configs).
- TypeScript DTOs: Zod schemas for validation and shared typing.
Adopt these as-is or extend; keep names consistent across services to enable cross-service matching.

## Contributing
Follow coding conventions and PR guidance in AGENTS.md. TS code uses Biome (`pnpm lint`, `pnpm format`); Python follows PEP 8. Include tests for new endpoints where feasible (pytest or Hono testing utilities).

## Roadmap
- v0.1 Beta: core profiling, asset ingestion, LLM metadata, basic search, auth primitives.
- Upcoming: richer scoring functions, active-learning feedback loops, marketplace UX templates, and multi-tenant packaging.

## License
MIT — see LICENSE.

## Further Reading
- Architecture: docs/architecture.md
- Microservices: docs/services/
- Use cases: docs/use-cases.md
