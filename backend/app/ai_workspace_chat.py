from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.ai_workspace_access import require_ai_chat_access
from app.dashboard_auth import _engine
from app.native_agent_runtime import NativeAgentInvokeInput, invoke_native_agent
from app.native_agent_tools import run_native_read_tools, select_native_read_tools

router = APIRouter(prefix="/dashboard/api/ai-workspace", tags=["ai-workspace-chat"])

MAX_CONTEXT_MESSAGES = 24
MAX_MESSAGE_CHARS = 20_000
MAX_MESSAGE_ATTACHMENTS = 4
AUTHORITY_ORDER = {"READ": 1, "PROPOSE": 2, "WRITE": 3, "CONTROL": 4}
WORKSPACE_OUTPUT_TOKENS = 2048
WORKSPACE_TOOL_OUTPUT_TOKENS = 4096


class ConversationCreateInput(BaseModel):
    agent_id: str
    title: str | None = Field(default=None, max_length=160)


class WorkspaceMessageInput(BaseModel):
    message: str = Field(default="", max_length=MAX_MESSAGE_CHARS)
    attachment_ids: list[str] = Field(default_factory=list, max_length=MAX_MESSAGE_ATTACHMENTS)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _eligible_agent(connection: Any, agent_id: str) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT a.agent_id::text AS agent_id, a.display_name, a.call_name, a.description,
                   a.capability_scopes, a.location_scope,
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


def _agent_read_allowed(agent: dict[str, Any]) -> bool:
    scopes = agent.get("capability_scopes") or []
    if isinstance(scopes, str):
        try:
            scopes = json.loads(scopes)
        except json.JSONDecodeError:
            scopes = [scopes]
    normalized = {str(scope).strip().lower() for scope in scopes if str(scope).strip()}
    ceiling = str(agent.get("authority_ceiling") or "").upper()
    return "mcp:read" in normalized and AUTHORITY_ORDER.get(ceiling, 0) >= AUTHORITY_ORDER["READ"]


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


def _attach_tool_context(contextual_message: str, tool_results: list[dict[str, Any]]) -> str:
    if not tool_results:
        return contextual_message
    serialized = json.dumps(tool_results, ensure_ascii=False, default=str, separators=(",", ":"))
    return (
        contextual_message
        + "\n\n--- MSA NATIVE READ RESULTS ---\n"
        + serialized
        + "\n--- END MSA NATIVE READ RESULTS ---\n"
        + "Use these results as the only source for current Medicine Store Assistant/store-specific facts in this answer. "
          "Prefer each tool result's presentation object for the normal user-facing answer. Raw batch IDs, row UUIDs, source labels, and raw field names are provenance/debug details: omit them unless the user requests them or they are needed to answer accurately. "
          "Deterministic derived display values supplied by the backend, such as a calendar date derived from a stored spreadsheet serial, may be shown as derived values while the raw source value remains provenance. "
          "The current database evidence is test/shadow and non-canonical unless a result explicitly says otherwise. Keep that warning concise. "
          "Do not invent missing rows, counts, prices, expiries, mappings, capabilities, or state transitions. "
          "A missing field or blocker does not prove that fixing it will automatically change classification: say revalidation/reclassification must run and pass. "
          "Clearly separate retrieved facts from your inference. Answer in the user's language when practical."
    )


def _attach_upload_context(contextual_message: str, attachments: list[dict[str, Any]]) -> str:
    if not attachments:
        return contextual_message
    metadata = [
        {
            "attachment_id": item["attachment_id"],
            "kind": item["kind"],
            "filename": item["original_filename"],
            "content_type": item["content_type"],
            "byte_size": item["byte_size"],
        }
        for item in attachments
    ]
    return (
        contextual_message
        + "\n\n--- USER ATTACHMENTS ---\n"
        + json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
        + "\n--- END USER ATTACHMENTS ---\n"
        + "Attachment metadata is persisted as conversation evidence, but attachment bytes are NOT supplied to this model in the current slice. "
          "Do not claim to have seen, OCRed, read, or interpreted the image/file contents. If the user's request requires the contents, state briefly that attachment processing is not wired yet."
    )


def _workspace_response_prompt(contextual_message: str) -> str:
    return (
        contextual_message
        + "\n\n--- AI WORKSPACE PRESENTATION ---\n"
          "Answer the user's actual question first. Use clean plain text that is easy to read on a phone. "
          "Do not use Markdown heading markers (#), bold/italic markers (** or __), backticks, or pipe-table syntax. "
          "Use short natural section labels and simple hyphen bullets only when useful. "
          "Avoid developer-style dumps, internal UUIDs, raw JSON keys, and repeated provenance unless the user explicitly asks for technical details. "
          "Preserve exact factual values from tool results and never turn an inference into a verified fact."
    )


