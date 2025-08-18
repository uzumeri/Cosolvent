from uuid import uuid4
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import HTTPException, UploadFile
import logging
import os
from src.core.config import settings
import io

import asyncio

logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

TEMP_DIR = "tmp/"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
def ensure_bucket_exists(bucket_name: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        err = e.response.get("Error", {})
        code = err.get("Code", "")
        if code in ["404", "NoSuchBucket", "NotFound", "404 Not Found"]:
            create_kwargs = {"Bucket": bucket_name}
            if settings.AWS_REGION and settings.AWS_REGION != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": settings.AWS_REGION}
            try:
                s3_client.create_bucket(**create_kwargs)
            except ClientError as ce:
                msg = ce.response.get("Error", {}).get("Message", str(ce))
                raise HTTPException(status_code=500, detail=f"Failed to create bucket: {msg}") from ce
        else:
            msg = err.get("Message", "")
            raise HTTPException(status_code=500, detail=f"Failed to access bucket: {msg}") from e

async def upload_file_to_s3(file: UploadFile, object_name: str = None) -> str:
    """
    Uploads a file to an S3 bucket and makes it public.

    :param file: File to upload (FastAPI UploadFile object).
    :param object_name: S3 object name. If not specified, filename is used.
    :return: Public URL of the uploaded file, or None if upload fails.
    """



    ALLOWED_MIME_TYPES = {
    "image/png", "image/jpeg", "image/webp",
    "video/mp4", "video/mpeg",
    "audio/mpeg", "audio/wav",
    "text/plain",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    # Ensure the bucket exists
    ensure_bucket_exists(settings.S3_BUCKET_NAME)
    data = await file.read()
    key = f"{uuid4().hex}-{file.filename}"

    try:
        s3_client.upload_fileobj(
            io.BytesIO(data),
            
            settings.S3_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )
    except ClientError as e:
        err = e.response.get("Error", {})
        msg = err.get("Message", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {msg}") from e

    # Public URL (objects must be public via bucket policy)
    url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
    return url


async def delete_file_from_s3(file_url: str):
    """
    Deletes a file from an S3 bucket based on its URL.
    """
    try:
        bucket_name = settings.S3_BUCKET_NAME
        # Extract the object key from the URL
        key = file_url.split(f"{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
        
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        logger.info(f"Successfully deleted {key} from S3 bucket {bucket_name}.")
        return True
    except (ClientError, IndexError) as e:
        logger.error(f"Failed to delete file from S3: {e}")
        return False
