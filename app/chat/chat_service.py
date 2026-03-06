from uuid import UUID
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.conversation import Conversation
from app.models.conversation import Message


class ChatService:
    async def handle_chat(
        self,
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
        user_input: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, any]:
        
        if conversation_id is not None:
            conversation_id = UUID(conversation_id)

            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.tenant_id == tenant_id,
                Conversation.user_id == user_id
            )

            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()

            if conversation is None:
                raise ValueError("Conversation not found or access denied.")
        
        else:
            conversation = Conversation(
                tenant_id=tenant_id,
                user_id=user_id,
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        user_message = Message(
            tenant_id=tenant_id,
            conversation_id=conversation.id,
            role="user",
            content=user_input,
        )

        db.add(user_message)

        # update conversation
        conversation.last_activity_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(user_message)
            
        return {
            "conversation_id": str(conversation.id),
            "message_id": str(user_message.id),
        }