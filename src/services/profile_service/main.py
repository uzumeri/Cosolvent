import logging
from fastapi import FastAPI

from src.routes.profile_route import router as profile_routes
from src.routes.template_route import router as template_routes
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cosolvent", root_path="/profile")

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_routes, prefix="/api")
app.include_router(template_routes, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup.")
