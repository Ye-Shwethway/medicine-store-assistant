from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014_mcp_agent_bindings"
down_revision = "0013_saved_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mcp_agent_bindings",
        sa.Column(
            "grant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mcp_oauth_grants.grant_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_agents.agent_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_mcp_agent_bindings_agent_id", "mcp_agent_bindings", ["agent_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_mcp_agent_bindings_agent_id", table_name="mcp_agent_bindings")
    op.drop_table("mcp_agent_bindings")
