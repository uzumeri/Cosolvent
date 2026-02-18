from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import config, prompts, market, mcp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Admin Service", root_path="/admin")

# CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
	logger.info("Admin service startup.")


@app.get("/healthz")
async def healthz():
	return {"status": "ok"}


@app.get("/health")
async def health():
	return {"status": "ok"}


app.include_router(config.router, prefix="/api/v1", tags=["Configuration"])
app.include_router(prompts.router, prefix="/api/v1", tags=["Prompts"])
app.include_router(market.router, prefix="/api/v1", tags=["Market"])
app.include_router(mcp.router, prefix="/api/v1", tags=["MCP"])

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8003)
