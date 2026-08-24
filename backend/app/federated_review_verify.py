from __future__ import annotations

from pathlib import Path

import app.mcp_schema_v2 as schema
import app.mcp_shadow_reads  # noqa: F401 - loads v2.2 before MCP transport in production
from app.federated_review import router


ROOT = Path(__file__).resolve().parent


def main() -> None:
    routes = {(getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", set()) or set()))) for route in router.routes}
    assert any(path.endswith("/work-items/{work_item_id}/request-external-review") and "POST" in methods for path, methods in routes)

    assert schema.SCHEMA_VERSION == "2026-08-24.v2.2"
    assert "msa_federated_review_query" in schema.FINAL_TOOL_NAMES
    assert "msa_federated_review_submit" in schema.FINAL_TOOL_NAMES

    source = (ROOT / "federated_review.py").read_text(encoding="utf-8")
    assert "AGENT_BINDING_REQUIRED" in source
    assert '"mcp:read"' in source
    assert '"mcp:propose"' in source
    assert "ARTIFACT_BINDING_MISMATCH" in source
    assert "REQUEST_VERSION_STALE" in source
    assert "ARTIFACT_HASH_MISMATCH" in source
    assert "EXTERNAL_MCP_AGENT" in source
    assert "WAITING_EXTERNAL" in source
    assert "WAITING_OWNER" in source
    assert "EXTERNAL_REVIEW_REQUESTED" in source
    assert "EXTERNAL_REVIEW_SUBMITTED" in source
    assert '"production_mutation": False' in source
    assert '"database_canonical": False' in source

    schema_source = (ROOT / "mcp_schema_v22_federated.py").read_text(encoding="utf-8")
    assert "@mcp.tool(annotations=READ)" in schema_source
    assert "@mcp.tool(annotations=PROPOSE)" in schema_source
    assert "artifact_version: int" in schema_source
    assert "request_artifact_id: str" in schema_source

    ui_source = (ROOT / "dashboard_assets" / "dashboard_multi_agent_live_export.js").read_text(encoding="utf-8")
    assert "Request external review" in ui_source
    assert "WAITING_EXTERNAL" in ui_source
    assert "EXTERNAL_REVIEW_SUBMISSION" in ui_source
    assert "External MCP evidence" in ui_source

    print(
        "d4_8_federated_review_contract=pass "
        "exact_version_binding=pass external_authority=isolated mutation=none"
    )


if __name__ == "__main__":
    main()
