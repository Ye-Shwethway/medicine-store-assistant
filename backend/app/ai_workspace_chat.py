from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.ai_workspace_access import require_ai_chat_access
from app.dashboard_auth import _engine
from app.native_agent_runtime import NativeAgentInvokeInput, invoke_native_agent

router = APIRouter(prefix="/dashboard/api/ai-workspace", tags=["ai-workspace-chat"])

MAX_CONTEXT_MESSAGES = 24
MAX_MESSAGE_CHARS = 20_000


class ConversationCreateInput(BaseModel):
    agent_id: str
    title: str | None = Field(default=None, max_length=160)


class WorkspaceMessageInput(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _eligible_agent(connection: Any, agent_id: str) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT a.agent_id::text AS agent_id, a.display_name, a.call_name, a.description,
                   a.authority_ceiling, a.execution_policy, a.confirmation_policy
            FROM ai_agents a
            WHERE a.agent_id=CAST(:agent_id AS uuid)
              AND a.state='ACTIVE'
              AND a.runtime_mode='INTERNAL_MODEL'
              AND EXISTS (
                  SELECT 1
                  FROM ai_agent_model_assignments ama
                  JOIN ai_saved_provider_models sm ON sm.saved_model_id=ama.saved_model_id
                  JOIN ai_providers p ON p.provider_id=sm.provider_id
                  WHERE ama.agent_id=a.agent_id
                    AND ama.assignment_kind='PRIMARY'
                    AND ama.enabled=true
                    AND sm.state='ACTIVE'
                    AND sm.last_test_status='HEALTHY'
                    AND p.state='ENABLED'
              )
            """
        ),
        {"agent_id": agent_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=409, detail="Selected agent is not available for AI Workspace Chat")
    return dict(row)


def _owned_conversation(connection: Any, conversation_id: str, principal: dict[str, str]) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT c.conversation_id::text AS conversation_id,
                   c.owner_user_id::text AS owner_user_id,
                   c.agent_id::text AS agent_id,
                   c.title, c.state, c.created_at, c.updated_at,
                   a.display_name AS agent_display_name,
                   a.call_name AS agent_call_name
            FROM ai_workspace_conversations c
            JOIN ai_agents a ON a.agent_id=c.agent_id
            WHERE c.conversation_id=CAST(:conversation_id AS uuid)
              AND c.owner_user_id=CAST(:owner_user_id AS uuid)
            """
        ),
        {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
    ).mappings().first()
    if row is None:
        # Do not reveal whether another user's conversation exists.
        raise HTTPException(status_code=404, detail="Conversation not found")
    if row["state"] != "ACTIVE":
        raise HTTPException(status_code=409, detail="Conversation is not active")
    return dict(row)


def _context_prompt(history: list[dict[str, Any]], current_message: str) -> str:
    if not history:
        return current_message
    lines = [
        "Continue the following Medicine Store Assistant conversation. Preserve context and answer the newest user message.",
        "",
    ]
    for item in history[-MAX_CONTEXT_MESSAGES:]:
        speaker = "User" if item["role"] == "USER" else "Assistant"
        lines.append(f"{speaker}: {item['content']}")
    lines.extend(["", f"User: {current_message}"])
    return "\n".join(lines)


