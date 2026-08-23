from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0018_ai_workspace_conversations"
down_revision = "0017_ai_workspace_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_workspace_conversations",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.agent_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("state IN ('ACTIVE','ARCHIVED')", name="ck_ai_workspace_conversation_state"),
    )
    op.create_index("ix_ai_workspace_conversations_owner_updated", "ai_workspace_conversations", ["owner_user_id", "updated_at"])

    op.create_table(
        "ai_workspace_messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_workspace_conversations.conversation_id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("runtime_provenance", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('USER','ASSISTANT')", name="ck_ai_workspace_message_role"),
    )
    op.create_index("ix_ai_workspace_messages_conversation_created", "ai_workspace_messages", ["conversation_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_workspace_messages_conversation_created", table_name="ai_workspace_messages")
    op.drop_table("ai_workspace_messages")
    op.drop_index("ix_ai_workspace_conversations_owner_updated", table_name="ai_workspace_conversations")
    op.drop_table("ai_workspace_conversations")
