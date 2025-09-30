import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Core
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent",
    )

    # Embeddings
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION") or 1536)

    # Service internal URLs 
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://profile_service:5000/profile/api")
    ASSET_SERVICE_URL: str = os.getenv("ASSET_SERVICE_URL", "http://asset_service:5001/asset")
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://search_service:5002")

    # Object storage (S3/MinIO). Canonical names with backward-compatible fallbacks
    S3_BUCKET: str | None = (
        os.getenv("S3_BUCKET")
        or os.getenv("S3_BUCKET_NAME")
        or os.getenv("ASSETS_BUCKET")
    )
    S3_ACCESS_KEY: str | None = (
        os.getenv("S3_ACCESS_KEY")
        or os.getenv("S3_AWS_ACCESS_KEY_ID")
        or os.getenv("MINIO_ACCESS_KEY")
    )
    S3_SECRET_KEY: str | None = (
        os.getenv("S3_SECRET_KEY")
        or os.getenv("S3_AWS_SECRET_ACCESS_KEY")
        or os.getenv("MINIO_SECRET_KEY")
    )
    S3_REGION: str = (
        os.getenv("S3_REGION")
        or os.getenv("AWS_REGION")
        or "us-east-1"
    )
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")

    # Backwards-compat 
    @property
    def S3_BUCKET_NAME(self) -> str | None:
        return self.S3_BUCKET

    @property
    def AWS_ACCESS_KEY_ID(self) -> str | None:
        return self.S3_ACCESS_KEY

    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str | None:
        return self.S3_SECRET_KEY

    @property
    def AWS_REGION(self) -> str:
        return self.S3_REGION


settings = Settings()