def _load_pending_attachments(connection: Any, conversation_id: str, attachment_ids: list[str], principal: dict[str, str]) -> list[dict[str, Any]]:
    ids = list(dict.fromkeys(attachment_ids))
    if len(ids) != len(attachment_ids):
        raise HTTPException(status_code=422, detail="Duplicate attachment IDs are not allowed")
    if len(ids) > MAX_MESSAGE_ATTACHMENTS:
        raise HTTPException(status_code=422, detail=f"At most {MAX_MESSAGE_ATTACHMENTS} attachments can be sent with one message")
    if not ids:
        return []
    rows = connection.execute(
        text(
            """
            SELECT attachment_id::text AS attachment_id, kind, original_filename,
                   content_type, byte_size, sha256, state, message_id
            FROM ai_workspace_attachments
            WHERE conversation_id=CAST(:conversation_id AS uuid)
              AND owner_user_id=CAST(:owner_user_id AS uuid)
              AND attachment_id::text = ANY(CAST(:attachment_ids AS text[]))
            ORDER BY created_at, attachment_id
            """
        ),
        {
            "conversation_id": conversation_id,
            "owner_user_id": principal["user_id"],
            "attachment_ids": ids,
        },
    ).mappings().all()
    if len(rows) != len(ids):
        raise HTTPException(status_code=404, detail="One or more attachments were not found")
    result = [dict(row) for row in rows]
    if any(item["state"] != "PENDING" or item["message_id"] is not None for item in result):
        raise HTTPException(status_code=409, detail="Only pending attachments can be sent")
    return result


