from __future__ import annotations

import json
import time
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session
from app.provider_secrets import read_provider_secret

router = APIRouter(tags=["native-agent-runtime"])

MAX_NATIVE_RESPONSE_BYTES = 512 * 1024
MAX_NATIVE_INPUT_CHARS = 20_000
DEFAULT_MAX_OUTPUT_TOKENS = 1024
HARD_MAX_OUTPUT_TOKENS = 4096


class NativeAgentInvokeInput(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_NATIVE_INPUT_CHARS)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_output_tokens: int = Field(default=DEFAULT_MAX_OUTPUT_TOKENS, ge=1, le=HARD_MAX_OUTPUT_TOKENS)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _read_bounded_json(response: requests.Response) -> dict[str, Any]:
    if 300 <= response.status_code < 400:
        raise RuntimeError("REDIRECT_BLOCKED")
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP_{response.status_code}")

    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=32768):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_NATIVE_RESPONSE_BYTES:
            raise RuntimeError("RESPONSE_TOO_LARGE")
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("INVALID_RESPONSE")
    return payload


def _safe_error_code(exc: Exception) -> str:
    value = str(exc)
    if value.startswith(("HTTP_", "NETWORK_ERROR", "TIMEOUT", "INVALID_", "EMPTY_", "RESPONSE_TOO_LARGE", "REDIRECT_BLOCKED", "MISSING_")):
        return value[:80]
    return "NATIVE_INVOKE_ERROR"


