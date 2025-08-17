import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    MONGO_URI: str = os.getenv("MONGODB_URI")
    MONGODB_NAME: str = os.getenv("MONGODB_NAME")
    ASSET_SERVICE_URL: str = os.getenv("ASSET_SERVICE_URL", "http://asset_service:5000")
    # URL for the Search service (indexing and search)
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://search_service:5002")

settings = Settings()
