from __future__ import annotations

import json
import time
from typing import Any

import requests
from fastapi import HTTPException, Response

from app.native_agent_runtime import (
    NativeAgentInvokeInput,
    _assignment_available,
    _identity_prompt,
    _load_agent_and_chain,
    _model_output_limit,
    _read_bounded_json,
    _safe_error_code,
)
from app.native_agent_tools import execute_native_read_tool, native_read_tool_definitions
from app.provider_secrets import read_provider_secret

MAX_TOOL_ROUNDS = 4


def _assignment_supports_tools(assignment: dict[str, Any]) -> bool:
    if assignment.get("provider_kind") == "GEMINI":
        return False
    snapshot = assignment.get("snapshot_metadata") or {}
    return isinstance(snapshot, dict) and snapshot.get("supports_tools") is True


def _extract_message(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise RuntimeError("INVALID_RESPONSE")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("INVALID_RESPONSE")
    return message


def _extract_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict) and isinstance(part.get("text"), str)]
        merged = "".join(parts).strip()
        if merged:
            return merged
    raise RuntimeError("EMPTY_RESPONSE")


def _post_chat(
    assignment: dict[str, Any],
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    temperature: float,
    max_output_tokens: int,
) -> tuple[dict[str, Any], int]:
    secret = read_provider_secret(assignment.get("credential_ref"))
    if secret is None:
        raise RuntimeError("MISSING_CREDENTIAL")
    session = requests.Session()
    session.trust_env = False
    started = time.monotonic()
    try:
        payload = {
            "model": assignment["model_id"],
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "stream": False,
            "temperature": temperature,
            "max_tokens": _model_output_limit(assignment, max_output_tokens),
        }
        try:
            response = session.post(
                str(assignment["base_url"]).rstrip("/") + "/chat/completions",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + secret,
                    "User-Agent": "MedicineStoreAssistant/NativeAgentTools",
                },
                json=payload,
                timeout=(5, 45),
                allow_redirects=False,
                stream=True,
            )
        except requests.Timeout as exc:
            raise RuntimeError("TIMEOUT") from exc
        except requests.RequestException as exc:
            raise RuntimeError("NETWORK_ERROR") from exc
        return _read_bounded_json(response), max(0, int((time.monotonic() - started) * 1000))
    finally:
        session.close()


def invoke_native_agent_with_read_tools(
    agent_id: str,
    payload: NativeAgentInvokeInput,
    response: Response,
    *,
    owner: dict[str, str],
) -> dict[str, Any] | None:
    if owner.get("role") != "OWNER":
        return None

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    agent, chain = _load_agent_and_chain(agent_id)
    tools = native_read_tool_definitions()
    if not tools:
        return None

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
        if not _assignment_supports_tools(assignment):
            attempts.append({**base_attempt, "status": "SKIPPED", "error_code": "NATIVE_TOOLS_UNSUPPORTED", "latency_ms": None})
            continue

        system_prompt = _identity_prompt(agent) + (
            "\nFor this invocation, the runtime has supplied a bounded set of native MSA read tools. "
            "You may request those tools whenever current store evidence would improve the answer, including contextual follow-ups. "
            "Do not ask the user to manually supply facts that an exposed tool can retrieve. "
            "Tool visibility does not grant authority: the backend validates every request. "
            "Use tool results as the only source of current store-specific facts."
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.message.strip()},
        ]
        tool_trace: list[dict[str, Any]] = []
        total_latency = 0
        try:
            for round_index in range(MAX_TOOL_ROUNDS + 1):
                body, latency_ms = _post_chat(
                    assignment,
                    messages=messages,
                    tools=tools,
                    temperature=payload.temperature,
                    max_output_tokens=payload.max_output_tokens,
                )
                total_latency += latency_ms
                message = _extract_message(body)
                calls = message.get("tool_calls")
                if not isinstance(calls, list) or not calls:
                    text_out = _extract_text(message)
                    attempts.append({**base_attempt, "status": "SUCCESS", "error_code": None, "latency_ms": total_latency})
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
                        "tool_execution_enabled": True,
                        "native_tools_exposed": [item["function"]["name"] for item in tools],
                        "native_tool_calls": tool_trace,
                        "selected_provider_id": assignment["provider_id"],
                        "selected_provider_name": assignment["provider_name"],
                        "selected_provider_kind": assignment["provider_kind"],
                        "selected_saved_model_id": assignment["saved_model_id"],
                        "selected_model_id": assignment["model_id"],
                        "selected_model_name": assignment["model_name"],
                        "fallback_used": chain_index > 0,
                        "fallback_index": chain_index if chain_index > 0 else None,
                        "latency_ms": total_latency,
                        "attempts": attempts,
                        "response": text_out,
                    }
                if round_index >= MAX_TOOL_ROUNDS:
                    raise RuntimeError("TOOL_ROUND_LIMIT")

                messages.append({"role": "assistant", "content": message.get("content"), "tool_calls": calls})
                for call in calls:
                    if not isinstance(call, dict):
                        continue
                    call_id = str(call.get("id") or "")
                    fn = call.get("function") if isinstance(call.get("function"), dict) else {}
                    name = str(fn.get("name") or "")
                    raw_args = fn.get("arguments")
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) and raw_args.strip() else {}
                    except json.JSONDecodeError:
                        args = {}
                    if not isinstance(args, dict):
                        args = {}
                    result = execute_native_read_tool(name, args)
                    tool_trace.append({"round": round_index + 1, "tool": name, "arguments": args, "status": "SUCCESS" if result.get("ok", True) else "REJECTED"})
                    messages.append({"role": "tool", "tool_call_id": call_id, "name": name, "content": json.dumps(result, ensure_ascii=False, default=str, separators=(",", ":"))})
        except RuntimeError as exc:
            attempts.append({**base_attempt, "status": "FAILED", "error_code": _safe_error_code(exc), "latency_ms": total_latency or None})
            continue

    hard_failures = [item for item in attempts if item.get("status") == "FAILED"]
    if hard_failures:
        raise HTTPException(status_code=502, detail={"code": "NATIVE_AGENT_TOOL_CHAIN_EXHAUSTED", "agent_id": agent["agent_id"], "attempts": attempts})
    return None
