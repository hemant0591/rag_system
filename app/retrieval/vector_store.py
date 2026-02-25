from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.core.config import settings

client = QdrantClient(url=settings.qdrant_url)

def create_semantic_memory_collection():
    client.recreate_collection(
        collection_name="user_memory_semantic",
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )