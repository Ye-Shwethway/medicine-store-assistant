from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session
from app.multi_agent_review import (
    NativeReviewStartInput,
    _event,
    _insert_artifact,
    _parse_verdict,
    _provenance,
    _role_instruction,
    _session_participants,
    _set_status,
    _validate_attachment_refs,
    _work_item_detail,
)
from app.native_agent_runtime import NativeAgentInvokeInput, invoke_native_agent

router = APIRouter(prefix="/dashboard/api/ai-workspace/multi-agent", tags=["multi-agent-review-live"])


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _configured_context(
    task: str,
    participants: list[dict[str, Any]],
    prior_outputs: list[dict[str, Any]],
) -> str:
    sequence = " -> ".join(str(item["orchestration_role"]) for item in participants)
    parts = [
        "CONFIGURED REVIEW SEQUENCE:\n" + sequence,
        "Only the roles listed above are configured for this run. Do not imply that an unconfigured role has executed.",
        "OWNER TASK:\n" + task.strip(),
    ]
    for index, item in enumerate(prior_outputs, start=1):
        parts.append(
            f"PRIOR PARTICIPANT {index} — {item['role']} / {item['agent_display_name']}:\n{item['response']}"
        )
    return "\n\n".join(parts)


def _mark_failed(
    *,
    work_item_id: str,
    owner_user_id: str,
    participant: dict[str, Any] | None,
    reason_code: str,
) -> None:
    engine = _engine()
    try:
        with engine.begin() as connection:
            _set_status(connection, work_item_id, "FAILED")
            actor_id = participant["agent_id"] if participant else None
            role = participant.get("orchestration_role") if participant else None
            event_id = _event(
                connection,
                work_item_id,
                "NATIVE_PARTICIPANT_FAILED",
                "INTERNAL_AGENT" if participant else "SYSTEM",
                actor_id,
                {"role": role, "reason_code": reason_code},
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
                    "owner_user_id": owner_user_id,
                    "source_event_id": event_id,
                    "summary": "Native REVIEW failed" + (f" at {participant['display_name']}" if participant else ""),
                    "metadata": json.dumps({"role": role, "reason_code": reason_code}),
                },
            )
    finally:
        engine.dispose()


def _execute_live_review(
    *,
    work_item_id: str,
    owner: dict[str, str],
    task: str,
    participants: list[dict[str, Any]],
    owner_artifact_id: str,
) -> None:
    engine = _engine()
    prior_outputs: list[dict[str, Any]] = []
    previous_artifact_id = owner_artifact_id
    previous_artifact_version = 1
    try:
        for output_version, participant in enumerate(participants, start=1):
            role = participant["orchestration_role"]
            display_label = participant.get("display_label") or participant.get("role_label")
            message = _role_instruction(role, display_label) + "\n\n" + _configured_context(task, participants, prior_outputs)
            try:
                result = invoke_native_agent(
                    participant["agent_id"],
                    NativeAgentInvokeInput(message=message, temperature=0.2, max_output_tokens=2048),
                    Response(),
                    owner=owner,
                )
            except HTTPException:
                _mark_failed(
                    work_item_id=work_item_id,
                    owner_user_id=owner["user_id"],
                    participant=participant,
                    reason_code="NATIVE_AGENT_HTTP_ERROR",
                )
                return
            except Exception:
                _mark_failed(
                    work_item_id=work_item_id,
                    owner_user_id=owner["user_id"],
                    participant=participant,
                    reason_code="NATIVE_AGENT_RUNTIME_ERROR",
                )
                return

            response_text = str(result.get("response") or "").strip()
            if not response_text:
                _mark_failed(
                    work_item_id=work_item_id,
                    owner_user_id=owner["user_id"],
                    participant=participant,
                    reason_code="EMPTY_NATIVE_REVIEW_OUTPUT",
                )
                return

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
                    "summary": "Review ready",
                    "metadata": json.dumps({"final_artifact_id": previous_artifact_id}),
                },
            )
    except Exception:
        _mark_failed(
            work_item_id=work_item_id,
            owner_user_id=owner["user_id"],
            participant=None,
            reason_code="REVIEW_BACKGROUND_ERROR",
        )
    finally:
        engine.dispose()


@router.post("/reviews/live", status_code=status.HTTP_202_ACCEPTED, summary="Start one persisted live native REVIEW")
def start_live_review(
    payload: NativeReviewStartInput,
    background_tasks: BackgroundTasks,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    title = " ".join(payload.title.strip().split())[:180]
    task = payload.task.strip()
    if not title or not task:
        raise HTTPException(status_code=422, detail="title and task are required")

    engine = _engine()
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
                    "configured_roles": [item["orchestration_role"] for item in participants],
                    "evidence_conversation_id": payload.evidence_conversation_id,
                    "attachments": attachment_refs,
                    "attachment_processing": "NOT_PROCESSED",
                },
            )
            _event(
                connection,
                work_item_id,
                "WORK_ITEM_CREATED",
                "OWNER",
                owner["user_id"],
                {"artifact_id": owner_artifact_id, "configured_roles": [item["orchestration_role"] for item in participants]},
            )
            _set_status(connection, work_item_id, "REVIEWING")
            _event(
                connection,
                work_item_id,
                "NATIVE_REVIEW_STARTED",
                "OWNER",
                owner["user_id"],
                {
                    "participant_count": len(participants),
                    "configured_roles": [item["orchestration_role"] for item in participants],
                    "turn_streaming": "PERSISTED_POLLING",
                },
            )
            initial = _work_item_detail(connection, work_item_id)
    finally:
        engine.dispose()

    background_tasks.add_task(
        _execute_live_review,
        work_item_id=work_item_id,
        owner=dict(owner),
        task=task,
        participants=[dict(item) for item in participants],
        owner_artifact_id=owner_artifact_id,
    )
    return initial
