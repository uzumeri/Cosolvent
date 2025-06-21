#!/usr/bin/env bash

# Wait for dependencies if needed (e.g., RabbitMQ). Optionally add checks here.

# Start consumer in background using module path for correct imports
echo "Starting profile consumer..."
python -u -m src.utils.profile_consumer &

# Start FastAPI app
echo "Starting FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port 8009
