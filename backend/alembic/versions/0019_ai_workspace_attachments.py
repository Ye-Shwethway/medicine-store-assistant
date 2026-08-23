from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0019_ai_workspace_attachments"
down_revision = "0018_ai_workspace_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_workspace_attachments",
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_workspace_conversations.conversation_id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_workspace_messages.message_id", ondelete="CASCADE"), nullable=True),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("content_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('IMAGE','FILE')", name="ck_ai_workspace_attachment_kind"),
        sa.CheckConstraint("state IN ('PENDING','BOUND')", name="ck_ai_workspace_attachment_state"),
        sa.CheckConstraint("byte_size >= 0 AND byte_size <= 8388608", name="ck_ai_workspace_attachment_size"),
    )
    op.create_index(
        "ix_ai_workspace_attachments_conversation_state",
        "ai_workspace_attachments",
        ["conversation_id", "state", "created_at"],
    )
    op.create_index(
        "ix_ai_workspace_attachments_message",
        "ai_workspace_attachments",
        ["message_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_workspace_attachments_message", table_name="ai_workspace_attachments")
    op.drop_index("ix_ai_workspace_attachments_conversation_state", table_name="ai_workspace_attachments")
    op.drop_table("ai_workspace_attachments")
