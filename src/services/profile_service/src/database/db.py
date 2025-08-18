import logging
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
logger = logging.getLogger(__name__)


class MongoService:
    def __init__(self):
        logger.info("Initializing Async MongoService...")
        # Use Motor for async MongoDB operations
        # Configure UUID representation for BSON compatibility
        self.client = AsyncIOMotorClient(settings.MONGO_URI, uuidRepresentation="standard")
        self.db = self.client[settings.MONGODB_NAME]
        # Collections
        self.producers = self.db["producers"]
        self.templates = self.db["templates"]
        logger.info("Async MongoService initialized.")

mongoService = MongoService()

def get_mongo_service():
    """Dependency callable that returns a MongoService instance."""
    return mongoService