import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.semantic_memory import UserMemorySemantic
from app.retrieval.embedding_service import embedding_service
from app.retrieval.vector_store import upsert_semantic_memory

async def create_semantic_memory(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str
):
    
    memory = UserMemorySemantic(
        tenant_id=tenant_id,
        user_id=user_id,
        content=content,
    )

    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    embedding = embedding_service.embed(content)

    upsert_semantic_memory(
        memory_id=memory.id,
        tenant_id=tenant_id,
        user_id=user_id,
        embedding=embedding,
    )

    return memory