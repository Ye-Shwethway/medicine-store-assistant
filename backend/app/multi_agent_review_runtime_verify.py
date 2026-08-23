from __future__ import annotations

import secrets

from fastapi import Response
from sqlalchemy import text

from app.dashboard_auth import _engine, ensure_bootstrap_owner
from app.multi_agent_review import NativeReviewStartInput, run_native_review
import app.multi_agent_review as review_module


def _fake_invoke(agent_id, payload, response, owner):
    message = payload.message
    if "REVIEWER" in message:
        body = "VERDICT: APPROVE\nDeterministic runtime verification review."
    elif "SYNTHESIZER" in message:
        body = "Deterministic runtime verification synthesis."
    else:
        body = "Deterministic runtime verification analysis."
    return {
        "ok": True,
        "status": "SUCCESS",
        "runtime_mode": "INTERNAL_MODEL",
        "transport": "NATIVE_MSA_BACKEND",
        "mcp_used": False,
        "agent_id": agent_id,
        "agent_display_name": "Runtime verifier",
        "agent_call_name": "runtime-verifier",
        "agent_authority_ceiling": "READ_ONLY",
        "agent_execution_policy": "MANUAL",
        "agent_confirmation_policy": "ALWAYS",
        "selected_provider_id": "runtime-verifier",
        "selected_provider_name": "Runtime verifier",
        "selected_provider_kind": "TEST",
        "selected_saved_model_id": "runtime-verifier",
        "selected_model_id": "runtime-verifier",
        "selected_model_name": "Runtime verifier",
        "fallback_used": False,
        "fallback_index": None,
        "latency_ms": 0,
        "attempts": [],
        "response": body,
    }


def main() -> None:
    owner = ensure_bootstrap_owner()
    engine = _engine()
    title = f"D4.8 runtime verify {secrets.token_hex(6)}"
    try:
        with engine.connect() as connection:
            session = connection.execute(
                text(
                    """
                    SELECT s.session_id::text AS session_id
                    FROM ai_agent_sessions s
                    WHERE s.mode='REVIEW' AND s.state='OPEN'
                      AND EXISTS (
                        SELECT 1 FROM ai_agent_session_participants p
                        WHERE p.session_id=s.session_id AND p.is_active=true
                      )
                      AND NOT EXISTS (
                        SELECT 1
                        FROM ai_agent_session_participants p
                        LEFT JOIN workflow_session_participant_roles r
                          ON r.session_id=p.session_id AND r.agent_id=p.agent_id
                        WHERE p.session_id=s.session_id AND p.is_active=true
                          AND r.agent_id IS NULL
                      )
                    ORDER BY s.created_at DESC
                    LIMIT 1
                    """
                )
            ).mappings().first()
        if session is None:
            print("d4_8_review_runtime_verify=skip:no_configured_open_review_session")
            return

        original = review_module.invoke_native_agent
        review_module.invoke_native_agent = _fake_invoke
        try:
            result = run_native_review(
                NativeReviewStartInput(
                    session_id=session["session_id"],
                    title=title,
                    task="Deterministic D4.8 runtime persistence verification. Do not access or mutate inventory.",
                    evidence_conversation_id=None,
                    attachment_ids=[],
                ),
                Response(),
                owner=owner,
            )
        finally:
            review_module.invoke_native_agent = original

        if result.get("status") != "WAITING_OWNER":
            raise RuntimeError(f"unexpected review status: {result.get('status')}")
        if result.get("production_mutation") is not False or result.get("database_canonical") is not False:
            raise RuntimeError("authority boundary changed during review runtime verification")
        if not result.get("artifacts"):
            raise RuntimeError("review runtime verification produced no artifacts")
        print(
            "d4_8_review_runtime_verify=pass "
            f"status={result['status']} artifacts={len(result.get('artifacts', []))} reviews={len(result.get('reviews', []))}"
        )
    finally:
        try:
            with engine.begin() as connection:
                connection.execute(
                    text("DELETE FROM workflow_work_items WHERE title=:title"),
                    {"title": title},
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
