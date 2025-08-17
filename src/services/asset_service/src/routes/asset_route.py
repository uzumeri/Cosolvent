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
    get_application,
    get_all_applications,
    get_all_producers,
    delete_profile as delete_profile_crud,
    generate_ai_profile as generate_ai_profile_crud,
    approve_ai_draft as approve_ai_draft_crud,
    approve_profile as approve_profile_crud,
    reject_profile as reject_profile_crud,
    get_application_by_email,
    reject_ai_draft as reject_ai_draft_crud,
)
from src.database.crud.producer_file_crud import (
    create_producer_file,
    delete_producer_file_crud,
    get_producer_file,
    get_all_profile_files_by_email,
    update_producer_file_crud,
    change_file_url
)
from src.schema.profile_schema import (
    ProducerRegisterSchema, ProfileUpdateResponse, 
    ProducerSchema, SuccessResponse, ApprovalResponse,
    ProfileUpdateSchema, RejectApplicationSchema,
    ProducerFileUpdateSchema
)
from src.schema.producer_file_schema import ProducerFileSchema
from src.schema.application_schema import ApplicationSchema
from src.database.db import get_mongo_service
from utils.s3_uploader import upload_file_to_s3
from utils.openai_analyzer import get_image_metadata_from_openai ,get_document_text_from_openai 
from utils.auth import get_current_user_email
from utils.account_service import create_farmer_account
from utils.email_service import send_welcome_email
from src.core.config import settings
import secrets
import string

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201, response_model=ApplicationSchema)
async def register_producer(
    payload: ProducerRegisterSchema = Depends(),
    files: List[UploadFile] = File(...),
    files_metadata: str = Form(
        ...,
        description="A JSON string representing a list of metadata objects for the uploaded files. Each object must contain 'filename' and 'file_type'. For 'certificate' file_type, 'certification' is also required.",
    ),
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
    if await get_application_by_email(db, payload.email) or await get_profile_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="An application or profile with this email already exists.")

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

    created_profile, application_id = await create_profile(db, profile_data)

    metadata_map = {meta.get('filename'): meta for meta in files_metadata_list if meta.get('filename')}
    
    if len(files) != len(files_metadata_list):
        raise HTTPException(status_code=400, detail="The number of files must match the number of metadata entries.")

    for file in files:
        if not file.filename or file.filename not in metadata_map:
            raise HTTPException(status_code=400, detail=f"Metadata for file '{file.filename}' is missing.")
        
        file_meta = metadata_map[file.filename]
        file_type = file_meta.get("file_type")
        if not file_type:
            raise HTTPException(status_code=400, detail=f"file_type is missing for file '{file.filename}'.")

        certification = file_meta.get("certification", "")

        s3_url = await upload_file_to_s3(file, file.filename)
        file_doc = {
            "email": created_profile.email,
            "url": s3_url,
            "file_type": file_type,
            "certification": certification,
            "priority": 0,
            "privacy": "private",
        }
        # Pass user email to ensure file is added to producer's embedded files list
        await create_producer_file(db, file_doc, created_profile.email)

    application = await get_application(db, application_id)
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
async def delete_producer_profile(producer_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Performs a 'soft delete' by setting the profile status to suspended.
    """
    if not await delete_profile_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {"success": True, "message": "Profile has been suspended."}

@router.get("/files/{file_id}", response_model=ProducerFileSchema)
async def get_file_by_id(file_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Retrieves a specific file by its ID.
    """
    file = await get_producer_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")
    return jsonable_encoder(file)

@router.delete("/files/{file_id}", response_model=SuccessResponse)
async def delete_producer_file(file_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Deletes a specific file associated with a producer.
    """
    if not await delete_producer_file_crud(db, file_id, current_user_email):
        raise HTTPException(status_code=404, detail="File not found.")
    return {"success": True, "message": "File has been deleted."}


@router.put("/files_metadata/{file_id}", response_model=SuccessResponse)
async def update_producer_file(
    file_id: str,
    payload: ProducerFileUpdateSchema,
    db=Depends(get_mongo_service),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Updates a file's metadata.
    """
    update_data = payload.dict(exclude_unset=True)
    if not await update_producer_file_crud(db, file_id, update_data, current_user_email):
        raise HTTPException(status_code=404, detail="File not found or failed to update.")
    return {"success": True, "message": "File metadata updated successfully."}

@router.put("/profiles/files/{file_id}", response_model=SuccessResponse)
@router.put("/files/{file_id}", response_model=SuccessResponse)
async def update_file(
    file_id: str,
    file: UploadFile= File(...),
    db=Depends(get_mongo_service),
    current_user_email: str = Depends(get_current_user_email)
):  
    s3_url = await upload_file_to_s3(file, file.filename)
    if not await change_file_url(db, file_id, s3_url, current_user_email):
        raise HTTPException(status_code=409, detail="File not found or failed to update.")
    return {"success": True, "message": "File url updated successfully."}

    
@router.post("/files/{file_id}/generate-metadata")
@router.post("/profiles/files/{file_id}/generate-metadata")
async def generate_file_pometadata(file_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Generates AI-powered metadata (description) for a given file.
    Supports images and PDF documents.
    """
    file_doc = await get_producer_file(db, file_id)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found.")

    file_url = file_doc.url
    if not file_url:
        raise HTTPException(status_code=400, detail="File has no URL.")

    # Derive file extension and type key from filename
    filename = file_url.rsplit('/', 1)[-1]
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    # part after hyphen if present
    name_part = filename.split('-', 1)[-1] if '-' in filename else filename
    base_name = name_part.rsplit('.', 1)[0]
    type_key = base_name.split('_')[-1].lower()
    description = None

    try:
        if ext in ["jpeg", "jpg", "png", "gif", "bmp", "tiff"]:
            logger.info(f"Generating image metadata for file {file_id} (type {type_key})")
            description = await get_image_metadata_from_openai(file_url)
        elif ext == "pdf":
            logger.info(f"Generating document metadata for file {file_id} (type {type_key})")
            description = await get_document_text_from_openai(file_url)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Metadata generation is not supported for file extension '{ext}'."
            )

        if not description:
            raise HTTPException(status_code=500, detail=f"Could not analyze file. The analysis returned no data for file type '{type_key}'.")

        update_data = {"description": description}
        if not await update_producer_file_crud(db, file_id, update_data, current_user_email):
            raise HTTPException(status_code=500, detail="Failed to update file with new metadata.")
        
        return {"success": True, "metadata": description}
    except Exception as e:
        logger.error(f"Failed to generate metadata for file {file_id}: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="An error occurred during AI metadata generation.")

@router.get("/applications", response_model=List[ApplicationSchema])
async def list_applications(
    status: Optional[str] = Query(None, enum=["pending_review", "rejected"]),
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_mongo_service),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Lists applications with optional status filtering and pagination.
    """
    applications = await get_all_applications(db, status, skip, limit)
    return jsonable_encoder(applications)


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

@router.post("/applications/{application_id}/approve", response_model=ApprovalResponse)
async def approve_application(application_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Approves an application, moving it to the producers collection.
    """
    approved_producer = await approve_profile_crud(db, application_id)
    if not approved_producer:
        raise HTTPException(status_code=404, detail="Application not found or failed to approve.")
    # Extract producer ID from the Pydantic model
    producer_id_str = str(approved_producer.dict().get("id"))

    # After approval, auto-create an auth account and email credentials
    try:
        name = approved_producer.contact_name
        email = approved_producer.email
        # Generate a temporary password (12 chars, letters+digits)
        alphabet = string.ascii_letters + string.digits
        temp_password = "".join(secrets.choice(alphabet) for _ in range(12))

        ok, err = await create_farmer_account(name=name, email=email, password=temp_password)
        if ok:
            try:
                # Send welcome email with login details
                send_welcome_email(name=name, to_email=email, temp_password=temp_password, frontend_url=settings.FRONTEND_URL)
            except Exception as e:
                logger.error(f"Failed to send welcome email to {email}: {e}")
        else:
            logger.error(f"Failed to create auth account for {email}: {err}")
    except Exception as e:
        # Do not fail the approval if downstream actions fail; just log.
        logger.error(f"Post-approval actions failed for application {application_id}: {e}")

    return {"success": True, "message": "Application approved successfully.", "producerId": producer_id_str}


@router.post("/applications/{application_id}/reject", response_model=SuccessResponse)
async def reject_application(application_id: str, payload: RejectApplicationSchema, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Rejects an application with a reason.
    """
    if not await reject_profile_crud(db, application_id, payload.reason):
        raise HTTPException(status_code=404, detail="Application not found.")
    return {"success": True, "message": "Application rejected."}


@router.post("/profiles/{producer_id}/generate-ai-profile", response_model=SuccessResponse)
async def generate_ai_profile(producer_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
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
async def approve_ai_draft(producer_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Approves the AI-generated profile draft, making it the official AI profile.
    """
    if not await approve_ai_draft_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="AI draft not found or could not be approved.")
    return {"success": True, "message": "AI draft approved."}


@router.post("/profiles/{producer_id}/reject-ai-draft", response_model=SuccessResponse)
async def reject_ai_draft(producer_id: str, db=Depends(get_mongo_service), current_user_email: str = Depends(get_current_user_email)):
    """
    Rejects and deletes the current AI profile draft.
    """
    if not await reject_ai_draft_crud(db, producer_id):
        raise HTTPException(status_code=404, detail="AI draft not found or could not be rejected.")
    return {"success": True, "message": "AI draft rejected."}


@router.get("/profiles/{profile_id}/files", response_model=List[ProducerFileSchema])
async def get_files_for_profile(
    profile_id: str,
    db=Depends(get_mongo_service),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Retrieves all files associated with a specific producer profile.
    """
    profile = await get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    files = await get_all_profile_files_by_email(db, profile.email)
    return jsonable_encoder(files)

@router.post("/profiles/{profile_id}/files", status_code=201, response_model=List[ProducerFileSchema])
@router.post("/{profile_id}/files", status_code=201, response_model=List[ProducerFileSchema])
async def upload_files_to_profile(
    profile_id: str,
    files: List[UploadFile] = File(...),
    files_metadata: str = Form(
        ...,
        description="A JSON string representing a list of metadata objects for the uploaded files. Each object must contain 'filename' and 'file_type'. For 'certificate' file_type, 'certification' is also required.",
    ),
    db=Depends(get_mongo_service),
):
    """
    Uploads one or more files to an existing producer profile.
    """
    
    try:
        files_metadata_list = json.loads(files_metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in files_metadata.")

    if len(files) != len(files_metadata_list):
        raise HTTPException(status_code=400, detail="The number of files must match the number of metadata entries.")

    metadata_map = {meta.get('filename'): meta for meta in files_metadata_list if meta.get('filename')}
    file_objs: List[ProducerFileSchema] = []
    for file in files:
        if not file.filename or file.filename not in metadata_map:
            raise HTTPException(status_code=400, detail=f"Metadata for file '{file.filename}' is missing.")

        file_meta = metadata_map[file.filename]
        file_type = file_meta.get("file_type")
        if not file_type:
            raise HTTPException(status_code=400, detail=f"file_type is missing for file '{file.filename}'.")

        certification = file_meta.get("certification", "")

        s3_url = await upload_file_to_s3(file, file.filename)
        file_doc = {
            "profile_id": profile_id,
            "url": s3_url,
            "file_type": file_type,
            "certification": certification,
            "priority": file_meta.get("priority", 0),
            "privacy": file_meta.get("privacy", "private"),
        }
        created_file, file_id = await create_producer_file(db, file_doc)
        file_objs.append(created_file)
    # return list of ProducerFileSchema objects
    return file_objs