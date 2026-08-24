from __future__ import annotations

import os

from sqlalchemy import create_engine, text

from app.db import normalize_database_url


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            batch = connection.execute(
                text(
                    """
                    SELECT migration_batch_id::text AS migration_batch_id,
                           source_kind,
                           source_label,
                           source_hash,
                           row_count,
                           store_id::text AS store_id
                    FROM migration_batches
                    WHERE source_kind IN ('f6d_google_sheet_snapshot', 'google_sheet_snapshot')
                    ORDER BY CASE WHEN source_kind='f6d_google_sheet_snapshot' THEN 0 ELSE 1 END,
                             created_at DESC
                    LIMIT 1
                    """
                )
            ).mappings().one_or_none()
            if batch is None:
                raise SystemExit("no Google Sheet shadow batch found")

            counts = {
                row["classification"]: row["row_count"]
                for row in connection.execute(
                    text(
                        """
                        SELECT classification, COUNT(*) AS row_count
                        FROM migration_source_rows
                        WHERE migration_batch_id::text = :batch_id
                        GROUP BY classification
                        """
                    ),
                    {"batch_id": batch["migration_batch_id"]},
                ).mappings()
            }
            staged_count = sum(counts.values())
            if staged_count != batch["row_count"]:
                raise SystemExit(
                    f"shadow row-count mismatch: batch={batch['row_count']} staged={staged_count}"
                )

            if batch["source_kind"] == "f6d_google_sheet_snapshot" and not batch["store_id"]:
                raise SystemExit("F6D shadow batch is missing explicit store binding")

            print("F6D shadow read foundation verification PASS")
            print(
                "shadow_batch=pass provenance=pass classification_summary=pass "
                "migration_baseline_accepted=false database_canonical=false"
            )
            print(
                f"source_kind={batch['source_kind']} batch_id={batch['migration_batch_id']} "
                f"row_count={batch['row_count']} safe={counts.get('SAFE', 0)} "
                f"review={counts.get('REVIEW', 0)} conflict={counts.get('CONFLICT', 0)} "
                f"new_unmapped={counts.get('NEW_UNMAPPED', 0)}"
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
