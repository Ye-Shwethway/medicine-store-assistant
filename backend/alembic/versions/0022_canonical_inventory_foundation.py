from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0022_inventory_foundation"
down_revision = "0021_review_orchestration_roles"
branch_labels = None
depends_on = None

LEGACY_MAIN_STORE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column(
            "store_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("store_type", sa.String(length=16), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("store_type IN ('MAIN','SUB')", name="ck_stores_type"),
    )
    op.create_index(
        "uq_stores_one_active_main",
        "stores",
        ["store_type"],
        unique=True,
        postgresql_where=sa.text("store_type = 'MAIN' AND active"),
    )

    stores = sa.table(
        "stores",
        sa.column("store_id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("store_type", sa.String),
        sa.column("active", sa.Boolean),
        sa.column("display_order", sa.Integer),
    )
    op.bulk_insert(
        stores,
        [
            {
                "store_id": LEGACY_MAIN_STORE_ID,
                "code": "MAIN",
                "name": "Main Store",
                "store_type": "MAIN",
                "active": True,
                "display_order": 1,
            }
        ],
    )

    op.add_column(
        "inventory_transactions",
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_inventory_transactions_store",
        "inventory_transactions",
        "stores",
        ["store_id"],
        ["store_id"],
        ondelete="RESTRICT",
    )
    op.execute(
        sa.text("UPDATE inventory_transactions SET store_id = :store_id WHERE store_id IS NULL").bindparams(
            store_id=LEGACY_MAIN_STORE_ID
        )
    )
    op.alter_column("inventory_transactions", "store_id", nullable=False)
    op.create_index(
        "ix_inventory_transactions_store_lot_effective_date",
        "inventory_transactions",
        ["store_id", "lot_id", "effective_date"],
        unique=False,
    )

    op.drop_constraint("ck_inventory_transactions_type", "inventory_transactions", type_="check")
    op.create_check_constraint(
        "ck_inventory_transactions_type",
        "inventory_transactions",
        "transaction_type IN ('OPENING_BALANCE','RECEIPT','USAGE','ADJUSTMENT_POSITIVE','ADJUSTMENT_NEGATIVE','TRANSFER_OUT','TRANSFER_IN')",
    )

    op.add_column(
        "migration_batches",
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_migration_batches_store",
        "migration_batches",
        "stores",
        ["store_id"],
        ["store_id"],
        ondelete="RESTRICT",
    )
    op.execute(
        sa.text(
            "UPDATE migration_batches SET store_id = :store_id "
            "WHERE store_id IS NULL AND source_kind IN ('google_sheet','excel','inventory','shadow')"
        ).bindparams(store_id=LEGACY_MAIN_STORE_ID)
    )
    op.create_index("ix_migration_batches_store", "migration_batches", ["store_id"], unique=False)

    op.create_table(
        "receipt_batches",
        sa.Column(
            "receipt_batch_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "destination_store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.store_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_transfer_no", sa.String(length=191), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("source_label", sa.String(length=255), nullable=True),
        sa.Column("source_hash", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="staged"),
        sa.Column("operation_id", sa.String(length=128), nullable=False, unique=True),
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
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('staged','reviewed','committed','reconciled','rejected')",
            name="ck_receipt_batches_status",
        ),
        sa.CheckConstraint(
            "NOT (created_by_user_id IS NOT NULL AND created_by_service_principal_id IS NOT NULL)",
            name="ck_receipt_batches_single_actor",
        ),
    )
    op.create_index(
        "ix_receipt_batches_store_effective_date",
        "receipt_batches",
        ["destination_store_id", "effective_date"],
        unique=False,
    )
    op.create_index("ix_receipt_batches_source_hash", "receipt_batches", ["source_hash"], unique=False)

    op.create_table(
        "receipt_lines",
        sa.Column(
            "receipt_line_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "receipt_batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("receipt_batches.receipt_batch_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_line_no", sa.Integer(), nullable=False),
        sa.Column(
            "lot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_lots.lot_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("quantity_received", sa.Numeric(18, 3), nullable=False),
        sa.Column("source_unit", sa.String(length=64), nullable=True),
        sa.Column("source_price", sa.Numeric(18, 3), nullable=True),
        sa.Column("source_code", sa.String(length=120), nullable=True),
        sa.Column("source_description", sa.Text(), nullable=True),
        sa.Column("source_expiry_date", sa.Date(), nullable=True),
        sa.Column("mapping_status", sa.String(length=24), nullable=False, server_default="PENDING"),
        sa.Column(
            "inventory_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_transactions.transaction_id", ondelete="RESTRICT"),
            nullable=True,
            unique=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity_received > 0", name="ck_receipt_lines_quantity_positive"),
        sa.CheckConstraint(
            "mapping_status IN ('PENDING','MAPPED','REVIEW','REJECTED')",
            name="ck_receipt_lines_mapping_status",
        ),
        sa.UniqueConstraint(
            "receipt_batch_id",
            "source_line_no",
            name="uq_receipt_lines_batch_source_line",
        ),
    )
    op.create_index("ix_receipt_lines_lot", "receipt_lines", ["lot_id"], unique=False)

    op.create_table(
        "inventory_transfers",
        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "source_store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.store_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "destination_store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.store_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="draft"),
        sa.Column("operation_id", sa.String(length=128), nullable=False, unique=True),
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
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("source_store_id <> destination_store_id", name="ck_inventory_transfers_distinct_stores"),
        sa.CheckConstraint(
            "status IN ('draft','reviewed','committed','cancelled')",
            name="ck_inventory_transfers_status",
        ),
        sa.CheckConstraint(
            "NOT (created_by_user_id IS NOT NULL AND created_by_service_principal_id IS NOT NULL)",
            name="ck_inventory_transfers_single_actor",
        ),
    )
    op.create_index(
        "ix_inventory_transfers_source_destination_date",
        "inventory_transfers",
        ["source_store_id", "destination_store_id", "effective_date"],
        unique=False,
    )

    op.create_table(
        "inventory_transfer_lines",
        sa.Column(
            "transfer_line_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_transfers.transfer_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_lots.lot_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column(
            "transfer_out_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_transactions.transaction_id", ondelete="RESTRICT"),
            nullable=True,
            unique=True,
        ),
        sa.Column(
            "transfer_in_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_transactions.transaction_id", ondelete="RESTRICT"),
            nullable=True,
            unique=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_transfer_lines_quantity_positive"),
        sa.UniqueConstraint("transfer_id", "lot_id", name="uq_inventory_transfer_lines_transfer_lot"),
    )
    op.create_index("ix_inventory_transfer_lines_lot", "inventory_transfer_lines", ["lot_id"], unique=False)

    op.create_table(
        "product_cms_mappings",
        sa.Column(
            "mapping_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.product_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "catalogue_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cms_catalogue_items.catalogue_item_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("cms_code_snapshot", sa.String(length=120), nullable=True),
        sa.Column("cms_name_snapshot", sa.String(length=255), nullable=True),
        sa.Column("mapping_status", sa.String(length=32), nullable=False),
        sa.Column("accepted_operational_price", sa.Numeric(18, 3), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "superseded_by_mapping_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_cms_mappings.mapping_id", ondelete="RESTRICT"),
            nullable=True,
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
        sa.Column("operation_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "mapping_status IN ('ACTIVE_MATCH','HISTORICAL_MATCH','REVIEW_REQUIRED','UNMAPPED','RECYCLED_CODE','CMS_DISCONTINUED','SUPERSEDED')",
            name="ck_product_cms_mappings_status",
        ),
        sa.CheckConstraint(
            "NOT (created_by_user_id IS NOT NULL AND created_by_service_principal_id IS NOT NULL)",
            name="ck_product_cms_mappings_single_actor",
        ),
        sa.CheckConstraint(
            "superseded_by_mapping_id IS NULL OR superseded_by_mapping_id <> mapping_id",
            name="ck_product_cms_mappings_not_self_superseded",
        ),
    )
    op.create_index(
        "uq_product_cms_mappings_one_active",
        "product_cms_mappings",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("mapping_status = 'ACTIVE_MATCH' AND valid_to IS NULL"),
    )
    op.create_index(
        "ix_product_cms_mappings_product_status",
        "product_cms_mappings",
        ["product_id", "mapping_status", "valid_from"],
        unique=False,
    )
    op.create_index(
        "ix_product_cms_mappings_catalogue_item",
        "product_cms_mappings",
        ["catalogue_item_id"],
        unique=False,
    )

    op.execute(
        """
        CREATE VIEW inventory_location_balances AS
        SELECT
            store_id,
            lot_id,
            CAST(SUM(
                CASE
                    WHEN transaction_type IN ('OPENING_BALANCE','RECEIPT','ADJUSTMENT_POSITIVE','TRANSFER_IN')
                        THEN quantity
                    WHEN transaction_type IN ('USAGE','ADJUSTMENT_NEGATIVE','TRANSFER_OUT')
                        THEN -quantity
                    ELSE 0
                END
            ) AS NUMERIC(18,3)) AS current_qty
        FROM inventory_transactions
        GROUP BY store_id, lot_id
        """
    )
    op.execute(
        """
        CREATE VIEW inventory_total_stock AS
        SELECT
            lot_id,
            CAST(SUM(current_qty) AS NUMERIC(18,3)) AS total_qty
        FROM inventory_location_balances
        GROUP BY lot_id
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS inventory_total_stock")
    op.execute("DROP VIEW IF EXISTS inventory_location_balances")

    op.drop_index("ix_product_cms_mappings_catalogue_item", table_name="product_cms_mappings")
    op.drop_index("ix_product_cms_mappings_product_status", table_name="product_cms_mappings")
    op.drop_index("uq_product_cms_mappings_one_active", table_name="product_cms_mappings")
    op.drop_table("product_cms_mappings")

    op.drop_index("ix_inventory_transfer_lines_lot", table_name="inventory_transfer_lines")
    op.drop_table("inventory_transfer_lines")
    op.drop_index("ix_inventory_transfers_source_destination_date", table_name="inventory_transfers")
    op.drop_table("inventory_transfers")

    op.drop_index("ix_receipt_lines_lot", table_name="receipt_lines")
    op.drop_table("receipt_lines")
    op.drop_index("ix_receipt_batches_source_hash", table_name="receipt_batches")
    op.drop_index("ix_receipt_batches_store_effective_date", table_name="receipt_batches")
    op.drop_table("receipt_batches")

    op.drop_index("ix_migration_batches_store", table_name="migration_batches")
    op.drop_constraint("fk_migration_batches_store", "migration_batches", type_="foreignkey")
    op.drop_column("migration_batches", "store_id")

    op.drop_constraint("ck_inventory_transactions_type", "inventory_transactions", type_="check")
    op.create_check_constraint(
        "ck_inventory_transactions_type",
        "inventory_transactions",
        "transaction_type IN ('OPENING_BALANCE','RECEIPT','USAGE','ADJUSTMENT_POSITIVE','ADJUSTMENT_NEGATIVE')",
    )
    op.drop_index("ix_inventory_transactions_store_lot_effective_date", table_name="inventory_transactions")
    op.drop_constraint("fk_inventory_transactions_store", "inventory_transactions", type_="foreignkey")
    op.drop_column("inventory_transactions", "store_id")

    op.drop_index("uq_stores_one_active_main", table_name="stores")
    op.drop_table("stores")
