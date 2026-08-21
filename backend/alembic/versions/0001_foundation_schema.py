from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("code", sa.String(length=32), primary_key=True),
        sa.Column("description", sa.String(length=255), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("code", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {"code": "OWNER", "description": "Full system authority"},
            {"code": "ADMIN", "description": "Operational administration"},
            {"code": "STAFF", "description": "Routine store operations"},
            {"code": "READ_ONLY", "description": "Read-only inventory and reports"},
        ],
    )

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("login_name", sa.String(length=120), nullable=True, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active','disabled','pending')", name="ck_users_status"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("role_code", sa.String(length=32), sa.ForeignKey("roles.code", ondelete="RESTRICT"), primary_key=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "external_identities",
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_subject", sa.String(length=191), nullable=False),
        sa.Column("provider_username", sa.String(length=191), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_external_identity_provider_subject"),
    )

    op.create_table(
        "service_principals",
        sa.Column("service_principal_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active','disabled')", name="ck_service_principals_status"),
    )

    op.create_table(
        "service_credentials",
        sa.Column("credential_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("service_principal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("service_principals.service_principal_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "products",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("local_name", sa.String(length=255), nullable=False),
        sa.Column("default_unit", sa.String(length=64), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "product_lots",
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active','depleted','expired','closed','review')", name="ck_product_lots_status"),
        sa.UniqueConstraint("product_id", "expiry_date", name="uq_product_lots_product_expiry"),
    )

    op.create_table(
        "inventory_months",
        sa.Column("month_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month_number", sa.SmallInteger(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("month_number BETWEEN 1 AND 12", name="ck_inventory_months_month_number"),
        sa.CheckConstraint("status IN ('open','closing','closed')", name="ck_inventory_months_status"),
        sa.UniqueConstraint("year", "month_number", name="uq_inventory_months_year_month"),
    )

    op.create_table(
        "cms_catalogue_versions",
        sa.Column("catalogue_version_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("source_hash", sa.String(length=128), nullable=True),
        sa.Column("source_label", sa.String(length=255), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cms_catalogue_versions_source_hash", "cms_catalogue_versions", ["source_hash"], unique=False)

    op.create_table(
        "cms_catalogue_items",
        sa.Column("catalogue_item_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("catalogue_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cms_catalogue_versions.catalogue_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cms_code", sa.String(length=120), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("form", sa.String(length=120), nullable=True),
        sa.Column("type", sa.String(length=120), nullable=True),
        sa.Column("class_name", sa.String(length=120), nullable=True),
        sa.Column("selling_price", sa.Numeric(18, 3), nullable=True),
        sa.UniqueConstraint("catalogue_version_id", "cms_code", name="uq_cms_catalogue_items_version_code"),
    )

    op.create_table(
        "audit_events",
        sa.Column("audit_event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("actor_service_principal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("service_principals.service_principal_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("client_channel", sa.String(length=48), nullable=False),
        sa.Column("operation_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "NOT (actor_user_id IS NOT NULL AND actor_service_principal_id IS NOT NULL)",
            name="ck_audit_events_single_primary_actor",
        ),
    )
    op.create_index("ix_audit_events_operation_id", "audit_events", ["operation_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_operation_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("cms_catalogue_items")
    op.drop_index("ix_cms_catalogue_versions_source_hash", table_name="cms_catalogue_versions")
    op.drop_table("cms_catalogue_versions")
    op.drop_table("inventory_months")
    op.drop_table("product_lots")
    op.drop_table("products")
    op.drop_table("service_credentials")
    op.drop_table("service_principals")
    op.drop_table("external_identities")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
