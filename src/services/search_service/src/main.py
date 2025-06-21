import logging
from fastapi import FastAPI
from src.routes.search_service import router as search_router
from src.core.vector_store import index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Service")

# Include search router
app.include_router(search_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Search service starting up")
    try:
        stats = index.describe_index_stats()
        print("Stats:", stats)

        logger.info(f"Pinecone index reachable, stats: {stats}")
    except Exception as e:
        logger.error(f"Pinecone connectivity check failed: {e}")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}