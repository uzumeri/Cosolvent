from fastapi import  HTTPException, status, Depends
from pydantic import ValidationError
from src.database.db import get_mongo_service
from src.database.models.search_model import IndexResponse
from src.services.pinecone_service import pinecone_service
from src.services.openai_service import openai_service
import logging


logger = logging.getLogger(__name__)


async def index_producer(producer_id: str, db=Depends(get_mongo_service)):
    """
    Indexes a producer's information and their AI-generated profile into Pinecone.
    Calls external functions to get producer and AI profile data.
    """
    try:
        # 1. Get producer by ID
        from database.crud.profile_crud import get_profile
        producer_data = await get_profile(db, producer_id)

        logger.info(f"Producer Data: {producer_data}")
        if not producer_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producer with ID '{producer_id}' not found via external function call."
            )

        # 2. Get AI profile by user_id - Calling the provided function
        ai_profile_data = producer_data.ai_profile

        logger.info(f"AI Profile Data: {ai_profile_data}")
        if not ai_profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI profile for producer ID '{producer_id}' not found via external function call."
            )

        # Combine relevant text for vectorization
        text_to_embed = (
            
            f"AI Profile: {ai_profile_data}"
        )

        embedding_vector = openai_service.get_embedding(text_to_embed)

        metadata = {
            "region": producer_data.region,
            "certifications": producer_data.certifications,
            "primary_crops": producer_data.primary_crops,
            "producer_id": producer_id, # Storing producer_id as metadata for filtering

        }

        # Prepare vector for upsert
        vector_to_upsert = {
            "id": str(producer_id), # Convert ObjectId to str for Pinecone
            "values": embedding_vector,
            "metadata": metadata
        }

        # Store in Pinecone
        pinecone_service.upsert_vectors(vectors=[vector_to_upsert])

        return IndexResponse(
            success=True,
            message=f"Producer '{producer_id}' successfully indexed.",
            indexed_id=producer_id
        )

    except HTTPException as e:
        raise e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data validation error during indexing: {e.errors()}"
        )
    except Exception as e:
        print(f"Error during indexing for producer ID '{producer_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during indexing for producer '{producer_id}': {str(e)}"
        )