@router.get("/chat/agents", summary="List internal agents available to AI Workspace Chat")
def list_workspace_agents(
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    del principal
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT a.agent_id::text AS agent_id, a.display_name, a.call_name, a.description,
                           a.authority_ceiling, a.execution_policy, a.confirmation_policy
                    FROM ai_agents a
                    WHERE a.state='ACTIVE'
                      AND a.runtime_mode='INTERNAL_MODEL'
                      AND EXISTS (
                          SELECT 1
                          FROM ai_agent_model_assignments ama
                          JOIN ai_saved_provider_models sm ON sm.saved_model_id=ama.saved_model_id
                          JOIN ai_providers p ON p.provider_id=sm.provider_id
                          WHERE ama.agent_id=a.agent_id
                            AND ama.assignment_kind='PRIMARY'
                            AND ama.enabled=true
                            AND sm.state='ACTIVE'
                            AND sm.last_test_status='HEALTHY'
                            AND p.state='ENABLED'
                      )
                    ORDER BY lower(a.display_name), a.agent_id
                    """
                )
            ).mappings().all()
            return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.get("/conversations", summary="List current user's AI Workspace conversations")
def list_conversations(
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT c.conversation_id::text AS conversation_id,
                           c.agent_id::text AS agent_id, c.title, c.state,
                           c.created_at, c.updated_at,
                           a.display_name AS agent_display_name,
                           a.call_name AS agent_call_name,
                           (SELECT count(*) FROM ai_workspace_messages m WHERE m.conversation_id=c.conversation_id) AS message_count
                    FROM ai_workspace_conversations c
                    JOIN ai_agents a ON a.agent_id=c.agent_id
                    WHERE c.owner_user_id=CAST(:owner_user_id AS uuid)
                    ORDER BY c.updated_at DESC, c.created_at DESC
                    LIMIT 100
                    """
                ),
                {"owner_user_id": principal["user_id"]},
            ).mappings().all()
            return {"items": [dict(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.post("/conversations", summary="Create a single-agent AI Workspace conversation")
def create_conversation(
    payload: ConversationCreateInput,
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    conversation_id = str(uuid.uuid4())
    engine = _engine()
    try:
        with engine.begin() as connection:
            agent = _eligible_agent(connection, payload.agent_id)
            title = (payload.title or f"Chat with {agent['display_name']}").strip()[:160]
            if not title:
                title = f"Chat with {agent['display_name']}"
            row = connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_conversations (
                        conversation_id, owner_user_id, agent_id, title
                    ) VALUES (
                        CAST(:conversation_id AS uuid), CAST(:owner_user_id AS uuid),
                        CAST(:agent_id AS uuid), :title
                    )
                    RETURNING conversation_id::text AS conversation_id,
                              owner_user_id::text AS owner_user_id,
                              agent_id::text AS agent_id, title, state, created_at, updated_at
                    """
                ),
                {
                    "conversation_id": conversation_id,
                    "owner_user_id": principal["user_id"],
                    "agent_id": agent["agent_id"],
                    "title": title,
                },
            ).mappings().one()
            return {**dict(row), "agent_display_name": agent["display_name"], "agent_call_name": agent["call_name"]}
    finally:
        engine.dispose()


@router.get("/conversations/{conversation_id}", summary="Read one owned AI Workspace conversation")
def read_conversation(
    conversation_id: str,
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            conversation = _owned_conversation(connection, conversation_id, principal)
            rows = connection.execute(
                text(
                    """
                    SELECT message_id::text AS message_id, role, content, runtime_provenance, created_at
                    FROM ai_workspace_messages
                    WHERE conversation_id=CAST(:conversation_id AS uuid)
                    ORDER BY created_at, message_id
                    """
                ),
                {"conversation_id": conversation_id},
            ).mappings().all()
            return {"conversation": conversation, "messages": [dict(row) for row in rows]}
    finally:
        engine.dispose()


@router.post("/conversations/{conversation_id}/messages", summary="Send a message in one owned AI Workspace conversation")
def send_conversation_message(
    conversation_id: str,
    payload: WorkspaceMessageInput,
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message is required")

    engine = _engine()
    try:
        with engine.connect() as connection:
            conversation = _owned_conversation(connection, conversation_id, principal)
            _eligible_agent(connection, conversation["agent_id"])
            history = [
                dict(row)
                for row in connection.execute(
                    text(
                        """
                        SELECT role, content
                        FROM ai_workspace_messages
                        WHERE conversation_id=CAST(:conversation_id AS uuid)
                        ORDER BY created_at DESC, message_id DESC
                        LIMIT :limit
                        """
                    ),
                    {"conversation_id": conversation_id, "limit": MAX_CONTEXT_MESSAGES},
                ).mappings().all()
            ]
            history.reverse()

        contextual_message = _context_prompt(history, message)
        runtime = invoke_native_agent(
            conversation["agent_id"],
            NativeAgentInvokeInput(message=contextual_message),
            response,
            owner=principal,
        )

        user_message_id = str(uuid.uuid4())
        assistant_message_id = str(uuid.uuid4())
        provenance = {
            "transport": runtime.get("transport"),
            "mcp_used": runtime.get("mcp_used"),
            "provider_id": runtime.get("selected_provider_id"),
            "provider_name": runtime.get("selected_provider_name"),
            "model_id": runtime.get("selected_model_id"),
            "model_name": runtime.get("selected_model_name"),
            "fallback_used": runtime.get("fallback_used"),
            "latency_ms": runtime.get("latency_ms"),
            "attempts": runtime.get("attempts", []),
        }
        with engine.begin() as connection:
            # Re-check ownership immediately before persistence.
            _owned_conversation(connection, conversation_id, principal)
            connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_messages (message_id, conversation_id, role, content)
                    VALUES (CAST(:message_id AS uuid), CAST(:conversation_id AS uuid), 'USER', :content)
                    """
                ),
                {"message_id": user_message_id, "conversation_id": conversation_id, "content": message},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_messages (message_id, conversation_id, role, content, runtime_provenance)
                    VALUES (CAST(:message_id AS uuid), CAST(:conversation_id AS uuid), 'ASSISTANT', :content, CAST(:provenance AS jsonb))
                    """
                ),
                {
                    "message_id": assistant_message_id,
                    "conversation_id": conversation_id,
                    "content": runtime["response"],
                    "provenance": __import__("json").dumps(provenance),
                },
            )
            connection.execute(
                text("UPDATE ai_workspace_conversations SET updated_at=now() WHERE conversation_id=CAST(:conversation_id AS uuid)"),
                {"conversation_id": conversation_id},
            )
        return {
            "ok": True,
            "conversation_id": conversation_id,
            "user_message": {"message_id": user_message_id, "role": "USER", "content": message},
            "assistant_message": {
                "message_id": assistant_message_id,
                "role": "ASSISTANT",
                "content": runtime["response"],
                "runtime_provenance": provenance,
            },
        }
    finally:
        engine.dispose()
