#!/usr/bin/env bash

# Wait for RabbitMQ (optional)
# exec any pre-start scripts here

# Start FastAPI via uvicorn
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1