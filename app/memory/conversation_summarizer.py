from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Message
from app.models.memory import ConversationSummary
from app.llm.tokenizer import TokenCounter
from app.llm.llm_provider import llm_provider
from app.core.config import settings

async def maybe_summarize_conversation(
    db: AsyncSession,
    tenant_id: str,
    conversation_id: str,
):
    counter = TokenCounter(settings.generation_model)

    # fetch all messages with conversation_id
    stmt = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id,
            )
        .order_by(Message.created_at.asc())
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    if not messages:
        return
    
    message_dicts = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    total_tokens = counter.count_messages(message_dicts)

    if total_tokens <= settings.max_recent_message_tokens:
        return # no summarization needed
    
    # preserve last N messages
    preserve_count = settings.recent_message_window
    to_summarize = messages[:-preserve_count]
    remaining_messages = messages[-preserve_count:]

    print("##### Remaining message count #####")
    print(len(remaining_messages))

    if not to_summarize:
        return
    
    summary_stmt = select(ConversationSummary).where(
        ConversationSummary.conversation_id == conversation_id,
        ConversationSummary.tenant_id == tenant_id,
    )

    existing = (await db.execute(summary_stmt)).scalar_one_or_none()

    conversation_text = ""

    if existing:
        conversation_text += f"Previous summary:\n{existing.summary_text}\n\n"

    conversation_text += "New conversation segment:\n"
    
    conversation_text += "\n".join(
        f"{msg.role.capitalize()}: {msg.content}"
        for msg in to_summarize
    )
    
    summary_prompt = [
        {
            "role": "system",
            "content": "Summarize the following conversation accurately and concisely.",
        },
        {
            "role": "user",
            "content": conversation_text,
        },
    ]

    summary_text = await llm_provider.generate(
        messages=summary_prompt,
        temperature=0.1,
        max_tokens=300,
    )

    print("##### summary text #####")
    print(summary_text)

    # upsert summary
    if existing:
        existing.summary_text = summary_text
    else:
        db.add(
            ConversationSummary(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                summary_text=summary_text,
            )
        )
    
    # Delete summarized messages
    ids_to_delete_stmt = (
        select(Message.id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(len(messages) - preserve_count)
    )

    result = await db.execute(ids_to_delete_stmt)
    ids_to_delete = [row[0] for row in result.all()]

    if ids_to_delete:
        # Step 2 — Delete by IDs
        delete_stmt = delete(Message).where(
            Message.id.in_(ids_to_delete)
        )
        await db.execute(delete_stmt)
    
    await db.commit()
