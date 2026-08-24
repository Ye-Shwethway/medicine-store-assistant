from __future__ import annotations

from app.multi_agent_review_live import _participant_provenance
from app.native_agent_tool_runtime import native_agent_read_allowed


def main() -> None:
    read_agent = {
        "agent_id": "00000000-0000-0000-0000-000000000001",
        "capability_scopes": ["mcp:read"],
        "authority_ceiling": "READ",
    }
    propose_agent = {
        "agent_id": "00000000-0000-0000-0000-000000000002",
        "capability_scopes": ["mcp:read"],
        "authority_ceiling": "PROPOSE",
    }
    no_scope_agent = {
        "agent_id": "00000000-0000-0000-0000-000000000003",
        "capability_scopes": [],
        "authority_ceiling": "CONTROL",
    }
    invalid_ceiling_agent = {
        "agent_id": "00000000-0000-0000-0000-000000000004",
        "capability_scopes": ["mcp:read"],
        "authority_ceiling": "NONE",
    }

    assert native_agent_read_allowed(read_agent) is True
    assert native_agent_read_allowed(propose_agent) is True
    assert native_agent_read_allowed(no_scope_agent) is False
    assert native_agent_read_allowed(invalid_ceiling_agent) is False

    # Session membership never unions privileges: evaluate each participant independently.
    participants = [read_agent, no_scope_agent]
    assert [native_agent_read_allowed(item) for item in participants] == [True, False]

    result = {
        "runtime_mode": "INTERNAL_MODEL",
        "transport": "NATIVE_MSA_BACKEND",
        "mcp_used": False,
        "agent_id": read_agent["agent_id"],
        "agent_display_name": "Verifier",
        "agent_call_name": "verifier",
        "agent_authority_ceiling": "READ",
        "tool_execution_enabled": True,
        "native_tools_exposed": ["inventory_summary", "new_unmapped_rows", "review_reasons"],
        "native_tool_calls": [
            {"round": 1, "tool": "new_unmapped_rows", "arguments": {"limit": 7}, "status": "SUCCESS"}
        ],
        "selected_provider_name": "Synthetic",
        "selected_model_name": "Synthetic model",
        "fallback_used": False,
        "latency_ms": 10,
        "attempts": [],
    }
    provenance = _participant_provenance(result, read_agent)
    assert provenance["native_store_tools_allowed"] is True
    assert provenance["tool_execution_enabled"] is True
    assert provenance["native_model_tools_executed"] == ["new_unmapped_rows"]
    assert provenance["native_tool_calls"][0]["status"] == "SUCCESS"

    no_tool_result = {
        "runtime_mode": "INTERNAL_MODEL",
        "transport": "NATIVE_MSA_BACKEND",
        "mcp_used": False,
        "agent_id": no_scope_agent["agent_id"],
        "agent_display_name": "No read",
        "agent_call_name": "no-read",
        "agent_authority_ceiling": "CONTROL",
        "tool_execution_enabled": False,
        "attempts": [],
    }
    no_tool_provenance = _participant_provenance(no_tool_result, no_scope_agent)
    assert no_tool_provenance["native_store_tools_allowed"] is False
    assert no_tool_provenance["native_tools_exposed"] == []
    assert no_tool_provenance["native_model_tools_executed"] == []

    print("d4_8_participant_native_read_tools=pass privilege_union=blocked provenance=pass")


if __name__ == "__main__":
    main()
