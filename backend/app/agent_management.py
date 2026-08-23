from __future__ import annotations

import json
import re
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(prefix="/dashboard/api/agents", tags=["agent-management"])

CALL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")
CAPABILITY_ALLOWLIST = frozenset({"mcp:read", "mcp:propose", "mcp:write", "mcp:control"})
RUNTIME_MODES = frozenset({"INTERNAL_MODEL", "EXTERNAL_MCP_CLIENT", "EXTERNAL_ACTION_CLIENT", "SYSTEM_AUTOMATION"})
AUTHORITY_LEVELS = frozenset({"READ", "PROPOSE", "WRITE", "CONTROL"})
EXECUTION_POLICIES = frozenset({"DELEGATED", "AUTONOMOUS"})
CONFIRMATION_POLICIES = frozenset({"READ_ONLY", "PROPOSE_ONLY", "CONFIRM_BEFORE_WRITE", "AUTONOMOUS_PREAUTHORIZED"})
SESSION_MODES = frozenset({"GROUP", "COMPARE", "REVIEW", "DEBATE"})


class AgentCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    call_name: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=1000)
    runtime_mode: Literal["INTERNAL_MODEL", "EXTERNAL_MCP_CLIENT", "EXTERNAL_ACTION_CLIENT", "SYSTEM_AUTOMATION"] = "INTERNAL_MODEL"
    capability_scopes: list[str] = Field(default_factory=lambda: ["mcp:read"])
    location_scope: dict[str, Any] = Field(default_factory=lambda: {"mode": "ALL_READABLE"})
    authority_ceiling: Literal["READ", "PROPOSE", "WRITE", "CONTROL"] = "READ"
    execution_policy: Literal["DELEGATED", "AUTONOMOUS"] = "DELEGATED"
    confirmation_policy: Literal["READ_ONLY", "PROPOSE_ONLY", "CONFIRM_BEFORE_WRITE", "AUTONOMOUS_PREAUTHORIZED"] = "READ_ONLY"


class AgentUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    call_name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=1000)
    capability_scopes: list[str] | None = None
    location_scope: dict[str, Any] | None = None
    authority_ceiling: Literal["READ", "PROPOSE", "WRITE", "CONTROL"] | None = None
    execution_policy: Literal["DELEGATED", "AUTONOMOUS"] | None = None
    confirmation_policy: Literal["READ_ONLY", "PROPOSE_ONLY", "CONFIRM_BEFORE_WRITE", "AUTONOMOUS_PREAUTHORIZED"] | None = None


class SessionParticipantInput(BaseModel):
    agent_id: str
    position: int = Field(ge=0)
    role_label: str | None = Field(default=None, max_length=80)


class SessionCreate(BaseModel):
    session_name: str = Field(min_length=1, max_length=120)
    objective: str | None = Field(default=None, max_length=2000)
    mode: Literal["GROUP", "COMPARE", "REVIEW", "DEBATE"] = "GROUP"
    participants: list[SessionParticipantInput] = Field(default_factory=list, max_length=32)


class SessionUpdate(BaseModel):
    session_name: str | None = Field(default=None, min_length=1, max_length=120)
    objective: str | None = Field(default=None, max_length=2000)
    mode: Literal["GROUP", "COMPARE", "REVIEW", "DEBATE"] | None = None
    participants: list[SessionParticipantInput] | None = Field(default=None, max_length=32)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _clean_name(value: str, *, field: str, max_length: int) -> str:
    cleaned = " ".join(value.strip().split())
    if not cleaned or len(cleaned) > max_length:
        raise HTTPException(status_code=400, detail=f"Enter a valid {field}")
    return cleaned


def _clean_call_name(value: str) -> str:
    cleaned = _clean_name(value, field="call name", max_length=64)
    if not CALL_NAME_RE.fullmatch(cleaned):
        raise HTTPException(status_code=400, detail="Call name must use letters, numbers, spaces, dots, dashes, or underscores")
    return cleaned


