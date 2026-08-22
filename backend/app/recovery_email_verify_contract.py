from __future__ import annotations

from sqlalchemy import text

from app.dashboard_auth import _engine


def main() -> None:
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT is_nullable
                    FROM information_schema.columns
                    WHERE table_name='recovery_email_verifications'
                      AND column_name='token_digest'
                    """
                )
            ).mappings().one()
            if row["is_nullable"] != "YES":
                raise RuntimeError("recovery verification token_digest must be nullable for secure cleanup")
        print("recovery_email_cleanup_contract=pass token_digest_nullable=yes")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
