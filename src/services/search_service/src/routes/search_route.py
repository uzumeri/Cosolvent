from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from pydantic import ValidationError
from src.schema.search_schema import SearchResponse, QueryRequest, ProducerSimilarity, IndexRequest
from src.services.embedding_service import embedding_service
from src.services.index_service import index_producer
from src.services.vector_service import vector_service
router = APIRouter()

@router.post("/index", response_model=dict)
async def index_producer_data(request: IndexRequest):
    """
    Index a producer's AI profile and metadata into pgvector.
    Expects JSON body with profile_id and ai_profile.
    """
    try:
        result = await index_producer(request.profile_id, request.ai_profile, 
                                      request.region, request.certifications, request.primary_crops)
        return {"success": result.success, "message": result.message}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while indexing: {str(e)}"
        )
@router.post("/search-producers", response_model=SearchResponse)
async def search_producers(request: QueryRequest):
    """
    Performs a semantic search against the indexed producer data.
    Returns a list of producer_ids ordered by similarity (most similar on top).
    Allows for optional metadata filtering (region, certifications, primary crops).
    """
    try:
        # Vectorize the query using the centralized orchestration embeddings
        query_vector = embedding_service.get_embedding(request.query)

        # Prepare metadata filters
        filters = {}
        if request.filter_region:
            filters["region"] = request.filter_region
        if request.filter_certification:
            filters["certifications"] = {"$in": [request.filter_certification]}
        if request.filter_primary_crop:
            filters["primary_crops"] = {"$in": [request.filter_primary_crop]}

        rows = await vector_service.query(query_vector, request.top_k, filters if filters else None)

        results: List[ProducerSimilarity] = [
            ProducerSimilarity(id=row["id"], score=row["score"]) for row in rows
        ]

        return SearchResponse(
            success=True,
            message="Search completed successfully.",
            results=results
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search query parameters: {e.errors()}"
        )
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during search: {str(e)}"
        )
@router.delete("/search/clear-index")
async def clear_index():
    try:
        deleted = await vector_service.delete_all()
        return {"success": True, "message": f"Index cleared. Deleted {deleted} rows."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {e}")