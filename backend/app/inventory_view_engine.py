from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.dashboard_auth import require_dashboard_session
from app.shadow_read_api import _query

router = APIRouter(prefix="/dashboard/api/inventory-view", tags=["inventory-view"])

FieldKind = Literal["ENTITY_FIELD", "COMPUTED_FIELD", "COMMAND_EDITABLE_FIELD", "DISPLAY_HELPER"]
SortDirection = Literal["asc", "desc"]
REVIEW_CONTEXT_PRESETS = {"migration-review", "cms-mapping-review"}
MAX_REVIEW_CONTEXT_ROWS = 20


@dataclass(frozen=True)
class FieldDefinition:
    key: str
    label: str
    kind: FieldKind
    data_type: str
    editable: bool = False
    description: str = ""


@dataclass(frozen=True)
class ViewColumn:
    field: str
    label: str | None = None
    width: int | None = None


@dataclass(frozen=True)
class ViewDefinition:
    view_id: str
    name: str
    preset_type: str
    provider: str
    row_grain: str
    store_scope: str
    system_preset: bool
    columns: tuple[ViewColumn, ...]
    description: str


class InventoryReviewContextInput(BaseModel):
    preset: str = Field(max_length=80)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)
    q: str | None = Field(default=None, max_length=255)
    mapping_status: str | None = Field(default=None, max_length=64)
    source_classification: str | None = Field(default=None, max_length=64)
    review_reason: str | None = Field(default=None, max_length=255)
    sort_field: str | None = Field(default=None, max_length=80)
    sort_dir: str | None = Field(default=None, max_length=8)
    selected_indices: list[int] = Field(min_length=1, max_length=MAX_REVIEW_CONTEXT_ROWS)


FIELD_REGISTRY: dict[str, FieldDefinition] = {
    "display_no": FieldDefinition("display_no", "No.", "DISPLAY_HELPER", "integer", description="Presentation row number only."),
    "product_id": FieldDefinition("product_id", "Product ID", "ENTITY_FIELD", "uuid"),
    "lot_id": FieldDefinition("lot_id", "Lot ID", "ENTITY_FIELD", "uuid"),
    "local_item_name": FieldDefinition("local_item_name", "Items", "ENTITY_FIELD", "string", editable=False, description="Stable local Product display name."),
    "expiry_date": FieldDefinition("expiry_date", "Expiry Date", "ENTITY_FIELD", "date", editable=False),
    "unit": FieldDefinition("unit", "Unit", "ENTITY_FIELD", "string", editable=False),
    "store_code": FieldDefinition("store_code", "Store", "ENTITY_FIELD", "string"),
    "opening_qty": FieldDefinition("opening_qty", "Opening / Original Qty", "COMPUTED_FIELD", "decimal", description="Opening movement projection for the selected Store+Lot."),
    "received_qty": FieldDefinition("received_qty", "Received Stock", "COMPUTED_FIELD", "decimal"),
    "usage_qty": FieldDefinition("usage_qty", "This Month Usage", "COMPUTED_FIELD", "decimal"),
    "current_qty": FieldDefinition("current_qty", "Current Qty", "COMPUTED_FIELD", "decimal", description="Ledger-derived Store+Lot balance."),
    "cms_code": FieldDefinition("cms_code", "CMS Code", "ENTITY_FIELD", "string"),
    "cms_name": FieldDefinition("cms_name", "CMS Name", "ENTITY_FIELD", "string"),
    "mapping_status": FieldDefinition("mapping_status", "Mapping Status", "ENTITY_FIELD", "string"),
    "catalogue_price": FieldDefinition("catalogue_price", "Current Catalogue Price", "COMPUTED_FIELD", "decimal"),
    "accepted_operational_price": FieldDefinition("accepted_operational_price", "Accepted Store Price", "ENTITY_FIELD", "decimal"),
    "source_sheet": FieldDefinition("source_sheet", "Source Sheet", "DISPLAY_HELPER", "string"),
    "source_row_no": FieldDefinition("source_row_no", "Source Row", "DISPLAY_HELPER", "integer"),
    "source_classification": FieldDefinition("source_classification", "Source Class", "DISPLAY_HELPER", "string"),
    "review_reason": FieldDefinition("review_reason", "Review Reason", "DISPLAY_HELPER", "string"),
    "source_current_qty": FieldDefinition("source_current_qty", "Source Current Qty", "DISPLAY_HELPER", "decimal"),
}


