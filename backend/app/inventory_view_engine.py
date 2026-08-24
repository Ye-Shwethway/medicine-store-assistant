from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dashboard_auth import require_dashboard_session
from app.shadow_read_api import _query

router = APIRouter(prefix="/dashboard/api/inventory-view", tags=["inventory-view"])

FieldKind = Literal["ENTITY_FIELD", "COMPUTED_FIELD", "COMMAND_EDITABLE_FIELD", "DISPLAY_HELPER"]


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


def _main_stock_rows(*, q: str | None, mapping_status: str | None, limit: int, offset: int) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
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
        ORDER BY COALESCE(p.display_order, 2147483647), lower(p.local_name), pl.expiry_date NULLS LAST, pl.lot_id
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
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
    classification_clause = ""
    reason_clause = ""
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
        ORDER BY msr.source_row_no
        LIMIT :limit OFFSET :offset
        """,
        params,
    )


def _cms_mapping_review_rows(
    *,
    q: str | None,
    mapping_status: str | None,
    review_reason: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    search_clause = ""
    mapping_clause = ""
    reason_clause = ""
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
        ORDER BY COALESCE(p.display_order, 2147483647), lower(p.local_name), p.product_id
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
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    if provider == "lot_balance":
        return _main_stock_rows(q=q, mapping_status=mapping_status, limit=limit, offset=offset)
    if provider == "migration_review":
        return _migration_review_rows(
            q=q,
            mapping_status=mapping_status,
            source_classification=source_classification,
            review_reason=review_reason,
            limit=limit,
            offset=offset,
        )
    if provider == "cms_mapping_review":
        return _cms_mapping_review_rows(
            q=q,
            mapping_status=mapping_status,
            review_reason=review_reason,
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
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    _no_store(response)
    view = SYSTEM_PRESETS.get(preset)
    if view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory view preset not found")
    columns = _resolve_columns(view, fields)
    normalized_q = q.strip() if q and q.strip() else None
    normalized_mapping_status = mapping_status.strip() if mapping_status and mapping_status.strip() else None
    normalized_source_classification = source_classification.strip() if source_classification and source_classification.strip() else None
    normalized_review_reason = review_reason.strip() if review_reason and review_reason.strip() else None
    provider_rows = _render_provider(
        view.provider,
        q=normalized_q,
        mapping_status=normalized_mapping_status,
        source_classification=normalized_source_classification,
        review_reason=normalized_review_reason,
        limit=limit,
        offset=offset,
    )
    selected = [{column.field: row.get(column.field) for column in columns} for row in provider_rows]
    return {
        "view": _serialize_view(view),
        "columns": [
            {
                **asdict(column),
                "label": column.label or FIELD_REGISTRY[column.field].label,
                "field_definition": asdict(FIELD_REGISTRY[column.field]),
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
        "read_only": True,
        "customizable_projection": True,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }
