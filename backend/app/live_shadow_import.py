from __future__ import annotations

import json
import os

from sqlalchemy import create_engine

from app.db import normalize_database_url
from app.live_sheet_snapshot import configured_snapshot_read, stage_live_snapshot


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    snapshot = configured_snapshot_read()
    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            result = stage_live_snapshot(
                connection,
                spreadsheet_id=snapshot.spreadsheet_id,
                main_values=snapshot.main_values,
                usage_values=snapshot.usage_values,
            )
        print("F6B live workbook shadow snapshot staged")
        print(json.dumps(result, sort_keys=True))
        print("database_canonical=false source_authority=google_workbook")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