SYSTEM_PRESETS: dict[str, ViewDefinition] = {
    "main-stock": ViewDefinition(
        view_id="main-stock",
        name="Main Stock",
        preset_type="MAIN_STOCK_COMPATIBILITY",
        provider="lot_balance",
        row_grain="PRODUCT_LOT",
        store_scope="MAIN",
        system_preset=True,
        description="Familiar Main Stock projection over normalized Product/Lot/Store/Ledger state.",
        columns=(
            ViewColumn("display_no", "No.", 72),
            ViewColumn("local_item_name", "Items", 280),
            ViewColumn("expiry_date", "Expiry Date", 130),
            ViewColumn("unit", "Unit", 90),
            ViewColumn("opening_qty", "Opening / Original Qty", 150),
            ViewColumn("received_qty", "Received Stock", 130),
            ViewColumn("usage_qty", "This Month Usage", 140),
            ViewColumn("current_qty", "Current Qty", 120),
            ViewColumn("cms_code", "CMS Code", 120),
            ViewColumn("cms_name", "CMS Name", 260),
            ViewColumn("mapping_status", "Mapping Status", 150),
            ViewColumn("catalogue_price", "Catalogue Price", 130),
            ViewColumn("accepted_operational_price", "Accepted Store Price", 150),
        ),
    ),
    "migration-review": ViewDefinition(
        view_id="migration-review",
        name="Migration Review",
        preset_type="MIGRATION_REVIEW",
        provider="migration_review",
        row_grain="SOURCE_MAIN_ROW",
        store_scope="MAIN",
        system_preset=True,
        description="Source-vs-shadow review projection. This is a system preset, not a separate inventory truth.",
        columns=(
            ViewColumn("source_row_no", "Source Row", 90),
            ViewColumn("local_item_name", "Local Item", 280),
            ViewColumn("expiry_date", "Expiry Date", 130),
            ViewColumn("unit", "Unit", 90),
            ViewColumn("source_current_qty", "Source Current Qty", 140),
            ViewColumn("current_qty", "Shadow Current Qty", 150),
            ViewColumn("cms_code", "CMS Code", 120),
            ViewColumn("cms_name", "CMS Name", 260),
            ViewColumn("mapping_status", "Mapping Status", 150),
            ViewColumn("source_classification", "Source Class", 120),
            ViewColumn("review_reason", "Review Reason", 320),
        ),
    ),
    "cms-mapping-review": ViewDefinition(
        view_id="cms-mapping-review",
        name="CMS Mapping Review",
        preset_type="CMS_MAPPING_REVIEW",
        provider="cms_mapping_review",
        row_grain="PRODUCT_CMS_MAPPING",
        store_scope="ALL",
        system_preset=True,
        description="Current non-accepted Product↔CMS mapping review state. Read-only; no mapping or price acceptance occurs here.",
        columns=(
            ViewColumn("local_item_name", "Local Item", 280),
            ViewColumn("unit", "Unit", 90),
            ViewColumn("cms_code", "CMS Code", 120),
            ViewColumn("cms_name", "CMS Name", 260),
            ViewColumn("mapping_status", "Mapping Status", 170),
            ViewColumn("catalogue_price", "Current Catalogue Price", 150),
            ViewColumn("accepted_operational_price", "Accepted Store Price", 150),
            ViewColumn("review_reason", "Review Reason", 360),
        ),
    ),
}


