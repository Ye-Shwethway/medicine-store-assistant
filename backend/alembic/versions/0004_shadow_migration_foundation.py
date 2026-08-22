from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_shadow"
down_revision = "0003_catalogue"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "migration_batches",
        sa.Column(
            "migration_batch_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("source_kind", sa.String(length=64), nullable=False),
        sa.Column("source_label", sa.String(length=255), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="staged"),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('staged','classified','verified','rejected')",
            name="ck_migration_batches_status",
        ),
    )

    op.create_table(
        "migration_source_rows",
        sa.Column(
            "migration_source_row_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "migration_batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("migration_batches.migration_batch_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_sheet", sa.String(length=64), nullable=False),
        sa.Column("source_row_no", sa.Integer(), nullable=False),
        sa.Column("source_row_hash", sa.String(length=64), nullable=False),
        sa.Column("classification", sa.String(length=64), nullable=False),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "migration_batch_id",
            "source_sheet",
            "source_row_no",
            name="uq_migration_source_rows_batch_sheet_row",
        ),
        sa.UniqueConstraint(
            "migration_batch_id",
            "source_row_hash",
            name="uq_migration_source_rows_batch_hash",
        ),
    )
    op.create_index(
        "ix_migration_source_rows_batch_classification",
        "migration_source_rows",
        ["migration_batch_id", "classification"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_migration_source_rows_batch_classification",
        table_name="migration_source_rows",
    )
    op.drop_table("migration_source_rows")
    op.drop_table("migration_batches")
