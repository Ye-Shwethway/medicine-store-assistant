from __future__ import annotations

from pathlib import Path

from app.conversation_export import SNAPSHOT_SCHEMA_VERSION, _tool_summary
from app.multi_agent_review_live import RETRIEVAL_FIRST_RULE
from app.multi_agent_review_ui_api import router as multi_agent_review_ui_router


ROOT = Path(__file__).resolve().parent


def main() -> None:
    assert "retrieve the required evidence before evaluating" in RETRIEVAL_FIRST_RULE
    assert "Do not merely tell a later participant to call tools" in RETRIEVAL_FIRST_RULE

    tools, count = _tool_summary(
        {
            "native_unique_tools_executed": ["inventory_summary", "new_unmapped_rows", "inventory_summary"],
            "native_tool_call_count": 3,
        }
    )
    assert tools == ["inventory_summary", "new_unmapped_rows"]
    assert count == 3
    assert SNAPSHOT_SCHEMA_VERSION == "2026-08-24.v2"

    delete_route = None
    for route in multi_agent_review_ui_router.routes:
        if getattr(route, "path", "") == "/dashboard/api/ai-workspace/multi-agent/work-items/{work_item_id}":
            methods = set(getattr(route, "methods", set()) or set())
            if "DELETE" in methods:
                delete_route = route
                break
    assert delete_route is not None, "Owner Review DELETE route must exist on the Review UI router"

    registration_source = (ROOT / "multi_agent_review_registration.py").read_text(encoding="utf-8")
    assert "native_agent_runtime_router.include_router(multi_agent_review_ui_router)" in registration_source

    ui_source = (ROOT / "multi_agent_review_ui_api.py").read_text(encoding="utf-8")
    assert "w.status <> 'CANCELLED'" in ui_source
    assert "WORK_ITEM_DELETED_BY_OWNER" in ui_source
    assert "audit_evidence_preserved" in ui_source
    assert "UPDATE workflow_attention_items" in ui_source

    live_source = (ROOT / "multi_agent_review_live.py").read_text(encoding="utf-8")
    assert live_source.count("review_work_item_cancelled(work_item_id)") >= 4
    assert '"native_tool_call_count": len(tool_calls)' in live_source
    assert '"native_unique_tools_executed": list(dict.fromkeys(executed_tools))' in live_source

    js_source = (ROOT / "dashboard_assets" / "dashboard_multi_agent_live_export.js").read_text(encoding="utf-8")
    assert "review-delete-action" in js_source
    assert "Audit evidence will be preserved" in js_source
    assert "native_unique_tools_executed" in js_source

    print("multi_agent_review_polish_contract=pass")


if __name__ == "__main__":
    main()
