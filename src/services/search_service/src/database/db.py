import pinecone
from src.core.config import settings
from src.core.pinecone import init_pinecone, get_index

# Initialize Pinecone client
init_pinecone()
# Get index by host URL
index = get_index()