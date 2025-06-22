from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    RABBITMQ_URL: str = Field(..., env="RABBITMQ_URL")
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_INDEX_HOST: str = Field(..., env="PINECONE_INDEX_HOST")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    CACHE_TTL: int = Field(300, env="CACHE_TTL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
