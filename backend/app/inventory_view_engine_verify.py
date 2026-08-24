from __future__ import annotations

from fastapi import HTTPException

from app.inventory_view_engine import FIELD_REGISTRY, SYSTEM_PRESETS, _resolve_columns


def main() -> None:
    assert {"ENTITY_FIELD", "COMPUTED_FIELD", "COMMAND_EDITABLE_FIELD", "DISPLAY_HELPER"} == {
        field.kind for field in FIELD_REGISTRY.values()
    } | {"COMMAND_EDITABLE_FIELD"}
    assert "main-stock" in SYSTEM_PRESETS
    assert "migration-review" in SYSTEM_PRESETS
    main_stock = SYSTEM_PRESETS["main-stock"]
    migration_review = SYSTEM_PRESETS["migration-review"]
    assert main_stock.system_preset is True
    assert main_stock.row_grain == "PRODUCT_LOT"
    assert migration_review.system_preset is True
    assert migration_review.row_grain == "SOURCE_MAIN_ROW"
    assert all(column.field in FIELD_REGISTRY for view in SYSTEM_PRESETS.values() for column in view.columns)

    selected = _resolve_columns(main_stock, "local_item_name,current_qty,expiry_date")
    assert [column.field for column in selected] == ["local_item_name", "current_qty", "expiry_date"]

    try:
        _resolve_columns(main_stock, "local_item_name,raw_sql_expression")
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("unknown field key must be rejected")

    assert not any(field.editable for field in FIELD_REGISTRY.values())
    print("inventory_view_engine=pass presets=2 generic_field_selection=pass arbitrary_field_rejected=pass read_only=pass")


if __name__ == "__main__":
    main()
