from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query, Body
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
import mimetypes
import json
import logging
from bson.objectid import ObjectId  # type: ignore
import httpx  # type: ignore

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
    remove_file_from_producer_profile as remove_file,
)
from src.schema.profile_schema import (
    ProducerRegisterSchema,
    ProfileUpdateResponse,
    ProducerSchema,
    SuccessResponse,
    ProfileUpdateSchema,
)
from src.schema.producer_file_schema import ProducerFileSchema
from src.database.db import get_mongo_service
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201, response_model=ProducerSchema)
async def register_producer(
    payload: ProducerRegisterSchema = Depends(ProducerRegisterSchema.as_form),
    files: List[UploadFile] = File(...),
    files_metadata: Optional[str] = Form(None),
    db=Depends(get_mongo_service),
):
    """
    Submits a new producer application.
    """
    # Parse files metadata: if provided, must be valid JSON array; if missing, synthesize from files
    files_metadata_list: List[dict] = []
    if files_metadata is not None:
        try:
            parsed = json.loads(files_metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in files_metadata.")
        if not isinstance(parsed, list):
            raise HTTPException(status_code=400, detail="files_metadata must be a JSON array.")
        files_metadata_list = parsed
    else:
        # synthesize minimal metadata matching each file
        files_metadata_list = [
            {
                "filename": f.filename,
                "file_type": (f.content_type or "unknown").split("/")[0],
            }
            for f in files
        ]

    # Ensure counts match exactly
    if len(files) != len(files_metadata_list):
        raise HTTPException(
            status_code=400,
            detail="The number of files must match the number of metadata entries.",
        )

    logger.info(f"Registration attempt for email: {payload.email}")
    if await get_profile_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="A profile with this email already exists.")

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

    # Prepare files payload with normalized content types that asset_service accepts
    ALLOWED_CT = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "video/mp4",
        "video/mpeg",
        "audio/mpeg",
        "audio/wav",
        "text/plain",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def normalize_content_type(filename: str, content_type: Optional[str]) -> str:
        ct = (content_type or "").strip().lower()
        if ct in ALLOWED_CT:
            return ct
        # Try to guess from filename
        guess, _ = mimetypes.guess_type(filename)
        if guess and guess in ALLOWED_CT:
            return guess
        # Common mappings by extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        mapping = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "pdf": "application/pdf",
            "txt": "text/plain",
            "mp4": "video/mp4",
            "mpeg": "video/mpeg",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        return mapping.get(ext, "application/octet-stream")

    files_payload = []
    for file in files:
        file.file.seek(0)
        normalized_ct = normalize_content_type(file.filename, file.content_type)
        files_payload.append(("files", (file.filename, await file.read(), normalized_ct)))

    # Call asset service endpoint with small retry/backoff for transient issues
    asset_url = f"{settings.ASSET_SERVICE_URL}/api/{profile_id}/files"
    last_exc: Optional[Exception] = None
    response = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=5.0)) as client:
                response = await client.post(
                    asset_url,
                    files=files_payload,
                    data={"files_metadata": json.dumps(files_metadata_list)},
                )
            break
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            last_exc = e
            logger.warning(f"Asset service call failed on attempt {attempt + 1}: {e}")
            if attempt < 2:
                import asyncio

                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                raise HTTPException(status_code=502, detail="Could not reach asset service.")

    if response is None:
        raise HTTPException(status_code=502, detail="Asset service did not respond.")
    if response.status_code != 201:
        # Surface upstream error detail to help diagnose (map 4xx to client, 5xx to gateway error)
        detail = None
        try:
            data = response.json()
            detail = data.get("detail") if isinstance(data, dict) else None
        except Exception:
            detail = response.text
        status = 400 if 400 <= response.status_code < 500 else 502
        raise HTTPException(status_code=status, detail=detail or "Asset service rejected file upload.")

    # Parse returned file objects and convert to dicts for MongoDB storage
    files_data = response.json()
    parsed_files = []
    for item in files_data:
        pf = ProducerFileSchema(**item)
        d = pf.dict(by_alias=True)
        # ensure _id is string for embedding
        if isinstance(d.get("_id"), (bytes, bytearray)):
            d["_id"] = str(d.get("_id"))
        else:
            d["_id"] = str(d.get("_id"))
        d["profile_id"] = profile_id
        parsed_files.append(d)

    # Update producer record with embedded files
    await db.producers.update_one({"_id": ObjectId(profile_id)}, {"$set": {"files": parsed_files}})

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