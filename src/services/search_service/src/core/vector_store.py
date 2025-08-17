import logging
from pinecone import Pinecone
import openai
from src.core.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = settings.OPENAI_API_KEY

# Initialize Pinecone client
try:
    # Include environment if you have it: Pinecone(api_key=..., environment=...)
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    logger.info("Initialized Pinecone client")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone client: {e}")
    raise

# Connect to the Pinecone index
try:
    index = pc.Index(
        name=settings.PINECONE_INDEX_NAME,
        host=settings.PINECONE_INDEX_HOST
    )
    # Check by describing stats
    stats = index.describe_index_stats()
    logger.info(f"Connected to Pinecone index '{settings.PINECONE_INDEX_NAME}', stats: {stats}")
except Exception as e:
    logger.error(f"Failed to connect or describe Pinecone index '{settings.PINECONE_INDEX_NAME}': {e}")
    raise
