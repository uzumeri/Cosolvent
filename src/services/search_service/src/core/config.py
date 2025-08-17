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

    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = os.getenv("SEARCH_PINECONE_INDEX_NAME")

    # Embedding model and dimension
    OPENAI_EMBEDDING_MODEL: str = os.getenv("SEARCH_OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = int(os.getenv("SEARCH_OPENAI_EMBEDDING_DIMENSION") or 1536)
    
    # Base URL for profile service API (with prefix and root_path)
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://profile_service:5000/profile/api")
settings = Settings()
