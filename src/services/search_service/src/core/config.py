import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION") or 1536)
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://profile_service:5000")

settings = Settings()
