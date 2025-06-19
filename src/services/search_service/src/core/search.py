import openai
from cachetools import TTLCache
from datetime import datetime

from core.config import settings
from database.crud.search_service_crud import query_vectors
from schemas.search_service_schema import SearchRequest, SearchResponse, SearchResult

openai.api_key = settings.OPENAI_API_KEY

# In-memory cache for recent queries
ttl_cache = TTLCache(maxsize=1024, ttl=settings.CACHE_TTL)


def refine_query(query: str) -> str:
    """Use OpenAI to refine or expand a search query."""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a semantic search assistant."},
            {"role": "user", "content": f"Refine this search query for vector search: '{query}'"}
        ],
        temperature=0.0
    )
    return resp.choices[0].message.content


def embed_text(text: str) -> list[float]:
    """Generate embedding for text using OpenAI."""
    resp = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return resp.data[0].embedding


def search_assets(req: SearchRequest) -> SearchResponse:
    """Perform a semantic search with optional filters and caching."""
    key = f"{req.query}|{req.user_id}|{req.date_from}|{req.date_to}|{req.top_k}"
    if key in ttl_cache:
        return ttl_cache[key]

    # Agentic query refinement
    refined = refine_query(req.query)
    vector = embed_text(refined)

    # Build Pinecone filters
    filters = {}
    if req.user_id:
        filters["user_id"] = {"$eq": req.user_id}
    if req.date_from or req.date_to:
        date_filter = {}
        if req.date_from:
            date_filter["$gte"] = req.date_from.isoformat()
        if req.date_to:
            date_filter["$lte"] = req.date_to.isoformat()
        filters["created_at"] = date_filter

    # Query Pinecone
    matches = query_vectors(vector, filters if filters else None, req.top_k)
    results = [
        SearchResult(asset_id=m["id"], score=m["score"], metadata=m.get("metadata", {}))
        for m in matches
    ]

    response = SearchResponse(results=results)
    ttl_cache[key] = response
    return response
