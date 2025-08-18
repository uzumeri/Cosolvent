# Industry Context Service

[← Services](./README.md) | [← Contents](../README.md)

TypeScript service with HTTP server (Hono) and background workers to ingest, transform, and enrich domain content.

## Responsibilities
- Ingest files/text, extract features and embeddings, and build industry context.
- Schedule background jobs (BullMQ) and persist artifacts in MongoDB/MinIO.

## Tech Stack
- Hono, BullMQ (Redis), TypeScript, TSUP/TSX, Biome.

## Commands (run in `src/services/industry_context_service`)
- `pnpm install`
- `pnpm dev` — concurrently runs server and worker.
- `pnpm dev:server` / `pnpm dev:worker` — focused dev.
- `pnpm build && pnpm start` and `pnpm start:worker` — production run.

## Configuration
- Uses root `.env` and service `.env.example`. Requires Redis, MongoDB, and optional S3/LLM keys.
- Compose mounts `shared-temp` for transient files.

## Notes
- See `src/workers/` for job definitions and `src/app.ts` / `src/server.ts` for routes.

Prev: Auth Service (./auth_service.md) | Next: LLM Orchestration Service (./llm_orchestration_service.md)
