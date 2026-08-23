from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013_saved_models"
down_revision = "0012_providers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_provider_models", sa.Column("last_test_status", sa.String(length=20), nullable=False, server_default="UNTESTED"))
    op.add_column("ai_provider_models", sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ai_provider_models", sa.Column("last_test_error_code", sa.String(length=80), nullable=True))
    op.create_check_constraint(
        "ck_ai_provider_models_test_status",
        "ai_provider_models",
        "last_test_status IN ('UNTESTED','HEALTHY','ERROR')",
    )

    op.create_table(
        "ai_saved_provider_models",
        sa.Column("saved_model_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_providers.provider_id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_id", sa.String(length=240), nullable=False),
        sa.Column("display_name", sa.String(length=240), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("last_test_status", sa.String(length=20), nullable=False, server_default="HEALTHY"),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_test_error_code", sa.String(length=80), nullable=True),
        sa.Column("snapshot_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("state IN ('ACTIVE','STALE','DISABLED')", name="ck_ai_saved_provider_models_state"),
        sa.CheckConstraint("last_test_status IN ('UNTESTED','HEALTHY','ERROR')", name="ck_ai_saved_provider_models_test_status"),
        sa.UniqueConstraint("provider_id", "model_id", name="uq_ai_saved_provider_models_provider_model"),
    )
    op.create_index("ix_ai_saved_provider_models_provider", "ai_saved_provider_models", ["provider_id", "display_name"])

    op.create_table(
        "ai_agent_model_assignments",
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.agent_id", ondelete="CASCADE"), nullable=False),
        sa.Column("saved_model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_saved_provider_models.saved_model_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assignment_kind", sa.String(length=20), nullable=False, server_default="PRIMARY"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("assignment_kind IN ('PRIMARY','FALLBACK')", name="ck_ai_agent_model_assignments_kind"),
        sa.CheckConstraint("position >= 0", name="ck_ai_agent_model_assignments_position"),
        sa.UniqueConstraint("agent_id", "assignment_kind", "position", name="uq_ai_agent_model_assignment_position"),
    )
    op.create_index("ix_ai_agent_model_assignments_agent", "ai_agent_model_assignments", ["agent_id", "assignment_kind", "position"])


def downgrade() -> None:
    op.drop_index("ix_ai_agent_model_assignments_agent", table_name="ai_agent_model_assignments")
    op.drop_table("ai_agent_model_assignments")
    op.drop_index("ix_ai_saved_provider_models_provider", table_name="ai_saved_provider_models")
    op.drop_table("ai_saved_provider_models")
    op.drop_constraint("ck_ai_provider_models_test_status", "ai_provider_models", type_="check")
    op.drop_column("ai_provider_models", "last_test_error_code")
    op.drop_column("ai_provider_models", "last_tested_at")
    op.drop_column("ai_provider_models", "last_test_status")
