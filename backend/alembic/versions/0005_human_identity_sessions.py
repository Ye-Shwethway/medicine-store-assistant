from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_identity"
down_revision = "0004_shadow"
branch_labels = None
depends_on = None


HUMAN_ROLES = "'OWNER','ADMIN','STAFF','READ_ONLY'"
USER_STATES = "'PENDING','ACTIVE','DISABLED'"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("credential_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"role IN ({HUMAN_ROLES})", name="ck_users_role"),
        sa.CheckConstraint(f"state IN ({USER_STATES})", name="ck_users_state"),
        sa.CheckConstraint("credential_version >= 1", name="ck_users_credential_version"),
    )
    op.create_index("uq_users_username_ci", "users", [sa.text("lower(username)")], unique=True)
    op.create_index("ix_users_role_state", "users", ["role", "state"], unique=False)

    op.create_table(
        "user_sessions",
        sa.Column(
            "session_id",
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
        sa.Column("token_digest", sa.String(length=64), nullable=False, unique=True),
        sa.Column("credential_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("credential_version >= 1", name="ck_user_sessions_credential_version"),
    )
    op.create_index("ix_user_sessions_user_active", "user_sessions", ["user_id", "expires_at", "revoked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_sessions_user_active", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("ix_users_role_state", table_name="users")
    op.drop_index("uq_users_username_ci", table_name="users")
    op.drop_table("users")
