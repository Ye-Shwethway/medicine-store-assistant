from __future__ import annotations

import inspect

import app.ai_workspace_chat as chat
import app.native_agent_runtime as runtime
import app.native_agent_tools as tools


def main() -> None:
    assert tools.select_native_read_tools("Give me the inventory summary") == ["inventory_summary"]
    assert "inventory_summary" in tools.select_native_read_tools("လက်ကျန် စာရင်းချုပ် ပြောပါ")
    unmapped = tools.select_native_read_tools("Show NEW_UNMAPPED rows")
    assert unmapped == ["inventory_summary", "new_unmapped_rows"]
    review = tools.select_native_read_tools("Summarize shadow review reasons")
    assert "inventory_summary" in review and "review_reasons" in review

    tool_source = inspect.getsource(tools).upper()
    for forbidden in ("INSERT INTO", "UPDATE ", "DELETE FROM", "DROP TABLE", "ALTER TABLE"):
        assert forbidden not in tool_source, forbidden
    assert "MAX_TOOL_ROWS = 25" in inspect.getsource(tools)

    chat_source = inspect.getsource(chat)
    assert "Depends(require_ai_chat_access)" in chat_source
    assert "_agent_read_allowed(agent)" in chat_source
    assert "run_native_read_tools(requested_tools)" in chat_source
    assert "native_read_tools_executed" in chat_source
    assert "MSA NATIVE READ RESULTS" in chat_source

    runtime_source = inspect.getsource(runtime)
    assert "Never invent Medicine Store Assistant facts" in runtime_source
    assert "If the user writes Burmese, answer in Burmese" in runtime_source
    assert "explicit 'MSA NATIVE READ RESULTS' block" in runtime_source

    print("native_agent_grounded_reads_contract=pass")


if __name__ == "__main__":
    main()
