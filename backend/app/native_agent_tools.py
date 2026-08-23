from __future__ import annotations

from typing import Any

from app.shadow_read_api import _query


MAX_TOOL_ROWS = 25
MAX_REVIEW_REASONS = 30


def latest_inventory_summary() -> dict[str, Any]:
    rows = _query(
        """
        SELECT mb.migration_batch_id::text AS migration_batch_id,
               mb.source_kind,
               mb.source_label,
               mb.status,
               mb.row_count,
               mb.created_at,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'SAFE') AS safe_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'REVIEW') AS review_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'CONFLICT') AS conflict_count,
               COUNT(msr.migration_source_row_id) FILTER (WHERE msr.classification = 'NEW_UNMAPPED') AS new_unmapped_count
        FROM migration_batches mb
        LEFT JOIN migration_source_rows msr ON msr.migration_batch_id=mb.migration_batch_id
        WHERE mb.source_kind='google_sheet_snapshot'
        GROUP BY mb.migration_batch_id, mb.source_kind, mb.source_label, mb.status, mb.row_count, mb.created_at
        ORDER BY mb.created_at DESC, mb.migration_batch_id DESC
        LIMIT 1
        """
    )
    return {
        "tool": "inventory_summary",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "batch": rows[0] if rows else None,
    }


def latest_new_unmapped_rows(limit: int = MAX_TOOL_ROWS) -> dict[str, Any]:
    summary = latest_inventory_summary()
    batch = summary.get("batch") or {}
    batch_id = batch.get("migration_batch_id")
    bounded_limit = max(1, min(int(limit), MAX_TOOL_ROWS))
    if not batch_id:
        items: list[dict[str, Any]] = []
    else:
        items = _query(
            """
            SELECT msr.migration_source_row_id::text AS migration_source_row_id,
                   msr.source_sheet,
                   msr.source_row_no,
                   msr.classification,
                   msr.review_reason,
                   msr.payload,
                   msr.created_at
            FROM migration_source_rows msr
            WHERE msr.migration_batch_id::text=:migration_batch_id
              AND msr.classification='NEW_UNMAPPED'
            ORDER BY msr.source_sheet, msr.source_row_no, msr.migration_source_row_id
            LIMIT :limit
            """,
            {"migration_batch_id": batch_id, "limit": bounded_limit},
        )
    return {
        "tool": "new_unmapped_rows",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "migration_batch_id": batch_id,
        "items": items,
        "count": len(items),
        "limit": bounded_limit,
    }


def latest_review_reasons(limit: int = MAX_REVIEW_REASONS) -> dict[str, Any]:
    summary = latest_inventory_summary()
    batch = summary.get("batch") or {}
    batch_id = batch.get("migration_batch_id")
    bounded_limit = max(1, min(int(limit), MAX_REVIEW_REASONS))
    if not batch_id:
        items: list[dict[str, Any]] = []
    else:
        items = _query(
            """
            SELECT classification,
                   COALESCE(review_reason, '(none)') AS review_reason,
                   COUNT(*) AS row_count
            FROM migration_source_rows
            WHERE migration_batch_id::text=:migration_batch_id
              AND classification IN ('REVIEW', 'CONFLICT', 'NEW_UNMAPPED')
            GROUP BY classification, COALESCE(review_reason, '(none)')
            ORDER BY row_count DESC, classification, review_reason
            LIMIT :limit
            """,
            {"migration_batch_id": batch_id, "limit": bounded_limit},
        )
    return {
        "tool": "review_reasons",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "migration_batch_id": batch_id,
        "items": items,
        "count": len(items),
    }


def native_read_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "inventory_summary",
                "description": "Read the latest bounded MSA inventory/shadow migration summary, including row and classification counts. Current evidence is test/shadow and non-canonical unless explicitly stated otherwise.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "new_unmapped_rows",
                "description": "Read bounded NEW_UNMAPPED shadow rows from the latest MSA migration batch, including source sheet/row, review reason, and payload.",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": MAX_TOOL_ROWS}},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "review_reasons",
                "description": "Read a bounded grouped summary of REVIEW, CONFLICT, and NEW_UNMAPPED reasons in the latest MSA shadow migration batch.",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": MAX_REVIEW_REASONS}},
                    "additionalProperties": False,
                },
            },
        },
    ]


def execute_native_read_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments or {}
    if name == "inventory_summary":
        return latest_inventory_summary()
    if name == "new_unmapped_rows":
        return latest_new_unmapped_rows(args.get("limit", MAX_TOOL_ROWS))
    if name == "review_reasons":
        return latest_review_reasons(args.get("limit", MAX_REVIEW_REASONS))
    return {"ok": False, "tool": name, "error_code": "NATIVE_TOOL_NOT_ALLOWED"}


def select_native_read_tools(message: str) -> list[str]:
    text_value = (message or "").casefold()
    selected: list[str] = []

    inventory_terms = (
        "inventory", "stock", "summary", "on hand", "on-hand", "လက်ကျန်", "စတော့", "စာရင်းချုပ်", "အကျဉ်းချုပ်"
    )
    unmapped_terms = (
        "new_unmapped", "unmapped", "mapping", "မပ်", "မချိတ်", "မကိုက်"
    )
    review_terms = (
        "review reason", "review reasons", "review", "conflict", "shadow", "စစ်ဆေး", "ပြန်စစ်", "အကြောင်းရင်း"
    )

    if any(term in text_value for term in unmapped_terms):
        selected.append("new_unmapped_rows")
    if any(term in text_value for term in review_terms):
        selected.append("review_reasons")
    if any(term in text_value for term in inventory_terms) or selected:
        selected.insert(0, "inventory_summary")

    return list(dict.fromkeys(selected))


def run_native_read_tools(tool_names: list[str]) -> list[dict[str, Any]]:
    return [execute_native_read_tool(name) for name in tool_names]
