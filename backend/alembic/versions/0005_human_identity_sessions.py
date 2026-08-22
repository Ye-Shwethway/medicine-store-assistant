from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_identity"
down_revision = "0004_shadow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # F2 already established users/roles/user_roles. F7.2A evolves that
    # canonical foundation rather than creating a parallel identity store.
    op.drop_constraint("ck_users_status", "users", type_="check")
    op.alter_column("users", "login_name", new_column_name="username")
    op.alter_column("users", "status", new_column_name="state")
    op.execute("UPDATE users SET state = upper(state)")
    op.add_column(
        "users",
        sa.Column("credential_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_check_constraint(
        "ck_users_state",
        "users",
        "state IN ('PENDING','ACTIVE','DISABLED')",
    )
    op.create_check_constraint(
        "ck_users_credential_version",
        "users",
        "credential_version >= 1",
    )
    op.create_index("uq_users_username_ci", "users", [sa.text("lower(username)")], unique=True)
    op.create_index("uq_user_roles_one_role_per_user", "user_roles", ["user_id"], unique=True)

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
    op.create_index(
        "ix_user_sessions_user_active",
        "user_sessions",
        ["user_id", "expires_at", "revoked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_sessions_user_active", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("uq_user_roles_one_role_per_user", table_name="user_roles")
    op.drop_index("uq_users_username_ci", table_name="users")
    op.drop_constraint("ck_users_credential_version", "users", type_="check")
    op.drop_constraint("ck_users_state", "users", type_="check")
    op.drop_column("users", "credential_version")
    op.execute("UPDATE users SET state = lower(state)")
    op.alter_column("users", "state", new_column_name="status")
    op.alter_column("users", "username", new_column_name="login_name")
    op.create_check_constraint(
        "ck_users_status",
        "users",
        "status IN ('active','disabled','pending')",
    )