def _load_agent_and_chain(agent_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            agent = connection.execute(
                text(
                    """
                    SELECT agent_id::text AS agent_id, display_name, call_name, description,
                           runtime_mode, state, capability_scopes, location_scope,
                           authority_ceiling, execution_policy, confirmation_policy
                    FROM ai_agents
                    WHERE agent_id=CAST(:agent_id AS uuid)
                    """
                ),
                {"agent_id": agent_id},
            ).mappings().first()
            if agent is None:
                raise HTTPException(status_code=404, detail="AI agent not found")
            if agent["runtime_mode"] != "INTERNAL_MODEL":
                raise HTTPException(status_code=409, detail="Only INTERNAL_MODEL agents can be invoked by the native runtime")
            if agent["state"] != "ACTIVE":
                raise HTTPException(status_code=409, detail="Only ACTIVE internal agents can be invoked")

            assignments = connection.execute(
                text(
                    """
                    SELECT a.assignment_id::text AS assignment_id,
                           a.assignment_kind, a.position, a.enabled,
                           s.saved_model_id::text AS saved_model_id,
                           s.model_id, s.display_name AS model_name,
                           s.state AS saved_model_state, s.last_test_status,
                           s.snapshot_metadata,
                           p.provider_id::text AS provider_id,
                           p.display_name AS provider_name,
                           p.provider_kind, p.base_url, p.compatibility_mode,
                           p.credential_ref, p.state AS provider_state,
                           EXISTS (
                               SELECT 1 FROM ai_provider_models d
                               WHERE d.provider_id=s.provider_id AND d.model_id=s.model_id
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
    finally:
        engine.dispose()

    chain = [dict(row) for row in assignments]
    if not any(item["assignment_kind"] == "PRIMARY" and item["enabled"] for item in chain):
        raise HTTPException(status_code=409, detail="Internal agent has no enabled primary model assignment")
    return dict(agent), chain


def _identity_prompt(agent: dict[str, Any]) -> str:
    description = str(agent.get("description") or "").strip()
    parts = [
        f"You are {agent['display_name']}.",
        f"Your stable Medicine Store Assistant agent identity is {agent['agent_id']} and your call name is {agent['call_name']}.",
        "You are running through the native INTERNAL_MODEL runtime inside Medicine Store Assistant, independently of ChatGPT and independently of the public MCP transport.",
        f"Current authority ceiling: {agent['authority_ceiling']}. Execution policy: {agent['execution_policy']}. Confirmation policy: {agent['confirmation_policy']}.",
        "This bounded invocation has no MSA typed tools attached yet. Do not claim that you read, wrote, changed, approved, or executed any database/store operation unless tool execution is explicitly supplied in a later runtime slice.",
        "If asked to perform an unavailable store action, explain that this invocation can reason and answer but cannot yet execute MSA tools.",
        "Do not claim another configured agent identity even if the underlying provider model changes or fallback is used.",
    ]
    if description:
        parts.insert(3, f"Configured role/purpose: {description}")
    return "\n".join(parts)


def _model_output_limit(assignment: dict[str, Any], requested: int) -> int:
    snapshot = assignment.get("snapshot_metadata") or {}
    if not isinstance(snapshot, dict):
        return requested
    candidate = snapshot.get("max_output_tokens")
    try:
        model_limit = int(candidate) if candidate is not None else None
    except (TypeError, ValueError):
        model_limit = None
    if model_limit is None or model_limit <= 0:
        return requested
    return max(1, min(requested, model_limit))


def _extract_openai_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("INVALID_RESPONSE")
    first = choices[0]
    if not isinstance(first, dict):
        raise RuntimeError("INVALID_RESPONSE")
    message = first.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("INVALID_RESPONSE")
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        merged = "".join(text_parts).strip()
        if merged:
            return merged
    raise RuntimeError("EMPTY_RESPONSE")


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("INVALID_RESPONSE")
    first = candidates[0]
    if not isinstance(first, dict):
        raise RuntimeError("INVALID_RESPONSE")
    content = first.get("content")
    if not isinstance(content, dict):
        raise RuntimeError("INVALID_RESPONSE")
    parts = content.get("parts")
    if not isinstance(parts, list):
        raise RuntimeError("INVALID_RESPONSE")
    texts = [part.get("text", "") for part in parts if isinstance(part, dict) and isinstance(part.get("text"), str)]
    merged = "".join(texts).strip()
    if not merged:
        raise RuntimeError("EMPTY_RESPONSE")
    return merged


def _invoke_assignment(
    assignment: dict[str, Any],
    *,
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_output_tokens: int,
) -> tuple[str, int]:
    secret = read_provider_secret(assignment.get("credential_ref"))
    if secret is None:
        raise RuntimeError("MISSING_CREDENTIAL")

    session = requests.Session()
    session.trust_env = False
    started = time.monotonic()
    timeout = (5, 45)
    try:
        provider_kind = assignment["provider_kind"]
        base_url = str(assignment["base_url"]).rstrip("/")
        output_limit = _model_output_limit(assignment, max_output_tokens)
        if provider_kind == "GEMINI":
            endpoint = base_url + "/models/" + assignment["model_id"] + ":generateContent"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-goog-api-key": secret,
                "User-Agent": "MedicineStoreAssistant/NativeAgent",
            }
            payload = {
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_message}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": output_limit,
                },
            }
        else:
            endpoint = base_url + "/chat/completions"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + secret,
                "User-Agent": "MedicineStoreAssistant/NativeAgent",
            }
            payload = {
                "model": assignment["model_id"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "temperature": temperature,
                "max_tokens": output_limit,
            }

        try:
            response = session.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout,
                allow_redirects=False,
                stream=True,
            )
        except requests.Timeout as exc:
            raise RuntimeError("TIMEOUT") from exc
        except requests.RequestException as exc:
            raise RuntimeError("NETWORK_ERROR") from exc

        body = _read_bounded_json(response)
        text_out = _extract_gemini_text(body) if provider_kind == "GEMINI" else _extract_openai_text(body)
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        return text_out, latency_ms
    finally:
        session.close()


def _assignment_available(item: dict[str, Any]) -> tuple[bool, str | None]:
    if not item["enabled"]:
        return False, "ASSIGNMENT_DISABLED"
    if item["provider_state"] != "ENABLED":
        return False, "PROVIDER_DISABLED"
    if item["saved_model_state"] != "ACTIVE":
        return False, "MODEL_NOT_ACTIVE"
    if item["last_test_status"] != "HEALTHY":
        return False, "MODEL_NOT_HEALTHY"
    if not item["currently_discovered"]:
        return False, "MODEL_NOT_DISCOVERED"
    return True, None


@router.post(
    "/dashboard/api/agents/{agent_id}/invoke",
    summary="Invoke one internal agent through the native provider-backed runtime",
)
def invoke_native_agent(
    agent_id: str,
    payload: NativeAgentInvokeInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    del owner
    _no_store(response)
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message is required")

    agent, chain = _load_agent_and_chain(agent_id)
    system_prompt = _identity_prompt(agent)
    attempts: list[dict[str, Any]] = []

    for chain_index, assignment in enumerate(chain):
        available, unavailable_reason = _assignment_available(assignment)
        base_attempt = {
            "chain_index": chain_index,
            "assignment_kind": assignment["assignment_kind"],
            "position": assignment["position"],
            "provider_id": assignment["provider_id"],
            "provider_name": assignment["provider_name"],
            "provider_kind": assignment["provider_kind"],
            "saved_model_id": assignment["saved_model_id"],
            "model_id": assignment["model_id"],
            "model_name": assignment["model_name"],
        }
        if not available:
            attempts.append({**base_attempt, "status": "SKIPPED", "error_code": unavailable_reason, "latency_ms": None})
            continue

        try:
            text_out, latency_ms = _invoke_assignment(
                assignment,
                system_prompt=system_prompt,
                user_message=message,
                temperature=payload.temperature,
                max_output_tokens=payload.max_output_tokens,
            )
        except RuntimeError as exc:
            attempts.append({
                **base_attempt,
                "status": "FAILED",
                "error_code": _safe_error_code(exc),
                "latency_ms": None,
            })
            continue

        attempts.append({**base_attempt, "status": "SUCCESS", "error_code": None, "latency_ms": latency_ms})
        return {
            "ok": True,
            "status": "SUCCESS",
            "runtime_mode": "INTERNAL_MODEL",
            "transport": "NATIVE_MSA_BACKEND",
            "mcp_used": False,
            "agent_id": agent["agent_id"],
            "agent_display_name": agent["display_name"],
            "agent_call_name": agent["call_name"],
            "agent_authority_ceiling": agent["authority_ceiling"],
            "agent_execution_policy": agent["execution_policy"],
            "agent_confirmation_policy": agent["confirmation_policy"],
            "tool_execution_enabled": False,
            "selected_provider_id": assignment["provider_id"],
            "selected_provider_name": assignment["provider_name"],
            "selected_provider_kind": assignment["provider_kind"],
            "selected_saved_model_id": assignment["saved_model_id"],
            "selected_model_id": assignment["model_id"],
            "selected_model_name": assignment["model_name"],
            "fallback_used": chain_index > 0,
            "fallback_index": chain_index if chain_index > 0 else None,
            "latency_ms": latency_ms,
            "attempts": attempts,
            "response": text_out,
        }

    raise HTTPException(
        status_code=502,
        detail={
            "code": "NATIVE_AGENT_CHAIN_EXHAUSTED",
            "agent_id": agent["agent_id"],
            "attempts": attempts,
        },
    )