# Client sort keys never become SQL identifiers. Every sortable field resolves through a
# provider-owned expression below, and direction is normalized to the two literal values.
PROVIDER_SORT_FIELDS: dict[str, dict[str, str]] = {
    "lot_balance": {
        "display_no": "COALESCE(p.display_order, 2147483647)",
        "product_id": "p.product_id",
        "lot_id": "pl.lot_id",
        "local_item_name": "lower(p.local_name)",
        "expiry_date": "pl.expiry_date",
        "unit": "lower(COALESCE(p.default_unit,''))",
        "store_code": "lower(s.code)",
        "opening_qty": "COALESCE(o.opening_qty,0)",
        "received_qty": "COALESCE(r.received_qty,0)",
        "usage_qty": "COALESCE(u.usage_qty,0)",
        "current_qty": "COALESCE(b.current_qty,0)",
        "cms_code": "lower(COALESCE(map.cms_code_snapshot,''))",
        "cms_name": "lower(COALESCE(map.cms_name_snapshot,''))",
        "mapping_status": "COALESCE(map.mapping_status,'')",
        "catalogue_price": "ci.selling_price",
        "accepted_operational_price": "map.accepted_operational_price",
    },
    "migration_review": {
        "source_row_no": "msr.source_row_no",
        "local_item_name": "lower(COALESCE(msr.payload->>'product_name_candidate', msr.payload->>'item_name',''))",
        "expiry_date": "NULLIF(msr.payload->>'expiry_date','')::date",
        "unit": "lower(COALESCE(msr.payload->>'unit',''))",
        "source_current_qty": "NULLIF(msr.payload->>'stock_status_today','')::numeric(18,3)",
        "current_qty": "COALESCE(b.current_qty,0)",
        "cms_code": "lower(COALESCE(map.cms_code_snapshot, msr.payload->>'serial_code',''))",
        "cms_name": "lower(COALESCE(map.cms_name_snapshot, msr.payload->>'cs_name',''))",
        "mapping_status": "COALESCE(map.mapping_status,'')",
        "source_classification": "COALESCE(msr.classification,'')",
        "review_reason": "lower(COALESCE(msr.review_reason,''))",
    },
    "cms_mapping_review": {
        "product_id": "p.product_id",
        "local_item_name": "lower(p.local_name)",
        "unit": "lower(COALESCE(p.default_unit,''))",
        "cms_code": "lower(COALESCE(map.cms_code_snapshot,''))",
        "cms_name": "lower(COALESCE(map.cms_name_snapshot,''))",
        "mapping_status": "COALESCE(map.mapping_status,'')",
        "catalogue_price": "ci.selling_price",
        "accepted_operational_price": "map.accepted_operational_price",
        "review_reason": "lower(COALESCE(map.review_reason,''))",
    },
}

DEFAULT_ORDER_BY: dict[str, str] = {
    "lot_balance": "COALESCE(p.display_order, 2147483647), lower(p.local_name), pl.expiry_date NULLS LAST, pl.lot_id",
    "migration_review": "msr.source_row_no",
    "cms_mapping_review": "COALESCE(p.display_order, 2147483647), lower(p.local_name), p.product_id",
}

SORT_TIE_BREAKERS: dict[str, str] = {
    "lot_balance": "COALESCE(p.display_order, 2147483647), lower(p.local_name), pl.expiry_date NULLS LAST, pl.lot_id",
    "migration_review": "msr.source_row_no",
    "cms_mapping_review": "COALESCE(p.display_order, 2147483647), lower(p.local_name), p.product_id",
}


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _serialize_view(view: ViewDefinition) -> dict[str, Any]:
    data = asdict(view)
    data["columns"] = [asdict(column) for column in view.columns]
    return data


def _resolve_columns(view: ViewDefinition, requested_fields: str | None) -> list[ViewColumn]:
    if not requested_fields:
        return list(view.columns)
    result: list[ViewColumn] = []
    seen: set[str] = set()
    for raw in requested_fields.split(","):
        key = raw.strip()
        if not key or key in seen:
            continue
        if key not in FIELD_REGISTRY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown inventory view field: {key}")
        result.append(ViewColumn(key))
        seen.add(key)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one valid field is required")
    return result


