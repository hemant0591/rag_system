"""add server default to created_at

Revision ID: 2ed634e93182
Revises: 4dedf18f27d9
Create Date: 2026-02-25 17:16:33.397295

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2ed634e93182'
down_revision: Union[str, None] = '4dedf18f27d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # conversation_summaries.updated_at
    op.alter_column(
        "conversation_summaries",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "conversation_summaries",
        "updated_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # conversations.created_at
    op.alter_column(
        "conversations",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "conversations",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # conversations.last_activity_at
    op.alter_column(
        "conversations",
        "last_activity_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "conversations",
        "last_activity_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # messages.created_at
    op.alter_column(
        "messages",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "messages",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # tenants.created_at
    op.alter_column(
        "tenants",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "tenants",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # user_memory_semantic.created_at
    op.alter_column(
        "user_memory_semantic",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "user_memory_semantic",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # user_memory_structured.created_at
    op.alter_column(
        "user_memory_structured",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "user_memory_structured",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # user_memory_structured.updated_at
    op.alter_column(
        "user_memory_structured",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "user_memory_structured",
        "updated_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # users.created_at
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

def downgrade() -> None:
    tables = [
        ("conversation_summaries", "updated_at"),
        ("conversations", "created_at"),
        ("conversations", "last_activity_at"),
        ("messages", "created_at"),
        ("tenants", "created_at"),
        ("user_memory_semantic", "created_at"),
        ("user_memory_structured", "created_at"),
        ("user_memory_structured", "updated_at"),
        ("users", "created_at"),
    ]

    for table, column in tables:
        op.alter_column(
            table,
            column,
            server_default=None,
        )
        op.alter_column(
            table,
            column,
            type_=postgresql.TIMESTAMP(),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )