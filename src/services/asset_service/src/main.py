from fastapi import FastAPI
from src.routes.asset_service import router as asset_router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from src.utils.asset_consumer import consume_messages

app = FastAPI(title="Asset Service", description="Comprehensive asset management including metadata extraction and translation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(asset_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "asset_service"}

@app.on_event("startup")
async def startup_event():
    """Start the asset consumer on startup"""
    asyncio.create_task(consume_messages())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
