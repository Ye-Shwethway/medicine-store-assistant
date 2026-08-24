from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dashboard_auth import _engine, require_owner_session
from app.multi_agent_review import _event, _set_status

router = APIRouter(prefix="/dashboard/api/ai-workspace/multi-agent", tags=["multi-agent-review"])


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def review_work_item_cancelled(work_item_id: str) -> bool:
    """Fail closed for background Review execution after Owner deletion/cancellation."""
    engine = _engine()
    try:
        with engine.connect() as connection:
            value = connection.execute(
                text(
                    """
                    SELECT status
                    FROM workflow_work_items
                    WHERE work_item_id=CAST(:work_item_id AS uuid)
                    """
                ),
                {"work_item_id": work_item_id},
            ).scalar_one_or_none()
            return value is None or value == "CANCELLED"
    finally:
        engine.dispose()


@router.get("/work-items", summary="List recent Owner REVIEW work items")
def list_review_work_items(
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    """Return reload-safe Owner REVIEW history without blocking the workspace.

    CANCELLED items are intentionally hidden from normal Review history. Their immutable
    artifacts/reviews/events remain in the shared workflow substrate for audit evidence.
    """
    _no_store(response)
    engine = _engine()
    try:
        try:
            with engine.connect() as connection:
                rows = connection.execute(
                    text(
                        """
                        SELECT w.work_item_id::text AS work_item_id,
                               w.work_type, w.status, w.title, w.objective,
                               w.session_id::text AS session_id,
                               s.session_name,
                               w.created_at, w.updated_at, w.completed_at
                        FROM workflow_work_items w
                        LEFT JOIN ai_agent_sessions s ON s.session_id=w.session_id
                        WHERE w.work_type='NATIVE_REVIEW'
                          AND w.status <> 'CANCELLED'
                          AND w.created_by_actor_type='OWNER'
                          AND CAST(w.created_by_actor_id AS text)=CAST(:owner_user_id AS text)
                        ORDER BY w.updated_at DESC, w.created_at DESC
                        LIMIT 50
                        """
                    ),
                    {"owner_user_id": owner["user_id"]},
                ).mappings().all()
        except SQLAlchemyError:
            return {
                "items": [],
                "count": 0,
                "degraded": True,
                "degraded_code": "REVIEW_HISTORY_UNAVAILABLE",
                "production_mutation": False,
                "database_canonical": False,
            }

        items = [
            {
                **dict(row),
                "artifact_count": 0,
                "review_count": 0,
                "open_attention_count": 0,
            }
            for row in rows
        ]
        return {
            "items": items,
            "count": len(items),
            "degraded": False,
            "production_mutation": False,
            "database_canonical": False,
        }
    finally:
        engine.dispose()


@router.delete(
    "/work-items/{work_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete one Owner Review from workspace history while preserving audit evidence",
)
def delete_review_work_item(
    work_item_id: str,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> Response:
    """Owner-facing delete uses audit-preserving cancellation semantics.

    The Work Item is hidden from Recent Review work, open Attention is resolved, and an
    immutable deletion event is appended. Existing Artifacts/Reviews/Events are not erased.
    """
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            item = connection.execute(
                text(
                    """
                    SELECT work_item_id::text AS work_item_id, status, created_by_actor_type,
                           created_by_actor_id, work_type
                    FROM workflow_work_items
                    WHERE work_item_id=CAST(:work_item_id AS uuid)
                    """
                ),
                {"work_item_id": work_item_id},
            ).mappings().first()
            if (
                item is None
                or item["work_type"] != "NATIVE_REVIEW"
                or item["created_by_actor_type"] != "OWNER"
                or str(item["created_by_actor_id"]) != str(owner["user_id"])
            ):
                raise HTTPException(status_code=404, detail="Work item not found")

            if item["status"] != "CANCELLED":
                _set_status(connection, work_item_id, "CANCELLED")
                connection.execute(
                    text(
                        """
                        UPDATE workflow_attention_items
                        SET status='RESOLVED', resolved_at=COALESCE(resolved_at, now())
                        WHERE work_item_id=CAST(:work_item_id AS uuid)
                          AND status <> 'RESOLVED'
                        """
                    ),
                    {"work_item_id": work_item_id},
                )
                _event(
                    connection,
                    work_item_id,
                    "WORK_ITEM_DELETED_BY_OWNER",
                    "OWNER",
                    owner["user_id"],
                    {
                        "previous_status": item["status"],
                        "workspace_visibility": "HIDDEN",
                        "audit_evidence_preserved": True,
                        "production_mutation": False,
                    },
                )
    finally:
        engine.dispose()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
