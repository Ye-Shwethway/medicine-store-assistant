from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text

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
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT w.work_item_id::text AS work_item_id,
                           w.work_type, w.status, w.title, w.objective,
                           w.session_id::text AS session_id,
                           s.session_name,
                           w.created_at, w.updated_at, w.completed_at,
                           (SELECT count(*) FROM workflow_artifacts a WHERE a.work_item_id=w.work_item_id) AS artifact_count,
                           (SELECT count(*) FROM workflow_reviews r WHERE r.work_item_id=w.work_item_id) AS review_count,
                           (SELECT count(*) FROM workflow_attention_items q WHERE q.work_item_id=w.work_item_id AND q.status='OPEN') AS open_attention_count
                    FROM workflow_work_items w
                    LEFT JOIN ai_agent_sessions s ON s.session_id=w.session_id
                    WHERE w.work_type='NATIVE_REVIEW'
                      AND w.created_by_actor_type='OWNER'
                      AND w.created_by_actor_id=:owner_user_id
                    ORDER BY w.updated_at DESC, w.created_at DESC
                    LIMIT 50
                    """
                ),
                {"owner_user_id": owner["user_id"]},
            ).mappings().all()
        return {
            "items": [dict(row) for row in rows],
            "count": len(rows),
            "production_mutation": False,
            "database_canonical": False,
        }
    finally:
        engine.dispose()
