from __future__ import annotations

import hashlib
from typing import Any

from mcp.types import ToolAnnotations

import app.mcp_schema_v2 as schema
from app.federated_review import mcp_federated_review_query as _federated_query
from app.federated_review import mcp_federated_review_submit as _federated_submit
from app.mcp_server import mcp

READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
PROPOSE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)


@mcp.tool(annotations=READ)
def msa_federated_review_query(
    action: str,
    work_item_id: str | None = None,
    request_artifact_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Read optional external-review requests. Actions: list_pending, get_request. Exact artifact/version binding is returned by get_request."""
    return _federated_query(
        action=action,
        work_item_id=work_item_id,
        request_artifact_id=request_artifact_id,
        limit=limit,
        offset=offset,
    )


@mcp.tool(annotations=PROPOSE)
def msa_federated_review_submit(
    work_item_id: str,
    request_artifact_id: str,
    artifact_id: str,
    artifact_version: int,
    verdict: str,
    notes: str,
    findings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Submit evidence-only external review bound to one exact artifact version. Requires mcp:propose and never mutates inventory."""
    return _federated_submit(
        work_item_id=work_item_id,
        request_artifact_id=request_artifact_id,
        artifact_id=artifact_id,
        artifact_version=artifact_version,
        verdict=verdict,
        notes=notes,
        findings=findings,
    )


_NEW_TOOL_NAMES = {"msa_federated_review_query", "msa_federated_review_submit"}
schema.SCHEMA_VERSION = "2026-08-24.v2.2"
schema.FINAL_TOOL_NAMES = tuple(sorted(set(schema.FINAL_TOOL_NAMES) | _NEW_TOOL_NAMES))
schema.FINAL_TOOL_COUNT = len(schema.FINAL_TOOL_NAMES)
schema.FINAL_TOOL_HASH = hashlib.sha256("\n".join(schema.FINAL_TOOL_NAMES).encode("utf-8")).hexdigest()
