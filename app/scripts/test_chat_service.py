import asyncio

from app.chat.chat_service import ChatService
from app.core.database import AsyncSessionLocal
from app.models.identity import Tenant, User

service = ChatService()


async def run_test():
    async with AsyncSessionLocal() as db:

        tenant = Tenant(name="Test Tenant")
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

        user = User(
            tenant_id=tenant.id,
            email="test@email.com"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        service = ChatService()

        # First message (no conversation_id)
        response1 = await service.handle_chat(
            db=db,
            tenant_id=tenant.id,
            user_id=user.id,
            user_input="Hello",
        )

        conversation_id = response1["conversation_id"]

        print("First conversation id:", conversation_id)
        print("First message id:", response1["message_id"])

        # Second message (reuse same conversation)
        response2 = await service.handle_chat(
            db=db,
            tenant_id=tenant.id,
            user_id=user.id,
            user_input="Tell me more",
            conversation_id=conversation_id,
        )

        print("Second call works.")
        return response2

if __name__ == "__main__":
    result = asyncio.run(run_test())
    print("Result:", result)
