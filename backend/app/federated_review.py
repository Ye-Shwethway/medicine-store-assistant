from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.dashboard_auth import _engine, require_owner_session
from app.mcp_server import _bound_agent_context, _caller, _deny, _gate
from app.multi_agent_review import _event, _insert_artifact, _set_status, _work_item_detail

router = APIRouter(prefix="/dashboard/api/ai-workspace/multi-agent", tags=["multi-agent-review-federation"])

VALID_VERDICTS = {"APPROVE", "NEEDS_FIX", "REJECT", "COMMENT"}


class ExternalReviewRequestInput(BaseModel):
    artifact_id: str | None = None
    artifact_version: int | None = Field(default=None, ge=1)
    instruction: str | None = Field(default=None, max_length=4000)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _external_agent_context(tool_name: str, required_scope: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    denied = _gate(tool_name, required_scope)
    if denied:
        return None, denied
    context = _bound_agent_context(_caller())
    if not context or context.get("runtime_mode") != "EXTERNAL_MCP_CLIENT" or context.get("state") != "ACTIVE":
        return None, _deny(tool_name, required_scope, reason="AGENT_BINDING_REQUIRED")
    return context, None


def _latest_reviewable_artifact(connection, work_item_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        text(
            """
            SELECT artifact_id::text AS artifact_id, artifact_type, version, actor_type, actor_id, payload, content_hash, created_at
            FROM workflow_artifacts
            WHERE work_item_id=CAST(:work_item_id AS uuid)
              AND artifact_type IN ('PARTICIPANT_OUTPUT','OWNER_TASK','OWNER_REVISION')
            ORDER BY CASE artifact_type WHEN 'PARTICIPANT_OUTPUT' THEN 0 WHEN 'OWNER_REVISION' THEN 1 ELSE 2 END,
                     version DESC, created_at DESC
            LIMIT 1
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().first()
    return dict(row) if row else None


def _artifact_exact(connection, work_item_id: str, artifact_id: str, artifact_version: int) -> dict[str, Any] | None:
    row = connection.execute(
        text(
            """
            SELECT artifact_id::text AS artifact_id, artifact_type, version, actor_type, actor_id, payload, content_hash, created_at
            FROM workflow_artifacts
            WHERE work_item_id=CAST(:work_item_id AS uuid)
              AND artifact_id=CAST(:artifact_id AS uuid)
              AND version=:artifact_version
            LIMIT 1
            """
        ),
        {"work_item_id": work_item_id, "artifact_id": artifact_id, "artifact_version": artifact_version},
    ).mappings().first()
    return dict(row) if row else None


def _latest_external_request(connection, work_item_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        text(
            """
            SELECT artifact_id::text AS request_artifact_id, version AS request_version, payload, created_at
            FROM workflow_artifacts
            WHERE work_item_id=CAST(:work_item_id AS uuid)
              AND artifact_type='EXTERNAL_REVIEW_REQUEST'
            ORDER BY version DESC
            LIMIT 1
            """
        ),
        {"work_item_id": work_item_id},
    ).mappings().first()
    return dict(row) if row else None


@router.post("/work-items/{work_item_id}/request-external-review", summary="Freeze an exact artifact version for optional external MCP review")
def request_external_review(
    work_item_id: str,
    payload: ExternalReviewRequestInput,
    response: Response,
    owner: dict[str, str] = Depends(require_owner_session),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.begin() as connection:
            item = _work_item_detail(connection, work_item_id)
            if item["created_by_actor_type"] == "OWNER" and item["created_by_actor_id"] != owner["user_id"]:
                raise HTTPException(status_code=404, detail="Work item not found")
            if item["status"] != "WAITING_OWNER":
                raise HTTPException(status_code=409, detail="Only WAITING_OWNER Review work can request external review")

            bound = None
            if payload.artifact_id and payload.artifact_version:
                bound = _artifact_exact(connection, work_item_id, payload.artifact_id, payload.artifact_version)
            elif payload.artifact_id or payload.artifact_version:
                raise HTTPException(status_code=422, detail="artifact_id and artifact_version must be supplied together")
            else:
                bound = _latest_reviewable_artifact(connection, work_item_id)
            if not bound:
                raise HTTPException(status_code=404, detail="Reviewable artifact not found")

            request_version = int(connection.execute(
                text("SELECT COALESCE(MAX(version),0)+1 FROM workflow_artifacts WHERE work_item_id=CAST(:work_item_id AS uuid) AND artifact_type='EXTERNAL_REVIEW_REQUEST'"),
                {"work_item_id": work_item_id},
            ).scalar_one())
            request_artifact_id = _insert_artifact(
                connection,
                work_item_id=work_item_id,
                artifact_type="EXTERNAL_REVIEW_REQUEST",
                version=request_version,
                actor_type="OWNER",
                actor_id=owner["user_id"],
                payload={
                    "bound_artifact_id": bound["artifact_id"],
                    "bound_artifact_version": int(bound["version"]),
                    "bound_artifact_type": bound["artifact_type"],
                    "bound_content_hash": bound.get("content_hash"),
                    "instruction": (payload.instruction or "Review the exact bound artifact and return evidence-only findings for Owner review.").strip(),
                    "production_mutation": False,
                    "database_canonical": False,
                },
            )
            connection.execute(
                text("UPDATE workflow_attention_items SET status='RESOLVED', resolved_at=now() WHERE work_item_id=CAST(:work_item_id AS uuid) AND status <> 'RESOLVED'"),
                {"work_item_id": work_item_id},
            )
            _set_status(connection, work_item_id, "WAITING_EXTERNAL")
            event_id = _event(
                connection,
                work_item_id,
                "EXTERNAL_REVIEW_REQUESTED",
                "OWNER",
                owner["user_id"],
                {
                    "request_artifact_id": request_artifact_id,
                    "request_version": request_version,
                    "bound_artifact_id": bound["artifact_id"],
                    "bound_artifact_version": int(bound["version"]),
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO workflow_attention_items (
                        work_item_id, category, target_actor_type, target_actor_id,
                        source_event_id, summary, metadata
                    ) VALUES (
                        CAST(:work_item_id AS uuid), 'WAITING_EXTERNAL', 'EXTERNAL_MCP_AGENT', NULL,
                        CAST(:source_event_id AS uuid), :summary, CAST(:metadata AS jsonb)
                    )
                    """
                ),
                {
                    "work_item_id": work_item_id,
                    "source_event_id": event_id,
                    "summary": f"External review requested: {item['title']}",
                    "metadata": json.dumps({
                        "request_artifact_id": request_artifact_id,
                        "bound_artifact_id": bound["artifact_id"],
                        "bound_artifact_version": int(bound["version"]),
                    }),
                },
            )
            return _work_item_detail(connection, work_item_id)
    finally:
        engine.dispose()


def mcp_federated_review_query(
    *,
    action: str,
    work_item_id: str | None = None,
    request_artifact_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    tool_name = "msa_federated_review_query"
    context, denied = _external_agent_context(tool_name, "mcp:read")
    if denied:
        return denied
    bounded_limit = min(max(int(limit), 1), 50)
    bounded_offset = max(int(offset), 0)
    engine = _engine()
    try:
        with engine.connect() as connection:
            if action == "list_pending":
                rows = connection.execute(
                    text(
                        """
                        SELECT w.work_item_id::text AS work_item_id, w.title, w.objective, w.status,
                               r.artifact_id::text AS request_artifact_id, r.version AS request_version,
                               r.payload AS request_payload, r.created_at
                        FROM workflow_work_items w
                        JOIN LATERAL (
                            SELECT artifact_id, version, payload, created_at
                            FROM workflow_artifacts
                            WHERE work_item_id=w.work_item_id AND artifact_type='EXTERNAL_REVIEW_REQUEST'
                            ORDER BY version DESC LIMIT 1
                        ) r ON TRUE
                        WHERE w.status='WAITING_EXTERNAL'
                        ORDER BY r.created_at ASC
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    {"limit": bounded_limit, "offset": bounded_offset},
                ).mappings().all()
                return {
                    "ok": True,
                    "status": "AVAILABLE",
                    "action": action,
                    "external_agent_id": context["agent_id"],
                    "items": [dict(row) for row in rows],
                    "count": len(rows),
                    "database_canonical": False,
                    "migration_baseline_accepted": False,
                }

            if action == "get_request":
                if not work_item_id:
                    return _deny(tool_name, "mcp:read", reason="WORK_ITEM_ID_REQUIRED")
                request = _latest_external_request(connection, work_item_id)
                if not request:
                    return _deny(tool_name, "mcp:read", reason="REQUEST_NOT_FOUND")
                if request_artifact_id and request["request_artifact_id"] != request_artifact_id:
                    return _deny(tool_name, "mcp:read", reason="REQUEST_VERSION_STALE")
                item = connection.execute(
                    text("SELECT work_item_id::text AS work_item_id, title, objective, status, created_at, updated_at FROM workflow_work_items WHERE work_item_id=CAST(:work_item_id AS uuid)"),
                    {"work_item_id": work_item_id},
                ).mappings().first()
                if not item or item["status"] != "WAITING_EXTERNAL":
                    return _deny(tool_name, "mcp:read", reason="REQUEST_NOT_PENDING")
                req_payload = dict(request["payload"] or {})
                bound = _artifact_exact(connection, work_item_id, str(req_payload.get("bound_artifact_id")), int(req_payload.get("bound_artifact_version") or 0))
                if not bound:
                    return _deny(tool_name, "mcp:read", reason="BOUND_ARTIFACT_NOT_FOUND")
                return {
                    "ok": True,
                    "status": "AVAILABLE",
                    "action": action,
                    "external_agent_id": context["agent_id"],
                    "work_item": dict(item),
                    "request": request,
                    "bound_artifact": bound,
                    "production_mutation": False,
                    "database_canonical": False,
                    "migration_baseline_accepted": False,
                }
            return _deny(tool_name, "mcp:read", reason="ACTION_NOT_ALLOWED")
    except (TypeError, ValueError):
        return _deny(tool_name, "mcp:read", reason="INVALID_IDENTIFIER")
    finally:
        engine.dispose()


def mcp_federated_review_submit(
    *,
    work_item_id: str,
    request_artifact_id: str,
    artifact_id: str,
    artifact_version: int,
    verdict: str,
    notes: str,
    findings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tool_name = "msa_federated_review_submit"
    context, denied = _external_agent_context(tool_name, "mcp:propose")
    if denied:
        return denied
    normalized_verdict = str(verdict).strip().upper()
    if normalized_verdict not in VALID_VERDICTS:
        return _deny(tool_name, "mcp:propose", reason="VERDICT_NOT_ALLOWED")
    if not notes.strip():
        return _deny(tool_name, "mcp:propose", reason="NOTES_REQUIRED")
    try:
        UUID(str(work_item_id)); UUID(str(request_artifact_id)); UUID(str(artifact_id))
    except (TypeError, ValueError):
        return _deny(tool_name, "mcp:propose", reason="INVALID_IDENTIFIER")

    engine = _engine()
    try:
        with engine.begin() as connection:
            item = connection.execute(
                text("SELECT work_item_id::text AS work_item_id, title, status, created_by_actor_type, created_by_actor_id FROM workflow_work_items WHERE work_item_id=CAST(:work_item_id AS uuid) FOR UPDATE"),
                {"work_item_id": work_item_id},
            ).mappings().first()
            if not item:
                return _deny(tool_name, "mcp:propose", reason="WORK_ITEM_NOT_FOUND")
            if item["status"] != "WAITING_EXTERNAL":
                return _deny(tool_name, "mcp:propose", reason="REQUEST_NOT_PENDING")
            request = _latest_external_request(connection, work_item_id)
            if not request or request["request_artifact_id"] != request_artifact_id:
                return _deny(tool_name, "mcp:propose", reason="REQUEST_VERSION_STALE")
            req_payload = dict(request["payload"] or {})
            if str(req_payload.get("bound_artifact_id")) != str(artifact_id) or int(req_payload.get("bound_artifact_version") or 0) != int(artifact_version):
                return _deny(tool_name, "mcp:propose", reason="ARTIFACT_BINDING_MISMATCH")
            bound = _artifact_exact(connection, work_item_id, artifact_id, int(artifact_version))
            if not bound:
                return _deny(tool_name, "mcp:propose", reason="BOUND_ARTIFACT_NOT_FOUND")
            if req_payload.get("bound_content_hash") and bound.get("content_hash") != req_payload.get("bound_content_hash"):
                return _deny(tool_name, "mcp:propose", reason="ARTIFACT_HASH_MISMATCH")

            review_id = str(connection.execute(
                text(
                    """
                    INSERT INTO workflow_reviews (
                        work_item_id, artifact_id, artifact_version, reviewer_actor_type, reviewer_actor_id,
                        verdict, notes, findings
                    ) VALUES (
                        CAST(:work_item_id AS uuid), CAST(:artifact_id AS uuid), :artifact_version,
                        'EXTERNAL_MCP_AGENT', :reviewer_actor_id, :verdict, :notes, CAST(:findings AS jsonb)
                    ) RETURNING review_id::text
                    """
                ),
                {
                    "work_item_id": work_item_id,
                    "artifact_id": artifact_id,
                    "artifact_version": int(artifact_version),
                    "reviewer_actor_id": context["agent_id"],
                    "verdict": normalized_verdict,
                    "notes": notes.strip(),
                    "findings": json.dumps({
                        **(findings or {}),
                        "request_artifact_id": request_artifact_id,
                        "external_agent_display_name": context.get("display_name"),
                    }),
                },
            ).scalar_one())
            submission_version = int(connection.execute(
                text("SELECT COALESCE(MAX(version),0)+1 FROM workflow_artifacts WHERE work_item_id=CAST(:work_item_id AS uuid) AND artifact_type='EXTERNAL_REVIEW_SUBMISSION'"),
                {"work_item_id": work_item_id},
            ).scalar_one())
            submission_artifact_id = _insert_artifact(
                connection,
                work_item_id=work_item_id,
                artifact_type="EXTERNAL_REVIEW_SUBMISSION",
                version=submission_version,
                actor_type="EXTERNAL_MCP_AGENT",
                actor_id=context["agent_id"],
                payload={
                    "review_id": review_id,
                    "request_artifact_id": request_artifact_id,
                    "bound_artifact_id": artifact_id,
                    "bound_artifact_version": int(artifact_version),
                    "verdict": normalized_verdict,
                    "notes": notes.strip(),
                    "findings": findings or {},
                    "external_agent_display_name": context.get("display_name"),
                    "external_agent_call_name": context.get("call_name"),
                    "production_mutation": False,
                },
            )
            connection.execute(
                text("UPDATE workflow_attention_items SET status='RESOLVED', resolved_at=now() WHERE work_item_id=CAST(:work_item_id AS uuid) AND category='WAITING_EXTERNAL' AND status <> 'RESOLVED'"),
                {"work_item_id": work_item_id},
            )
            _set_status(connection, work_item_id, "WAITING_OWNER")
            submitted_event_id = _event(
                connection,
                work_item_id,
                "EXTERNAL_REVIEW_SUBMITTED",
                "EXTERNAL_MCP_AGENT",
                context["agent_id"],
                {
                    "review_id": review_id,
                    "submission_artifact_id": submission_artifact_id,
                    "request_artifact_id": request_artifact_id,
                    "bound_artifact_id": artifact_id,
                    "bound_artifact_version": int(artifact_version),
                    "verdict": normalized_verdict,
                },
            )
            if item["created_by_actor_type"] == "OWNER" and item["created_by_actor_id"]:
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
                        "owner_user_id": item["created_by_actor_id"],
                        "source_event_id": submitted_event_id,
                        "summary": f"External review received: {item['title']}",
                        "metadata": json.dumps({"review_id": review_id, "submission_artifact_id": submission_artifact_id}),
                    },
                )
            return {
                "ok": True,
                "status": "WAITING_OWNER",
                "work_item_id": work_item_id,
                "review_id": review_id,
                "submission_artifact_id": submission_artifact_id,
                "external_agent_id": context["agent_id"],
                "artifact_id": artifact_id,
                "artifact_version": int(artifact_version),
                "verdict": normalized_verdict,
                "production_mutation": False,
                "database_canonical": False,
                "migration_baseline_accepted": False,
            }
    finally:
        engine.dispose()
