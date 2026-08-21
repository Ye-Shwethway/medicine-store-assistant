from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.getenv("DATABASE_URL")


def database_readiness() -> dict[str, object]:
    if not DATABASE_URL:
        return {"ok": False, "database": "unconfigured", "migration": "unknown"}

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            ).scalar_one_or_none()
        return {
            "ok": revision is not None,
            "database": "reachable",
            "migration": revision or "missing",
        }
    except SQLAlchemyError:
        return {"ok": False, "database": "unreachable_or_unmigrated", "migration": "unknown"}
    finally:
        engine.dispose()
