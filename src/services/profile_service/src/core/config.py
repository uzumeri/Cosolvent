import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    MONGO_URI: str = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://mongodb:27017"
    MONGODB_NAME: str = os.getenv("MONGODB_NAME") or "administration"
    # Internal URL for the Asset service (includes its root_path '/asset')
    ASSET_SERVICE_URL: str = os.getenv("ASSET_SERVICE_URL", "http://asset_service:5001/asset")
    # URL for the Search service (indexing and search)
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://search_service:5002")

settings = Settings()
