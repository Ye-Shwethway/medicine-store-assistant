from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0020_work_review_substrate"
down_revision = "0019_ai_workspace_attachments"
branch_labels = None
depends_on = None

ACTOR_TYPES = "'OWNER','USER','INTERNAL_AGENT','EXTERNAL_MCP_AGENT','SYSTEM'"
WORK_STATUSES = "'DRAFT','REVIEWING','WAITING_EXTERNAL','WAITING_OWNER','APPROVED','COMMITTABLE','COMMITTED','FAILED','CANCELLED'"


def upgrade() -> None:
    op.create_table(
        "workflow_work_items",
        sa.Column("work_item_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("work_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="DRAFT"),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("created_by_actor_type", sa.String(length=24), nullable=False),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=True),
        sa.Column("source_channel", sa.String(length=40), nullable=False, server_default="WEB"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agent_sessions.session_id", ondelete="SET NULL"), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"created_by_actor_type IN ({ACTOR_TYPES})", name="ck_work_item_actor_type"),
        sa.CheckConstraint(f"status IN ({WORK_STATUSES})", name="ck_work_item_status"),
    )
    op.create_index("ix_work_items_status_created", "workflow_work_items", ["status", "created_at"])
    op.create_index("ix_work_items_session", "workflow_work_items", ["session_id", "created_at"])

    op.create_table(
        "workflow_artifacts",
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("work_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_work_items.work_item_id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_type", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("actor_type", sa.String(length=24), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("supersedes_artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_artifacts.artifact_id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("version >= 1", name="ck_workflow_artifact_version"),
        sa.CheckConstraint(f"actor_type IN ({ACTOR_TYPES})", name="ck_workflow_artifact_actor_type"),
        sa.UniqueConstraint("work_item_id", "artifact_type", "version", name="uq_workflow_artifact_type_version"),
    )
    op.create_index("ix_workflow_artifacts_work_item", "workflow_artifacts", ["work_item_id", "created_at"])

    op.create_table(
        "workflow_reviews",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("work_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_work_items.work_item_id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False),
        sa.Column("reviewer_actor_type", sa.String(length=24), nullable=False),
        sa.Column("reviewer_actor_id", sa.String(length=128), nullable=True),
        sa.Column("verdict", sa.String(length=24), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("findings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("artifact_version >= 1", name="ck_workflow_review_artifact_version"),
        sa.CheckConstraint(f"reviewer_actor_type IN ({ACTOR_TYPES})", name="ck_workflow_review_actor_type"),
        sa.CheckConstraint("verdict IN ('APPROVE','NEEDS_FIX','REJECT','COMMENT')", name="ck_workflow_review_verdict"),
    )
    op.create_index("ix_workflow_reviews_work_item", "workflow_reviews", ["work_item_id", "created_at"])
    op.create_index("ix_workflow_reviews_artifact_version", "workflow_reviews", ["artifact_id", "artifact_version", "created_at"])

    op.create_table(
        "workflow_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("work_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_work_items.work_item_id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_type", sa.String(length=24), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"actor_type IN ({ACTOR_TYPES})", name="ck_workflow_event_actor_type"),
    )
    op.create_index("ix_workflow_events_work_item", "workflow_events", ["work_item_id", "created_at"])

    op.create_table(
        "workflow_attention_items",
        sa.Column("attention_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("work_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_work_items.work_item_id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("target_actor_type", sa.String(length=24), nullable=False),
        sa.Column("target_actor_id", sa.String(length=128), nullable=True),
        sa.Column("source_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_events.event_id", ondelete="SET NULL"), nullable=True),
        sa.Column("summary", sa.String(length=240), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"target_actor_type IN ({ACTOR_TYPES})", name="ck_workflow_attention_actor_type"),
        sa.CheckConstraint("status IN ('OPEN','ACKNOWLEDGED','RESOLVED')", name="ck_workflow_attention_status"),
        sa.CheckConstraint("category IN ('WAITING_EXTERNAL','WAITING_OWNER','WORKFLOW_FAILURE','DISAGREEMENT','COMPLETED')", name="ck_workflow_attention_category"),
    )
    op.create_index("ix_workflow_attention_open", "workflow_attention_items", ["status", "target_actor_type", "created_at"])
    op.create_index("ix_workflow_attention_work_item", "workflow_attention_items", ["work_item_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_workflow_attention_work_item", table_name="workflow_attention_items")
    op.drop_index("ix_workflow_attention_open", table_name="workflow_attention_items")
    op.drop_table("workflow_attention_items")
    op.drop_index("ix_workflow_events_work_item", table_name="workflow_events")
    op.drop_table("workflow_events")
    op.drop_index("ix_workflow_reviews_artifact_version", table_name="workflow_reviews")
    op.drop_index("ix_workflow_reviews_work_item", table_name="workflow_reviews")
    op.drop_table("workflow_reviews")
    op.drop_index("ix_workflow_artifacts_work_item", table_name="workflow_artifacts")
    op.drop_table("workflow_artifacts")
    op.drop_index("ix_work_items_session", table_name="workflow_work_items")
    op.drop_index("ix_work_items_status_created", table_name="workflow_work_items")
    op.drop_table("workflow_work_items")