def _normalize_optional(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def _normalize_sort(provider: str, sort_field: str | None, sort_dir: str | None) -> tuple[str | None, SortDirection | None]:
    field = _normalize_optional(sort_field)
    direction_raw = _normalize_optional(sort_dir)
    if not field:
        if direction_raw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_dir requires sort_field")
        return None, None
    provider_fields = PROVIDER_SORT_FIELDS.get(provider)
    if provider_fields is None or field not in provider_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Inventory field is not sortable for this view: {field}")
    direction = (direction_raw or "asc").lower()
    if direction not in {"asc", "desc"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_dir must be asc or desc")
    return field, direction  # type: ignore[return-value]


def _order_by_clause(provider: str, sort_field: str | None, sort_dir: SortDirection | None) -> str:
    if not sort_field:
        return DEFAULT_ORDER_BY[provider]
    expression = PROVIDER_SORT_FIELDS[provider][sort_field]
    direction = "ASC" if sort_dir == "asc" else "DESC"
    return f"{expression} {direction} NULLS LAST, {SORT_TIE_BREAKERS[provider]}"


def _review_context_view(preset: str) -> ViewDefinition:
    view = SYSTEM_PRESETS.get(preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory view preset not found")
    if preset not in REVIEW_CONTEXT_PRESETS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI review context is available only for review presets")
    return view


def _select_review_context_rows(
    view: ViewDefinition,
    provider_rows: list[dict[str, Any]],
    selected_indices: list[int],
) -> list[dict[str, Any]]:
    if len(set(selected_indices)) != len(selected_indices):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selected row indices must be unique")
    if any(index < 0 or index >= len(provider_rows) for index in selected_indices):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selected row index is outside the current rehydrated page")
    return [
        {column.field: provider_rows[index].get(column.field) for column in view.columns}
        for index in selected_indices
    ]


def _main_stock_rows(
    *,
    q: str | None,
    mapping_status: str | None,
    sort_field: str | None,
    sort_dir: SortDirection | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
    order_by = _order_by_clause("lot_balance", sort_field, sort_dir)
    if q:
        params["q"] = q
        search_clause = "AND (p.local_name ILIKE '%' || :q || '%' OR COALESCE(map.cms_code_snapshot,'') ILIKE '%' || :q || '%' OR COALESCE(map.cms_name_snapshot,'') ILIKE '%' || :q || '%')"
    if mapping_status:
        params["mapping_status"] = mapping_status
        mapping_clause = "AND map.mapping_status = :mapping_status"
    return _query(
        f"""
        WITH opening AS (
            SELECT store_id, lot_id, SUM(quantity)::numeric(18,3) AS opening_qty
            FROM inventory_transactions
            WHERE transaction_type='OPENING_BALANCE'
            GROUP BY store_id, lot_id
        ), receipts AS (
            SELECT store_id, lot_id, SUM(quantity)::numeric(18,3) AS received_qty
            FROM inventory_transactions
            WHERE transaction_type='RECEIPT'
              AND date_trunc('month', effective_date)=date_trunc('month', CURRENT_DATE)
            GROUP BY store_id, lot_id
        ), usage AS (
            SELECT store_id, lot_id, SUM(quantity)::numeric(18,3) AS usage_qty
            FROM inventory_transactions
            WHERE transaction_type='USAGE'
              AND date_trunc('month', effective_date)=date_trunc('month', CURRENT_DATE)
            GROUP BY store_id, lot_id
        ), current_mapping AS (
            SELECT DISTINCT ON (product_id)
                   product_id, catalogue_item_id, cms_code_snapshot, cms_name_snapshot,
                   mapping_status, accepted_operational_price, valid_from
            FROM product_cms_mappings
            WHERE valid_to IS NULL
            ORDER BY product_id,
                     CASE mapping_status WHEN 'ACTIVE_MATCH' THEN 0 WHEN 'REVIEW_REQUIRED' THEN 1 WHEN 'RECYCLED_CODE' THEN 2 WHEN 'CMS_DISCONTINUED' THEN 3 WHEN 'UNMAPPED' THEN 4 ELSE 5 END,
                     valid_from DESC
        )
        SELECT row_number() OVER (ORDER BY COALESCE(p.display_order, 2147483647), lower(p.local_name), pl.expiry_date NULLS LAST, pl.lot_id)::int AS display_no,
               p.product_id::text AS product_id,
               pl.lot_id::text AS lot_id,
               p.local_name AS local_item_name,
               pl.expiry_date,
               p.default_unit AS unit,
               s.code AS store_code,
               COALESCE(o.opening_qty,0)::numeric(18,3) AS opening_qty,
               COALESCE(r.received_qty,0)::numeric(18,3) AS received_qty,
               COALESCE(u.usage_qty,0)::numeric(18,3) AS usage_qty,
               COALESCE(b.current_qty,0)::numeric(18,3) AS current_qty,
               map.cms_code_snapshot AS cms_code,
               map.cms_name_snapshot AS cms_name,
               map.mapping_status,
               ci.selling_price AS catalogue_price,
               map.accepted_operational_price
        FROM product_lots pl
        JOIN products p ON p.product_id=pl.product_id
        JOIN stores s ON s.code='MAIN' AND s.active
        LEFT JOIN inventory_location_balances b ON b.store_id=s.store_id AND b.lot_id=pl.lot_id
        LEFT JOIN opening o ON o.store_id=s.store_id AND o.lot_id=pl.lot_id
        LEFT JOIN receipts r ON r.store_id=s.store_id AND r.lot_id=pl.lot_id
        LEFT JOIN usage u ON u.store_id=s.store_id AND u.lot_id=pl.lot_id
        LEFT JOIN current_mapping map ON map.product_id=p.product_id
        LEFT JOIN cms_catalogue_items ci ON ci.catalogue_item_id=map.catalogue_item_id
        WHERE p.active {search_clause} {mapping_clause}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
        """,
        params,
    )


def _migration_review_rows(
    *,
    q: str | None,
    mapping_status: str | None,
    source_classification: str | None,
    review_reason: str | None,
    sort_field: str | None,
    sort_dir: SortDirection | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
    classification_clause = ""
    reason_clause = ""
    order_by = _order_by_clause("migration_review", sort_field, sort_dir)
    if q:
        params["q"] = q
        search_clause = "AND (COALESCE(msr.payload->>'item_name','') ILIKE '%' || :q || '%' OR COALESCE(msr.payload->>'serial_code','') ILIKE '%' || :q || '%' OR COALESCE(msr.review_reason,'') ILIKE '%' || :q || '%')"
    if mapping_status:
        params["mapping_status"] = mapping_status
        mapping_clause = "AND map.mapping_status = :mapping_status"
    if source_classification:
        params["source_classification"] = source_classification
        classification_clause = "AND msr.classification = :source_classification"
    if review_reason:
        params["review_reason"] = review_reason
        reason_clause = "AND COALESCE(msr.review_reason,'') ILIKE '%' || :review_reason || '%'"
    return _query(
        f"""
        WITH latest_batch AS (
            SELECT migration_batch_id
            FROM migration_batches
            WHERE source_kind='f6d_google_sheet_snapshot'
            ORDER BY created_at DESC, migration_batch_id DESC
            LIMIT 1
        ), current_mapping AS (
            SELECT DISTINCT ON (product_id)
                   product_id, cms_code_snapshot, cms_name_snapshot, mapping_status, valid_from
            FROM product_cms_mappings
            WHERE valid_to IS NULL
            ORDER BY product_id, valid_from DESC
        )
        SELECT msr.source_row_no,
               COALESCE(msr.payload->>'product_name_candidate', msr.payload->>'item_name') AS local_item_name,
               NULLIF(msr.payload->>'expiry_date','')::date AS expiry_date,
               msr.payload->>'unit' AS unit,
               NULLIF(msr.payload->>'stock_status_today','')::numeric(18,3) AS source_current_qty,
               COALESCE(b.current_qty,0)::numeric(18,3) AS current_qty,
               COALESCE(map.cms_code_snapshot, msr.payload->>'serial_code') AS cms_code,
               COALESCE(map.cms_name_snapshot, msr.payload->>'cs_name') AS cms_name,
               map.mapping_status,
               msr.source_sheet,
               msr.classification AS source_classification,
               msr.review_reason
        FROM migration_source_rows msr
        JOIN latest_batch lb ON lb.migration_batch_id=msr.migration_batch_id
        LEFT JOIN products p ON lower(p.local_name)=lower(COALESCE(msr.payload->>'product_name_candidate', msr.payload->>'item_name'))
        LEFT JOIN product_lots pl ON pl.product_id=p.product_id AND pl.expiry_date IS NOT DISTINCT FROM NULLIF(msr.payload->>'expiry_date','')::date
        LEFT JOIN stores s ON s.code='MAIN' AND s.active
        LEFT JOIN inventory_location_balances b ON b.store_id=s.store_id AND b.lot_id=pl.lot_id
        LEFT JOIN current_mapping map ON map.product_id=p.product_id
        WHERE msr.source_sheet='Main Stock' {search_clause} {mapping_clause} {classification_clause} {reason_clause}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
        """,
        params,
    )


def _cms_mapping_review_rows(
    *,
    q: str | None,
    mapping_status: str | None,
    review_reason: str | None,
    sort_field: str | None,
    sort_dir: SortDirection | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
    reason_clause = ""
    order_by = _order_by_clause("cms_mapping_review", sort_field, sort_dir)
    if q:
        params["q"] = q
        search_clause = "AND (p.local_name ILIKE '%' || :q || '%' OR COALESCE(map.cms_code_snapshot,'') ILIKE '%' || :q || '%' OR COALESCE(map.cms_name_snapshot,'') ILIKE '%' || :q || '%' OR COALESCE(map.review_reason,'') ILIKE '%' || :q || '%')"
    if mapping_status:
        params["mapping_status"] = mapping_status
        mapping_clause = "AND map.mapping_status = :mapping_status"
    if review_reason:
        params["review_reason"] = review_reason
        reason_clause = "AND COALESCE(map.review_reason,'') ILIKE '%' || :review_reason || '%'"
    return _query(
        f"""
        WITH current_mapping AS (
            SELECT DISTINCT ON (product_id)
                   product_id, catalogue_item_id, cms_code_snapshot, cms_name_snapshot,
                   mapping_status, accepted_operational_price, review_reason, valid_from
            FROM product_cms_mappings
            WHERE valid_to IS NULL
            ORDER BY product_id,
                     CASE mapping_status WHEN 'ACTIVE_MATCH' THEN 0 WHEN 'REVIEW_REQUIRED' THEN 1 WHEN 'RECYCLED_CODE' THEN 2 WHEN 'CMS_DISCONTINUED' THEN 3 WHEN 'UNMAPPED' THEN 4 ELSE 5 END,
                     valid_from DESC
        )
        SELECT p.product_id::text AS product_id,
               p.local_name AS local_item_name,
               p.default_unit AS unit,
               map.cms_code_snapshot AS cms_code,
               map.cms_name_snapshot AS cms_name,
               map.mapping_status,
               ci.selling_price AS catalogue_price,
               map.accepted_operational_price,
               map.review_reason
        FROM products p
        JOIN current_mapping map ON map.product_id=p.product_id
        LEFT JOIN cms_catalogue_items ci ON ci.catalogue_item_id=map.catalogue_item_id
        WHERE p.active {search_clause} {mapping_clause} {reason_clause}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
        """,
        params,
    )


def _render_provider(
    provider: str,
    *,
    q: str | None,
    mapping_status: str | None,
    source_classification: str | None,
    review_reason: str | None,
    sort_field: str | None,
    sort_dir: SortDirection | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    if provider == "lot_balance":
        return _main_stock_rows(
            q=q,
            mapping_status=mapping_status,
            sort_field=sort_field,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )
    if provider == "migration_review":
        return _migration_review_rows(
            q=q,
            mapping_status=mapping_status,
            source_classification=source_classification,
            review_reason=review_reason,
            sort_field=sort_field,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )
    if provider == "cms_mapping_review":
        return _cms_mapping_review_rows(
            q=q,
            mapping_status=mapping_status,
            review_reason=review_reason,
            sort_field=sort_field,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown inventory view provider")


@router.get("/registry", dependencies=[Depends(require_dashboard_session)])
def inventory_field_registry(response: Response) -> dict[str, Any]:
    _no_store(response)
    return {
        "fields": [asdict(FIELD_REGISTRY[key]) for key in sorted(FIELD_REGISTRY)],
        "semantic_classes": ["ENTITY_FIELD", "COMPUTED_FIELD", "COMMAND_EDITABLE_FIELD", "DISPLAY_HELPER"],
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.get("/presets", dependencies=[Depends(require_dashboard_session)])
def inventory_view_presets(response: Response) -> dict[str, Any]:
    _no_store(response)
    return {
        "items": [_serialize_view(SYSTEM_PRESETS[key]) for key in sorted(SYSTEM_PRESETS)],
        "custom_view_persistence": False,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.get("/rows", dependencies=[Depends(require_dashboard_session)])
def inventory_view_rows(
    response: Response,
    preset: str = Query(default="main-stock"),
    fields: str | None = Query(default=None, description="Optional comma-separated registry field keys; validates the generic renderer contract."),
    q: str | None = None,
    mapping_status: str | None = Query(default=None, max_length=64),
    source_classification: str | None = Query(default=None, max_length=64),
    review_reason: str | None = Query(default=None, max_length=255),
    sort_field: str | None = Query(default=None, max_length=80),
    sort_dir: str | None = Query(default=None, max_length=8),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    _no_store(response)
    view = SYSTEM_PRESETS.get(preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory view preset not found")
    columns = _resolve_columns(view, fields)
    normalized_q = _normalize_optional(q)
    normalized_mapping_status = _normalize_optional(mapping_status)
    normalized_source_classification = _normalize_optional(source_classification)
    normalized_review_reason = _normalize_optional(review_reason)
    normalized_sort_field, normalized_sort_dir = _normalize_sort(view.provider, sort_field, sort_dir)
    provider_rows = _render_provider(
        view.provider,
        q=normalized_q,
        mapping_status=normalized_mapping_status,
        source_classification=normalized_source_classification,
        review_reason=normalized_review_reason,
        sort_field=normalized_sort_field,
        sort_dir=normalized_sort_dir,
        limit=limit,
        offset=offset,
    )
    selected = [{column.field: row.get(column.field) for column in columns} for row in provider_rows]
    sortable_fields = PROVIDER_SORT_FIELDS[view.provider]
    return {
        "view": _serialize_view(view),
        "columns": [
            {
                **asdict(column),
                "label": column.label or FIELD_REGISTRY[column.field].label,
                "field_definition": asdict(FIELD_REGISTRY[column.field]),
                "sortable": column.field in sortable_fields,
            }
            for column in columns
        ],
        "items": selected,
        "count": len(selected),
        "limit": limit,
        "offset": offset,
        "filters": {
            "q": normalized_q,
            "mapping_status": normalized_mapping_status,
            "source_classification": normalized_source_classification,
            "review_reason": normalized_review_reason,
        },
        "sort": {"field": normalized_sort_field, "direction": normalized_sort_dir},
        "read_only": True,
        "customizable_projection": True,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


@router.post("/review-context", dependencies=[Depends(require_dashboard_session)])
def inventory_review_context(payload: InventoryReviewContextInput, response: Response) -> dict[str, Any]:
    _no_store(response)
    view = _review_context_view(payload.preset)
    normalized_q = _normalize_optional(payload.q)
    normalized_mapping_status = _normalize_optional(payload.mapping_status)
    normalized_source_classification = _normalize_optional(payload.source_classification)
    normalized_review_reason = _normalize_optional(payload.review_reason)
    normalized_sort_field, normalized_sort_dir = _normalize_sort(view.provider, payload.sort_field, payload.sort_dir)
    provider_rows = _render_provider(
        view.provider,
        q=normalized_q,
        mapping_status=normalized_mapping_status,
        source_classification=normalized_source_classification if payload.preset == "migration-review" else None,
        review_reason=normalized_review_reason,
        sort_field=normalized_sort_field,
        sort_dir=normalized_sort_dir,
        limit=payload.limit,
        offset=payload.offset,
    )
    rows = _select_review_context_rows(view, provider_rows, payload.selected_indices)
    return {
        "context_type": "INVENTORY_REVIEW_CONTEXT_V1",
        "context_origin": "SERVER_REHYDRATED_INVENTORY_VIEW",
        "view": {
            "view_id": view.view_id,
            "name": view.name,
            "row_grain": view.row_grain,
            "store_scope": view.store_scope,
            "columns": [
                {
                    "field": column.field,
                    "label": column.label or FIELD_REGISTRY[column.field].label,
                    "data_type": FIELD_REGISTRY[column.field].data_type,
                }
                for column in view.columns
            ],
        },
        "filters": {
            "q": normalized_q,
            "mapping_status": normalized_mapping_status,
            "source_classification": normalized_source_classification if payload.preset == "migration-review" else None,
            "review_reason": normalized_review_reason,
        },
        "sort": {"field": normalized_sort_field, "direction": normalized_sort_dir},
        "page": {"limit": payload.limit, "offset": payload.offset},
        "selected_indices": payload.selected_indices,
        "selected_count": len(rows),
        "rows": rows,
        "read_only": True,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }
