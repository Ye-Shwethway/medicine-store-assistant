from __future__ import annotations

import json
import re
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session
from app.native_agent_runtime import NativeAgentInvokeInput, invoke_native_agent

router = APIRouter(prefix="/dashboard/api/ai-workspace/multi-agent", tags=["multi-agent-review"])

ROLE_VALUES = frozenset({"ANALYST", "REVIEWER", "SYNTHESIZER"})
VERDICT_RE = re.compile(r"^\s*VERDICT\s*:\s*(APPROVE|NEEDS_FIX|REJECT|COMMENT)\b", re.IGNORECASE)
MAX_TASK_CHARS = 20_000


class RoleAssignmentInput(BaseModel):
    agent_id: str
    orchestration_role: Literal["ANALYST", "REVIEWER", "SYNTHESIZER"]
    display_label: str | None = Field(default=None, max_length=80)


class SessionRolesInput(BaseModel):
    assignments: list[RoleAssignmentInput] = Field(min_length=1, max_length=32)


class NativeReviewStartInput(BaseModel):
    session_id: str
    title: str = Field(min_length=1, max_length=180)
    task: str = Field(min_length=1, max_length=MAX_TASK_CHARS)
    evidence_conversation_id: str | None = None
    attachment_ids: list[str] = Field(default_factory=list, max_length=4)


