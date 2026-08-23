from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012_providers"
down_revision = "0011_ai_agents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_providers",
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("provider_kind", sa.String(length=40), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("credential_ref", sa.String(length=160), nullable=True),
        sa.Column("compatibility_mode", sa.String(length=32), nullable=False, server_default="OPENAI_MODELS"),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="DISABLED"),
        sa.Column("last_connection_status", sa.String(length=20), nullable=False, server_default="UNTESTED"),
        sa.Column("last_connection_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_model_fetch_status", sa.String(length=20), nullable=False, server_default="NEVER"),
        sa.Column("last_model_fetch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=80), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("provider_kind IN ('OPENAI','GEMINI','OPENROUTER','NANOGPT','OPENAI_COMPATIBLE')", name="ck_ai_providers_kind"),
        sa.CheckConstraint("compatibility_mode IN ('OPENAI_MODELS','GEMINI_NATIVE_MODELS')", name="ck_ai_providers_compatibility"),
        sa.CheckConstraint("state IN ('ENABLED','DISABLED')", name="ck_ai_providers_state"),
        sa.CheckConstraint("last_connection_status IN ('UNTESTED','HEALTHY','ERROR')", name="ck_ai_providers_connection_status"),
        sa.CheckConstraint("last_model_fetch_status IN ('NEVER','SUCCESS','ERROR')", name="ck_ai_providers_fetch_status"),
    )
    op.create_index("uq_ai_providers_display_name_lower", "ai_providers", [sa.text("lower(display_name)")], unique=True)

    op.create_table(
        "ai_provider_models",
        sa.Column("provider_model_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_providers.provider_id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_id", sa.String(length=240), nullable=False),
        sa.Column("display_name", sa.String(length=240), nullable=False),
        sa.Column("availability", sa.String(length=20), nullable=False, server_default="AVAILABLE"),
        sa.Column("supports_text", sa.Boolean(), nullable=True),
        sa.Column("supports_vision", sa.Boolean(), nullable=True),
        sa.Column("supports_tools", sa.Boolean(), nullable=True),
        sa.Column("supports_structured_output", sa.Boolean(), nullable=True),
        sa.Column("context_window", sa.BigInteger(), nullable=True),
        sa.Column("max_output_tokens", sa.BigInteger(), nullable=True),
        sa.Column("provider_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("availability IN ('AVAILABLE','UNAVAILABLE','UNKNOWN')", name="ck_ai_provider_models_availability"),
        sa.UniqueConstraint("provider_id", "model_id", name="uq_ai_provider_models_provider_model"),
    )
    op.create_index("ix_ai_provider_models_provider", "ai_provider_models", ["provider_id", "display_name"])


def downgrade() -> None:
    op.drop_index("ix_ai_provider_models_provider", table_name="ai_provider_models")
    op.drop_table("ai_provider_models")
    op.drop_index("uq_ai_providers_display_name_lower", table_name="ai_providers")
    op.drop_table("ai_providers")
