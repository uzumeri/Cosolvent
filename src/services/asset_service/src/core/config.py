import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
    # S3/MinIO
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME") or os.getenv("ASSETS_BUCKET")
    AWS_ACCESS_KEY_ID: str = os.getenv("S3_AWS_ACCESS_KEY_ID") or os.getenv("MINIO_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("S3_AWS_SECRET_ACCESS_KEY") or os.getenv("MINIO_SECRET_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION") or os.getenv("S3_REGION") or "us-east-1"
    # Optional S3-compatible endpoint (e.g., MinIO); if unset, defaults to AWS S3
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    
    # Base URL for profile service API (with prefix and root_path)
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://profile_service:5000/profile/api")
settings = Settings()
