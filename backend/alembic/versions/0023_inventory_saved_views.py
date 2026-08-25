from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0023_inventory_saved_views"
down_revision = "0022_inventory_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_saved_views",
        sa.Column(
            "view_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_preset", sa.String(length=80), nullable=False),
        sa.Column("definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("length(btrim(name)) > 0", name="ck_inventory_saved_views_name_nonempty"),
    )
    op.create_index(
        "ix_inventory_saved_views_owner_updated",
        "inventory_saved_views",
        ["owner_user_id", "updated_at"],
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_inventory_saved_views_owner_name_ci "
        "ON inventory_saved_views (owner_user_id, lower(name))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_inventory_saved_views_owner_name_ci")
    op.drop_index("ix_inventory_saved_views_owner_updated", table_name="inventory_saved_views")
    op.drop_table("inventory_saved_views")
