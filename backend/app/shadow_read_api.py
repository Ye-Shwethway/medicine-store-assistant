from __future__ import annotations

import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.auth import require_read_scope
from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL")
router = APIRouter(
    prefix="/v1/shadow",
    tags=["read-only", "shadow"],
    dependencies=[Depends(require_read_scope)],
)


def _engine():
    if not DATABASE_URL:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)


def _query(sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(text(sql), params or {}).mappings().all()
            return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database read failed") from exc
    finally:
        engine.dispose()


@router.get("/batches", summary="List shadow migration/test batches")
def list_shadow_batches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = _query(
        """
        SELECT mb.migration_batch_id::text AS migration_batch_id,
               mb.source_kind,
               mb.source_label,
               mb.source_hash,
               mb.status,
               mb.row_count,
               mb.created_at,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'SAFE') AS safe_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'REVIEW') AS review_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'CONFLICT') AS conflict_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'NEW_UNMAPPED') AS new_unmapped_count
        FROM migration_batches mb
        LEFT JOIN migration_source_rows msr
          ON msr.migration_batch_id = mb.migration_batch_id
        GROUP BY mb.migration_batch_id, mb.source_kind, mb.source_label, mb.source_hash,
                 mb.status, mb.row_count, mb.created_at
        ORDER BY mb.created_at DESC, mb.migration_batch_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": limit, "offset": offset},
    )
    return {
        "items": rows,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "migration_baseline_accepted": False,
        "database_canonical": False,
    }


@router.get("/batches/{migration_batch_id}", summary="Read one shadow batch summary")
def get_shadow_batch(migration_batch_id: str) -> dict[str, Any]:
    rows = _query(
        """
        SELECT mb.migration_batch_id::text AS migration_batch_id,
               mb.source_kind,
               mb.source_label,
               mb.source_hash,
               mb.status,
               mb.row_count,
               mb.created_at,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'SAFE') AS safe_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'REVIEW') AS review_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'CONFLICT') AS conflict_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'NEW_UNMAPPED') AS new_unmapped_count
        FROM migration_batches mb
        LEFT JOIN migration_source_rows msr
          ON msr.migration_batch_id = mb.migration_batch_id
        WHERE mb.migration_batch_id::text = :migration_batch_id
        GROUP BY mb.migration_batch_id, mb.source_kind, mb.source_label, mb.source_hash,
                 mb.status, mb.row_count, mb.created_at
        """,
        {"migration_batch_id": migration_batch_id},
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shadow batch not found")
    return {
        "batch": rows[0],
        "migration_baseline_accepted": False,
        "database_canonical": False,
    }


@router.get("/rows", summary="Inspect staged shadow source rows")
def list_shadow_rows(
    migration_batch_id: str | None = None,
    source_sheet: str | None = None,
    classification: Literal["SAFE", "REVIEW", "CONFLICT", "NEW_UNMAPPED"] | None = None,
    q: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = _query(
        """
        SELECT msr.migration_source_row_id::text AS migration_source_row_id,
               msr.migration_batch_id::text AS migration_batch_id,
               msr.source_sheet,
               msr.source_row_no,
               msr.source_row_hash,
               msr.classification,
               msr.review_reason,
               msr.payload,
               msr.created_at
        FROM migration_source_rows msr
        WHERE (:migration_batch_id IS NULL OR msr.migration_batch_id::text = :migration_batch_id)
          AND (:source_sheet IS NULL OR msr.source_sheet = :source_sheet)
          AND (:classification IS NULL OR msr.classification = :classification)
          AND (
            :q IS NULL
            OR COALESCE(msr.payload->>'item_name', '') ILIKE '%' || :q || '%'
            OR COALESCE(msr.payload->>'serial_code', '') ILIKE '%' || :q || '%'
            OR COALESCE(msr.review_reason, '') ILIKE '%' || :q || '%'
          )
        ORDER BY msr.created_at DESC, msr.source_sheet, msr.source_row_no, msr.migration_source_row_id
        LIMIT :limit OFFSET :offset
        """,
        {
            "migration_batch_id": migration_batch_id,
            "source_sheet": source_sheet,
            "classification": classification,
            "q": q,
            "limit": limit,
            "offset": offset,
        },
    )
    return {
        "items": rows,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "migration_baseline_accepted": False,
        "database_canonical": False,
    }


@router.get("/review-reasons", summary="Summarize shadow review reasons")
def shadow_review_reasons(migration_batch_id: str | None = None) -> dict[str, Any]:
    rows = _query(
        """
        SELECT classification,
               COALESCE(review_reason, '(none)') AS review_reason,
               COUNT(*) AS row_count
        FROM migration_source_rows
        WHERE (:migration_batch_id IS NULL OR migration_batch_id::text = :migration_batch_id)
          AND classification IN ('REVIEW', 'CONFLICT', 'NEW_UNMAPPED')
        GROUP BY classification, COALESCE(review_reason, '(none)')
        ORDER BY classification, row_count DESC, review_reason
        """,
        {"migration_batch_id": migration_batch_id},
    )
    return {
        "items": rows,
        "count": len(rows),
        "migration_baseline_accepted": False,
        "database_canonical": False,
    }
