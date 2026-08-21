from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_ledger"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_transactions",
        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "lot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_lots.lot_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("transaction_type", sa.String(length=32), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False, server_default="synthetic"),
        sa.Column("source_id", sa.String(length=191), nullable=True),
        sa.Column("operation_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column(
            "reversal_of_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_transactions.transaction_id", ondelete="RESTRICT"),
            nullable=True,
            unique=True,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "created_by_service_principal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_principals.service_principal_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_transactions_quantity_positive"),
        sa.CheckConstraint(
            "transaction_type IN ('OPENING_BALANCE','RECEIPT','USAGE','ADJUSTMENT_POSITIVE','ADJUSTMENT_NEGATIVE')",
            name="ck_inventory_transactions_type",
        ),
        sa.CheckConstraint(
            "NOT (created_by_user_id IS NOT NULL AND created_by_service_principal_id IS NOT NULL)",
            name="ck_inventory_transactions_single_actor",
        ),
        sa.CheckConstraint(
            "transaction_id IS DISTINCT FROM reversal_of_transaction_id",
            name="ck_inventory_transactions_not_self_reversal",
        ),
    )
    op.create_index(
        "ix_inventory_transactions_lot_effective_date",
        "inventory_transactions",
        ["lot_id", "effective_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_transactions_lot_effective_date", table_name="inventory_transactions")
    op.drop_table("inventory_transactions")
