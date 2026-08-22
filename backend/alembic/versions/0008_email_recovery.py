from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_email_recovery"
down_revision = "0007_credential_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("recovery_email", sa.String(length=320), nullable=True))
    op.add_column("users", sa.Column("recovery_email_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_recovery_email_lower", "users", [sa.text("lower(recovery_email)")], unique=False)

    op.create_table(
        "recovery_email_verifications",
        sa.Column(
            "verification_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("token_digest", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="ISSUED"),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('ISSUED','CONSUMED','EXPIRED','CANCELLED')", name="ck_recovery_email_verification_status"),
    )
    op.create_index("ix_recovery_email_verifications_user_status", "recovery_email_verifications", ["user_id", "status"])

    op.add_column("password_reset_requests", sa.Column("delivery_channel", sa.String(length=24), nullable=True))
    op.add_column("password_reset_requests", sa.Column("delivery_state", sa.String(length=24), nullable=True))
    op.add_column("password_reset_requests", sa.Column("delivery_provider_id", sa.String(length=160), nullable=True))
    op.add_column("password_reset_requests", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("password_reset_requests", "delivered_at")
    op.drop_column("password_reset_requests", "delivery_provider_id")
    op.drop_column("password_reset_requests", "delivery_state")
    op.drop_column("password_reset_requests", "delivery_channel")
    op.drop_index("ix_recovery_email_verifications_user_status", table_name="recovery_email_verifications")
    op.drop_table("recovery_email_verifications")
    op.drop_index("ix_users_recovery_email_lower", table_name="users")
    op.drop_column("users", "recovery_email_verified_at")
    op.drop_column("users", "recovery_email")
