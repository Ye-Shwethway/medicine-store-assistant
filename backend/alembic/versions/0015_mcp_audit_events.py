from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0015_mcp_audit"
down_revision = "0014_mcp_agent_bindings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operation_audit_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("actor_type", sa.String(length=24), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.agent_id", ondelete="SET NULL"), nullable=True),
        sa.Column("authorized_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
        sa.Column("client_source", sa.String(length=32), nullable=False),
        sa.Column("client_id", sa.String(length=160), nullable=True),
        sa.Column("runtime_type", sa.String(length=40), nullable=True),
        sa.Column("action_type", sa.String(length=160), nullable=False),
        sa.Column("capability_scope", sa.String(length=64), nullable=True),
        sa.Column("outcome", sa.String(length=24), nullable=False),
        sa.Column("safe_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("actor_type IN ('HUMAN','AI_AGENT','SYSTEM','INTEGRATION')", name="ck_operation_audit_actor_type"),
        sa.CheckConstraint("outcome IN ('SUCCESS','AUTHORIZED','REJECTED','FAILED')", name="ck_operation_audit_outcome"),
    )
    op.create_index("ix_operation_audit_occurred_at", "operation_audit_events", [sa.text("occurred_at DESC")])
    op.create_index("ix_operation_audit_agent_time", "operation_audit_events", ["agent_id", sa.text("occurred_at DESC")])
    op.create_index("ix_operation_audit_action_time", "operation_audit_events", ["action_type", sa.text("occurred_at DESC")])


def downgrade() -> None:
    op.drop_index("ix_operation_audit_action_time", table_name="operation_audit_events")
    op.drop_index("ix_operation_audit_agent_time", table_name="operation_audit_events")
    op.drop_index("ix_operation_audit_occurred_at", table_name="operation_audit_events")
    op.drop_table("operation_audit_events")
