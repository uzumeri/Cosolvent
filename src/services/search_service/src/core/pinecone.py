from pinecone import Pinecone
from .config import settings

# Initialize Pinecone client instance
pc = Pinecone(api_key=settings.PINECONE_API_KEY)


def init_pinecone() -> None:
    """No-op or verify Pinecone client is ready."""
    # Client is initialized on import
    return None


def get_index():
    """Connect to an existing Pinecone index by host URL."""
    host = settings.PINECONE_INDEX_HOST
    return pc.Index(host=host)