def _validate_capabilities(values: list[str]) -> list[str]:
    unique = sorted(set(values))
    unknown = set(unique) - CAPABILITY_ALLOWLIST
    if unknown:
        raise HTTPException(status_code=400, detail="Unsupported capability scope")
    if not unique:
        raise HTTPException(status_code=400, detail="Select at least one capability scope")
    return unique


def _identity_context(row: dict[str, Any]) -> str:
    return (
        f"You are {row['display_name']}. Your stable MSA agent identity is {row['agent_id']}. "
        "Respond as this configured agent and do not claim another agent identity."
    )


def _agent_dict(row: Any) -> dict[str, Any]:
    item = dict(row)
    item["identity_context"] = _identity_context(item)
    return item


def _fetch_agent(connection, agent_id: str, *, for_update: bool = False):
    suffix = " FOR UPDATE" if for_update else ""
    row = connection.execute(
        text(
            """
            SELECT agent_id::text AS agent_id, display_name, call_name, description,
                   runtime_mode, state, capability_scopes, location_scope,
                   authority_ceiling, execution_policy, confirmation_policy,
                   created_by_user_id::text AS created_by_user_id,
                   created_at, updated_at, disabled_at, revoked_at
            FROM ai_agents
            WHERE agent_id = CAST(:agent_id AS uuid)
            """ + suffix
        ),
        {"agent_id": agent_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return row


def _replace_participants(connection, session_id: str, participants: list[SessionParticipantInput]) -> None:
    agent_ids = [p.agent_id for p in participants]
    positions = [p.position for p in participants]
    if len(agent_ids) != len(set(agent_ids)):
        raise HTTPException(status_code=400, detail="An agent may appear only once in a session")
    if len(positions) != len(set(positions)):
        raise HTTPException(status_code=400, detail="Participant positions must be unique")

    if agent_ids:
        rows = connection.execute(
            text(
                """
                SELECT agent_id::text AS agent_id, state
                FROM ai_agents
                WHERE agent_id = ANY(CAST(:agent_ids AS uuid[]))
                """
            ),
            {"agent_ids": agent_ids},
        ).mappings().all()
        found = {row["agent_id"]: row["state"] for row in rows}
        if set(agent_ids) != set(found):
            raise HTTPException(status_code=400, detail="One or more selected agents do not exist")
        if any(found[agent_id] != "ACTIVE" for agent_id in agent_ids):
            raise HTTPException(status_code=409, detail="Only ACTIVE agents can be selected for a session")

    connection.execute(
        text("DELETE FROM ai_agent_session_participants WHERE session_id = CAST(:session_id AS uuid)"),
        {"session_id": session_id},
    )
    for participant in sorted(participants, key=lambda p: p.position):
        connection.execute(
            text(
                """
                INSERT INTO ai_agent_session_participants (session_id, agent_id, position, role_label)
                VALUES (CAST(:session_id AS uuid), CAST(:agent_id AS uuid), :position, :role_label)
                """
            ),
            {
                "session_id": session_id,
                "agent_id": participant.agent_id,
                "position": participant.position,
                "role_label": _clean_name(participant.role_label, field="role label", max_length=80) if participant.role_label else None,
            },
        )


def _session_dict(connection, row: Any) -> dict[str, Any]:
    item = dict(row)
    participants = connection.execute(
        text(
            """
            SELECT p.agent_id::text AS agent_id, a.display_name, a.call_name, a.state AS agent_state,
                   p.position, p.role_label, p.is_active, p.joined_at
            FROM ai_agent_session_participants p
            JOIN ai_agents a ON a.agent_id = p.agent_id
            WHERE p.session_id = CAST(:session_id AS uuid)
            ORDER BY p.position, a.call_name
            """
        ),
        {"session_id": item["session_id"]},
    ).mappings().all()
    item["participants"] = [dict(p) for p in participants]
    return item


@router.get("", summary="List AI agents", dependencies=[Depends(require_owner_session)])
def list_agents(response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT agent_id::text AS agent_id, display_name, call_name, description,
                           runtime_mode, state, capability_scopes, location_scope,
                           authority_ceiling, execution_policy, confirmation_policy,
                           created_by_user_id::text AS created_by_user_id,
                           created_at, updated_at, disabled_at, revoked_at
                    FROM ai_agents
                    ORDER BY CASE state WHEN 'ACTIVE' THEN 0 WHEN 'DISABLED' THEN 1 ELSE 2 END,
                             lower(call_name), created_at
                    """
                )
            ).mappings().all()
        return {"items": [_agent_dict(row) for row in rows], "count": len(rows), "system_write_gate": "CLOSED"}
    finally:
        engine.dispose()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create named AI agent")
def create_agent(payload: AgentCreate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    display_name = _clean_name(payload.display_name, field="display name", max_length=80)
    call_name = _clean_call_name(payload.call_name)
    capabilities = _validate_capabilities(payload.capability_scopes)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                row = connection.execute(
                    text(
                        """
                        INSERT INTO ai_agents (
                            display_name, call_name, description, runtime_mode, capability_scopes,
                            location_scope, authority_ceiling, execution_policy, confirmation_policy,
                            created_by_user_id
                        ) VALUES (
                            :display_name, :call_name, :description, :runtime_mode, :capability_scopes,
                            CAST(:location_scope AS jsonb), :authority_ceiling, :execution_policy, :confirmation_policy,
                            CAST(:owner_id AS uuid)
                        )
                        RETURNING agent_id::text AS agent_id, display_name, call_name, description,
                                  runtime_mode, state, capability_scopes, location_scope,
                                  authority_ceiling, execution_policy, confirmation_policy,
                                  created_by_user_id::text AS created_by_user_id,
                                  created_at, updated_at, disabled_at, revoked_at
                        """
                    ),
                    {
                        "display_name": display_name,
                        "call_name": call_name,
                        "description": payload.description.strip() if payload.description else None,
                        "runtime_mode": payload.runtime_mode,
                        "capability_scopes": capabilities,
                        "location_scope": json.dumps(payload.location_scope),
                        "authority_ceiling": payload.authority_ceiling,
                        "execution_policy": payload.execution_policy,
                        "confirmation_policy": payload.confirmation_policy,
                        "owner_id": owner["user_id"],
                    },
                ).mappings().one()
            return _agent_dict(row)
        except IntegrityError as exc:
            if "uq_ai_agents_call_name_lower" in str(exc.orig):
                raise HTTPException(status_code=409, detail="Call name is already in use") from exc
            raise
    finally:
        engine.dispose()


@router.get("/{agent_id}", summary="Read AI agent", dependencies=[Depends(require_owner_session)])
def get_agent(agent_id: str, response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            return _agent_dict(_fetch_agent(connection, agent_id))
    finally:
        engine.dispose()


@router.patch("/{agent_id}", summary="Update AI agent")
def update_agent(agent_id: str, payload: AgentUpdate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    updates: dict[str, Any] = {}
    if payload.display_name is not None:
        updates["display_name"] = _clean_name(payload.display_name, field="display name", max_length=80)
    if payload.call_name is not None:
        updates["call_name"] = _clean_call_name(payload.call_name)
    if "description" in payload.model_fields_set:
        updates["description"] = payload.description.strip() if payload.description else None
    if payload.capability_scopes is not None:
        updates["capability_scopes"] = _validate_capabilities(payload.capability_scopes)
    if payload.location_scope is not None:
        updates["location_scope"] = json.dumps(payload.location_scope)
    if payload.authority_ceiling is not None:
        updates["authority_ceiling"] = payload.authority_ceiling
    if payload.execution_policy is not None:
        updates["execution_policy"] = payload.execution_policy
    if payload.confirmation_policy is not None:
        updates["confirmation_policy"] = payload.confirmation_policy
    if not updates:
        raise HTTPException(status_code=400, detail="No agent changes supplied")

    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                current = _fetch_agent(connection, agent_id, for_update=True)
                if current["state"] == "REVOKED":
                    raise HTTPException(status_code=409, detail="Revoked agents cannot be edited")
                assignments = []
                params: dict[str, Any] = {"agent_id": agent_id, "owner_id": owner["user_id"]}
                for key, value in updates.items():
                    if key == "location_scope":
                        assignments.append("location_scope = CAST(:location_scope AS jsonb)")
                    else:
                        assignments.append(f"{key} = :{key}")
                    params[key] = value
                assignments.append("updated_at = now()")
                row = connection.execute(
                    text(
                        f"""
                        UPDATE ai_agents SET {', '.join(assignments)}
                        WHERE agent_id = CAST(:agent_id AS uuid)
                        RETURNING agent_id::text AS agent_id, display_name, call_name, description,
                                  runtime_mode, state, capability_scopes, location_scope,
                                  authority_ceiling, execution_policy, confirmation_policy,
                                  created_by_user_id::text AS created_by_user_id,
                                  created_at, updated_at, disabled_at, revoked_at
                        """
                    ),
                    params,
                ).mappings().one()
            return _agent_dict(row)
        except IntegrityError as exc:
            if "uq_ai_agents_call_name_lower" in str(exc.orig):
                raise HTTPException(status_code=409, detail="Call name is already in use") from exc
            raise
    finally:
        engine.dispose()


def _set_agent_state(agent_id: str, target: str, owner: dict[str, str]) -> dict[str, Any]:
    engine = _engine()
    try:
        with engine.begin() as connection:
            current = _fetch_agent(connection, agent_id, for_update=True)
            if current["state"] == "REVOKED" and target != "REVOKED":
                raise HTTPException(status_code=409, detail="Revoked agents cannot be reactivated")
            if target == "ACTIVE":
                fields = "state='ACTIVE', disabled_at=NULL, updated_at=now()"
            elif target == "DISABLED":
                fields = "state='DISABLED', disabled_at=now(), updated_at=now()"
            else:
                fields = "state='REVOKED', revoked_at=now(), disabled_at=now(), updated_at=now()"
            row = connection.execute(
                text(
                    f"""
                    UPDATE ai_agents SET {fields}
                    WHERE agent_id = CAST(:agent_id AS uuid)
                    RETURNING agent_id::text AS agent_id, display_name, call_name, description,
                              runtime_mode, state, capability_scopes, location_scope,
                              authority_ceiling, execution_policy, confirmation_policy,
                              created_by_user_id::text AS created_by_user_id,
                              created_at, updated_at, disabled_at, revoked_at
                    """
                ),
                {"agent_id": agent_id},
            ).mappings().one()
        return _agent_dict(row)
    finally:
        engine.dispose()


@router.post("/{agent_id}/disable", summary="Disable AI agent")
def disable_agent(agent_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    return _set_agent_state(agent_id, "DISABLED", owner)


@router.post("/{agent_id}/reactivate", summary="Reactivate AI agent")
def reactivate_agent(agent_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    return _set_agent_state(agent_id, "ACTIVE", owner)


@router.post("/{agent_id}/revoke", summary="Permanently revoke AI agent")
def revoke_agent(agent_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    return _set_agent_state(agent_id, "REVOKED", owner)


@router.get("/sessions/list", summary="List multi-agent sessions", dependencies=[Depends(require_owner_session)])
def list_sessions(response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT session_id::text AS session_id, session_name, objective, mode, state,
                           created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    FROM ai_agent_sessions
                    ORDER BY CASE state WHEN 'OPEN' THEN 0 ELSE 1 END, updated_at DESC, created_at DESC
                    """
                )
            ).mappings().all()
            items = [_session_dict(connection, row) for row in rows]
        return {"items": items, "count": len(items), "inference_enabled": False}
    finally:
        engine.dispose()


@router.post("/sessions", status_code=status.HTTP_201_CREATED, summary="Create multi-agent session")
def create_session(payload: SessionCreate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    session_name = _clean_name(payload.session_name, field="session name", max_length=120)
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    INSERT INTO ai_agent_sessions (session_name, objective, mode, created_by_user_id)
                    VALUES (:session_name, :objective, :mode, CAST(:owner_id AS uuid))
                    RETURNING session_id::text AS session_id, session_name, objective, mode, state,
                              created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    """
                ),
                {
                    "session_name": session_name,
                    "objective": payload.objective.strip() if payload.objective else None,
                    "mode": payload.mode,
                    "owner_id": owner["user_id"],
                },
            ).mappings().one()
            _replace_participants(connection, row["session_id"], payload.participants)
            return _session_dict(connection, row)
    finally:
        engine.dispose()


@router.patch("/sessions/{session_id}", summary="Update multi-agent session")
def update_session(session_id: str, payload: SessionUpdate, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            current = connection.execute(
                text(
                    """
                    SELECT session_id::text AS session_id, session_name, objective, mode, state,
                           created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    FROM ai_agent_sessions WHERE session_id = CAST(:session_id AS uuid) FOR UPDATE
                    """
                ),
                {"session_id": session_id},
            ).mappings().first()
            if current is None:
                raise HTTPException(status_code=404, detail="Agent session not found")
            if current["state"] == "CLOSED":
                raise HTTPException(status_code=409, detail="Reopen the session before editing")
            assignments = []
            params: dict[str, Any] = {"session_id": session_id}
            if payload.session_name is not None:
                params["session_name"] = _clean_name(payload.session_name, field="session name", max_length=120)
                assignments.append("session_name=:session_name")
            if "objective" in payload.model_fields_set:
                params["objective"] = payload.objective.strip() if payload.objective else None
                assignments.append("objective=:objective")
            if payload.mode is not None:
                params["mode"] = payload.mode
                assignments.append("mode=:mode")
            if assignments:
                assignments.append("updated_at=now()")
                connection.execute(
                    text(f"UPDATE ai_agent_sessions SET {', '.join(assignments)} WHERE session_id=CAST(:session_id AS uuid)"),
                    params,
                )
            if payload.participants is not None:
                _replace_participants(connection, session_id, payload.participants)
                connection.execute(text("UPDATE ai_agent_sessions SET updated_at=now() WHERE session_id=CAST(:session_id AS uuid)"), {"session_id": session_id})
            row = connection.execute(
                text(
                    """
                    SELECT session_id::text AS session_id, session_name, objective, mode, state,
                           created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    FROM ai_agent_sessions WHERE session_id = CAST(:session_id AS uuid)
                    """
                ),
                {"session_id": session_id},
            ).mappings().one()
            return _session_dict(connection, row)
    finally:
        engine.dispose()


@router.post("/sessions/{session_id}/close", summary="Close multi-agent session")
def close_session(session_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE ai_agent_sessions
                    SET state='CLOSED', closed_at=now(), updated_at=now()
                    WHERE session_id=CAST(:session_id AS uuid)
                    RETURNING session_id::text AS session_id, session_name, objective, mode, state,
                              created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    """
                ),
                {"session_id": session_id},
            ).mappings().first()
            if row is None:
                raise HTTPException(status_code=404, detail="Agent session not found")
            return _session_dict(connection, row)
    finally:
        engine.dispose()


@router.post("/sessions/{session_id}/reopen", summary="Reopen multi-agent session")
def reopen_session(session_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE ai_agent_sessions
                    SET state='OPEN', closed_at=NULL, updated_at=now()
                    WHERE session_id=CAST(:session_id AS uuid)
                    RETURNING session_id::text AS session_id, session_name, objective, mode, state,
                              created_by_user_id::text AS created_by_user_id, created_at, updated_at, closed_at
                    """
                ),
                {"session_id": session_id},
            ).mappings().first()
            if row is None:
                raise HTTPException(status_code=404, detail="Agent session not found")
            return _session_dict(connection, row)
    finally:
        engine.dispose()
