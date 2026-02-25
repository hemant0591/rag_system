import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )

    summary_text: Mapped[str] = mapped_column(Text, nullable=False)

    last_message_id_processed: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    version: Mapped[int] = mapped_column(Integer, default=1)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc).isoformat()
    )

    conversation = relationship("Conversation")