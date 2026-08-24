from __future__ import annotations

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.db import EXPECTED_MIGRATION


def main() -> None:
    config = Config("alembic.ini")
    head = ScriptDirectory.from_config(config).get_current_head()
    if head != EXPECTED_MIGRATION:
        raise AssertionError(
            f"readiness migration drift: EXPECTED_MIGRATION={EXPECTED_MIGRATION!r}, alembic_head={head!r}"
        )
    print(f"readiness_contract=pass expected_migration={EXPECTED_MIGRATION}")


if __name__ == "__main__":
    main()
