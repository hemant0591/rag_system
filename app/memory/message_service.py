from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Message

async def create_message(
    db: AsyncSession,
    tenant_id: str,
    conversation_id: str,
    role: str,
    content: str,
) -> Message:
    
    message = Message(
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    await db.commit()
    await db.refresh(message)

    return message