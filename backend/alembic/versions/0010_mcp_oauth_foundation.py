from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010_mcp_oauth"
down_revision = "0009_recovery_token_cleanup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mcp_oauth_clients",
        sa.Column("client_id", sa.String(length=160), primary_key=True),
        sa.Column("client_name", sa.String(length=200), nullable=False),
        sa.Column("redirect_uris", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("grant_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("token_endpoint_auth_method", sa.String(length=40), nullable=False, server_default="none"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "mcp_oauth_grants",
        sa.Column("grant_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("client_id", sa.String(length=160), sa.ForeignKey("mcp_oauth_clients.client_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("capability_scopes", postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("ARRAY['mcp:read']::text[]")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("client_id", "user_id", name="uq_mcp_oauth_grant_client_user"),
    )

    op.create_table(
        "mcp_oauth_authorization_requests",
        sa.Column("request_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("client_id", sa.String(length=160), sa.ForeignKey("mcp_oauth_clients.client_id", ondelete="CASCADE"), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("oauth_scopes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("code_challenge", sa.String(length=128), nullable=False),
        sa.Column("code_challenge_method", sa.String(length=12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "mcp_oauth_authorization_codes",
        sa.Column("code_digest", sa.String(length=64), primary_key=True),
        sa.Column("grant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mcp_oauth_grants.grant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.String(length=160), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("oauth_scopes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("code_challenge", sa.String(length=128), nullable=False),
        sa.Column("code_challenge_method", sa.String(length=12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "mcp_oauth_tokens",
        sa.Column("token_digest", sa.String(length=64), primary_key=True),
        sa.Column("grant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mcp_oauth_grants.grant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.String(length=160), nullable=False),
        sa.Column("token_kind", sa.String(length=16), nullable=False),
        sa.Column("oauth_scopes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_mcp_oauth_tokens_grant_kind", "mcp_oauth_tokens", ["grant_id", "token_kind"])


def downgrade() -> None:
    op.drop_index("ix_mcp_oauth_tokens_grant_kind", table_name="mcp_oauth_tokens")
    op.drop_table("mcp_oauth_tokens")
    op.drop_table("mcp_oauth_authorization_codes")
    op.drop_table("mcp_oauth_authorization_requests")
    op.drop_table("mcp_oauth_grants")
    op.drop_table("mcp_oauth_clients")
