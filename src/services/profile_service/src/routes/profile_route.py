from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query, Body
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
import json
import logging
from src.database.crud.profile_crud import (
    create_profile,
    update_profile as update_profile_crud,
    get_profile,
    get_profile_by_email,
    get_all_producers,
    delete_profile as delete_profile_crud,
    generate_ai_profile as generate_ai_profile_crud,
    approve_ai_draft as approve_ai_draft_crud,
    reject_ai_draft as reject_ai_draft_crud,
    add_file_in_producer_profile,
    update_file_in_producer_profile as update_file,
    remove_file_from_producer_profile as remove_file
    
)
from src.schema.profile_schema import (
    ProducerRegisterSchema, ProfileUpdateResponse, 
    ProducerSchema, SuccessResponse, 
    ProfileUpdateSchema,
)
from src.schema.producer_file_schema import ProducerFileSchema
from src.database.db import get_mongo_service
from src.core.config import settings
import httpx  # type: ignore
from bson.objectid import ObjectId  # type: ignore

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201, response_model=ProducerSchema)
async def register_producer(
    payload: ProducerRegisterSchema = Depends(ProducerRegisterSchema.as_form),
    files: List[UploadFile] = File(...),
    files_metadata: str = Form(...),
    db=Depends(get_mongo_service)
):
    """
    Submits a new producer application.
    """
    try:
        files_metadata_list = json.loads(files_metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in files_metadata.")

    logger.info(f"Registration attempt for email: {payload.email}")
    if await get_profile_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="A profile with this email already exists.")

    logger.info(f"Creating new application for email: {payload.email}")
    profile_data = payload.dict(exclude_unset=True)
    
    # Convert field names to match DB schema
    profile_data["farm_name"] = profile_data.pop("farmName")
    profile_data["contact_name"] = profile_data.pop("contactName")
    profile_data["farm_size"] = profile_data.pop("farmSize")
    profile_data["annual_production"] = profile_data.pop("annualProduction")
    profile_data["farm_description"] = profile_data.pop("farmDescription")
    profile_data["export_experience"] = profile_data.pop("exportExperience")
    profile_data["primary_crops"] = profile_data.pop("primaryCrops")

    created_profile, profile_id = await create_profile(db, profile_data)

    
    if len(files) != len(files_metadata_list):
        raise HTTPException(status_code=400, detail="The number of files must match the number of metadata entries.")

    metadata_map = {meta.get('filename'): meta for meta in files_metadata_list if meta.get('filename')}
        
    # Call asset service to register files and retrieve full ProducerFileSchema objects
    asset_url = f"{settings.ASSET_SERVICE_URL}/api/{profile_id}/files"

    # Prepare multipart files payload
    files_payload = []
    for file in files:
        file.file.seek(0)
        files_payload.append(("files", (file.filename, await file.read(), file.content_type)))


    # Call asset service endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(asset_url, files=files_payload, data={"files_metadata": files_metadata})
    if response.status_code != 201:
        raise HTTPException(status_code=502, detail="Failed to register files with asset service.")
    
    # Parse returned file objects and convert to dicts for MongoDB storage
    files_data = response.json()
    parsed = []
    for item in files_data:
        pf = ProducerFileSchema(**item)
        d = pf.dict(by_alias=True)
        d["_id"] = str(d.get("_id"))
        d["profile_id"] = profile_id
        parsed.append(d)

    # Update producer record with embedded files
    await db.producers.update_one(
        {"_id": ObjectId(profile_id)},
        {"$set": {"files": parsed}}
    )

    application = await get_profile(db, profile_id)
    if not application:
        raise HTTPException(status_code=500, detail="Failed to create and retrieve application.")

    return jsonable_encoder(application)


@router.put("/{profile_id}", response_model=ProfileUpdateResponse)
async def update_producer_profile(
    profile_id: str,
    payload: ProfileUpdateSchema = Body(...),
    db=Depends(get_mongo_service),
):
    """
    Updates an existing producer profile (both applications and approved producers).
    """
    update_data = payload.dict(exclude_unset=True)

    db_update_data = {}
    field_map = {
        "farmName": "farm_name",
        "contactName": "contact_name",
        "farmSize": "farm_size",
        "annualProduction": "annual_production",
        "farmDescription": "farm_description",
        "exportExperience": "export_experience",
        "primaryCrops": "primary_crops"
    }
    for key, value in update_data.items():
        db_key = field_map.get(key, key)
        db_update_data[db_key] = value

    updated_profile = await update_profile_crud(db, profile_id, db_update_data)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    

    return {"success": True, "message": "Profile updated successfully", "profileId": profile_id}


