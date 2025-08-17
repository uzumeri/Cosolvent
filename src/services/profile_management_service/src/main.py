from fastapi import FastAPI
from src.routes.profile_management_service import router as profile_management_router
from fastapi.middleware.cors import CORSMiddleware  
import asyncio
from src.utils.profile_consumer import consume_messages

app = FastAPI(title="Profile Management Service", description="Comprehensive profile management including user management and profile generation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_management_router, prefix="/profiles", tags=["Profiles"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "profile_management_service"}

@app.on_event("startup")
async def startup_event():
    """Start the profile consumer on startup"""
    asyncio.create_task(consume_messages())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
