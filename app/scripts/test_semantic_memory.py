import asyncio

from app.core.database import AsyncSessionLocal
from app.models.identity import Tenant, User
from app.memory.semantic_memory_service import create_semantic_memory
from app.retrieval.vector_store import client
from app.memory.sematic_memory_retrieval import retrieve_semantic_memory
from app.core.logging import configure_logging
from app.llm.context_builder import build_context
from app.llm.llm_provider import llm_provider
from app.core.config import settings
from app.prompts.loader import load_system_prompt
from app.memory.conversation_service import create_conversation
from app.memory.message_service import create_message
from app.memory.conversation_memory_service import fetch_recent_messages

configure_logging()

queries = [
    # "Ton 618 is the most massive black hole.",
    # "Anatarctica is the coldest place on earth",
    # "Death valley is the hottest place on earth",
    # "Mt. Everest is the highest mountain on earth",
    "Mount Everest is 7,000 meters tall",
    # "Aconcagua is the highest mountain in South America",
    # "Denali is the highest mountain in North America",
    # "Kilimanjaro is the highest mountain in Africa,",
    # "Elbrus is the highest mountain in Europe",
    # "Vinson Massif is the highest mountain in Antarctica",
    # "Puncak Jaya is the highest mountain in Oceania/Australia",
    # "Olympus Mons is the highest mountain in the solar system",
    # "There are 2 trillion galaxies in the universe",
    # "Andromeda is the nearest galaxy from milky way",
    # "Milky way is in the Laniakea supercluster",
]

user_preferences = {
        "user_preferences": {
        "verbosity": "short",
        "style": "technical",
        "tone": "to-the-point"
        }
    }
system_prompt = load_system_prompt()

query = "highest mountain"

async def run_test():
    async with AsyncSessionLocal() as db:

        tenant = Tenant(name="Test Tenant")
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

        print(f"Created tenant: {tenant.id}")

        user = User(
            tenant_id=tenant.id,
            email="test@email.com"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"Created user: {user.id}")

        for content in queries:
            memory = await create_semantic_memory(
                db=db,
                tenant_id=tenant.id,
                user_id=user.id,
                content=content,
            )

            print(f"created semantic memory: {memory.id}")

            points = client.retrieve(
                collection_name="user_memory_semantic",
                ids=[str(memory.id)],
            )

            if points:
                print("Vector successfully stored in Qdrant")
            else:
                print("Vector not found in Qdrant")

        results = await retrieve_semantic_memory(
            tenant_id=tenant.id,
            user_id=user.id,
            query_text="What is the height of Mount Everest?",
            top_k=5
        )

        print("##### Query results #####")
        print(results)

        messages, tokens = build_context(
            system_prompt=system_prompt,
            structured_memory=user_preferences,
            semantic_memory=results,
            current_user_input=query,
            conversation_summary=None,
            recent_messages=None,
        )

        print(f"Message: {messages}")
        print(f"Lenght of messages: {len(messages)}")
        print(f"Tokens used: {tokens}")

        max_gen_tokens = (
            settings.reserved_output_tokens
            - settings.generation_safety_margin
        )

        response = await llm_provider.generate(
            messages=messages,
            max_tokens=max_gen_tokens
        )

        print("##### LLM Response #####")
        print(response)

        conversation = await create_conversation(
            db=db,
            tenant_id=tenant.id,
            user_id=user.id
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="highest mountain",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content=response,
        )

        recent_messages = await fetch_recent_messages(
            db=db,
            conversation_id=conversation.id,
            limit=10,
        )

        print("##### recent messages #####")
        print(recent_messages)



if __name__ == "__main__":
    asyncio.run(run_test())

# from app.llm.tokenizer import TokenCounter
# from app.core.config import settings

# counter = TokenCounter(settings.generation_model)

# print(counter.count_text("highest mountain in the world"))