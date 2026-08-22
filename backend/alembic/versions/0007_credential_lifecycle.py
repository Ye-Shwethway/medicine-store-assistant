from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_credential_lifecycle"
down_revision = "0006_user_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_requests",
        sa.Column(
            "password_reset_request_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="PENDING"),
        sa.Column("token_digest", sa.String(length=64), nullable=True, unique=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "issued_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('PENDING','ISSUED','CONSUMED','EXPIRED','CANCELLED')",
            name="ck_password_reset_requests_status",
        ),
    )
    op.create_index(
        "ix_password_reset_requests_status_requested",
        "password_reset_requests",
        ["status", "requested_at"],
    )
    op.create_index(
        "ix_password_reset_requests_user_requested",
        "password_reset_requests",
        ["user_id", "requested_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_requests_user_requested", table_name="password_reset_requests")
    op.drop_index("ix_password_reset_requests_status_requested", table_name="password_reset_requests")
    op.drop_table("password_reset_requests")
