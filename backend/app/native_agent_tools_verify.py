from __future__ import annotations

import inspect

import app.ai_workspace_chat as chat
import app.native_agent_runtime as runtime
import app.native_agent_tool_runtime as tool_runtime
import app.native_agent_tools as tools


def main() -> None:
    assert tools.select_native_read_tools("Give me the inventory summary") == ["inventory_summary"]
    assert "inventory_summary" in tools.select_native_read_tools("လက်ကျန် စာရင်းချုပ် ပြောပါ")
    unmapped = tools.select_native_read_tools("Show NEW_UNMAPPED rows")
    assert unmapped == ["inventory_summary", "new_unmapped_rows"]
    review = tools.select_native_read_tools("Summarize shadow review reasons")
    assert "inventory_summary" in review and "review_reasons" in review
    assert tools.select_native_read_tools("Investigate this further") == []

    definitions = tools.native_read_tool_definitions()
    names = [item["function"]["name"] for item in definitions]
    assert names == ["inventory_summary", "new_unmapped_rows", "review_reasons"]
    rejected = tools.execute_native_read_tool("not_a_real_tool", {})
    assert rejected["ok"] is False and rejected["error_code"] == "NATIVE_TOOL_NOT_ALLOWED"

    tool_source = inspect.getsource(tools).upper()
    for forbidden in ("INSERT INTO", "UPDATE ", "DELETE FROM", "DROP TABLE", "ALTER TABLE"):
        assert forbidden not in tool_source, forbidden
    assert "MAX_TOOL_ROWS = 25" in inspect.getsource(tools)

    chat_source = inspect.getsource(chat)
    assert "Depends(require_ai_chat_access)" in chat_source
    assert 'principal.get("role") == "OWNER" and _agent_read_allowed(agent)' in chat_source
    assert "run_native_read_tools(requested_tools)" in chat_source
    assert "native_model_tool_calls" in chat_source
    assert "native_tools_exposed" in chat_source
    assert "MSA NATIVE READ RESULTS" in chat_source

    runtime_source = inspect.getsource(runtime)
    assert "Never invent Medicine Store Assistant facts" in runtime_source
    assert "If the user writes Burmese, answer in Burmese" in runtime_source
    assert "explicit 'MSA NATIVE READ RESULTS' block" in runtime_source
    assert "invoke_native_agent_with_read_tools" in runtime_source
    assert '"--- MSA NATIVE READ RESULTS ---" not in message' in runtime_source

    agentic_source = inspect.getsource(tool_runtime)
    assert 'owner.get("role") != "OWNER"' in agentic_source
    assert '"tool_choice": "auto"' in agentic_source
    assert "native_read_tool_definitions()" in agentic_source
    assert "execute_native_read_tool(name, args)" in agentic_source
    assert "MAX_TOOL_ROUNDS = 4" in agentic_source
    assert '"mcp_used": False' in agentic_source

    print("native_agent_hybrid_tool_runtime_contract=pass")


if __name__ == "__main__":
    main()
