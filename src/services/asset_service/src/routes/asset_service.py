import io
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status
import boto3
from botocore.exceptions import ClientError
from bson import ObjectId
import httpx

from src.utils.publisher import publish_asset
from src.schemas.asset_service_schema import AssetResponse, MetadataResponse
from src.database.crud.asset_service_crud import AssetCRUD
from src.database.crud.profile_generation_crud import PROFILECRUD
from src.core.config import Config

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "image/png", "image/jpeg", "image/webp",
    "video/mp4", "video/mpeg",
    "audio/mpeg", "audio/wav",
    "text/plain",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.S3_ACCESS_KEY,
    aws_secret_access_key=Config.S3_SECRET_KEY,
    region_name=Config.S3_REGION
)

def ensure_bucket_exists(bucket_name: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        err = e.response.get("Error", {})
        code = err.get("Code", "")
        if code in ["404", "NoSuchBucket", "NotFound", "404 Not Found"]:
            create_kwargs = {"Bucket": bucket_name}
            if Config.S3_REGION and Config.S3_REGION != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": Config.S3_REGION}
            try:
                s3_client.create_bucket(**create_kwargs)
            except ClientError as ce:
                msg = ce.response.get("Error", {}).get("Message", str(ce))
                raise HTTPException(status_code=500, detail=f"Failed to create bucket: {msg}") from ce
        else:
            msg = err.get("Message", "")
            raise HTTPException(status_code=500, detail=f"Failed to access bucket: {msg}") from e

# Asset CRUD Operations
@router.post("/assets", response_model=AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    user_id: str = Form(...),
):
    user = await PROFILECRUD.get_profile_by_user_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User is not registered")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    ensure_bucket_exists(Config.S3_BUCKET)

    data = await file.read()
    key = f"{uuid4().hex}-{file.filename}"

    try:
        s3_client.upload_fileobj(
            io.BytesIO(data),
            Config.S3_BUCKET,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )
    except ClientError as e:
        err = e.response.get("Error", {})
        msg = err.get("Message", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {msg}") from e

    # Public URL (objects must be public via bucket policy)
    url = f"https://{Config.S3_BUCKET}.s3.{Config.S3_REGION}.amazonaws.com/{key}"

    file_type = file.content_type.split("/")[0]
    asset_data = {
        "user_id": user_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_type": file_type,
        "url": url,
    }

    saved = await AssetCRUD.create(asset_data)
    await publish_asset({"asset_id": str(saved["id"])})
    return saved

@router.get("/assets", response_model=list[AssetResponse])
async def get_assets(
    user_id: str = Query(None),
    asset_id: str = Query(None)
):
    if asset_id:
        try:
            ObjectId(asset_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid asset_id format")
        asset = await AssetCRUD.get_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return [asset]
    elif user_id:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id cannot be empty")
        assets = await AssetCRUD.get_by_user_id(user_id)
        return assets
    else:
        raise HTTPException(status_code=400, detail="Either user_id or asset_id must be provided")

@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, metadata: dict):
    try:
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset_id format")
    
    updated_asset = await AssetCRUD.update(asset_id, metadata)
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return updated_asset

@router.delete("/assets/{asset_id}", status_code=status.HTTP_200_OK)
async def delete_asset(asset_id: str):
    try:
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset_id format")
    
    deleted = await AssetCRUD.delete(asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"success": True, "message": f"Asset {asset_id} deleted successfully"}

# Metadata Operations
@router.post("/assets/{asset_id}/metadata", response_model=MetadataResponse)
async def describe_asset(asset_id: str):
    """
    HTTP trigger to describe an asset by ID.
    """
    return await process_asset(asset_id)

@router.get("/assets/{asset_id}/metadata", response_model=MetadataResponse)
async def get_asset_metadata(asset_id: str):
    """
    Get metadata for an asset.
    """
    metadata = await AssetCRUD.get_metadata(asset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Asset metadata not found")
    return metadata

# Translation Operations
@router.post("/assets/{asset_id}/translate")
async def translate_asset_content(asset_id: str, target_language: str = "en"):
    """
    Translate asset content to target language.
    """
    try:
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset_id format")
    
    translation = await AssetCRUD.translate_content(asset_id, target_language)
    if not translation:
        raise HTTPException(status_code=404, detail="Asset not found or translation failed")
    return translation

@router.get("/assets/{asset_id}/translations")
async def get_asset_translations(asset_id: str):
    """
    Get all translations for an asset.
    """
    try:
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset_id format")
    
    translations = await AssetCRUD.get_translations(asset_id)
    if not translations:
        raise HTTPException(status_code=404, detail="Asset translations not found")
    return translations

async def process_asset(asset_id: str) -> MetadataResponse:
    """
    Fetch asset bytes and call LLM to generate description.
    """
    # 1) Fetch asset metadata (to get download URL) from Asset Service
    asset = await AssetCRUD.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    download_url = asset.get("url")
    if not download_url:
        raise HTTPException(status_code=400, detail="Invalid download URL")
    
    # 2) Download binary data
    async with httpx.AsyncClient() as client:
        resp_file = await client.get(download_url)
        resp_file.raise_for_status()
        data = resp_file.content
    
    # 3) Call LLM Orchestration metadata endpoint
    files = {"file": (f"{asset_id}", data, asset.get("content_type", "application/octet-stream"))}
    
    # For now, return basic metadata - in production, this would call the LLM service
    description = f"Asset {asset_id} of type {asset.get('file_type', 'unknown')}"
    
    # Save metadata to database
    metadata_data = {
        "asset_id": asset_id,
        "description": description,
        "file_type": asset.get("file_type"),
        "content_type": asset.get("content_type")
    }
    
    await AssetCRUD.save_metadata(metadata_data)
    
    return MetadataResponse(asset_id=asset_id, description=description)
