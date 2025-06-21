import os
from pydantic import BaseSettings, AnyHttpUrl

from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_index_host: str  # e.g. "https://<your-index-endpoint>.svc.<region>.pinecone.io"

    # Profile service: your existing service to GET profile by user_id
    profile_service_url: AnyHttpUrl  # e.g., "http://profile_management_service"

    # RabbitMQ or other broker URL
    rabbitmq_url: str  # e.g., "amqp://user:pass@rabbitmq:5672/"

    # Embedding model
    embedding_model: str = "text-embedding-ada-002"

    class Config:
        env_file = ".env"
        # Environment variables expected:
        # OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_INDEX_HOST,
        # PROFILE_SERVICE_URL, RABBITMQ_URL
        DB_NAME: str = os.getenv("DB_NAME", "COSOLVENT_DB")
        MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
        OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
        PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
        PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME")
        PINECONE_INDEX_HOST: str = os.getenv("PINECONE_INDEX_HOST")
        RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


settings = Settings()
