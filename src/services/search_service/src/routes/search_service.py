from fastapi import APIRouter
from src.schemas.search_service_schema import SearchRequest, SearchResponse
from src.core.search import search_assets

router = APIRouter()

@router.get("/health", tags=["Search"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=SearchResponse, tags=["Search"])
async def search_endpoint(request: SearchRequest):
    """Perform a semantic vector search."""
    return search_assets(request)
