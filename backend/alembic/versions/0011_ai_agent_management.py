from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011_ai_agents"
down_revision = "0010_mcp_oauth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_agents",
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("call_name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("runtime_mode", sa.String(length=40), nullable=False, server_default="INTERNAL_MODEL"),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("capability_scopes", postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("ARRAY['mcp:read']::text[]")),
        sa.Column("location_scope", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{\"mode\":\"ALL_READABLE\"}'::jsonb")),
        sa.Column("authority_ceiling", sa.String(length=20), nullable=False, server_default="READ"),
        sa.Column("execution_policy", sa.String(length=32), nullable=False, server_default="DELEGATED"),
        sa.Column("confirmation_policy", sa.String(length=40), nullable=False, server_default="READ_ONLY"),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("state IN ('ACTIVE','DISABLED','REVOKED')", name="ck_ai_agents_state"),
        sa.CheckConstraint("runtime_mode IN ('INTERNAL_MODEL','EXTERNAL_MCP_CLIENT','EXTERNAL_ACTION_CLIENT','SYSTEM_AUTOMATION')", name="ck_ai_agents_runtime_mode"),
        sa.CheckConstraint("authority_ceiling IN ('READ','PROPOSE','WRITE','CONTROL')", name="ck_ai_agents_authority_ceiling"),
        sa.CheckConstraint("execution_policy IN ('DELEGATED','AUTONOMOUS')", name="ck_ai_agents_execution_policy"),
        sa.CheckConstraint("confirmation_policy IN ('READ_ONLY','PROPOSE_ONLY','CONFIRM_BEFORE_WRITE','AUTONOMOUS_PREAUTHORIZED')", name="ck_ai_agents_confirmation_policy"),
    )
    op.create_index(
        "uq_ai_agents_call_name_lower",
        "ai_agents",
        [sa.text("lower(call_name)")],
        unique=True,
        postgresql_where=sa.text("state <> 'REVOKED'"),
    )

    op.create_table(
        "ai_agent_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_name", sa.String(length=120), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="GROUP"),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("mode IN ('GROUP','COMPARE','REVIEW','DEBATE')", name="ck_ai_agent_sessions_mode"),
        sa.CheckConstraint("state IN ('OPEN','CLOSED')", name="ck_ai_agent_sessions_state"),
    )

    op.create_table(
        "ai_agent_session_participants",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agent_sessions.session_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.agent_id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("role_label", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("position >= 0", name="ck_ai_agent_session_participant_position"),
        sa.UniqueConstraint("session_id", "position", name="uq_ai_agent_session_position"),
    )


def downgrade() -> None:
    op.drop_table("ai_agent_session_participants")
    op.drop_table("ai_agent_sessions")
    op.drop_index("uq_ai_agents_call_name_lower", table_name="ai_agents")
    op.drop_table("ai_agents")
