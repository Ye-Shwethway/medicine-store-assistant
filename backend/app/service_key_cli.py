from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets

from sqlalchemy import create_engine, text

from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a scoped MSA service credential")
    parser.add_argument("--name", required=True)
    parser.add_argument("--scope", action="append", default=[])
    parser.add_argument("--raw", action="store_true", help="Print only the generated token")
    args = parser.parse_args()

    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL is required")

    scopes = args.scope or ["inventory:read"]
    token = "msa_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            service_principal_id = connection.execute(
                text(
                    """
                    INSERT INTO service_principals (name, status)
                    VALUES (:name, 'active')
                    ON CONFLICT (name)
                    DO UPDATE SET status = 'active', disabled_at = NULL
                    RETURNING service_principal_id
                    """
                ),
                {"name": args.name},
            ).scalar_one()

            connection.execute(
                text(
                    """
                    UPDATE service_credentials
                    SET revoked_at = now()
                    WHERE service_principal_id = :service_principal_id
                      AND revoked_at IS NULL
                    """
                ),
                {"service_principal_id": service_principal_id},
            )

            connection.execute(
                text(
                    """
                    INSERT INTO service_credentials
                      (service_principal_id, key_hash, scopes)
                    VALUES
                      (:service_principal_id, :key_hash, CAST(:scopes AS jsonb))
                    """
                ),
                {
                    "service_principal_id": service_principal_id,
                    "key_hash": key_hash,
                    "scopes": json.dumps(scopes),
                },
            )
    finally:
        engine.dispose()

    if args.raw:
        print(token)
        return

    print("Service credential created. Save this token now; it will not be shown again:")
    print(token)
    print("Scopes:", ", ".join(scopes))


if __name__ == "__main__":
    main()
