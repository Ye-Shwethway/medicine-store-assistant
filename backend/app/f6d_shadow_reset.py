from __future__ import annotations

import argparse
import json
import os

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url

EXPECTED_BATCH_ID = "be13d127-5045-4284-a088-0a0b9b024d76"
EXPECTED_SOURCE_HASH = "cfe4c24201bbe9f519189572f0c4c1988a9785e6fb0ca3e8f9630f5ca0417192"
EXPECTED_SOURCE_LABEL = "google-sheet:1kATvZ3tfhwijd0wKx9m15QHNRIdmFnGdvbesVktpjsE"
EXPECTED_ROW_COUNT = 1646
MAIN_STORE_ID = "00000000-0000-0000-0000-000000000001"

MUST_BE_EMPTY = [
    "products",
    "product_lots",
    "inventory_transactions",
    "receipt_batches",
    "receipt_lines",
    "inventory_transfers",
    "inventory_transfer_lines",
    "product_cms_mappings",
    "cms_catalogue_versions",
    "cms_catalogue_items",
    "inventory_months",
]
CONTROL_TABLES = [
    "users",
    "user_roles",
    "service_principals",
    "ai_agents",
    "ai_workspace_conversations",
    "audit_events",
]


def _count(conn, table: str) -> int:
    return int(conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar_one())


def _control_counts(conn) -> dict[str, int]:
    tables = set(conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars())
    return {name: _count(conn, name) for name in CONTROL_TABLES if name in tables}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing mutation without --execute")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
            if revision != EXPECTED_MIGRATION:
                raise RuntimeError(f"migration drift: {revision!r} != {EXPECTED_MIGRATION!r}")

            for table in MUST_BE_EMPTY:
                count = _count(conn, table)
                if count != 0:
                    raise RuntimeError(f"refusing reset: {table} unexpectedly contains {count} rows")

            stores = conn.execute(text(
                "SELECT CAST(store_id AS text), code, store_type, active FROM stores ORDER BY code"
            )).all()
            expected_store = [(MAIN_STORE_ID, "MAIN", "MAIN", True)]
            actual_store = [(str(row[0]), row[1], row[2], bool(row[3])) for row in stores]
            if actual_store != expected_store:
                raise RuntimeError(f"refusing reset: unexpected store state {actual_store!r}")

            batches = conn.execute(text(
                "SELECT CAST(migration_batch_id AS text), source_hash, source_label, row_count, source_kind "
                "FROM migration_batches ORDER BY created_at"
            )).all()
            if len(batches) != 1:
                raise RuntimeError(f"refusing reset: expected exactly one legacy batch, found {len(batches)}")
            batch = batches[0]
            fingerprint = (str(batch[0]), batch[1], batch[2], int(batch[3]), batch[4])
            expected = (
                EXPECTED_BATCH_ID,
                EXPECTED_SOURCE_HASH,
                EXPECTED_SOURCE_LABEL,
                EXPECTED_ROW_COUNT,
                "google_sheet_snapshot",
            )
            if fingerprint != expected:
                raise RuntimeError(f"refusing reset: legacy batch fingerprint changed: {fingerprint!r}")

            source_rows = _count(conn, "migration_source_rows")
            if source_rows != EXPECTED_ROW_COUNT:
                raise RuntimeError(
                    f"refusing reset: expected {EXPECTED_ROW_COUNT} legacy source rows, found {source_rows}"
                )

            control_before = _control_counts(conn)
            deleted = conn.execute(
                text("DELETE FROM migration_batches WHERE migration_batch_id=CAST(:batch_id AS uuid)"),
                {"batch_id": EXPECTED_BATCH_ID},
            ).rowcount
            if deleted != 1:
                raise RuntimeError(f"expected to delete one legacy batch, deleted {deleted}")

            if _count(conn, "migration_batches") != 0 or _count(conn, "migration_source_rows") != 0:
                raise RuntimeError("post-reset staging state is not empty")
            control_after = _control_counts(conn)
            if control_after != control_before:
                raise RuntimeError(
                    f"control-plane counts changed during inventory reset: before={control_before} after={control_after}"
                )

            result = {
                "status": "RESET_COMPLETE",
                "migration": revision,
                "deleted_batch_id": EXPECTED_BATCH_ID,
                "deleted_source_rows": EXPECTED_ROW_COUNT,
                "inventory_batches_after": 0,
                "inventory_source_rows_after": 0,
                "main_store_preserved": True,
                "control_counts_before": control_before,
                "control_counts_after": control_after,
                "database_canonical": False,
                "migration_baseline_accepted": False,
            }
            print(json.dumps(result, sort_keys=True))
            print("f6d_shadow_reset=pass bounded_delete=true")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
