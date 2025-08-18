# Asset Service

[← Services](./README.md) | [← Contents](../README.md)

Python FastAPI service handling asset ingestion, processing, and storage to MinIO (S3-compatible).

## Responsibilities
- Receive and validate uploads; store to S3 bucket.
- Optionally trigger metadata extraction and publish events.

## Commands (run in repo root or service context)
- Local: `cd src/services/asset_service && uvicorn main:app --reload --port 5001`
- Docker: part of `docker compose up`.

## Configuration
- Requires S3 credentials and bucket (MinIO). Compose includes `s3-server` and `mc` initializer.
- RabbitMQ and MongoDB URLs are injected via `docker-compose.yml`.

## Notes
- Utilities under `utils/` include S3 uploader, file handling, and analyzers.

Prev: Profile Service (./profile_service.md) | Next: Search Service (./search_service.md)
