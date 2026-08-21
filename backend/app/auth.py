from __future__ import annotations

import hashlib
import os

from fastapi import Header, HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL")


def _credential_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def require_read_scope(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer credential required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or not DATABASE_URL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential")

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT sp.service_principal_id::text AS service_principal_id,
                           sp.name,
                           sc.scopes
                    FROM service_credentials sc
                    JOIN service_principals sp
                      ON sp.service_principal_id = sc.service_principal_id
                    WHERE sc.key_hash = :key_hash
                      AND sc.revoked_at IS NULL
                      AND sp.status = 'active'
                    LIMIT 1
                    """
                ),
                {"key_hash": _credential_hash(token)},
            ).mappings().first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authorization backend unavailable") from exc
    finally:
        engine.dispose()

    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential")

    scopes = row["scopes"] or []
    if "inventory:read" not in scopes and "*" not in scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credential lacks inventory:read scope")

    return {
        "service_principal_id": row["service_principal_id"],
        "service_principal_name": row["name"],
    }
