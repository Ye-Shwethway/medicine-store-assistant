from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0017_ai_workspace_access"
down_revision = "0016_revoke_stale_chatgpt_oauth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_workspace_settings",
        sa.Column("settings_id", sa.SmallInteger(), primary_key=True, server_default="1"),
        sa.Column("non_owner_chat_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("settings_id = 1", name="ck_ai_workspace_settings_singleton"),
    )
    op.execute("INSERT INTO ai_workspace_settings (settings_id, non_owner_chat_enabled) VALUES (1, false)")

    op.create_table(
        "ai_workspace_user_access",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("chat_entitlement", sa.String(length=16), nullable=False, server_default="INHERIT"),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("chat_entitlement IN ('INHERIT','ALLOW','BLOCK')", name="ck_ai_workspace_user_access_entitlement"),
    )


def downgrade() -> None:
    op.drop_table("ai_workspace_user_access")
    op.drop_table("ai_workspace_settings")
