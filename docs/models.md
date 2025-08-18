# Data Models

[← Contents](./README.md)

Cosolvent standardizes market entities using Pydantic (Python) and Zod (TypeScript). These models are intended to be adopted as-is or extended with domain-specific fields.

## Canonical Models
- Profile: participant identity, capabilities, constraints, and preferences.
- Asset: item listing metadata (type, descriptors, attachments, ownership).
- MatchRequest: query intent, filters, and context.
- MatchResult: ranked candidates with scores and rationales.
- IndustryContext: domain signals, embeddings, and references.
- User: auth/account profile (minimal fields for portability).

## Conventions
- Python: define in `models/` or alongside routes as Pydantic `BaseModel` classes.
- TypeScript: define in `schemas/` as Zod schemas and derive types via `z.infer`.
- Keep field names consistent across services; prefer snake_case in Python, camelCase in TS, with stable JSON keys.

## Tips
- Version your models as they evolve (e.g., `v1` namespaces) to avoid breaking consumers.
- Provide example payloads in service docs and tests; add validators for required business invariants.

Prev: Architecture (./architecture.md) | Next: Services Overview (./services/README.md)
