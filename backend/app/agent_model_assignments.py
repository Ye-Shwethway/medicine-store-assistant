from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(tags=["agent-model-assignments"])

MAX_FALLBACK_MODELS = 5


class AgentModelAssignmentChainInput(BaseModel):
    primary_saved_model_id: str
    fallback_saved_model_ids: list[str] = Field(default_factory=list, max_length=MAX_FALLBACK_MODELS)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _assignment_rows(connection, agent_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """
            SELECT a.assignment_id::text AS assignment_id,
                   a.agent_id::text AS agent_id,
                   a.saved_model_id::text AS saved_model_id,
                   a.assignment_kind,
                   a.position,
                   a.enabled,
                   s.provider_id::text AS provider_id,
                   p.display_name AS provider_name,
                   p.provider_kind,
                   p.state AS provider_state,
                   s.model_id,
                   s.display_name AS model_name,
                   s.state AS saved_model_state,
                   s.last_test_status,
                   s.last_tested_at,
                   EXISTS (
                       SELECT 1
                       FROM ai_provider_models d
                       WHERE d.provider_id=s.provider_id
                         AND d.model_id=s.model_id
                   ) AS currently_discovered
            FROM ai_agent_model_assignments a
            JOIN ai_saved_provider_models s ON s.saved_model_id=a.saved_model_id
            JOIN ai_providers p ON p.provider_id=s.provider_id
            WHERE a.agent_id=CAST(:agent_id AS uuid)
            ORDER BY CASE a.assignment_kind WHEN 'PRIMARY' THEN 0 ELSE 1 END,
                     a.position
            """
        ),
        {"agent_id": agent_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def _assert_internal_agent(connection, agent_id: str, *, lock: bool) -> dict[str, Any]:
    suffix = " FOR UPDATE" if lock else ""
    row = connection.execute(
        text(
            "SELECT agent_id::text AS agent_id, runtime_mode, state "
            "FROM ai_agents WHERE agent_id=CAST(:agent_id AS uuid)" + suffix
        ),
        {"agent_id": agent_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="AI agent not found")
    if row["runtime_mode"] != "INTERNAL_MODEL":
        raise HTTPException(status_code=409, detail="Only internal model agents can receive provider/model assignments")
    if row["state"] == "REVOKED":
        raise HTTPException(status_code=409, detail="Revoked agents cannot receive model assignments")
    return dict(row)


def _load_assignable_saved_models(connection, saved_model_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not saved_model_ids:
        return {}
    rows = connection.execute(
        text(
            """
            SELECT s.saved_model_id::text AS saved_model_id,
                   s.provider_id::text AS provider_id,
                   s.model_id,
                   s.display_name AS model_name,
                   s.state AS saved_model_state,
                   s.last_test_status,
                   p.display_name AS provider_name,
                   p.provider_kind,
                   p.state AS provider_state,
                   EXISTS (
                       SELECT 1
                       FROM ai_provider_models d
                       WHERE d.provider_id=s.provider_id
                         AND d.model_id=s.model_id
                   ) AS currently_discovered
            FROM ai_saved_provider_models s
            JOIN ai_providers p ON p.provider_id=s.provider_id
            WHERE s.saved_model_id = ANY(CAST(:saved_model_ids AS uuid[]))
            FOR UPDATE OF s
            """
        ),
        {"saved_model_ids": saved_model_ids},
    ).mappings().all()
    return {str(row["saved_model_id"]): dict(row) for row in rows}


def _validate_chain_models(saved_model_ids: list[str], rows: dict[str, dict[str, Any]]) -> None:
    missing = [saved_model_id for saved_model_id in saved_model_ids if saved_model_id not in rows]
    if missing:
        raise HTTPException(status_code=404, detail="One or more saved models were not found")
    for saved_model_id in saved_model_ids:
        row = rows[saved_model_id]
        if row["provider_state"] != "ENABLED":
            raise HTTPException(status_code=409, detail=f"Provider for saved model {saved_model_id} is not enabled")
        if row["saved_model_state"] != "ACTIVE":
            raise HTTPException(status_code=409, detail=f"Saved model {saved_model_id} is not active")
        if row["last_test_status"] != "HEALTHY":
            raise HTTPException(status_code=409, detail=f"Saved model {saved_model_id} is not healthy")
        if not row["currently_discovered"]:
            raise HTTPException(status_code=409, detail=f"Saved model {saved_model_id} is no longer discovered by its provider")


@router.get(
    "/dashboard/api/agents/{agent_id}/model-assignments",
    summary="Read ordered primary and fallback model assignments",
    dependencies=[Depends(require_owner_session)],
)
def get_agent_model_assignments(agent_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            agent = _assert_internal_agent(connection, agent_id, lock=False)
            items = _assignment_rows(connection, agent_id)
        primary = next((item for item in items if item["assignment_kind"] == "PRIMARY"), None)
        fallbacks = [item for item in items if item["assignment_kind"] == "FALLBACK"]
        return {
            "agent_id": agent["agent_id"],
            "runtime_mode": agent["runtime_mode"],
            "primary": primary,
            "fallbacks": fallbacks,
            "items": items,
            "fallback_count": len(fallbacks),
            "executable": bool(primary and primary["enabled"]),
        }
    finally:
        engine.dispose()


@router.put(
    "/dashboard/api/agents/{agent_id}/model-assignments",
    summary="Replace ordered primary and fallback model assignments",
)
def set_agent_model_assignments(
    agent_id: str,
    payload: AgentModelAssignmentChainInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    primary_id = payload.primary_saved_model_id.strip()
    fallback_ids = [value.strip() for value in payload.fallback_saved_model_ids]
    if not primary_id:
        raise HTTPException(status_code=422, detail="primary_saved_model_id is required")
    if any(not value for value in fallback_ids):
        raise HTTPException(status_code=422, detail="Fallback saved model IDs cannot be blank")
    ordered_ids = [primary_id, *fallback_ids]
    if len(set(ordered_ids)) != len(ordered_ids):
        raise HTTPException(status_code=409, detail="Primary and fallback assignments cannot contain duplicate saved models")

    engine = _engine()
    try:
        with engine.begin() as connection:
            _assert_internal_agent(connection, agent_id, lock=True)
            saved_rows = _load_assignable_saved_models(connection, ordered_ids)
            _validate_chain_models(ordered_ids, saved_rows)

            connection.execute(
                text("DELETE FROM ai_agent_model_assignments WHERE agent_id=CAST(:agent_id AS uuid)"),
                {"agent_id": agent_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO ai_agent_model_assignments
                        (agent_id, saved_model_id, assignment_kind, position, enabled, created_by_user_id)
                    VALUES
                        (CAST(:agent_id AS uuid), CAST(:saved_model_id AS uuid), 'PRIMARY', 0, true, CAST(:owner_id AS uuid))
                    """
                ),
                {"agent_id": agent_id, "saved_model_id": primary_id, "owner_id": owner["user_id"]},
            )
            for position, saved_model_id in enumerate(fallback_ids):
                connection.execute(
                    text(
                        """
                        INSERT INTO ai_agent_model_assignments
                            (agent_id, saved_model_id, assignment_kind, position, enabled, created_by_user_id)
                        VALUES
                            (CAST(:agent_id AS uuid), CAST(:saved_model_id AS uuid), 'FALLBACK', :position, true, CAST(:owner_id AS uuid))
                        """
                    ),
                    {
                        "agent_id": agent_id,
                        "saved_model_id": saved_model_id,
                        "position": position,
                        "owner_id": owner["user_id"],
                    },
                )
            items = _assignment_rows(connection, agent_id)

        return {
            "agent_id": agent_id,
            "primary": next((item for item in items if item["assignment_kind"] == "PRIMARY"), None),
            "fallbacks": [item for item in items if item["assignment_kind"] == "FALLBACK"],
            "items": items,
            "fallback_count": len(fallback_ids),
            "executable": True,
        }
    finally:
        engine.dispose()


@router.delete(
    "/dashboard/api/agents/{agent_id}/model-assignments",
    summary="Clear primary and fallback model assignments",
)
def clear_agent_model_assignments(
    agent_id: str,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    del owner
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            _assert_internal_agent(connection, agent_id, lock=True)
            deleted = connection.execute(
                text(
                    "DELETE FROM ai_agent_model_assignments "
                    "WHERE agent_id=CAST(:agent_id AS uuid) RETURNING assignment_id"
                ),
                {"agent_id": agent_id},
            ).all()
        return {
            "agent_id": agent_id,
            "cleared": True,
            "deleted_count": len(deleted),
            "primary": None,
            "fallbacks": [],
            "items": [],
            "executable": False,
        }
    finally:
        engine.dispose()
