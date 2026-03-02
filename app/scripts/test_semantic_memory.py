import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.identity import Tenant, User
from app.memory.semantic_memory_service import create_semantic_memory
from app.retrieval.vector_store import client
from app.memory.sematic_memory_retrieval import retrieve_semantic_memory
from app.core.logging import configure_logging

configure_logging()

queries = [
    "Ton 618 is the most massive black hole.",
    "Anatarctica is the coldest place on earth",
    "Death valley is the hottest place on earth",
    "Mt. Everest is the highest mountain on earth",
    "Aconcagua is the highest mountain in South America"
    "Denali is the highest mountain in North America",
    "Kilimanjaro is the highest mountain in Africa,",
    "Elbrus is the highest mountain in Europe",
    "Vinson Massif is the highest mountain in Antarctica",
    "Puncak Jaya is the highest mountain in Oceania/Australia"
    "Olympus Mons is the highest mountain in the solar system",
    "There are 2 trillion galaxies in the universe",
    "Andromeda is the nearest galaxy from milky way",
    "Milky way is in the Laniakea supercluster"
]

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
        query_text="highest mountain",
        top_k=5
    )

    print("##### Query results #####")
    print(results)

if __name__ == "__main__":
    asyncio.run(run_test())