import logging
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
logger = logging.getLogger(__name__)


class MongoService:
    def __init__(self):
        logger.info("Initializing Async MongoService...")
        self.client = AsyncIOMotorClient(settings.MONGO_URI, uuidRepresentation="standard")
        self.db = self.client[settings.MONGODB_NAME]
        self.producer_files = self.db["producer_files"]
        logger.info("Async MongoService initialized.")

mongoService = MongoService()

def get_mongo_service():
    """Dependency callable that returns a MongoService instance."""
    return mongoService