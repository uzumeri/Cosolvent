import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    MONGO_URI: str = os.getenv("MONGODB_URI")
    MONGODB_NAME: str = os.getenv("MONGODB_NAME")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    AWS_ACCESS_KEY_ID: str = os.getenv("S3_AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("S3_AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8020/api/verify")
    # Auth service signup endpoint (internal service-to-service)
    AUTH_SIGNUP_URL: str = os.getenv(
        "AUTH_SIGNUP_URL",
        "http://auth_service:8020/api/auth/sign-up/email",
    )
    # Frontend URL for email links
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://grainplaza.com")
    # Email configuration (Resend)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "no-reply@grainplaza.com")
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = os.getenv("SEARCH_PINECONE_INDEX_NAME")
    # Embedding model and dimension
    OPENAI_EMBEDDING_MODEL: str = os.getenv("SEARCH_OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = int(os.getenv("SEARCH_OPENAI_EMBEDDING_DIMENSION") or 1536)

settings = Settings()
