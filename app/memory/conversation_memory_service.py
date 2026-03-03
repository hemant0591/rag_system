from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Message

async def fetch_recent_messages(
        db: AsyncSession,
        conversation_id: str,
        limit: int = 10,
) -> List[dict]:
    """
    Fetch last N messages for a conversation,
    ordered chronologically (oldest first).
    """

    stmt = (
        select(Message)
        .where(Message.conversation_id==conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    messages.reverse()

    return [
        {
            "role": msg.role,
            "content": msg.content,
        }
        for msg in messages
    ]