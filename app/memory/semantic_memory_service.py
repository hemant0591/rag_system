import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.semantic_memory import UserMemorySemantic
from app.retrieval.embedding_service import embedding_provider
from app.retrieval.vector_store import upsert_semantic_memory

import logging
logger = logging.getLogger(__name__)

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

    logger.info("Creating semantic memory")
    
    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    logger.info("Postgres memory committed", extra={"memory_id": str(memory.id)})

    embedding = await embedding_provider.embed(content)

    logger.info("Upserting vector to Qdrant", extra={"memory_id": str(memory.id)})

    upsert_semantic_memory(
        memory_id=memory.id,
        tenant_id=tenant_id,
        user_id=user_id,
        embedding=embedding,
    )

    return memory