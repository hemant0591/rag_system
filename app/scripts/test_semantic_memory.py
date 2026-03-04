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
from app.memory.conversation_summarizer import maybe_summarize_conversation

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

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""K2, often called "The Savage Mountain," is the world's second-highest peak at 8,611 meters (28,251 ft), located on the Pakistan-China border in the Karakoram Range. Renowned for being far more difficult and dangerous to climb than Everest, it has a steep, technical ascent with a ~20% fatality rate.
            Key Aspects of K2:
            Geography: Situated in the Gilgit-Baltistan region of Pakistan and Xinjiang, China.
            Climbing Difficulty: Known for extreme weather, steep ice/rock, and high fatality rates. It is ranked as one of the most dangerous mountains, with the "Bottleneck" being a critical, high-risk section.
            History: First summited on July 31, 1954, by Italian climbers Achille Compagnoni and Lino Lacedelli.
            Name Origin: Named K2 in 1856 by Col. T.G. Montgomerie during the Survey of India as the second peak measured in the Karakoram range. """,
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""Other Uses of "K2":
            Joomla Extension: A popular, free content construction kit for Joomla.
            Audio Speakers: Professional sound systems produced by L-Acoustics.
            Kimi K2.5: A multimodal vision language model for AI.
            The K2 (Drama): A 2016 South Korean television series.
            K2 Cafe: A restaurant in Maryland.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Nanga Parbat, at 8,126 meters (26,660 ft), is the ninth-highest mountain in the world and the western anchor of the Himalayas in Pakistan's Gilgit-Baltistan region. Known as the "Killer Mountain" due to its extreme danger and high fatality rate, it features the massive, 4,600m Rupal Face. It was first summited in 1953 by Hermann Buhl.
            Location: Situated in the western Himalayas in the Diamer District of Pakistan-administered Kashmir.
            "Naked Mountain": The name translates from Sanskrit (nagna parvata) and refers to its steep, rocky, and often ice-free southern face.
            Local Name: Known as Diamir, which translates to "king of the mountains" or "huge mountain".
            High Fatalities: It has a notorious reputation in mountaineering, with a high death-to-summit ratio, although it is also considered one of the most beautiful, isolated peaks.
            Major Faces: The mountain has three main faces: the northern Rakhiot face, the western Diamir face, and the southern Rupal face (the highest rock wall in the world).
            First Ascent: Austrian climber Hermann Buhl made the first successful ascent on July 3, 1953.
            Winter Ascent: It was one of the last 8,000-meter peaks to be scaled in winter, with the first successful winter climb on February 26, 2016, by Ali Sadpara, Alex Txikon, and Simone Moro.
            """,
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""Diamir Face (West): The most common, modern, and relatively safer route, often called the Kinshofer route.
            Rupal Face (South): The most dramatic and steep, rising 4,600 meters from the base.
            Rakhiot Face (North): The route taken by the 1953 expedition.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="user",
            content="""Mount Everest is Earth's highest mountain above sea level, standing at 8,848.86 meters (29,031.7 feet) high in the Mahalangur Himal sub-range of the Himalayas. Situated on the border between Nepal and China, its summit is the highest point on Earth, first officially reached by Edmund Hillary and Tenzing Norgay on May 29, 1953.
            Key details about Mount Everest include:
            Location: The peak sits directly on the international border between Nepal (Sagarmatha Zone) and China (Tibet Autonomous Region).
            Elevation: The 2020 joint survey by Nepal and China established the official height as 8,848.86 meters (29,031.7 feet).
            Names: Known as Sagarmatha in Nepal, Chomolungma in Tibet, and named Everest by the British in 1865 after Sir George Everest.
            Climbing: The mountain features two main routes: the Southeast Ridge from Nepal (standard route) and the Northeast Ridge from Tibet.
            Hazards: Climbers face extreme, life-threatening conditions, including thin air (the "death zone" above 8,000m), freezing temperatures, high winds, and the dangers of the Khumbu Icefall.
            Environment: The upper reaches of the mountain are too harsh for plant or animal life. The region is inhabited by the Sherpa people. 
            You can watch this video to see the risks involved in navigating the Khumbu Icefall:
            """
        )

        messages = await create_message(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            role="assistant",
            content="""First Ascent: Edmund Hillary and Tenzing Norgay first summited on May 29, 1953.
            First Solo Ascent: Reinhold Messner completed the first solo ascent of Mount Everest in 1980.""",
        )


        recent_messages = await fetch_recent_messages(
            db=db,
            conversation_id=conversation.id,
            limit=10,
        )

        print("##### recent messages #####")
        print(recent_messages)

        await maybe_summarize_conversation(
            db=db,
            tenant_id=tenant.id,
            conversation_id=conversation.id,
        )



if __name__ == "__main__":
    asyncio.run(run_test())

# from app.llm.tokenizer import TokenCounter
# from app.core.config import settings

# counter = TokenCounter(settings.generation_model)

# print(counter.count_text("highest mountain in the world"))