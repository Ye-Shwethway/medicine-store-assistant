from __future__ import annotations

import csv
import io
import json
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
from app.tabular_excel_export import ExcelColumn, ExcelWorkbookSpec, build_excel_workbook

router = APIRouter(prefix="/dashboard/api/inventory-view", tags=["inventory-view-export"])

MAX_EXPORT_ROWS = 5000
MAX_CSV_EXPORT_ROWS = MAX_EXPORT_ROWS
MAX_COLUMN_LABELS_QUERY = 8192
MAX_COLUMN_LABEL_LENGTH = 120


def _parse_column_labels(raw: str | None, selected_fields: set[str]) -> dict[str, str]:
    if not raw:
        return {}
    try:
        decoded = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="column_labels must be a JSON object") from exc
    if not isinstance(decoded, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="column_labels must be a JSON object")
    labels: dict[str, str] = {}
    for field, value in decoded.items():
        if field not in selected_fields or field not in FIELD_REGISTRY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Column label targets an invalid export field: {field}")
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Column label must be text: {field}")
        label = value.strip()
        if not label:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Column label cannot be blank: {field}")
        if len(label) > MAX_COLUMN_LABEL_LENGTH:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Column label is too long: {field}")
        labels[field] = label
    return labels


def _resolve_export_columns(
    view: ViewDefinition,
    requested_fields: str | None,
    column_labels: str | None = None,
) -> list[ViewColumn]:
    columns = _resolve_columns(view, requested_fields)
    selected_fields = {column.field for column in columns}
    labels = _parse_column_labels(column_labels, selected_fields)
    preset_columns = {column.field: column for column in view.columns}
    return [
        ViewColumn(
            field=column.field,
            label=labels.get(column.field) or column.label or preset_columns.get(column.field, column).label,
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


def _inventory_excel_number_format(field: str) -> str | None:
    if field.endswith("_qty"):
        return "0"
    if "price" in field:
        return "0.00"
    if field == "expiry_date":
        return "mmm-yy"
    return None


def _excel_columns(columns: list[ViewColumn]) -> tuple[ExcelColumn, ...]:
    return tuple(
        ExcelColumn(
            key=column.field,
            label=column.label or FIELD_REGISTRY[column.field].label,
            data_type=FIELD_REGISTRY[column.field].data_type,
            preferred_width=(column.width / 7.0) if column.width else None,
            number_format=_inventory_excel_number_format(column.field),
        )
        for column in columns
    )


def _serialize_xlsx(view: ViewDefinition, columns: list[ViewColumn], rows: list[dict[str, Any]]) -> bytes:
    return build_excel_workbook(
        ExcelWorkbookSpec(
            sheet_name=view.name,
            table_name=f"MSA_{view.view_id}",
            columns=_excel_columns(columns),
            rows=tuple(rows),
        )
    )


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
        limit=MAX_EXPORT_ROWS + 1,
        offset=0,
    )


def _resolve_request(
    *,
    preset: str,
    fields: str | None,
    column_labels: str | None,
    q: str | None,
    mapping_status: str | None,
    source_classification: str | None,
    review_reason: str | None,
    sort_field: str | None,
    sort_dir: str | None,
) -> tuple[ViewDefinition, list[ViewColumn], list[dict[str, Any]]]:
    view = SYSTEM_PRESETS.get(preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory view preset not found")

    columns = _resolve_export_columns(view, fields, column_labels)
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
    if len(rows) > MAX_EXPORT_ROWS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Export exceeds the {MAX_EXPORT_ROWS}-row safety cap; narrow the current filters before exporting.",
        )
    return view, columns, rows


def _response_headers(filename: str) -> dict[str, str]:
    return {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
        "X-MSA-Export-Read-Only": "true",
        "X-MSA-Database-Canonical": "false",
        "X-MSA-Migration-Baseline-Accepted": "false",
    }


@router.get("/export.xlsx", dependencies=[Depends(require_dashboard_session)])
def inventory_view_export_xlsx(
    preset: str = Query(default="main-stock"),
    fields: str | None = Query(default=None, description="Optional comma-separated registered field keys in export order."),
    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description="Optional JSON object of presentation-only header labels keyed by selected registered field."),
    q: str | None = None,
    mapping_status: str | None = Query(default=None, max_length=64),
    source_classification: str | None = Query(default=None, max_length=64),
    review_reason: str | None = Query(default=None, max_length=255),
    sort_field: str | None = Query(default=None, max_length=80),
    sort_dir: str | None = Query(default=None, max_length=8),
) -> Response:
    view, columns, rows = _resolve_request(
        preset=preset,
        fields=fields,
        column_labels=column_labels,
        q=q,
        mapping_status=mapping_status,
        source_classification=source_classification,
        review_reason=review_reason,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )
    return Response(
        content=_serialize_xlsx(view, columns, rows),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=_response_headers(f"msa-{view.view_id}.xlsx"),
    )


@router.get("/export.csv", dependencies=[Depends(require_dashboard_session)])
def inventory_view_export_csv(
    preset: str = Query(default="main-stock"),
    fields: str | None = Query(default=None, description="Optional comma-separated registered field keys in export order."),
    column_labels: str | None = Query(default=None, max_length=MAX_COLUMN_LABELS_QUERY, description="Optional JSON object of presentation-only header labels keyed by selected registered field."),
    q: str | None = None,
    mapping_status: str | None = Query(default=None, max_length=64),
    source_classification: str | None = Query(default=None, max_length=64),
    review_reason: str | None = Query(default=None, max_length=255),
    sort_field: str | None = Query(default=None, max_length=80),
    sort_dir: str | None = Query(default=None, max_length=8),
) -> Response:
    view, columns, rows = _resolve_request(
        preset=preset,
        fields=fields,
        column_labels=column_labels,
        q=q,
        mapping_status=mapping_status,
        source_classification=source_classification,
        review_reason=review_reason,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )
    csv_text = _serialize_csv(columns, rows)
    return Response(
        content=("\ufeff" + csv_text).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers=_response_headers(f"msa-{view.view_id}.csv"),
    )
