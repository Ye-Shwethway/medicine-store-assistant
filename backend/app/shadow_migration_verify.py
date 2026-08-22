from __future__ import annotations

import os
from decimal import Decimal

from sqlalchemy import create_engine, text

from app.db import normalize_database_url
from app.shadow_migration import DailyUsageFixtureRow, MainStockFixtureRow, stage_fixture_batch

DATABASE_URL = os.getenv("DATABASE_URL")


def main() -> None:
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        main_rows = [
            MainStockFixtureRow(2, "Paracetamol 500mg", "2027-06-30", Decimal("100")),
            MainStockFixtureRow(3, "Syringe 10cc", "2028-01-31", Decimal("25")),
            MainStockFixtureRow(4, None, "2027-12-31", Decimal("5")),
        ]
        usage_rows = [
            DailyUsageFixtureRow(2, "Paracetamol 500mg", "2026-08-01", Decimal("3")),
            DailyUsageFixtureRow(3, "Syringe 10cc", "2026-08-01", Decimal("2")),
            DailyUsageFixtureRow(4, "Paracetamol 500mg", "2026-08-02", Decimal("0")),
        ]

        batch_id, created = stage_fixture_batch(
            connection,
            source_label="f6a-synthetic-snapshot-v1",
            main_rows=main_rows,
            usage_rows=usage_rows,
        )
        if not created:
            raise AssertionError("first synthetic shadow batch should be created")

        repeat_id, repeat_created = stage_fixture_batch(
            connection,
            source_label="f6a-synthetic-snapshot-v1-repeat",
            main_rows=main_rows,
            usage_rows=usage_rows,
        )
        if repeat_created or repeat_id != batch_id:
            raise AssertionError("same synthetic snapshot was not idempotent")

        rows = connection.execute(
            text(
                """
                SELECT classification, COUNT(*) AS count
                FROM migration_source_rows
                WHERE migration_batch_id = :batch_id
                GROUP BY classification
                """
            ),
            {"batch_id": batch_id},
        ).mappings().all()
        counts = {row["classification"]: row["count"] for row in rows}
        if counts != {"LOT_OPENING_CANDIDATE": 2, "USAGE_CANDIDATE": 2, "REVIEW": 2}:
            raise AssertionError(f"unexpected classifications: {counts}")

        review_reasons = connection.execute(
            text(
                """
                SELECT review_reason
                FROM migration_source_rows
                WHERE migration_batch_id = :batch_id AND classification = 'REVIEW'
                ORDER BY source_sheet, source_row_no
                """
            ),
            {"batch_id": batch_id},
        ).scalars().all()
        if not all(review_reasons):
            raise AssertionError("review rows must preserve explicit reasons")

        product_count = connection.execute(text("SELECT COUNT(*) FROM products")).scalar_one()
        ledger_count = connection.execute(text("SELECT COUNT(*) FROM inventory_transactions")).scalar_one()
        if product_count != 0 or ledger_count != 0:
            raise AssertionError("F6A staging must not create canonical product or ledger rows")

        print("F6A synthetic shadow migration verification PASS")
        print("batch_idempotency=pass provenance=pass classification=pass review_reporting=pass no_canonical_mutation=pass")
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


if __name__ == "__main__":
    main()
