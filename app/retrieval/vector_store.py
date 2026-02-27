from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
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

def upsert_semantic_memory(
        memory_id: str,
        tenant_id: str,
        user_id: str,
        embedding: list[float]
):
    client.upsert(
        collection_name="user_memory_semantic",
        points=[
            PointStruct(
                id=str(memory_id),
                vector=embedding,
                payload={
                    "tenant_id": str(tenant_id),
                    "user_id": str(user_id)
                },
            )
        ],
    )


def search_semantic_memory(
        query_embedding: list[float],
        tenant_id: str,
        user_id: str,
        top_k:int = 5,
):
    
    results = client.search(
        collection_name="user_memory_semantic",
        query_vector=query_embedding,
        limit=top_k,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="tenant_id",
                    match=MatchValue(value=str(tenant_id)),
                ),
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id)),
                ),
            ]
        ),
    )

    return results