from fastapi import FastAPI
from src.routes.profile_management_service import router as profile_management_router
from fastapi.middleware.cors import CORSMiddleware  


app = FastAPI(title="Profile Management Service",)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(profile_management_router, prefix="/profiles", tags=["Profiles"])
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
