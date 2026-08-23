from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.shadow_read_api import _query


MAX_TOOL_ROWS = 25
MAX_REVIEW_REASONS = 30
EXCEL_EPOCH = datetime(1899, 12, 30, tzinfo=timezone.utc)


def _excel_serial_to_date(value: Any) -> str | None:
    try:
        serial = float(value)
    except (TypeError, ValueError):
        return None
    if serial <= 0 or serial > 200_000:
        return None
    try:
        return (EXCEL_EPOCH + timedelta(days=serial)).date().isoformat()
    except (OverflowError, ValueError):
        return None


def _evidence_status() -> dict[str, Any]:
    return {
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "label": "test/shadow, non-canonical evidence",
    }


def _display_payload(payload: Any) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    expiry_raw = source.get("expiry_date")
    return {
        "item_name": source.get("item_name"),
        "unit": source.get("unit"),
        "expiry_date": _excel_serial_to_date(expiry_raw),
        "expiry_date_raw": expiry_raw,
        "remaining_stock": source.get("remaining_stock"),
        "this_month_usage": source.get("this_month_usage"),
        "stock_status_today": source.get("stock_status_today"),
        "received_stock": source.get("received_stock"),
        "cms_name": source.get("cs_name"),
        "cms_serial_code": source.get("serial_code"),
    }


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
    batch = rows[0] if rows else None
    presentation = None
    if batch:
        presentation = {
            "total_rows": batch.get("row_count"),
            "safe_rows": batch.get("safe_count"),
            "review_rows": batch.get("review_count"),
            "conflict_rows": batch.get("conflict_count"),
            "new_unmapped_rows": batch.get("new_unmapped_count"),
            "source_kind": batch.get("source_kind"),
            "status": batch.get("status"),
            "evidence": _evidence_status(),
        }
    return {
        "tool": "inventory_summary",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "presentation": presentation,
        "batch": batch,
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
    presentation_items = [
        {
            "source_sheet": row.get("source_sheet"),
            "source_row": row.get("source_row_no"),
            "classification": row.get("classification"),
            "review_reason": row.get("review_reason"),
            **_display_payload(row.get("payload")),
        }
        for row in items
    ]
    return {
        "tool": "new_unmapped_rows",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "presentation": {
            "count": len(items),
            "limit": bounded_limit,
            "items": presentation_items,
            "evidence": _evidence_status(),
        },
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
        "presentation": {
            "groups": items,
            "evidence": _evidence_status(),
        },
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
                "description": "Read the latest bounded MSA inventory/shadow migration summary. Prefer the presentation object for user-facing answers; raw batch metadata is provenance/debug evidence.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "new_unmapped_rows",
                "description": "Read bounded NEW_UNMAPPED shadow rows. Prefer presentation.items for human-facing facts; raw items preserve source evidence and identifiers.",
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
                "description": "Read a bounded grouped summary of REVIEW, CONFLICT, and NEW_UNMAPPED reasons. Prefer presentation for normal answers; raw batch ID is provenance.",
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
    unmapped_terms = ("new_unmapped", "unmapped", "mapping", "မပ်", "မချိတ်", "မကိုက်")
    review_terms = ("review reason", "review reasons", "review", "conflict", "shadow", "စစ်ဆေး", "ပြန်စစ်", "အကြောင်းရင်း")
    if any(term in text_value for term in unmapped_terms):
        selected.append("new_unmapped_rows")
    if any(term in text_value for term in review_terms):
        selected.append("review_reasons")
    if any(term in text_value for term in inventory_terms) or selected:
        selected.insert(0, "inventory_summary")
    return list(dict.fromkeys(selected))


def run_native_read_tools(tool_names: list[str]) -> list[dict[str, Any]]:
    return [execute_native_read_tool(name) for name in tool_names]
