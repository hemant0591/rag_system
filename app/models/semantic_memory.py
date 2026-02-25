import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserMemorySemantic(Base):
    __tablename__ = "user_memory_semantic"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    importance_score: Mapped[float] = mapped_column(
        Float, default=1.0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc).isoformat()
    )

    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    user = relationship("User")