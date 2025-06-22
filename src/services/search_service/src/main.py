import os
import logging
import aio_pika
from fastapi import FastAPI

from core.config import settings
from core.rabbitmq import connect, consume_asset_ready
import core.rabbitmq as _rmq
from core.pinecone import init_pinecone
from routes.search_service import router as search_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate FastAPI app
app = FastAPI(
    title="Search Service",
    description="Consumes AssetReadyForIndexing events and prepares for search indexing.",
    version="0.1.0"
)

# Health-check endpoint
@app.get("/health", tags=["Root"])
async def health():
    return {"status": "ok"}

# Startup: connect to RabbitMQ and start consumer
@app.on_event("startup")
async def startup_event():
    logger.info("Connecting to RabbitMQ...")
    await connect()
    # Initialize Pinecone client and index
    logger.info("Initializing Pinecone...")
    init_pinecone()
    logger.info("Pinecone initialized")
    logger.info("Starting AssetReadyForIndexing consumer...")
    await consume_asset_ready()

# Shutdown: close RabbitMQ connection
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing RabbitMQ connection...")
    await _rmq.connection.close()

# Include search router under /api/search
app.include_router(search_router, prefix="/api/search")
