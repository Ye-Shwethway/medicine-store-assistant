from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from app.dashboard_auth import (
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    authenticate_user,
    create_session_token,
    dashboard_auth_configured,
    require_dashboard_session,
    require_owner_session,
    resolve_session_token,
    revoke_session_token,
)
from app.shadow_read_api import _query

router = APIRouter(tags=["dashboard"])
ASSET_DIR = Path(__file__).resolve().parent / "dashboard_assets"
ALLOWED_ASSETS = {"dashboard.css", "dashboard.js"}
DASHBOARD_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "font-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "form-action 'self'"
)


class LoginRequest(BaseModel):
    username: str
    password: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _latest_google_snapshot_batch_id() -> str | None:
    rows = _query(
        """
        SELECT migration_batch_id::text AS migration_batch_id
        FROM migration_batches
        WHERE source_kind = 'google_sheet_snapshot'
        ORDER BY created_at DESC, migration_batch_id DESC
        LIMIT 1
        """
    )
    return rows[0]["migration_batch_id"] if rows else None


def _dashboard_row_where(
    *,
    migration_batch_id: str | None,
    source_sheet: str | None = None,
    classification: str | None = None,
    q: str | None = None,
) -> tuple[str, dict[str, Any]]:
    clauses: list[str] = []
    params: dict[str, Any] = {}
    if migration_batch_id is not None:
        clauses.append("msr.migration_batch_id::text = :migration_batch_id")
        params["migration_batch_id"] = migration_batch_id
    if source_sheet is not None:
        clauses.append("msr.source_sheet = :source_sheet")
        params["source_sheet"] = source_sheet
    if classification is not None:
        clauses.append("msr.classification = :classification")
        params["classification"] = classification
    if q is not None:
        clauses.append(
            "("
            "COALESCE(msr.payload->>'item_name', '') ILIKE '%' || :q || '%' "
            "OR COALESCE(msr.payload->>'serial_code', '') ILIKE '%' || :q || '%' "
            "OR COALESCE(msr.review_reason, '') ILIKE '%' || :q || '%'"
            ")"
        )
        params["q"] = q
    return (" AND ".join(clauses) if clauses else "TRUE"), params


@router.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/dashboard", include_in_schema=False)
def dashboard_shell() -> FileResponse:
    response = FileResponse(ASSET_DIR / "dashboard.html", media_type="text/html")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = DASHBOARD_CSP
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/dashboard/assets/{asset_name}", include_in_schema=False)
def dashboard_asset(asset_name: str) -> FileResponse:
    if asset_name not in ALLOWED_ASSETS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    media_type = "text/css" if asset_name.endswith(".css") else "text/javascript"
    response = FileResponse(ASSET_DIR / asset_name, media_type=media_type)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/dashboard/api/session", summary="Dashboard session state")
