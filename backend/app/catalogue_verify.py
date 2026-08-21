from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, text

from app.catalogue import CatalogueRow, diff_versions, import_catalogue
from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL")


def main() -> None:
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        v1_rows = [
            CatalogueRow("CMS-001", "Alpha", "Paracetamol 500mg tablet", "Tablet", "Medicine", "Analgesic", Decimal("10.000"), 2),
            CatalogueRow("CMS-002", "Beta", "Syringe 10cc", "Device", "Supply", "Consumable", Decimal("20.000"), 3),
            CatalogueRow("CMS-003", "Gamma", "Gauze 4x4", "Supply", "Supply", "Dressing", Decimal("5.000"), 4),
        ]
        v2_rows = [
            CatalogueRow("CMS-001", "Alpha", "Paracetamol 500mg tablet", "Tablet", "Medicine", "Analgesic", Decimal("12.000"), 2),
            CatalogueRow("CMS-002", "Delta", "Urinary catheter 16Fr", "Device", "Supply", "Catheter", Decimal("20.000"), 3),
            CatalogueRow("CMS-004", "Epsilon", "Gloves medium", "Supply", "Supply", "PPE", Decimal("8.000"), 4),
        ]

        v1_id, v1_created = import_catalogue(connection, rows=v1_rows, effective_date=date(2026, 7, 1), source_label="synthetic-cms-202607")
        if not v1_created:
            raise AssertionError("first catalogue import should create a version")

        v1_repeat_id, v1_repeat_created = import_catalogue(connection, rows=v1_rows, effective_date=date(2026, 7, 1), source_label="synthetic-cms-202607-repeat")
        if v1_repeat_created or v1_repeat_id != v1_id:
            raise AssertionError("identical catalogue re-import was not idempotent")

        v2_id, v2_created = import_catalogue(connection, rows=v2_rows, effective_date=date(2026, 8, 1), source_label="synthetic-cms-202608")
        if not v2_created:
            raise AssertionError("changed catalogue should create a new version")

        diff = diff_versions(connection, v1_id, v2_id)
        if diff["new_codes"] != ["CMS-004"] or diff["removed_codes"] != ["CMS-003"]:
            raise AssertionError(f"unexpected add/remove diff: {diff}")

        changed = {item["cms_code"]: item for item in diff["changed"]}
        if changed["CMS-001"]["fields"] != ["selling_price"]:
            raise AssertionError("price-only change classification failed")
        if changed["CMS-001"]["identity_shift_candidate"]:
            raise AssertionError("price-only change incorrectly flagged as identity shift")
        if not changed["CMS-002"]["identity_shift_candidate"]:
            raise AssertionError("reused code identity shift was not flagged")

        version_count = connection.execute(
            text("SELECT COUNT(*) FROM cms_catalogue_versions WHERE catalogue_version_id IN (:v1, :v2)"),
            {"v1": v1_id, "v2": v2_id},
        ).scalar_one()
        if version_count != 2:
            raise AssertionError("historical versions are not independently queryable")

        print("F5 synthetic catalogue verification PASS")
        print("hash_idempotency=pass version_history=pass add_remove_diff=pass price_diff=pass identity_shift_guard=pass")
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


if __name__ == "__main__":
    main()
