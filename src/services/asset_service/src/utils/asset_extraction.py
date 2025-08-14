import httpx
import asyncio
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import textract
from typing import Optional
from bson import ObjectId
from src.database.db import db
from src.database.models.asset_service import AssetModel
from src.database.crud.asset_service_crud import AssetCRUD
from src.utils.mock_llm_extraction import ExtractUsingLLM
import boto3
from botocore.exceptions import ClientError
from src.core.config import Config
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException

class AssetExtraction:
    """
    Service for reading asset contents from an S3 URL using boto3 and extracting text.
    """

    SUPPORTED_TYPES = {
        "plain",
        "pdf",
        "msword",
        "vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    @staticmethod
    def _parse_s3_url(url: str):
        """
        Parse an S3 URL (virtual-hosted or path-style) into (bucket, key).
        """
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path.lstrip("/")  # e.g. "key/with/path.pdf"

        # Virtual-hosted style: bucket.s3.region.amazonaws.com
        # Host may be like: bucket.s3.amazonaws.com or bucket.s3.us-east-2.amazonaws.com
        if host.endswith(".amazonaws.com"):
            # bucket is first label before ".s3"
            parts = host.split(".")
            # Expect ["bucket", "s3", "region", "amazonaws", "com"]
            if len(parts) >= 3 and parts[1] == "s3":
                bucket = parts[0]
                key = path
                return bucket, key
        # Fallback: maybe path-style: s3.amazonaws.com/bucket/key
        # or custom domain that embeds bucket in path. Try splitting path:
        parts = path.split("/", 1)
        if len(parts) == 2:
            bucket, key = parts
            return bucket, key
        raise ValueError(f"Cannot parse S3 URL: {url}")

    @staticmethod
    async def read_from_s3(url: str, content_type: str) -> str:
        """
        Fetches the file from the given S3 URL using boto3 and returns its text content.
        :param url: Public or presigned S3 URL of the asset
        :param content_type: MIME type of the asset, e.g. "application/pdf"
        :returns: Extracted text content
        :raises HTTPException: on invalid URL or S3 errors
        """
        try:
            bucket, key = AssetExtraction._parse_s3_url(url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Create S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=Config.S3_ACCESS_KEY,
            aws_secret_access_key=Config.S3_SECRET_KEY,
            region_name=Config.S3_REGION
        )

        # Get object
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
        except ClientError as e:
            code = e.response["Error"].get("Code", "")
            msg = e.response["Error"].get("Message", "")
            # If using presigned URL, you could fetch via HTTP instead of S3 API
            raise HTTPException(status_code=500, detail=f"S3 get_object failed: {code} {msg}")

        # Read body in threadpool
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, response["Body"].read)

        # Determine subtype
        subtype = content_type.split("/", 1)[-1]  # e.g. "pdf" or "msword"

        if subtype == "plain":
            return data.decode("utf-8", errors="ignore")

        if subtype == "pdf":
            try:
                reader = PdfReader(BytesIO(data))
                return "\n\n".join((page.extract_text() or "") for page in reader.pages)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"PDF parsing error: {e}")

        if subtype == "msword":
            try:
                text = textract.process(input_data=data, extension="doc")
                return text.decode("utf-8", errors="ignore")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"DOC parsing error: {e}")

        if subtype == "vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                with BytesIO(data) as bio:
                    doc = Document(bio)
                    return "\n\n".join(p.text for p in doc.paragraphs)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"DOCX parsing error: {e}")

        # Fallback: use LLM extraction
        return ExtractUsingLLM(url, content_type).extract()

    @staticmethod
    async def read_asset_by_id(asset_id: str) -> Optional[str]:
        raw = await AssetCRUD.get_by_id(asset_id)
        if not raw:
            return None
        asset_url = raw["url"]
        file_type = raw["content_type"]
        return await AssetExtraction.read_from_s3(asset_url, file_type)
