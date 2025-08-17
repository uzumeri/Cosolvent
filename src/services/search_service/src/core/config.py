from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl

class Settings(BaseSettings):
    RABBITMQ_URL: str = Field(..., env="RABBITMQ_URL")
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_INDEX_HOST: str = Field(..., env="PINECONE_INDEX_HOST")
    PINECONE_INDEX_NAME: str = Field(..., env="PINECONE_INDEX_NAME")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    CACHE_TTL: int = Field(300, env="CACHE_TTL")
    PROFILE_SERVICE_URL: AnyHttpUrl = Field(..., env="PROFILE_SERVICE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
