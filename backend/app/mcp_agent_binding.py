from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.dashboard_auth import _engine, require_owner_session

router = APIRouter(prefix="/dashboard/api/mcp-bindings", tags=["mcp-agent-binding"])


class MCPAgentBindRequest(BaseModel):
    grant_id: str
    agent_id: str


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


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
    return [dict(row) for row in rows]


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
            items = _binding_rows(connection)
            result = next((item for item in items if item["grant_id"] == payload.grant_id), None)
        if result is None:
            raise HTTPException(status_code=500, detail="Binding was created but could not be read back")
        return result
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
