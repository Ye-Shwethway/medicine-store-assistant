from __future__ import annotations

from alembic import op

revision = "0016_revoke_stale_chatgpt_oauth"
down_revision = "0015_mcp_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep the newest ACTIVE ChatGPT grant per user/client-name and revoke older
    # duplicates left behind by replacement ChatGPT app registrations.
    op.execute(
        """
        CREATE TEMP TABLE _msa_stale_chatgpt_grants ON COMMIT DROP AS
        WITH ranked AS (
            SELECT g.grant_id,
                   g.client_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY g.user_id, lower(c.client_name)
                       ORDER BY g.created_at DESC, g.grant_id DESC
                   ) AS rn
            FROM mcp_oauth_grants g
            JOIN mcp_oauth_clients c ON c.client_id = g.client_id
            WHERE g.state = 'ACTIVE'
              AND c.revoked_at IS NULL
              AND lower(c.client_name) = 'chatgpt'
        )
        SELECT grant_id, client_id
        FROM ranked
        WHERE rn > 1;

        DELETE FROM mcp_agent_bindings
        WHERE grant_id IN (SELECT grant_id FROM _msa_stale_chatgpt_grants);

        UPDATE mcp_oauth_tokens
        SET revoked_at = COALESCE(revoked_at, now())
        WHERE grant_id IN (SELECT grant_id FROM _msa_stale_chatgpt_grants);

        UPDATE mcp_oauth_grants
        SET state = 'REVOKED', updated_at = now()
        WHERE grant_id IN (SELECT grant_id FROM _msa_stale_chatgpt_grants);

        UPDATE mcp_oauth_clients c
        SET revoked_at = COALESCE(c.revoked_at, now())
        WHERE c.client_id IN (SELECT client_id FROM _msa_stale_chatgpt_grants)
          AND NOT EXISTS (
              SELECT 1
              FROM mcp_oauth_grants g
              WHERE g.client_id = c.client_id
                AND g.state = 'ACTIVE'
          );
        """
    )


def downgrade() -> None:
    # OAuth revocation is intentionally irreversible; restoring stale tokens/grants
    # would recreate credentials that the Owner explicitly asked to retire.
    pass
