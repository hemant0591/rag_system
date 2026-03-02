from app.retrieval.embedding_service import embedding_provider
from app.retrieval.vector_store import search_semantic_memory
from app.core.database import AsyncSessionLocal
from app.models.semantic_memory import UserMemorySemantic

async def retrieve_semantic_memory(
        tenant_id,
        user_id,
        query_text:str,
        top_k:int = 5,
):
    query_embedding = await embedding_provider.embed(query_text)

    results = search_semantic_memory(
        query_embedding=query_embedding,
        tenant_id=tenant_id,
        user_id=user_id,
        top_k=top_k
    )

    memory_ids = [r.id for r in results]

    if not memory_ids:
        return []
    
    async with AsyncSessionLocal() as db:
        records = await db.execute(
            UserMemorySemantic.__table__.select().where(
                UserMemorySemantic.id.in_(memory_ids)
            )
        )

    return records.fetchall()