import logging
from fastapi import FastAPI

from src.routes.asset_route import router as asset_routes
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="COSOLVENT", root_path="/asset")

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(asset_routes, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup.")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
