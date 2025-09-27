from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from fastapi.encoders import jsonable_encoder
from typing import List
import json
import logging
import httpx

from src.database.crud.producer_file_crud import (
    create_producer_file,
    delete_producer_file_crud,
    get_producer_file,
    update_producer_file_crud,
    change_file_url
)
from src.schema.producer_file_schema import (
    SuccessResponse,
    ProducerFileUpdateSchema
)
from src.schema.producer_file_schema import ProducerFileSchema
from src.database.db import get_mongo_service
from src.core.config import settings
from utils.s3_uploader import upload_file_to_s3
from utils.openrouter_analyzer import (
    get_image_metadata_from_openrouter,
    get_document_text_from_openrouter,
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/files/{file_id}", response_model=ProducerFileSchema)
async def get_file_by_id(file_id: str, db=Depends(get_mongo_service)):
    """
    Retrieves a specific file by its ID.
    """
    file = await get_producer_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")
    return jsonable_encoder(file)

@router.delete("/files/{file_id}", response_model=SuccessResponse)
async def delete_producer_file(file_id: str, profile_id: str, db=Depends(get_mongo_service)):
    """
    Deletes a specific file associated with a producer.
    """
    if not await delete_producer_file_crud(db, file_id):
        raise HTTPException(status_code=404, detail="File not found.")
    profile_service_url = settings.PROFILE_SERVICE_URL
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{profile_service_url}/profiles/{profile_id}/files/{file_id}")
    if response.status_code != 200:
         raise HTTPException(status_code=response.status_code, detail=response.text)

    logger.info(f"File {file_id} deleted successfully from producer's profile.")
    return {"success": True, "message": "File has been deleted."}


@router.put("/files_metadata/{file_id}", response_model=SuccessResponse)
async def update_producer_file(
    file_id: str,
    payload: ProducerFileUpdateSchema,
    db=Depends(get_mongo_service),
):
    """
    Updates a file's metadata.
    """
    update_data = payload.dict(exclude_unset=True)
    updated_file = await update_producer_file_crud(db, file_id, update_data)
    profile_service_url = settings.PROFILE_SERVICE_URL
    update_url = f"{profile_service_url}/profiles/{updated_file.profile_id}/files"
    async with httpx.AsyncClient() as client:
        await client.put(update_url, json=jsonable_encoder(updated_file))
    return {"success": True, "message": "File metadata updated successfully."}

@router.put("/files/{file_id}", response_model=SuccessResponse)
async def update_file(
    file_id: str,
    file: UploadFile= File(...),
    db=Depends(get_mongo_service),
    
):  
    s3_url = await upload_file_to_s3(file, file.filename)
    updated_file = await change_file_url(db, file_id, s3_url)
    profile_service_url = settings.PROFILE_SERVICE_URL
    update_url = f"{profile_service_url}/profiles/{updated_file.profile_id}/files"
    async with httpx.AsyncClient() as client:
        await client.put(update_url, json=jsonable_encoder(updated_file))
    return {"success": True, "message": "File url updated successfully."}

    
@router.post("/files/{file_id}/generate-metadata")
async def generate_file_metadata(file_id: str, db=Depends(get_mongo_service)):
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

    filename = file_url.rsplit('/', 1)[-1]
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    name_part = filename.split('-', 1)[-1] if '-' in filename else filename
    base_name = name_part.rsplit('.', 1)[0]
    type_key = base_name.split('_')[-1].lower()
    description = None

    try:
        if ext in ["jpeg", "jpg", "png", "gif", "bmp", "tiff"]:
            logger.info(f"Generating image metadata for file {file_id} (type {type_key})")
            description = await get_image_metadata_from_openrouter(file_url)
        elif ext == "pdf":
            logger.info(f"Generating document metadata for file {file_id} (type {type_key})")
            description = await get_document_text_from_openrouter(file_url)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Metadata generation is not supported for file extension '{ext}'."
            )

        if not description:
            raise HTTPException(status_code=500, detail=f"Could not analyze file. The analysis returned no data for file type '{type_key}'.")

        update_data = {"description": description}
        updated_file = await update_producer_file_crud(db, file_id, update_data)
        profile_service_url = settings.PROFILE_SERVICE_URL
        update_url = f"{profile_service_url}/profiles/{updated_file.profile_id}/files"
        async with httpx.AsyncClient() as client:
            await client.put(update_url, json=jsonable_encoder(updated_file))
        return {"success": True, "metadata": description}
    except Exception as e:
        logger.error(f"Failed to generate metadata for file {file_id}: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="An error occurred during AI metadata generation.")

@router.get("/{profile_id}/files", response_model=List[ProducerFileSchema])
async def get_files_for_profile(
    profile_id: str,
    db=Depends(get_mongo_service),
):
    """
    Retrieves all files associated with a specific producer profile.
    """
    # Fetch files directly by profile_id
    cursor = db.producer_files.find({"profile_id": profile_id})
    docs = await cursor.to_list(length=None)
    files = []
    for doc in docs:
        doc['id'] = str(doc['_id'])
        doc.pop('_id', None)
        files.append(ProducerFileSchema(**doc))
    return jsonable_encoder(files)

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
    # Propagate each new file to profile service
    async with httpx.AsyncClient() as client:
        for file in file_objs:
            await client.post(
                f"{settings.PROFILE_SERVICE_URL}/profiles/{profile_id}/files",
                json=jsonable_encoder(file)
            )
    return file_objs