from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dashboard_auth import require_dashboard_session
from app.inventory_view_engine import (
    FIELD_REGISTRY,
    SYSTEM_PRESETS,
    SortDirection,
    ViewColumn,
    ViewDefinition,
    _normalize_optional,
    _normalize_sort,
    _render_provider,
    _resolve_columns,
)

router = APIRouter(prefix="/dashboard/api/inventory-view", tags=["inventory-view-export"])

MAX_CSV_EXPORT_ROWS = 5000


def _resolve_export_columns(view: ViewDefinition, requested_fields: str | None) -> list[ViewColumn]:
    columns = _resolve_columns(view, requested_fields)
    preset_columns = {column.field: column for column in view.columns}
    return [
        ViewColumn(
            field=column.field,
            label=column.label or preset_columns.get(column.field, column).label,
            width=column.width,
        )
        for column in columns
    ]


def _csv_cell(value: Any, column: ViewColumn) -> Any:
    if value is None:
        return ""
    definition = FIELD_REGISTRY[column.field]
    if definition.data_type == "string":
        text = str(value)
        # Spreadsheet programs may evaluate cells beginning with these characters as formulas.
        # Preserve the visible value while forcing literal-text interpretation on paste/open.
        if text.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + text
        return text
    return value


def _serialize_csv(columns: list[ViewColumn], rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([column.label or FIELD_REGISTRY[column.field].label for column in columns])
    for row in rows:
        writer.writerow([_csv_cell(row.get(column.field), column) for column in columns])
    return buffer.getvalue()


def _export_rows(
    *,
    provider: str,
    q: str | None,
    mapping_status: str | None,
    source_classification: str | None,
    review_reason: str | None,
    sort_field: str | None,
    sort_dir: SortDirection | None,
) -> list[dict[str, Any]]:
    return _render_provider(
        provider,
        q=q,
        mapping_status=mapping_status,
        source_classification=source_classification,
        review_reason=review_reason,
        sort_field=sort_field,
        sort_dir=sort_dir,
        limit=MAX_CSV_EXPORT_ROWS + 1,
        offset=0,
    )


@router.get("/export.csv", dependencies=[Depends(require_dashboard_session)])
def inventory_view_export_csv(
    preset: str = Query(default="main-stock"),
    fields: str | None = Query(default=None, description="Optional comma-separated registered field keys in export order."),
    q: str | None = None,
    mapping_status: str | None = Query(default=None, max_length=64),
    source_classification: str | None = Query(default=None, max_length=64),
    review_reason: str | None = Query(default=None, max_length=255),
    sort_field: str | None = Query(default=None, max_length=80),
    sort_dir: str | None = Query(default=None, max_length=8),
) -> Response:
    view = SYSTEM_PRESETS.get(preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory view preset not found")

    columns = _resolve_export_columns(view, fields)
    normalized_q = _normalize_optional(q)
    normalized_mapping_status = _normalize_optional(mapping_status)
    normalized_source_classification = _normalize_optional(source_classification)
    normalized_review_reason = _normalize_optional(review_reason)
    normalized_sort_field, normalized_sort_dir = _normalize_sort(view.provider, sort_field, sort_dir)

    rows = _export_rows(
        provider=view.provider,
        q=normalized_q,
        mapping_status=normalized_mapping_status,
        source_classification=normalized_source_classification if preset == "migration-review" else None,
        review_reason=normalized_review_reason,
        sort_field=normalized_sort_field,
        sort_dir=normalized_sort_dir,
    )
    if len(rows) > MAX_CSV_EXPORT_ROWS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"CSV export exceeds the {MAX_CSV_EXPORT_ROWS}-row safety cap; narrow the current filters before exporting.",
        )

    csv_text = _serialize_csv(columns, rows)
    filename = f"msa-{view.view_id}.csv"
    return Response(
        content=("\ufeff" + csv_text).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "X-MSA-Export-Read-Only": "true",
            "X-MSA-Database-Canonical": "false",
            "X-MSA-Migration-Baseline-Accepted": "false",
        },
    )
