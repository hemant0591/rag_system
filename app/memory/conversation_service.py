from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation

async def create_conversation(
    db: AsyncSession,
    tenant_id: str,
    user_id: str,
) -> Conversation:
    
    conversation = Conversation(
        tenant_id=tenant_id,
        user_id=user_id,
    )

    db.add(conversation)

    await db.commit()
    await db.refresh(conversation)

    return conversation