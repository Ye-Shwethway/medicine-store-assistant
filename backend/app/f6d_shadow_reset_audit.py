from __future__ import annotations

import json
import os

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url

INVENTORY_TABLES = [
    "migration_source_rows",
    "migration_batches",
    "inventory_transfer_lines",
    "inventory_transfers",
    "receipt_lines",
    "receipt_batches",
    "product_cms_mappings",
    "inventory_transactions",
    "product_lots",
    "products",
    "cms_catalogue_items",
    "cms_catalogue_versions",
    "inventory_months",
    "stores",
]

CONTROL_TABLES = [
    "users",
    "user_roles",
    "service_principals",
    "ai_agents",
    "provider_registry",
    "providers",
    "ai_workspace_conversations",
    "work_items",
    "audit_events",
]


def _tables(conn) -> set[str]:
    return set(
        conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        ).scalars()
    )


def _counts(conn, names: list[str], present: set[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for name in names:
        if name in present:
            out[name] = int(conn.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar_one())
    return out


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
            if revision != EXPECTED_MIGRATION:
                raise SystemExit(
                    f"refusing audit: migration={revision!r} expected={EXPECTED_MIGRATION!r}"
                )
            present = _tables(conn)
            result: dict[str, object] = {
                "mode": "READ_ONLY_AUDIT",
                "migration": revision,
                "database_canonical": False,
                "migration_baseline_accepted": False,
                "inventory_counts": _counts(conn, INVENTORY_TABLES, present),
                "control_counts": _counts(conn, CONTROL_TABLES, present),
            }

            if "stores" in present:
                result["stores"] = [dict(row._mapping) for row in conn.execute(text(
                    "SELECT CAST(store_id AS text) store_id, code, name, store_type, active "
                    "FROM stores ORDER BY display_order NULLS LAST, code"
                ))]

            if "migration_batches" in present:
                result["migration_batches"] = [dict(row._mapping) for row in conn.execute(text(
                    "SELECT CAST(migration_batch_id AS text) migration_batch_id, source_kind, "
                    "source_label, source_hash, status, row_count, CAST(store_id AS text) store_id, created_at "
                    "FROM migration_batches ORDER BY created_at"
                ))]

            if "inventory_transactions" in present:
                result["transaction_sources"] = [dict(row._mapping) for row in conn.execute(text(
                    "SELECT transaction_type, source_type, COUNT(*) row_count, SUM(quantity) quantity_sum "
                    "FROM inventory_transactions GROUP BY transaction_type, source_type "
                    "ORDER BY transaction_type, source_type"
                ))]

            if "cms_catalogue_versions" in present:
                result["cms_versions"] = [dict(row._mapping) for row in conn.execute(text(
                    "SELECT CAST(catalogue_version_id AS text) catalogue_version_id, effective_date, "
                    "source_hash, source_label, row_count, import_status, parser_version, imported_at "
                    "FROM cms_catalogue_versions ORDER BY imported_at"
                ))]

            if "product_cms_mappings" in present:
                result["cms_mapping_status_counts"] = [dict(row._mapping) for row in conn.execute(text(
                    "SELECT mapping_status, COUNT(*) row_count FROM product_cms_mappings "
                    "GROUP BY mapping_status ORDER BY mapping_status"
                ))]

            print(json.dumps(result, default=str, sort_keys=True))
            print("f6d_shadow_reset_audit=pass mutation=false")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
