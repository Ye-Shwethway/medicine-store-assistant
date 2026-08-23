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
            {"migration_batch_id": batch_id, "limit": max(1, min(int(limit), MAX_TOOL_ROWS))},
        )
    return {
        "tool": "new_unmapped_rows",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "migration_batch_id": batch_id,
        "items": items,
        "count": len(items),
        "limit": max(1, min(int(limit), MAX_TOOL_ROWS)),
    }


def latest_review_reasons(limit: int = MAX_REVIEW_REASONS) -> dict[str, Any]:
    summary = latest_inventory_summary()
    batch = summary.get("batch") or {}
    batch_id = batch.get("migration_batch_id")
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
            {"migration_batch_id": batch_id, "limit": max(1, min(int(limit), MAX_REVIEW_REASONS))},
        )
    return {
        "tool": "review_reasons",
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "migration_batch_id": batch_id,
        "items": items,
        "count": len(items),
    }


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

    # Preserve order and remove duplicates.
    return list(dict.fromkeys(selected))


def run_native_read_tools(tool_names: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for name in tool_names:
        if name == "inventory_summary":
            results.append(latest_inventory_summary())
        elif name == "new_unmapped_rows":
            results.append(latest_new_unmapped_rows())
        elif name == "review_reasons":
            results.append(latest_review_reasons())
    return results