def dashboard_session_state(request: Request, response: Response) -> dict[str, Any]:
    _no_store(response)
    token = request.cookies.get(SESSION_COOKIE)
    principal = resolve_session_token(token)
    return {
        "configured": dashboard_auth_configured(),
        "authenticated": principal is not None,
        "user": (
            {
                "user_id": principal["user_id"],
                "username": principal["username"],
                "role": principal["role"],
                "state": principal["state"],
            }
            if principal
            else None
        ),
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.post("/dashboard/api/session", summary="Create dashboard user session")
def dashboard_login(payload: LoginRequest, response: Response) -> dict[str, Any]:
    _no_store(response)
    if not dashboard_auth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard access is not provisioned",
        )
    principal = authenticate_user(payload.username, payload.password)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(principal["user_id"]),
        max_age=max(300, SESSION_TTL_SECONDS),
        httponly=True,
        secure=True,
        samesite="strict",
        path="/dashboard",
    )
    return {
        "authenticated": True,
        "user": {
            "user_id": principal["user_id"],
            "username": principal["username"],
            "role": principal["role"],
            "state": principal["state"],
        },
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.delete("/dashboard/api/session", summary="Revoke current dashboard session")
def dashboard_logout(request: Request, response: Response) -> dict[str, bool]:
    _no_store(response)
    revoke_session_token(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(key=SESSION_COOKIE, path="/dashboard", secure=True, httponly=True, samesite="strict")
    return {"authenticated": False}


@router.get(
    "/dashboard/api/authorization/owner",
    summary="Verify Owner-only backend authorization",
    dependencies=[Depends(require_owner_session)],
)
def dashboard_owner_authorization_probe(response: Response) -> dict[str, bool]:
    _no_store(response)
    return {"authorized": True}


@router.get(
    "/dashboard/api/overview",
    summary="Read dashboard overview from test-only shadow data",
    dependencies=[Depends(require_dashboard_session)],
)
def dashboard_overview(response: Response) -> dict[str, Any]:
    _no_store(response)
    batch_rows = _query(
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
        """
    )
    latest_batch_id = batch_rows[0]["migration_batch_id"] if batch_rows else None
    reasons: list[dict[str, Any]] = []
    if latest_batch_id is not None:
        reasons = _query(
            """
            SELECT classification,
                   COALESCE(review_reason, '(none)') AS review_reason,
                   COUNT(*) AS row_count
            FROM migration_source_rows
            WHERE migration_batch_id::text = :migration_batch_id
              AND classification IN ('REVIEW', 'CONFLICT', 'NEW_UNMAPPED')
            GROUP BY classification, COALESCE(review_reason, '(none)')
            ORDER BY row_count DESC, classification, review_reason
            LIMIT 12
            """,
            {"migration_batch_id": latest_batch_id},
        )
    return {
        "batch": batch_rows[0] if batch_rows else None,
        "attention": reasons,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.get(
    "/dashboard/api/rows",
    summary="Read paginated dashboard rows",
    dependencies=[Depends(require_dashboard_session)],
)
def dashboard_rows(
    response: Response,
    migration_batch_id: str | None = None,
    source_sheet: str | None = None,
    classification: Literal["SAFE", "REVIEW", "CONFLICT", "NEW_UNMAPPED"] | None = None,
    q: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    _no_store(response)
    if migration_batch_id is None:
        migration_batch_id = _latest_google_snapshot_batch_id()
    where_sql, params = _dashboard_row_where(
        migration_batch_id=migration_batch_id,
        source_sheet=source_sheet,
        classification=classification,
        q=q,
    )
    params.update({"limit": limit, "offset": offset})
    rows = _query(
        f"""
        SELECT msr.migration_source_row_id::text AS migration_source_row_id,
               msr.migration_batch_id::text AS migration_batch_id,
               msr.source_sheet,
               msr.source_row_no,
               msr.classification,
               msr.review_reason,
               msr.payload,
               msr.created_at
        FROM migration_source_rows msr
        WHERE {where_sql}
        ORDER BY msr.source_sheet, msr.source_row_no, msr.migration_source_row_id
        LIMIT :limit OFFSET :offset
        """,
        params,
    )
    return {
        "items": rows,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "migration_batch_id": migration_batch_id,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.get(
    "/dashboard/api/review-reasons",
    summary="Read dashboard review reason summary",
    dependencies=[Depends(require_dashboard_session)],
)
def dashboard_review_reasons(response: Response, migration_batch_id: str | None = None) -> dict[str, Any]:
    _no_store(response)
    if migration_batch_id is None:
        migration_batch_id = _latest_google_snapshot_batch_id()
    if migration_batch_id is None:
        rows: list[dict[str, Any]] = []
    else:
        rows = _query(
            """
            SELECT classification,
                   COALESCE(review_reason, '(none)') AS review_reason,
                   COUNT(*) AS row_count
            FROM migration_source_rows
            WHERE migration_batch_id::text = :migration_batch_id
              AND classification IN ('REVIEW', 'CONFLICT', 'NEW_UNMAPPED')
            GROUP BY classification, COALESCE(review_reason, '(none)')
            ORDER BY classification, row_count DESC, review_reason
            """,
            {"migration_batch_id": migration_batch_id},
        )
    return {
        "items": rows,
        "count": len(rows),
        "migration_batch_id": migration_batch_id,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }
