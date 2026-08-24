from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(prefix="/dashboard/api/mcp-bindings", tags=["mcp-agent-binding"])

CAPABILITY_ALLOWLIST = frozenset({"mcp:read", "mcp:propose", "mcp:write", "mcp:control"})
AUTHORITY_INDEX = {"mcp:read": 0, "mcp:propose": 1, "mcp:write": 2, "mcp:control": 3}
CEILING_SCOPE = {"READ": "mcp:read", "PROPOSE": "mcp:propose", "WRITE": "mcp:write", "CONTROL": "mcp:control"}


class MCPAgentBindRequest(BaseModel):
    grant_id: str
    agent_id: str


class MCPGrantScopesUpdate(BaseModel):
    capability_scopes: list[str] = Field(min_length=1, max_length=4)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _validated_scopes(values: list[str]) -> list[str]:
    scopes = sorted(set(str(value).strip() for value in values if str(value).strip()))
    if not scopes or set(scopes) - CAPABILITY_ALLOWLIST:
        raise HTTPException(status_code=400, detail="Select only supported MCP capability scopes")
    return scopes


def _with_effective_scopes(item: dict[str, Any]) -> dict[str, Any]:
    grant_scopes = {str(scope) for scope in (item.get("grant_capability_scopes") or [])}
    agent_scopes = {str(scope) for scope in (item.get("agent_capability_scopes") or [])}
    ceiling = str(item.get("agent_authority_ceiling") or "READ")
    ceiling_scope = CEILING_SCOPE.get(ceiling, "mcp:read")
    ceiling_allowed = {scope for scope, index in AUTHORITY_INDEX.items() if index <= AUTHORITY_INDEX[ceiling_scope]}
    if item.get("agent_state") == "ACTIVE" and item.get("agent_runtime_mode") == "EXTERNAL_MCP_CLIENT":
        effective = grant_scopes & agent_scopes & ceiling_allowed
    else:
        effective = set()
    item["effective_capability_scopes"] = sorted(effective)
    return item


def _binding_rows(connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """
            SELECT g.grant_id::text AS grant_id,
                   g.client_id,
                   c.client_name,
                   g.user_id::text AS authorizing_user_id,
                   u.username AS authorizing_username,
                   g.state AS grant_state,
                   g.capability_scopes AS grant_capability_scopes,
                   b.agent_id::text AS agent_id,
                   a.display_name AS agent_display_name,
                   a.call_name AS agent_call_name,
                   a.runtime_mode AS agent_runtime_mode,
                   a.state AS agent_state,
                   a.capability_scopes AS agent_capability_scopes,
                   a.authority_ceiling AS agent_authority_ceiling,
                   a.confirmation_policy AS agent_confirmation_policy,
                   b.created_at AS bound_at,
                   b.updated_at AS binding_updated_at
            FROM mcp_oauth_grants g
            JOIN mcp_oauth_clients c ON c.client_id = g.client_id
            JOIN users u ON u.user_id = g.user_id
            LEFT JOIN mcp_agent_bindings b ON b.grant_id = g.grant_id
            LEFT JOIN ai_agents a ON a.agent_id = b.agent_id
            WHERE g.state = 'ACTIVE'
              AND c.revoked_at IS NULL
              AND u.state = 'ACTIVE'
            ORDER BY lower(c.client_name), g.created_at
            """
        )
    ).mappings().all()
    return [_with_effective_scopes(dict(row)) for row in rows]


def _read_back_grant(connection, grant_id: str) -> dict[str, Any]:
    items = _binding_rows(connection)
    result = next((item for item in items if item["grant_id"] == grant_id), None)
    if result is None:
        raise HTTPException(status_code=404, detail="Active MCP OAuth grant not found")
    return result


@router.get("", summary="List active MCP grants and named-agent bindings", dependencies=[Depends(require_owner_session)])
def list_mcp_bindings(response: Response) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            items = _binding_rows(connection)
        return {"items": items, "count": len(items)}
    finally:
        engine.dispose()


@router.put("/{grant_id}/scopes", summary="Update live MCP OAuth grant capability scopes")
def update_mcp_grant_scopes(
    grant_id: str,
    payload: MCPGrantScopesUpdate,
    response: Response,
    _: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    scopes = _validated_scopes(payload.capability_scopes)
    engine = _engine()
    try:
        with engine.begin() as connection:
            updated = connection.execute(
                text(
                    """
                    UPDATE mcp_oauth_grants g
                    SET capability_scopes=:scopes, updated_at=now()
                    FROM mcp_oauth_clients c, users u
                    WHERE g.grant_id=CAST(:grant_id AS uuid)
                      AND c.client_id=g.client_id
                      AND u.user_id=g.user_id
                      AND g.state='ACTIVE'
                      AND c.revoked_at IS NULL
                      AND u.state='ACTIVE'
                    RETURNING g.grant_id::text
                    """
                ),
                {"grant_id": grant_id, "scopes": scopes},
            ).scalar_one_or_none()
            if updated is None:
                raise HTTPException(status_code=404, detail="Active MCP OAuth grant not found")
        with engine.connect() as connection:
            return _read_back_grant(connection, grant_id)
    finally:
        engine.dispose()


@router.put("", summary="Bind an active MCP OAuth grant to a named external agent")
def bind_mcp_agent(
    payload: MCPAgentBindRequest,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        try:
            with engine.begin() as connection:
                grant = connection.execute(
                    text(
                        """
                        SELECT g.grant_id::text AS grant_id
                        FROM mcp_oauth_grants g
                        JOIN mcp_oauth_clients c ON c.client_id = g.client_id
                        JOIN users u ON u.user_id = g.user_id
                        WHERE g.grant_id = CAST(:grant_id AS uuid)
                          AND g.state = 'ACTIVE'
                          AND c.revoked_at IS NULL
                          AND u.state = 'ACTIVE'
                        FOR UPDATE
                        """
                    ),
                    {"grant_id": payload.grant_id},
                ).mappings().first()
                if grant is None:
                    raise HTTPException(status_code=404, detail="Active MCP OAuth grant not found")

                agent = connection.execute(
                    text(
                        """
                        SELECT agent_id::text AS agent_id, runtime_mode, state
                        FROM ai_agents
                        WHERE agent_id = CAST(:agent_id AS uuid)
                        FOR UPDATE
                        """
                    ),
                    {"agent_id": payload.agent_id},
                ).mappings().first()
                if agent is None:
                    raise HTTPException(status_code=404, detail="AI agent not found")
                if agent["runtime_mode"] != "EXTERNAL_MCP_CLIENT":
                    raise HTTPException(status_code=409, detail="Only External MCP client agents can bind to MCP OAuth grants")
                if agent["state"] != "ACTIVE":
                    raise HTTPException(status_code=409, detail="Only ACTIVE agents can receive an MCP binding")

                connection.execute(
                    text("DELETE FROM mcp_agent_bindings WHERE grant_id = CAST(:grant_id AS uuid) OR agent_id = CAST(:agent_id AS uuid)"),
                    {"grant_id": payload.grant_id, "agent_id": payload.agent_id},
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO mcp_agent_bindings (grant_id, agent_id, created_by_user_id)
                        VALUES (CAST(:grant_id AS uuid), CAST(:agent_id AS uuid), CAST(:owner_id AS uuid))
                        """
                    ),
                    {"grant_id": payload.grant_id, "agent_id": payload.agent_id, "owner_id": owner["user_id"]},
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail="MCP grant or agent is already bound") from exc

        with engine.connect() as connection:
            return _read_back_grant(connection, payload.grant_id)
    finally:
        engine.dispose()


@router.delete("/{grant_id}", summary="Unbind a named agent from an MCP OAuth grant")
def unbind_mcp_agent(grant_id: str, response: Response, _: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            deleted = connection.execute(
                text("DELETE FROM mcp_agent_bindings WHERE grant_id = CAST(:grant_id AS uuid) RETURNING agent_id::text AS agent_id"),
                {"grant_id": grant_id},
            ).mappings().first()
        if deleted is None:
            raise HTTPException(status_code=404, detail="MCP binding not found")
        return {"ok": True, "grant_id": grant_id, "agent_id": deleted["agent_id"], "agent_binding_status": "UNBOUND"}
    finally:
        engine.dispose()
