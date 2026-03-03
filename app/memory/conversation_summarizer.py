from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Message
from app.models.memory import ConversationSummary
from app.llm.tokenizer import TokenCounter
from app.llm.llm_provider import llm_provider
from app.core.config import settings

async def maybe_summarize_conversation(
    db: AsyncSession,
    conversation_id: str,
):
    counter = TokenCounter(settings.generation_model)

    # fetch all messages with conversation_id
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    if not messages:
        return
    
    message_dicts = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    total_tokens = counter.count_messages(message_dicts)

    if total_tokens <= settings.max_recent_message_tokens:
        return # no summarization needed
    
    # preserve last N messages
    preserve_count = settings.recent_message_window
    to_summarize = messages[:-preserve_count]

    if not to_summarize:
        return
    
    summary_prompt = [
        {
            "role": "system",
            "content": "Summarize the following conversation accurately and concisely.",
        },
        {
            "role": "user",
            "content": str(to_summarize),
        },
    ]

    summary_text = await llm_provider.generate(
        messages=summary_prompt,
        temperature=0.1,
        max_tokens=300,
    )

    # upsert summary
    summary_stmt = select(ConversationSummary).where(
        ConversationSummary.conversation_id == conversation_id
    )

    existing = (await db.execute(summary_stmt)).scalar_one_or_none()

    if existing:
        existing.summary_text = summary_text
    else:
        db.add(
            ConversationSummary(
                conversation_id=conversation_id,
                summary_text=summary_text,
            )
        )
    
    # Delete summarized messages
    delete_stmt = delete(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).limit(
        len(messages) - preserve_count
    )

    await db.execute(delete_stmt)
    await db.commit()
