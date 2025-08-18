# Auth Service

[← Services](./README.md) | [← Contents](../README.md)

TypeScript service built with Hono to provide authentication and session primitives.

## Responsibilities
- Issue and validate sessions, manage user accounts.
- Provide typed DTOs (Zod) for auth flows.

## Tech Stack
- Hono, Node 20+, TypeScript, Biome for lint/format, MongoDB.

## Commands (run in `src/services/auth_service`)
- `pnpm install`
- `pnpm dev` — run in watch mode.
- `pnpm build && pnpm start` — compile and run production output.
- `pnpm lint` / `pnpm format` — code quality.

## Configuration
- Environment comes from root `.env` and service `.env`. Typical keys: Mongo connection, JWT/session secrets.

## Notes
- Exposes auth endpoints for the frontend and other services. Review `src/app.ts` and `src/server.ts` for route mounting and middleware.

[Prev: Services Overview](./README.md) | [Next: Industry Context Service](./industry_context_service.md)
