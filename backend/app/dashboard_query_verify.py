from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.shadow_read_api import DATABASE_URL
from app.db import normalize_database_url


def run(name: str, sql: str, params: dict | None = None) -> None:
    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            rows = connection.execute(text(sql), params or {}).mappings().all()
            print(f"{name}=pass rows={len(rows)}")
    except SQLAlchemyError as exc:
        print(f"{name}=fail error_type={type(exc).__name__} error={str(exc).replace(chr(10), ' ')[:800]}")
        raise
    finally:
        engine.dispose()


def main() -> None:
    run(
        "dashboard_overview_batch_query",
        """
        SELECT mb.migration_batch_id::text AS migration_batch_id,
               mb.source_kind,
               mb.source_label,
               mb.row_count,
               mb.created_at,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'SAFE') AS safe_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'REVIEW') AS review_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'CONFLICT') AS conflict_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'NEW_UNMAPPED') AS new_unmapped_count
        FROM migration_batches mb
        LEFT JOIN migration_source_rows msr ON msr.migration_batch_id = mb.migration_batch_id
        WHERE mb.source_kind = 'google_sheet_snapshot'
        GROUP BY mb.migration_batch_id, mb.source_kind, mb.source_label, mb.row_count, mb.created_at
        ORDER BY mb.created_at DESC, mb.migration_batch_id DESC
        LIMIT 1
        """,
    )

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            batch_id = connection.execute(text("SELECT migration_batch_id::text FROM migration_batches WHERE source_kind='google_sheet_snapshot' ORDER BY created_at DESC LIMIT 1")).scalar_one_or_none()
    finally:
        engine.dispose()

    run(
        "dashboard_overview_reasons_query",
        """
        SELECT classification,
               COALESCE(review_reason, '(none)') AS review_reason,
               COUNT(*) AS row_count
        FROM migration_source_rows
        WHERE (:migration_batch_id IS NULL OR migration_batch_id::text = :migration_batch_id)
          AND classification IN ('REVIEW', 'CONFLICT', 'NEW_UNMAPPED')
        GROUP BY classification, COALESCE(review_reason, '(none)')
        ORDER BY row_count DESC, classification, review_reason
        LIMIT 12
        """,
        {"migration_batch_id": batch_id},
    )


if __name__ == "__main__":
    main()
