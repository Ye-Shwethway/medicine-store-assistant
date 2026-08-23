from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from mcp.server.auth.middleware.auth_context import get_access_token
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(prefix="/dashboard/api/audit", tags=["audit"])


def _current_bound_agent(access: Any) -> dict[str, Any] | None:
    if access is None or not access.client_id or not access.subject:
        return None
    try:
        UUID(str(access.subject))
    except (TypeError, ValueError):
        return None
    engine = _engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT a.agent_id::text AS agent_id,
                           a.display_name,
                           a.call_name,
                           a.runtime_mode,
                           a.state,
                           a.authority_ceiling,
                           a.execution_policy,
                           a.confirmation_policy,
                           c.client_name
                    FROM mcp_oauth_grants g
                    JOIN mcp_oauth_clients c ON c.client_id = g.client_id
                    JOIN mcp_agent_bindings b ON b.grant_id = g.grant_id
                    JOIN ai_agents a ON a.agent_id = b.agent_id
                    WHERE g.client_id = :client_id
                      AND g.user_id = CAST(:subject AS uuid)
                      AND g.state = 'ACTIVE'
                      AND c.revoked_at IS NULL
                    LIMIT 1
                    """
                ),
                {"client_id": str(access.client_id), "subject": str(access.subject)},
            ).mappings().first()
        return dict(row) if row is not None else None
    except SQLAlchemyError:
        return None
    finally:
        engine.dispose()


def record_mcp_event(*, access: Any, agent_context: dict[str, Any] | None, action_type: str, capability_scope: str | None, outcome: str, metadata: dict[str, Any] | None = None) -> None:
    """Best-effort append-only MCP audit evidence. Never logs tokens, prompts, or secrets."""
    if access is None:
        return
    safe_metadata = dict(metadata or {})
    safe_metadata.pop("token", None)
    safe_metadata.pop("authorization", None)
    actor_type = "AI_AGENT" if agent_context else "INTEGRATION"
    agent_id = agent_context.get("agent_id") if agent_context else None
    runtime_type = agent_context.get("runtime_mode") if agent_context else "EXTERNAL_MCP_CLIENT"
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO operation_audit_events (
                        actor_type, agent_id, authorized_by_user_id, client_source, client_id,
                        runtime_type, action_type, capability_scope, outcome, safe_metadata
                    ) VALUES (
                        :actor_type, CAST(:agent_id AS uuid), CAST(:authorized_by_user_id AS uuid),
                        'EXTERNAL_MCP', :client_id, :runtime_type, :action_type,
                        :capability_scope, :outcome, CAST(:safe_metadata AS jsonb)
                    )
                    """
                ),
                {
                    "actor_type": actor_type,
                    "agent_id": agent_id,
                    "authorized_by_user_id": str(access.subject) if actor_type == "AI_AGENT" else None,
                    "client_id": str(access.client_id) if access.client_id else None,
                    "runtime_type": runtime_type,
                    "action_type": action_type,
                    "capability_scope": capability_scope,
                    "outcome": outcome,
                    "safe_metadata": json.dumps(safe_metadata),
                },
            )
    except (SQLAlchemyError, ValueError, TypeError):
        return
    finally:
        engine.dispose()


def record_current_mcp_event(*, action_type: str, capability_scope: str | None, outcome: str = "SUCCESS", metadata: dict[str, Any] | None = None) -> None:
    access = get_access_token()
    if access is None:
        return
    record_mcp_event(
        access=access,
        agent_context=_current_bound_agent(access),
        action_type=action_type,
        capability_scope=capability_scope,
        outcome=outcome,
        metadata=metadata,
    )


@router.get("/recent", dependencies=[Depends(require_owner_session)], summary="Recent operational audit activity")
def recent_audit(response: Response, limit: int = 50) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    bounded = min(max(limit, 1), 200)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT e.event_id::text AS event_id,
                           e.correlation_id::text AS correlation_id,
                           e.actor_type,
                           e.agent_id::text AS agent_id,
                           a.display_name AS agent_name,
                           a.call_name,
                           e.authorized_by_user_id::text AS authorized_by_user_id,
                           u.username AS authorized_by_username,
                           e.client_source,
                           e.client_id,
                           e.runtime_type,
                           e.action_type,
                           e.capability_scope,
                           e.outcome,
                           e.safe_metadata,
                           e.occurred_at
                    FROM operation_audit_events e
                    LEFT JOIN ai_agents a ON a.agent_id = e.agent_id
                    LEFT JOIN users u ON u.user_id = e.authorized_by_user_id
                    ORDER BY e.occurred_at DESC
                    LIMIT :limit
                    """
                ),
                {"limit": bounded},
            ).mappings().all()
        return {"items": [dict(row) for row in rows], "count": len(rows), "limit": bounded}
    finally:
        engine.dispose()
