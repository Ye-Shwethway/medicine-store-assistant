from __future__ import annotations

from fastapi import HTTPException

from app.inventory_view_engine import (
    FIELD_REGISTRY,
    MAX_REVIEW_CONTEXT_ROWS,
    REVIEW_CONTEXT_PRESETS,
    SYSTEM_PRESETS,
    _resolve_columns,
    _review_context_view,
    _select_review_context_rows,
)


def main() -> None:
    assert {"ENTITY_FIELD", "COMPUTED_FIELD", "COMMAND_EDITABLE_FIELD", "DISPLAY_HELPER"} == {
        field.kind for field in FIELD_REGISTRY.values()
    } | {"COMMAND_EDITABLE_FIELD"}

    assert {"main-stock", "migration-review", "cms-mapping-review"}.issubset(SYSTEM_PRESETS)
    main_stock = SYSTEM_PRESETS["main-stock"]
    migration_review = SYSTEM_PRESETS["migration-review"]
    cms_mapping_review = SYSTEM_PRESETS["cms-mapping-review"]

    assert main_stock.system_preset is True
    assert main_stock.row_grain == "PRODUCT_LOT"
    assert migration_review.system_preset is True
    assert migration_review.row_grain == "SOURCE_MAIN_ROW"
    assert cms_mapping_review.system_preset is True
    assert cms_mapping_review.row_grain == "PRODUCT_CMS_MAPPING"
    assert cms_mapping_review.provider == "cms_mapping_review"
    assert "mapping_status" in {column.field for column in cms_mapping_review.columns}
    assert "review_reason" in {column.field for column in cms_mapping_review.columns}
    assert all(column.field in FIELD_REGISTRY for view in SYSTEM_PRESETS.values() for column in view.columns)

    selected = _resolve_columns(main_stock, "local_item_name,current_qty,expiry_date")
    assert [column.field for column in selected] == ["local_item_name", "current_qty", "expiry_date"]

    try:
        _resolve_columns(main_stock, "local_item_name,raw_sql_expression")
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("unknown field key must be rejected")

    assert REVIEW_CONTEXT_PRESETS == {"migration-review", "cms-mapping-review"}
    assert MAX_REVIEW_CONTEXT_ROWS == 20
    assert _review_context_view("migration-review") is migration_review
    assert _review_context_view("cms-mapping-review") is cms_mapping_review
    try:
        _review_context_view("main-stock")
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("non-review preset must be rejected for AI review context")

    mock_rows = [
        {
            "source_row_no": 41,
            "local_item_name": "Example A",
            "source_current_qty": "12.000",
            "current_qty": "0.000",
            "source_classification": "REVIEW",
            "review_reason": "duplicate source key",
        },
        {
            "source_row_no": 42,
            "local_item_name": "Example B",
            "source_current_qty": "8.000",
            "current_qty": "8.000",
            "source_classification": "REVIEW",
            "review_reason": "unit review",
        },
    ]
    context_rows = _select_review_context_rows(migration_review, mock_rows, [1, 0])
    assert [row["source_row_no"] for row in context_rows] == [42, 41]
    assert all(set(row).issubset({column.field for column in migration_review.columns}) for row in context_rows)
    try:
        _select_review_context_rows(migration_review, mock_rows, [0, 0])
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("duplicate review-context indices must be rejected")
    try:
        _select_review_context_rows(migration_review, mock_rows, [2])
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("out-of-page review-context index must be rejected")

    assert not any(field.editable for field in FIELD_REGISTRY.values())
    print(
        "inventory_view_engine=pass presets=3 cms_mapping_review=pass "
        "generic_field_selection=pass arbitrary_field_rejected=pass "
        "review_context=pass max_rows=20 server_selection=pass read_only=pass"
    )


if __name__ == "__main__":
    main()