@router.get("/producer", response_model=ProducerSchema)
async def read_producer_profile_by_email(
    email: str = Query(..., description="Email of the producer to retrieve"),
    db=Depends(get_mongo_service)
):
    """
    Retrieves public-facing information for a specific producer by email.
    """
    profile = await get_profile_by_email(db, email)
    if not profile:
        raise HTTPException(status_code=404, detail="Producer not found.")
    return jsonable_encoder(profile)


@router.delete("/{producer_id}", response_model=SuccessResponse)
async def delete_producer_profile(producer_id: str, db=Depends(get_mongo_service)):
    """
    Performs a 'soft delete' by setting the profile status to suspended.
    """
    if not await delete_profile_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"success": True, "message": "Profile has been suspended."}

    

@router.get("/producers", response_model=List[ProducerSchema])
async def list_producers(
    status: Optional[str] = Query(None, enum=["active", "suspended"]),
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_mongo_service)
):
    """
    Lists approved producers with optional status filtering and pagination.
    """
    producers = await get_all_producers(db, status, skip, limit)
    return jsonable_encoder(producers)

@router.get("/producers/{producer_id}", response_model=ProducerSchema)
async def read_producer_profile(producer_id: str, db=Depends(get_mongo_service)):
    """
    Retrieves a producer's profile by their ID.
    """
    producer = await get_profile(db, producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Producer not found.")
    return jsonable_encoder(producer)




@router.post("/profiles/{producer_id}/generate-ai-profile", response_model=SuccessResponse)
async def generate_ai_profile(producer_id: str, db=Depends(get_mongo_service)):
    """
    Generates an AI-powered profile description and saves it as a draft.
    """
    producer = await get_profile(db, producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Producer not found.")

    result = await generate_ai_profile_crud(db, producer_id, producer.dict())

    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate AI profile draft.")

    return {"success": True, "message": "AI profile draft generated successfully."}


@router.post("/profiles/{producer_id}/approve-ai-draft", response_model=SuccessResponse)
async def approve_ai_draft(producer_id: str, db=Depends(get_mongo_service)):
    """
    Approves the AI-generated profile draft, making it the official AI profile.
    """
    if not await approve_ai_draft_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="AI draft not found or could not be approved.")

    # Trigger search service to index this approved producer with AI profile text
    # Fetch updated producer including ai_profile
    producer = await get_profile(db, producer_id)
    search_url = f"{settings.SEARCH_SERVICE_URL}/search/api/index"
    payload = {"profile_id": producer_id, "ai_profile": producer.ai_profile, "region": producer.region, "certifications": producer.certifications, "primary_crops": producer.primary_crops}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(search_url, json=payload)
        if resp.status_code != 200:
            logger.error(f"Failed to index producer {producer_id} in search service: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"Error calling search service index endpoint: {e}")
    return {"success": True, "message": "AI draft approved."}

async def reject_ai_draft(producer_id: str, db=Depends(get_mongo_service)):
    """
    Rejects and deletes the current AI profile draft.
    """
    if not await reject_ai_draft_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="AI draft not found or could not be rejected.")
    return {"success": True, "message": "AI draft rejected."}


@router.post("/profiles/{producer_id}/files", response_model=ProducerSchema)
async def add_file_to_producer_profile(
    producer_id: str,
    file: ProducerFileSchema = Body(...),
    db=Depends(get_mongo_service)
):
    """
    Adds a file to the producer's profile.
    """
    updated_profile = await add_file_in_producer_profile(db, producer_id, file)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return jsonable_encoder(updated_profile)
@router.put("/profiles/{producer_id}/files", response_model=ProducerSchema)
async def update_file_in_producer_profile(
    producer_id: str,
    file: ProducerFileSchema = Body(...),
    db=Depends(get_mongo_service)
):
    """
    Updates a file in the producer's profile.
    """
    updated_profile = await update_file(db, producer_id, file)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile or file not found.")
    return jsonable_encoder(updated_profile)
@router.delete("/profiles/{producer_id}/files/{file_id}", response_model=SuccessResponse)
async def remove_file_from_producer_profile(
    producer_id: str,
    file_id: str,
    db=Depends(get_mongo_service)
):
    """
    Removes a file from the producer's profile.
    """
    if not await remove_file(db, producer_id, file_id):
        raise HTTPException(status_code=404, detail="Profile or file not found.")
    return {"success": True, "message": "File removed successfully."}