from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.auth import require_read_scope
from app.db import normalize_database_url

DATABASE_URL = os.getenv("DATABASE_URL")
router = APIRouter(prefix="/v1", tags=["read-only"], dependencies=[Depends(require_read_scope)])


def _query(sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if not DATABASE_URL:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            rows = connection.execute(text(sql), params or {}).mappings().all()
            return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database read failed") from exc
    finally:
        engine.dispose()


@router.get("/products", summary="List local products")
def list_products(
    active_only: bool = True,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = _query(
        """
        SELECT product_id::text AS product_id,
               local_name,
               default_unit,
               active,
               display_order
        FROM products
        WHERE (:active_only = FALSE OR active = TRUE)
        ORDER BY display_order NULLS LAST, local_name, product_id
        LIMIT :limit OFFSET :offset
        """,
        {"active_only": active_only, "limit": limit, "offset": offset},
    )
    return {"items": rows, "count": len(rows), "limit": limit, "offset": offset}


@router.get("/lots", summary="List product lots")
def list_lots(
    product_id: str | None = None,
    active_only: bool = True,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = _query(
        """
        SELECT pl.lot_id::text AS lot_id,
               pl.product_id::text AS product_id,
               p.local_name AS product_name,
               p.default_unit,
               pl.expiry_date,
               pl.status
        FROM product_lots pl
        JOIN products p ON p.product_id = pl.product_id
        WHERE (:product_id IS NULL OR pl.product_id::text = :product_id)
          AND (:active_only = FALSE OR pl.status = 'active')
        ORDER BY p.display_order NULLS LAST, p.local_name, pl.expiry_date NULLS LAST, pl.lot_id
        LIMIT :limit OFFSET :offset
        """,
        {"product_id": product_id, "active_only": active_only, "limit": limit, "offset": offset},
    )
    return {"items": rows, "count": len(rows), "limit": limit, "offset": offset}


@router.get("/months", summary="List operating months")
def list_months(limit: int = Query(default=36, ge=1, le=120)) -> dict[str, Any]:
    rows = _query(
        """
        SELECT month_id::text AS month_id,
               year,
               month_number,
               status,
               opened_at,
               closed_at
        FROM inventory_months
        ORDER BY year DESC, month_number DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )
    return {"items": rows, "count": len(rows), "limit": limit}


@router.get("/catalogue/versions", summary="List CMS catalogue versions")
def list_catalogue_versions(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    rows = _query(
        """
        SELECT cv.catalogue_version_id::text AS catalogue_version_id,
               cv.effective_date,
               cv.source_label,
               cv.imported_at,
               COUNT(ci.catalogue_item_id) AS item_count
        FROM cms_catalogue_versions cv
        LEFT JOIN cms_catalogue_items ci
          ON ci.catalogue_version_id = cv.catalogue_version_id
        GROUP BY cv.catalogue_version_id, cv.effective_date, cv.source_label, cv.imported_at
        ORDER BY cv.imported_at DESC, cv.catalogue_version_id DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )
    return {"items": rows, "count": len(rows), "limit": limit}


@router.get("/catalogue/items", summary="List CMS catalogue items")
def list_catalogue_items(
    catalogue_version_id: str,
    q: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = _query(
        """
        SELECT catalogue_item_id::text AS catalogue_item_id,
               catalogue_version_id::text AS catalogue_version_id,
               cms_code,
               brand_name,
               description,
               form,
               type,
               class_name,
               selling_price
        FROM cms_catalogue_items
        WHERE catalogue_version_id::text = :catalogue_version_id
          AND (
            :q IS NULL
            OR cms_code ILIKE '%' || :q || '%'
            OR COALESCE(brand_name, '') ILIKE '%' || :q || '%'
            OR COALESCE(description, '') ILIKE '%' || :q || '%'
          )
        ORDER BY cms_code, catalogue_item_id
        LIMIT :limit OFFSET :offset
        """,
        {"catalogue_version_id": catalogue_version_id, "q": q, "limit": limit, "offset": offset},
    )
    return {"items": rows, "count": len(rows), "limit": limit, "offset": offset}


@router.get("/access/summary", summary="Read safe access-control summary")
def access_summary() -> dict[str, Any]:
    rows = _query(
        """
        SELECT
          (SELECT COUNT(*) FROM users WHERE status = 'active') AS active_users,
          (SELECT COUNT(*) FROM users WHERE status = 'disabled') AS disabled_users,
          (SELECT COUNT(*) FROM external_identities WHERE revoked_at IS NULL) AS active_external_identities,
          (SELECT COUNT(*) FROM service_principals WHERE status = 'active') AS active_service_principals,
          (SELECT COUNT(*) FROM service_credentials WHERE revoked_at IS NULL) AS active_service_credentials
        """
    )
    return rows[0] if rows else {
        "active_users": 0,
        "disabled_users": 0,
        "active_external_identities": 0,
        "active_service_principals": 0,
        "active_service_credentials": 0,
    }