def _message_attachment_map(connection: Any, conversation_id: str, principal: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        text(
            """
            SELECT attachment_id::text AS attachment_id, message_id::text AS message_id,
                   kind, original_filename, content_type, byte_size, sha256, state, created_at
            FROM ai_workspace_attachments
            WHERE conversation_id=CAST(:conversation_id AS uuid)
              AND owner_user_id=CAST(:owner_user_id AS uuid)
              AND message_id IS NOT NULL
            ORDER BY created_at, attachment_id
            """
        ),
        {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
    ).mappings().all()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        item = dict(row)
        message_id = str(item.pop("message_id"))
        item["filename"] = item.pop("original_filename")
        item["processing_status"] = "NOT_PROCESSED"
        grouped.setdefault(message_id, []).append(item)
    return grouped


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
                           a.capability_scopes, a.location_scope,
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
                           (SELECT count(*) FROM ai_workspace_messages m WHERE m.conversation_id=c.conversation_id) AS message_count,
                           LEFT(COALESCE((
                               SELECT m.content
                               FROM ai_workspace_messages m
                               WHERE m.conversation_id=c.conversation_id AND m.role='USER'
                               ORDER BY m.created_at, m.message_id
                               LIMIT 1
                           ), ''), 96) AS first_user_preview
                    FROM ai_workspace_conversations c
                    JOIN ai_agents a ON a.agent_id=c.agent_id
                    WHERE c.owner_user_id=CAST(:owner_user_id AS uuid)
                      AND c.state='ACTIVE'
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


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete one owned AI Workspace conversation")
def delete_conversation(
    conversation_id: str,
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> Response:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            _owned_conversation(connection, conversation_id, principal)
            connection.execute(
                text(
                    """
                    DELETE FROM ai_workspace_conversations
                    WHERE conversation_id=CAST(:conversation_id AS uuid)
                      AND owner_user_id=CAST(:owner_user_id AS uuid)
                    """
                ),
                {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})
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
                    ORDER BY created_at,
                             CASE role WHEN 'USER' THEN 0 ELSE 1 END,
                             message_id
                    """
                ),
                {"conversation_id": conversation_id},
            ).mappings().all()
            attachments = _message_attachment_map(connection, conversation_id, principal)
            messages = []
            for row in rows:
                item = dict(row)
                item["attachments"] = attachments.get(item["message_id"], [])
                messages.append(item)
            return {"conversation": conversation, "messages": messages}
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
    if not message and not payload.attachment_ids:
        raise HTTPException(status_code=422, detail="message or attachment is required")

    engine = _engine()
    try:
        with engine.connect() as connection:
            conversation = _owned_conversation(connection, conversation_id, principal)
            agent = _eligible_agent(connection, conversation["agent_id"])
            pending_attachments = _load_pending_attachments(connection, conversation_id, payload.attachment_ids, principal)
            history = [
                dict(row)
                for row in connection.execute(
                    text(
                        """
                        SELECT role, content
                        FROM (
                            SELECT role, content, created_at, message_id
                            FROM ai_workspace_messages
                            WHERE conversation_id=CAST(:conversation_id AS uuid)
                            ORDER BY created_at DESC,
                                     CASE role WHEN 'ASSISTANT' THEN 0 ELSE 1 END,
                                     message_id DESC
                            LIMIT :limit
                        ) recent
                        ORDER BY created_at,
                                 CASE role WHEN 'USER' THEN 0 ELSE 1 END,
                                 message_id
                        """
                    ),
                    {"conversation_id": conversation_id, "limit": MAX_CONTEXT_MESSAGES},
                ).mappings().all()
            ]

        prompt_message = message or "The user sent attachment evidence without additional text."
        native_store_tools_allowed = principal.get("role") == "OWNER" and _agent_read_allowed(agent)
        requested_tools = select_native_read_tools(prompt_message) if native_store_tools_allowed else []
        tool_results: list[dict[str, Any]] = run_native_read_tools(requested_tools) if requested_tools else []

        contextual_message = _workspace_response_prompt(
            _attach_upload_context(
                _attach_tool_context(_context_prompt(history, prompt_message), tool_results),
                pending_attachments,
            )
        )
        output_tokens = WORKSPACE_TOOL_OUTPUT_TOKENS if tool_results else WORKSPACE_OUTPUT_TOKENS
        runtime = invoke_native_agent(
            conversation["agent_id"],
            NativeAgentInvokeInput(message=contextual_message, max_output_tokens=output_tokens),
            response,
            owner=principal,
        )

        user_message_id = str(uuid.uuid4())
        assistant_message_id = str(uuid.uuid4())
        model_tool_calls = runtime.get("native_tool_calls", []) or []
        model_tools_executed = [item.get("tool") for item in model_tool_calls if item.get("status") == "SUCCESS"]
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
            "native_read_tools_requested": requested_tools,
            "native_read_tools_executed": [item.get("tool") for item in tool_results],
            "native_tools_exposed": runtime.get("native_tools_exposed", []),
            "native_model_tool_calls": model_tool_calls,
            "native_model_tools_executed": model_tools_executed,
            "native_store_tools_allowed": native_store_tools_allowed,
            "agent_read_allowed": _agent_read_allowed(agent),
            "workspace_output_tokens": output_tokens,
            "attachment_ids": [item["attachment_id"] for item in pending_attachments],
            "attachment_processing": "NOT_PROCESSED",
        }
        with engine.begin() as connection:
            _owned_conversation(connection, conversation_id, principal)
            rebound = _load_pending_attachments(connection, conversation_id, payload.attachment_ids, principal)
            connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_messages (message_id, conversation_id, role, content)
                    VALUES (CAST(:message_id AS uuid), CAST(:conversation_id AS uuid), 'USER', :content)
                    """
                ),
                {"message_id": user_message_id, "conversation_id": conversation_id, "content": message},
            )
            if rebound:
                connection.execute(
                    text(
                        """
                        UPDATE ai_workspace_attachments
                        SET message_id=CAST(:message_id AS uuid), state='BOUND'
                        WHERE conversation_id=CAST(:conversation_id AS uuid)
                          AND owner_user_id=CAST(:owner_user_id AS uuid)
                          AND attachment_id::text = ANY(CAST(:attachment_ids AS text[]))
                          AND state='PENDING' AND message_id IS NULL
                        """
                    ),
                    {
                        "message_id": user_message_id,
                        "conversation_id": conversation_id,
                        "owner_user_id": principal["user_id"],
                        "attachment_ids": [item["attachment_id"] for item in rebound],
                    },
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
                    "provenance": json.dumps(provenance),
                },
            )
            connection.execute(
                text("UPDATE ai_workspace_conversations SET updated_at=now() WHERE conversation_id=CAST(:conversation_id AS uuid)"),
                {"conversation_id": conversation_id},
            )
        attachment_metadata = [
            {
                "attachment_id": item["attachment_id"],
                "kind": item["kind"],
                "filename": item["original_filename"],
                "content_type": item["content_type"],
                "byte_size": item["byte_size"],
                "processing_status": "NOT_PROCESSED",
            }
            for item in pending_attachments
        ]
        return {
            "ok": True,
            "conversation_id": conversation_id,
            "user_message": {"message_id": user_message_id, "role": "USER", "content": message, "attachments": attachment_metadata},
            "assistant_message": {
                "message_id": assistant_message_id,
                "role": "ASSISTANT",
                "content": runtime["response"],
                "runtime_provenance": provenance,
                "attachments": [],
            },
        }
    finally:
        engine.dispose()
