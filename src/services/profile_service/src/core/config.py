import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
    # Internal URL for the Asset service (includes its root_path '/asset')
    ASSET_SERVICE_URL: str = os.getenv("ASSET_SERVICE_URL", "http://asset_service:5001/asset")
    # URL for the Search service (indexing and search)
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://search_service:5002")

settings = Settings()
