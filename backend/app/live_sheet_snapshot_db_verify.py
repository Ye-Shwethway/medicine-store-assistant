from __future__ import annotations

import os

from sqlalchemy import create_engine, text

from app.db import normalize_database_url
from app.live_sheet_snapshot import stage_live_snapshot


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    main_values = [
        [
            "No.",
            "Items",
            "Expiry Date",
            "Unit",
            "Remaining Stock",
            "Received Stock",
            "Stock Status Today",
            "This Month Usage",
            "CMS Price",
            "Price",
            "Remark",
            "Serial Code",
            "CS Name",
        ],
        [1, "10cc Syringe (1/2026)", 46023, "Pcs", 200, "", 100, 100, 1.4, 1.4, "", "S10100667", "Syringe 10cc"],
        [2, "Unmapped No Expiry", "", "Pcs", 10, 5, 15, 0, 3.0, 3.0, "", "Nil", ""],
        [3, "Recycled Product", "", "Bot", 20, 0, 20, 0, 10.7, 10.7, "Recycled ID", "S10100193", "Different Current CMS Name"],
    ]
    usage_header = [
        "No.",
        "Items",
        "Remaining Stock",
        "Received Stock",
        *[str(day) for day in range(1, 32)],
        "This Month Usage",
        "This Month Remaining",
        "Remark",
        "Expiry Date",
    ]
    usage_values = [
        usage_header,
        [1, "10cc Syringe (1/2026)", 200, "", 100, *([""] * 30), 100, 100, "", 46023],
        [2, "Unmapped No Expiry", 10, 5, *([""] * 31), 0, 15, "", ""],
        [3, "Recycled Product", 20, 0, *([""] * 31), 0, 20, "", ""],
    ]

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            first = stage_live_snapshot(
                connection,
                spreadsheet_id="ci-f6d-live-sheet",
                main_values=main_values,
                usage_values=usage_values,
                store_code="MAIN",
            )
            if not first["created"]:
                raise AssertionError("first staging pass must create a batch")
            if first["classification_counts"] != {
                "SAFE": 4,
                "REVIEW": 1,
                "CONFLICT": 0,
                "NEW_UNMAPPED": 1,
            }:
                raise AssertionError(first["classification_counts"])
            if first["mapping_hint_counts"] != {
                "ACTIVE_MATCH": 1,
                "UNMAPPED": 1,
                "RECYCLED_CODE": 1,
            }:
                raise AssertionError(first["mapping_hint_counts"])

            second = stage_live_snapshot(
                connection,
                spreadsheet_id="ci-f6d-live-sheet",
                main_values=main_values,
                usage_values=usage_values,
                store_code="MAIN",
            )
            if second["created"] or second["migration_batch_id"] != first["migration_batch_id"]:
                raise AssertionError("snapshot replay must reuse the same migration batch")

            batch_id = first["migration_batch_id"]
            batch = connection.execute(
                text(
                    """
                    SELECT b.source_kind, b.source_hash, b.row_count, s.code AS store_code
                    FROM migration_batches b
                    JOIN stores s ON s.store_id = b.store_id
                    WHERE b.migration_batch_id = CAST(:batch_id AS uuid)
                    """
                ),
                {"batch_id": batch_id},
            ).one()
            if batch.source_kind != "f6d_google_sheet_snapshot" or batch.store_code != "MAIN" or batch.row_count != 6:
                raise AssertionError(batch)

            source_rows = connection.execute(
                text(
                    """
                    SELECT source_sheet, source_row_no, classification, review_reason, payload
                    FROM migration_source_rows
                    WHERE migration_batch_id = CAST(:batch_id AS uuid)
                    ORDER BY source_sheet, source_row_no
                    """
                ),
                {"batch_id": batch_id},
            ).all()
            if len(source_rows) != 6:
                raise AssertionError(f"expected 6 staged rows, got {len(source_rows)}")

            syringe = next(
                row for row in source_rows
                if row.source_sheet == "Main Stock" and row.source_row_no == 2
            )
            if syringe.payload["product_name_candidate"] != "10cc Syringe":
                raise AssertionError(syringe.payload)
            if syringe.payload["expiry_date"] != "2026-01-01":
                raise AssertionError(syringe.payload)
            if syringe.payload["mapping_hint"] != "ACTIVE_MATCH":
                raise AssertionError(syringe.payload)

            recycled = next(
                row for row in source_rows
                if row.source_sheet == "Main Stock" and row.source_row_no == 4
            )
            if recycled.classification != "REVIEW" or recycled.payload["mapping_hint"] != "RECYCLED_CODE":
                raise AssertionError((recycled.classification, recycled.payload))

            # CI fixture cleanup: the proof is read-only with respect to real source
            # data and leaves the shared migration DB clean for downgrade/re-upgrade.
            connection.execute(
                text("DELETE FROM migration_source_rows WHERE migration_batch_id = CAST(:batch_id AS uuid)"),
                {"batch_id": batch_id},
            )
            connection.execute(
                text("DELETE FROM migration_batches WHERE migration_batch_id = CAST(:batch_id AS uuid)"),
                {"batch_id": batch_id},
            )

        print("F6D live snapshot DB staging verification PASS")
        print("main_store_binding=pass normalization=pass mapping_hints=pass replay_idempotency=pass")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
