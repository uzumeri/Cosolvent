# app/api/routes.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import ValidationError
from src.schema.query_schema import  SearchResponse, QueryRequest, ProducerSimilarity
from src.services.pinecone_service import pinecone_service
from src.services.openai_service import openai_service

router = APIRouter()


@router.post("/search-producers", response_model=SearchResponse)
async def search_producers(request: QueryRequest):
    """
    Performs a semantic search against the indexed producer data.
    Returns a list of producer_ids ordered by similarity (most similar on top).
    Allows for optional metadata filtering (region, certifications, primary crops).
    """
    try:
        # Vectorize the query using OpenAI
        query_vector = openai_service.get_embedding(request.query)

        # Prepare metadata filters
        filters = {}
        if request.filter_region:
            filters["region"] = request.filter_region
        if request.filter_certification:
            filters["certifications"] = {"$in": [request.filter_certification]}
        if request.filter_primary_crop:
            filters["primary_crops"] = {"$in": [request.filter_primary_crop]}

        # Perform the query against Pinecone
        pinecone_matches = pinecone_service.query_vectors(
            vector=query_vector,
            top_k=request.top_k,
            filters=filters if filters else None
        )

        results: List[ProducerSimilarity] = []
        for match in pinecone_matches:
            # Pinecone results are already ordered by score (highest first) by default
            # Extract only the producer_id (which is the vector 'id') and score
            if match.id and match.score is not None:
                results.append(
                    ProducerSimilarity(
                        id=match.id, # Map Pinecone's vector ID to id
                        score=match.score
                    )
                )

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
async def clear_pinecone_index():
    """
    Deletes all vectors from the Pinecone index.
    """
    try:
        deleted = pinecone_service.delete_all_vectors()
        if deleted:
            return {"success": True, "message": "Pinecone index cleared successfully."}
        # If delete_all_vectors returns False, raise an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear Pinecone index"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear Pinecone index: {e}"
        )