class RevisionRequestInput(BaseModel):
    instruction: str = Field(min_length=1, max_length=5000)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _clean_label(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    return cleaned[:80]


def _session_participants(connection: Any, session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    session = connection.execute(
        text(
            """
            SELECT session_id::text AS session_id, session_name, objective, mode, state,
                   created_by_user_id::text AS created_by_user_id
            FROM ai_agent_sessions
            WHERE session_id=CAST(:session_id AS uuid)
            """
        ),
        {"session_id": session_id},
    ).mappings().first()
    if session is None:
        raise HTTPException(status_code=404, detail="Review preset not found")
    if session["mode"] != "REVIEW":
        raise HTTPException(status_code=409, detail="Selected preset is not REVIEW mode")
    if session["state"] != "OPEN":
        raise HTTPException(status_code=409, detail="Review preset is closed")

    rows = connection.execute(
        text(
            """
            SELECT p.agent_id::text AS agent_id, p.position, p.role_label,
                   a.display_name, a.call_name, a.runtime_mode, a.state AS agent_state,
                   a.capability_scopes, a.authority_ceiling, a.execution_policy, a.confirmation_policy,
                   r.orchestration_role, r.display_label
            FROM ai_agent_session_participants p
            JOIN ai_agents a ON a.agent_id=p.agent_id
            LEFT JOIN workflow_session_participant_roles r
              ON r.session_id=p.session_id AND r.agent_id=p.agent_id
            WHERE p.session_id=CAST(:session_id AS uuid) AND p.is_active=true
            ORDER BY p.position, a.call_name
            """
        ),
        {"session_id": session_id},
    ).mappings().all()
    participants = [dict(row) for row in rows]
    if not participants:
        raise HTTPException(status_code=409, detail="Review preset has no active participants")
    if any(item["runtime_mode"] != "INTERNAL_MODEL" for item in participants):
        raise HTTPException(status_code=409, detail="This slice supports native-only REVIEW presets")
    if any(item["agent_state"] != "ACTIVE" for item in participants):
        raise HTTPException(status_code=409, detail="All REVIEW participants must be ACTIVE")
    if any(item["orchestration_role"] not in ROLE_VALUES for item in participants):
        raise HTTPException(status_code=409, detail="Assign ANALYST/REVIEWER/SYNTHESIZER roles before running REVIEW")
    return dict(session), participants


def _validate_attachment_refs(
    connection: Any,
    *,
    owner_user_id: str,
    conversation_id: str | None,
    attachment_ids: list[str],
) -> list[dict[str, Any]]:
    if not attachment_ids:
        return []
    if not conversation_id:
        raise HTTPException(status_code=422, detail="evidence_conversation_id is required when attachments are supplied")
    if len(set(attachment_ids)) != len(attachment_ids):
        raise HTTPException(status_code=422, detail="Duplicate attachment references are not allowed")
    rows = connection.execute(
        text(
            """
            SELECT attachment_id::text AS attachment_id, conversation_id::text AS conversation_id,
                   message_id::text AS message_id, kind, original_filename AS filename,
                   content_type, byte_size, sha256, state
            FROM ai_workspace_attachments
            WHERE conversation_id=CAST(:conversation_id AS uuid)
              AND owner_user_id=CAST(:owner_user_id AS uuid)
              AND attachment_id = ANY(CAST(:attachment_ids AS uuid[]))
            ORDER BY created_at, attachment_id
            """
        ),
        {
            "conversation_id": conversation_id,
            "owner_user_id": owner_user_id,
            "attachment_ids": attachment_ids,
        },
    ).mappings().all()
    if len(rows) != len(attachment_ids):
        raise HTTPException(status_code=404, detail="One or more attachment references are unavailable")
    return [dict(row) for row in rows]


def _event(connection: Any, work_item_id: str, event_type: str, actor_type: str, actor_id: str | None, payload: dict[str, Any]) -> str:
    return connection.execute(
        text(
            """
            INSERT INTO workflow_events (work_item_id, event_type, actor_type, actor_id, payload)
            VALUES (CAST(:work_item_id AS uuid), :event_type, :actor_type, :actor_id, CAST(:payload AS jsonb))
            RETURNING event_id::text
            """
        ),
        {
            "work_item_id": work_item_id,
            "event_type": event_type,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "payload": json.dumps(payload),
        },
    ).scalar_one()


def _set_status(connection: Any, work_item_id: str, target: str) -> None:
    connection.execute(
        text(
            """
            UPDATE workflow_work_items
            SET status=:target, updated_at=now(),
                completed_at=CASE WHEN :target IN ('COMMITTED','CANCELLED') THEN now() ELSE completed_at END
            WHERE work_item_id=CAST(:work_item_id AS uuid)
            """
        ),
        {"work_item_id": work_item_id, "target": target},
    )


def _insert_artifact(
    connection: Any,
    *,
    work_item_id: str,
    artifact_type: str,
    version: int,
    actor_type: str,
    actor_id: str | None,
    payload: dict[str, Any],
    supersedes_artifact_id: str | None = None,
) -> str:
    return connection.execute(
        text(
            """
            INSERT INTO workflow_artifacts (
                work_item_id, artifact_type, version, actor_type, actor_id, payload, supersedes_artifact_id
            ) VALUES (
                CAST(:work_item_id AS uuid), :artifact_type, :version, :actor_type, :actor_id,
                CAST(:payload AS jsonb), CAST(:supersedes_artifact_id AS uuid)
            )
            RETURNING artifact_id::text
            """
        ),
        {
            "work_item_id": work_item_id,
            "artifact_type": artifact_type,
            "version": version,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "payload": json.dumps(payload),
            "supersedes_artifact_id": supersedes_artifact_id,
        },
    ).scalar_one()


def _parse_verdict(output: str) -> str:
    match = VERDICT_RE.search(output or "")
    return match.group(1).upper() if match else "COMMENT"


def _role_instruction(role: str, display_label: str | None) -> str:
    label = display_label or role.title()
    if role == "ANALYST":
        return (
            f"Act in orchestration role ANALYST ({label}). Analyze the Owner task and evidence carefully. "
            "Produce a concrete evidence-grounded working artifact. Do not claim inventory mutation or approval."
        )
    if role == "REVIEWER":
        return (
            f"Act in orchestration role REVIEWER ({label}). Review the prior artifact for factual, evidence, policy, and reasoning problems. "
            "Your first line must be exactly one of: VERDICT: APPROVE, VERDICT: NEEDS_FIX, VERDICT: REJECT, VERDICT: COMMENT. "
            "Then explain findings. This is review state only and never authorizes store mutation."
        )
    return (
        f"Act in orchestration role SYNTHESIZER ({label}). Reconcile the Owner task, prior artifacts, and reviewer findings into a clear final recommendation for Owner review. "
        "Do not claim approval, commit, or store mutation."
    )


def _review_context(task: str, prior_outputs: list[dict[str, Any]]) -> str:
    parts = ["OWNER TASK:\n" + task.strip()]
    for index, item in enumerate(prior_outputs, start=1):
        parts.append(
            f"PRIOR PARTICIPANT {index} — {item['role']} / {item['agent_display_name']}:\n{item['response']}"
        )
    return "\n\n".join(parts)


def _provenance(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime_mode": result.get("runtime_mode"),
        "transport": result.get("transport"),
        "mcp_used": result.get("mcp_used"),
        "agent_id": result.get("agent_id"),
        "agent_display_name": result.get("agent_display_name"),
        "agent_call_name": result.get("agent_call_name"),
        "agent_authority_ceiling": result.get("agent_authority_ceiling"),
        "agent_execution_policy": result.get("agent_execution_policy"),
        "agent_confirmation_policy": result.get("agent_confirmation_policy"),
        "selected_provider_id": result.get("selected_provider_id"),
        "selected_provider_name": result.get("selected_provider_name"),
        "selected_provider_kind": result.get("selected_provider_kind"),
        "selected_saved_model_id": result.get("selected_saved_model_id"),
        "selected_model_id": result.get("selected_model_id"),
        "selected_model_name": result.get("selected_model_name"),
        "fallback_used": result.get("fallback_used"),
        "fallback_index": result.get("fallback_index"),
        "latency_ms": result.get("latency_ms"),
        "attempts": result.get("attempts", []),
    }


def _work_item_detail(connection: Any, work_item_id: str) -> dict[str, Any]:
    item = connection.execute(
        text(
            """
            SELECT work_item_id::text AS work_item_id, work_type, status, title, objective,
                   created_by_actor_type, created_by_actor_id, source_channel,
                   session_id::text AS session_id, correlation_id, created_at, updated_at, completed_at
            FROM workflow_work_items
            WHERE work_item_id=CAST(:work_item_id AS uuid)
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Work item not found")
    artifacts = connection.execute(
        text(
            """
            SELECT artifact_id::text AS artifact_id, artifact_type, version, actor_type, actor_id,
                   payload, content_hash, supersedes_artifact_id::text AS supersedes_artifact_id, created_at
            FROM workflow_artifacts WHERE work_item_id=CAST(:work_item_id AS uuid)
            ORDER BY created_at, artifact_id
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().all()
    reviews = connection.execute(
        text(
            """
            SELECT review_id::text AS review_id, artifact_id::text AS artifact_id, artifact_version,
                   reviewer_actor_type, reviewer_actor_id, verdict, notes, findings, correlation_id, created_at
            FROM workflow_reviews WHERE work_item_id=CAST(:work_item_id AS uuid)
            ORDER BY created_at, review_id
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().all()
    events = connection.execute(
        text(
            """
            SELECT event_id::text AS event_id, event_type, actor_type, actor_id, payload, correlation_id, created_at
            FROM workflow_events WHERE work_item_id=CAST(:work_item_id AS uuid)
            ORDER BY created_at, event_id
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().all()
    attention = connection.execute(
        text(
            """
            SELECT attention_id::text AS attention_id, category, status, target_actor_type, target_actor_id,
                   source_event_id::text AS source_event_id, summary, metadata, created_at, acknowledged_at, resolved_at
            FROM workflow_attention_items WHERE work_item_id=CAST(:work_item_id AS uuid)
            ORDER BY created_at, attention_id
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().all()
    return {
        **dict(item),
        "artifacts": [dict(row) for row in artifacts],
        "reviews": [dict(row) for row in reviews],
        "events": [dict(row) for row in events],
        "attention": [dict(row) for row in attention],
        "production_mutation": False,
        "database_canonical": False,
    }


@router.put("/sessions/{session_id}/roles", summary="Assign stable REVIEW orchestration roles")
def set_review_roles(
    session_id: str,
    payload: SessionRolesInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    if len({item.agent_id for item in payload.assignments}) != len(payload.assignments):
        raise HTTPException(status_code=422, detail="An agent may receive only one orchestration role per preset")
    engine = _engine()
    try:
        with engine.begin() as connection:
            session, participants = _session_participants_without_roles(connection, session_id)
            participant_ids = {item["agent_id"] for item in participants}
            supplied_ids = {item.agent_id for item in payload.assignments}
            if supplied_ids != participant_ids:
                raise HTTPException(status_code=422, detail="Role assignments must cover every active preset participant exactly once")
            connection.execute(
                text("DELETE FROM workflow_session_participant_roles WHERE session_id=CAST(:session_id AS uuid)"),
                {"session_id": session_id},
            )
            for item in payload.assignments:
                connection.execute(
                    text(
                        """
                        INSERT INTO workflow_session_participant_roles (
                            session_id, agent_id, orchestration_role, display_label, configured_by_user_id
                        ) VALUES (
                            CAST(:session_id AS uuid), CAST(:agent_id AS uuid), :orchestration_role,
                            :display_label, CAST(:owner_user_id AS uuid)
                        )
                        """
                    ),
                    {
                        "session_id": session_id,
                        "agent_id": item.agent_id,
                        "orchestration_role": item.orchestration_role,
                        "display_label": _clean_label(item.display_label),
                        "owner_user_id": owner["user_id"],
                    },
                )
        return {"ok": True, "session_id": session_id, "mode": session["mode"], "count": len(payload.assignments)}
    finally:
        engine.dispose()


def _session_participants_without_roles(connection: Any, session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    session = connection.execute(
        text(
            """
            SELECT session_id::text AS session_id, session_name, objective, mode, state
            FROM ai_agent_sessions WHERE session_id=CAST(:session_id AS uuid)
            """
        ),
        {"session_id": session_id},
    ).mappings().first()
    if session is None:
        raise HTTPException(status_code=404, detail="Review preset not found")
    if session["mode"] != "REVIEW" or session["state"] != "OPEN":
        raise HTTPException(status_code=409, detail="Roles can be assigned only to an open REVIEW preset")
    rows = connection.execute(
        text(
            """
            SELECT p.agent_id::text AS agent_id, p.position, a.runtime_mode, a.state AS agent_state
            FROM ai_agent_session_participants p
            JOIN ai_agents a ON a.agent_id=p.agent_id
            WHERE p.session_id=CAST(:session_id AS uuid) AND p.is_active=true
            ORDER BY p.position
            """
        ),
        {"session_id": session_id},
    ).mappings().all()
    participants = [dict(row) for row in rows]
    if not participants:
        raise HTTPException(status_code=409, detail="Review preset has no active participants")
    if any(item["runtime_mode"] != "INTERNAL_MODEL" for item in participants):
        raise HTTPException(status_code=409, detail="This slice supports native-only REVIEW presets")
    if any(item["agent_state"] != "ACTIVE" for item in participants):
        raise HTTPException(status_code=409, detail="All REVIEW participants must be ACTIVE")
    return dict(session), participants


@router.get("/sessions/{session_id}/roles", summary="Read stable REVIEW orchestration roles")
def get_review_roles(session_id: str, response: Response, owner: dict[str, str] = Depends(require_owner_session)) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            session, participants = _session_participants_without_roles(connection, session_id)
            rows = connection.execute(
                text(
                    """
                    SELECT r.agent_id::text AS agent_id, r.orchestration_role, r.display_label,
                           a.display_name, a.call_name, p.position
                    FROM workflow_session_participant_roles r
                    JOIN ai_agents a ON a.agent_id=r.agent_id
                    JOIN ai_agent_session_participants p ON p.session_id=r.session_id AND p.agent_id=r.agent_id
                    WHERE r.session_id=CAST(:session_id AS uuid)
                    ORDER BY p.position
                    """
                ),
                {"session_id": session_id},
            ).mappings().all()
            return {"session": session, "participants": participants, "roles": [dict(row) for row in rows]}
    finally:
        engine.dispose()


@router.post("/reviews", status_code=status.HTTP_201_CREATED, summary="Run one Owner-only native REVIEW workflow")
def run_native_review(
    payload: NativeReviewStartInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    title = " ".join(payload.title.strip().split())[:180]
    task = payload.task.strip()
    if not title or not task:
        raise HTTPException(status_code=422, detail="title and task are required")

    engine = _engine()
    work_item_id: str
    participants: list[dict[str, Any]]
    try:
        with engine.begin() as connection:
            session, participants = _session_participants(connection, payload.session_id)
            attachment_refs = _validate_attachment_refs(
                connection,
                owner_user_id=owner["user_id"],
                conversation_id=payload.evidence_conversation_id,
                attachment_ids=payload.attachment_ids,
            )
            work_item_id = connection.execute(
                text(
                    """
                    INSERT INTO workflow_work_items (
                        work_type, status, title, objective, created_by_actor_type,
                        created_by_actor_id, source_channel, session_id
                    ) VALUES (
                        'NATIVE_REVIEW', 'DRAFT', :title, :objective, 'OWNER', :owner_user_id,
                        'WEB', CAST(:session_id AS uuid)
                    )
                    RETURNING work_item_id::text
                    """
                ),
                {
                    "title": title,
                    "objective": task,
                    "owner_user_id": owner["user_id"],
                    "session_id": payload.session_id,
                },
            ).scalar_one()
            owner_artifact_id = _insert_artifact(
                connection,
                work_item_id=work_item_id,
                artifact_type="OWNER_TASK",
                version=1,
                actor_type="OWNER",
                actor_id=owner["user_id"],
                payload={
                    "task": task,
                    "session_name": session["session_name"],
                    "evidence_conversation_id": payload.evidence_conversation_id,
                    "attachments": attachment_refs,
                    "attachment_processing": "NOT_PROCESSED",
                },
            )
            _event(connection, work_item_id, "WORK_ITEM_CREATED", "OWNER", owner["user_id"], {"artifact_id": owner_artifact_id})
            _set_status(connection, work_item_id, "REVIEWING")
            _event(connection, work_item_id, "NATIVE_REVIEW_STARTED", "OWNER", owner["user_id"], {"participant_count": len(participants)})
    except Exception:
        engine.dispose()
        raise

    prior_outputs: list[dict[str, Any]] = []
    previous_artifact_id = owner_artifact_id
    previous_artifact_version = 1
    try:
        for output_version, participant in enumerate(participants, start=1):
            role = participant["orchestration_role"]
            display_label = participant.get("display_label") or participant.get("role_label")
            message = _role_instruction(role, display_label) + "\n\n" + _review_context(task, prior_outputs)
            try:
                result = invoke_native_agent(
                    participant["agent_id"],
                    NativeAgentInvokeInput(message=message, temperature=0.2, max_output_tokens=2048),
                    Response(),
                    owner=owner,
                )
            except HTTPException as exc:
                with engine.begin() as connection:
                    _set_status(connection, work_item_id, "FAILED")
                    failure_event_id = _event(
                        connection,
                        work_item_id,
                        "NATIVE_PARTICIPANT_FAILED",
                        "INTERNAL_AGENT",
                        participant["agent_id"],
                        {"role": role, "http_status": exc.status_code},
                    )
                    connection.execute(
                        text(
                            """
                            INSERT INTO workflow_attention_items (
                                work_item_id, category, target_actor_type, target_actor_id,
                                source_event_id, summary, metadata
                            ) VALUES (
                                CAST(:work_item_id AS uuid), 'WORKFLOW_FAILURE', 'OWNER', :owner_user_id,
                                CAST(:source_event_id AS uuid), :summary, CAST(:metadata AS jsonb)
                            )
                            """
                        ),
                        {
                            "work_item_id": work_item_id,
                            "owner_user_id": owner["user_id"],
                            "source_event_id": failure_event_id,
                            "summary": f"Native REVIEW failed at {participant['display_name']}",
                            "metadata": json.dumps({"role": role}),
                        },
                    )
                raise HTTPException(
                    status_code=502,
                    detail={"code": "NATIVE_REVIEW_PARTICIPANT_FAILED", "work_item_id": work_item_id, "agent_id": participant["agent_id"]},
                ) from exc

            response_text = str(result.get("response") or "").strip()
            if not response_text:
                raise HTTPException(status_code=502, detail={"code": "EMPTY_NATIVE_REVIEW_OUTPUT", "work_item_id": work_item_id})
            provenance = _provenance(result)
            with engine.begin() as connection:
                artifact_id = _insert_artifact(
                    connection,
                    work_item_id=work_item_id,
                    artifact_type="PARTICIPANT_OUTPUT",
                    version=output_version,
                    actor_type="INTERNAL_AGENT",
                    actor_id=participant["agent_id"],
                    payload={
                        "role": role,
                        "display_label": display_label,
                        "response": response_text,
                        "provenance": provenance,
                    },
                    supersedes_artifact_id=previous_artifact_id if role == "SYNTHESIZER" else None,
                )
                if role == "REVIEWER":
                    connection.execute(
                        text(
                            """
                            INSERT INTO workflow_reviews (
                                work_item_id, artifact_id, artifact_version,
                                reviewer_actor_type, reviewer_actor_id, verdict, notes, findings
                            ) VALUES (
                                CAST(:work_item_id AS uuid), CAST(:artifact_id AS uuid), :artifact_version,
                                'INTERNAL_AGENT', :reviewer_actor_id, :verdict, :notes, CAST(:findings AS jsonb)
                            )
                            """
                        ),
                        {
                            "work_item_id": work_item_id,
                            "artifact_id": previous_artifact_id,
                            "artifact_version": previous_artifact_version,
                            "reviewer_actor_id": participant["agent_id"],
                            "verdict": _parse_verdict(response_text),
                            "notes": response_text,
                            "findings": json.dumps({"review_output_artifact_id": artifact_id}),
                        },
                    )
                _event(
                    connection,
                    work_item_id,
                    "NATIVE_PARTICIPANT_COMPLETED",
                    "INTERNAL_AGENT",
                    participant["agent_id"],
                    {"role": role, "artifact_id": artifact_id, "artifact_version": output_version, "provenance": provenance},
                )
            prior_outputs.append(
                {
                    "role": role,
                    "agent_display_name": participant["display_name"],
                    "response": response_text,
                }
            )
            previous_artifact_id = artifact_id
            previous_artifact_version = output_version

        with engine.begin() as connection:
            _set_status(connection, work_item_id, "WAITING_OWNER")
            event_id = _event(
                connection,
                work_item_id,
                "OWNER_REVIEW_REQUIRED",
                "SYSTEM",
                None,
                {"final_artifact_id": previous_artifact_id, "participant_count": len(participants)},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO workflow_attention_items (
                        work_item_id, category, target_actor_type, target_actor_id,
                        source_event_id, summary, metadata
                    ) VALUES (
                        CAST(:work_item_id AS uuid), 'WAITING_OWNER', 'OWNER', :owner_user_id,
                        CAST(:source_event_id AS uuid), :summary, CAST(:metadata AS jsonb)
                    )
                    """
                ),
                {
                    "work_item_id": work_item_id,
                    "owner_user_id": owner["user_id"],
                    "source_event_id": event_id,
                    "summary": f"Review ready: {title}",
                    "metadata": json.dumps({"final_artifact_id": previous_artifact_id}),
                },
            )
            return _work_item_detail(connection, work_item_id)
    finally:
        engine.dispose()


@router.get("/work-items/{work_item_id}", summary="Read one Owner-visible REVIEW work item")
def get_review_work_item(
    work_item_id: str,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            item = _work_item_detail(connection, work_item_id)
            if item["created_by_actor_type"] == "OWNER" and item["created_by_actor_id"] != owner["user_id"]:
                raise HTTPException(status_code=404, detail="Work item not found")
            return item
    finally:
        engine.dispose()


@router.post("/work-items/{work_item_id}/return-for-revision", summary="Return REVIEW work to REVIEWING without store mutation")
def return_for_revision(
    work_item_id: str,
    payload: RevisionRequestInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    instruction = payload.instruction.strip()
    engine = _engine()
    try:
        with engine.begin() as connection:
            item = _work_item_detail(connection, work_item_id)
            if item["created_by_actor_type"] == "OWNER" and item["created_by_actor_id"] != owner["user_id"]:
                raise HTTPException(status_code=404, detail="Work item not found")
            if item["status"] != "WAITING_OWNER":
                raise HTTPException(status_code=409, detail="Only WAITING_OWNER work can be returned for revision")
            version = connection.execute(
                text(
                    """
                    SELECT COALESCE(MAX(version),0)+1 FROM workflow_artifacts
                    WHERE work_item_id=CAST(:work_item_id AS uuid) AND artifact_type='OWNER_REVISION'
                    """
                ),
                {"work_item_id": work_item_id},
            ).scalar_one()
            artifact_id = _insert_artifact(
                connection,
                work_item_id=work_item_id,
                artifact_type="OWNER_REVISION",
                version=int(version),
                actor_type="OWNER",
                actor_id=owner["user_id"],
                payload={"instruction": instruction},
            )
            connection.execute(
                text(
                    """
                    UPDATE workflow_attention_items
                    SET status='RESOLVED', resolved_at=now()
                    WHERE work_item_id=CAST(:work_item_id AS uuid) AND status <> 'RESOLVED'
                    """
                ),
                {"work_item_id": work_item_id},
            )
            _set_status(connection, work_item_id, "REVIEWING")
            _event(connection, work_item_id, "OWNER_RETURNED_FOR_REVISION", "OWNER", owner["user_id"], {"artifact_id": artifact_id})
            return _work_item_detail(connection, work_item_id)
    finally:
        engine.dispose()
