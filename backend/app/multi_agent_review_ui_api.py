from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(prefix="/dashboard/api/ai-workspace/multi-agent", tags=["multi-agent-review"])


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


@router.get("/work-items", summary="List recent Owner REVIEW work items")
def list_review_work_items(
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    """Return reload-safe Owner REVIEW history without blocking the workspace.

    Recent history is a convenience/readback surface. A database read failure here must
    not disable preset selection, role configuration, or starting a new native REVIEW.
    The response intentionally exposes only a bounded degradation code and never raw
    SQL/database exception text.
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
