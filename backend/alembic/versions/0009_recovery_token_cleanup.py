from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009_recovery_token_cleanup"
down_revision = "0008_email_recovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "recovery_email_verifications",
        "token_digest",
        existing_type=sa.String(length=64),
        nullable=True,
    )


def downgrade() -> None:
    # Expired/cancelled/consumed rows intentionally clear verifier material.
    # Delete those historical rows before restoring the old NOT NULL constraint.
    op.execute("DELETE FROM recovery_email_verifications WHERE token_digest IS NULL")
    op.alter_column(
        "recovery_email_verifications",
        "token_digest",
        existing_type=sa.String(length=64),
        nullable=False,
    )
