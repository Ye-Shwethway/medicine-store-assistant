from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0021_review_orchestration_roles"
down_revision = "0020_work_review_substrate"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_session_participant_roles",
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_agent_sessions.session_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_agents.agent_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("orchestration_role", sa.String(length=24), nullable=False),
        sa.Column("display_label", sa.String(length=80), nullable=True),
        sa.Column("configured_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "orchestration_role IN ('ANALYST','REVIEWER','SYNTHESIZER')",
            name="ck_workflow_session_orchestration_role",
        ),
    )
    op.create_index(
        "ix_workflow_session_roles_session",
        "workflow_session_participant_roles",
        ["session_id", "orchestration_role", "agent_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_session_roles_session", table_name="workflow_session_participant_roles")
    op.drop_table("workflow_session_participant_roles")
