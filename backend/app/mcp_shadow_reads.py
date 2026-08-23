from __future__ import annotations

from typing import Any, Literal

from mcp.types import ToolAnnotations

from app.audit_events import record_current_mcp_event
from app.mcp_server import _gate, mcp
from app.shadow_read_api import get_shadow_batch, list_shadow_rows, shadow_review_reasons

READ = ToolAnnotations(read_only_hint=True, open_world_hint=False)
ShadowClassification = Literal["SAFE", "REVIEW", "CONFLICT", "NEW_UNMAPPED"]


@mcp.tool(annotations=READ)
def msa_shadow_read_rows(
    classification: ShadowClassification | None = None,
    migration_batch_id: str | None = None,
    source_sheet: str | None = None,
    query: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Read bounded shadow migration source rows, optionally filtered by classification, batch, sheet, or search text.

    This is the typed detail surface for SAFE, REVIEW, CONFLICT, and NEW_UNMAPPED rows.
    It never writes inventory truth and never exposes arbitrary SQL.
    """
    denied = _gate("msa_shadow_read_rows", "mcp:read")
    if denied:
        return denied
    bounded_limit = min(max(int(limit), 1), 500)
    bounded_offset = max(int(offset), 0)
    result = list_shadow_rows(
        migration_batch_id=migration_batch_id,
        source_sheet=source_sheet,
        classification=classification,
        q=query,
        limit=bounded_limit,
        offset=bounded_offset,
    )
    record_current_mcp_event(
        action_type="msa_shadow_read_rows",
        capability_scope="mcp:read",
        outcome="SUCCESS",
        metadata={
            "classification": classification,
            "migration_batch_id": migration_batch_id,
            "source_sheet": source_sheet,
            "query_present": bool(query),
            "result_count": result.get("count", 0),
            "limit": bounded_limit,
            "offset": bounded_offset,
        },
    )
    return {"ok": True, "status": "AVAILABLE", **result}


@mcp.tool(annotations=READ)
def msa_shadow_read_batch(migration_batch_id: str) -> dict[str, Any]:
    """Read one shadow migration batch summary by stable batch identifier."""
    denied = _gate("msa_shadow_read_batch", "mcp:read")
    if denied:
        return denied
    result = get_shadow_batch(migration_batch_id)
    record_current_mcp_event(
        action_type="msa_shadow_read_batch",
        capability_scope="mcp:read",
        outcome="SUCCESS",
        metadata={"migration_batch_id": migration_batch_id},
    )
    return {"ok": True, "status": "AVAILABLE", **result}


@mcp.tool(annotations=READ)
def msa_shadow_read_review_reasons(migration_batch_id: str | None = None) -> dict[str, Any]:
    """Read REVIEW, CONFLICT, and NEW_UNMAPPED reason counts, optionally for one batch."""
    denied = _gate("msa_shadow_read_review_reasons", "mcp:read")
    if denied:
        return denied
    result = shadow_review_reasons(migration_batch_id=migration_batch_id)
    record_current_mcp_event(
        action_type="msa_shadow_read_review_reasons",
        capability_scope="mcp:read",
        outcome="SUCCESS",
        metadata={"migration_batch_id": migration_batch_id, "result_count": result.get("count", 0)},
    )
    return {"ok": True, "status": "AVAILABLE", **result}


# mcp_server imports this module before constructing mcp_http_app. Register both the
# final v2 extension and its explicit exclusions/replacements here so ChatGPT scans the
# finalized catalog rather than a construction-time partial snapshot.
import app.mcp_schema_v2 as _mcp_schema_v2  # noqa: E402,F401
import app.mcp_schema_v2_finalize as _mcp_schema_v2_finalize  # noqa: E402,F401
