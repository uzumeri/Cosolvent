# Architecture Overview

[← Contents](./README.md)

Cosolvent is a polyglot microservice system orchestrated via Docker Compose. It ships batteries-included infrastructure to enable local development and deployment.

## Components
- Frontend (Next.js): User-facing UI for onboarding, exploration, and match workflows.
- Auth Service (TS/Hono): Authentication/session primitives backed by MongoDB.
- Industry Context Service (TS/Hono + workers): Ingests domain content, enriches via LLM/embeddings, queues jobs with Redis/BullMQ.
- LLM Orchestration Service (Python/FastAPI): Utilities for LLM tasks (e.g., metadata extraction), configuration persisted in MongoDB.
- Profile Service (Python/FastAPI): Profile CRUD and template endpoints.
- Asset Service (Python/FastAPI): Asset ingestion, storage to MinIO (S3-compatible), and metadata enrichment.
- Search Service (Python/FastAPI): Query and matching over profiles/assets.
- Reverse Proxy (Nginx): Path-based routing to services.

## Infrastructure
- MongoDB: system of record for users, profiles, assets, and configuration.
- Redis: job queue backing (BullMQ) and caching.
- RabbitMQ: event and task distribution where required.
- MinIO: S3-compatible object storage for asset files.

See `docker-compose.yml` for ports, dependencies, and health checks. For diagrams and design PDFs, see Assets & Diagrams (./assets.md).

## Data & Models
- Python services: Pydantic models for DTOs and validation.
- TypeScript services: Zod schemas for validation and runtime type-safety.

Keep schema names consistent across services to enable reliable, composable matching.

[Prev: Use Cases](./use-cases.md) | [Next: Data Models](./models.md)
