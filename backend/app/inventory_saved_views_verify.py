from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from app.inventory_saved_views import SavedViewUpsert, _validated_payload


def _payload(**overrides):
    data = {
        "name": "My Main Stock",
        "base_preset": "main-stock",
        "definition": {
            "fields": ["local_item_name", "current_qty", "cms_code"],
            "column_widths": {"local_item_name": 280, "current_qty": 120},
            "density": "compact",
            "filters": {"q": "", "mapping_status": "", "source_classification": "", "review_reason": ""},
            "sort": {"field": "local_item_name", "direction": "asc"},
            "fills": [{"row_key": "lot-1", "field": "current_qty", "fill": "green"}],
        },
    }
    data.update(overrides)
    return SavedViewUpsert.model_validate(data)


def _must_reject(payload: SavedViewUpsert) -> None:
    try:
        _validated_payload(payload)
    except HTTPException:
        return
    raise AssertionError("payload should have been rejected")


def main() -> None:
    valid = _validated_payload(_payload())
    assert valid.base_preset == "main-stock"
    assert valid.definition.fields == ["local_item_name", "current_qty", "cms_code"]

    _must_reject(_payload(base_preset="not-a-preset"))

    bad_field = _payload()
    bad_field.definition.fields = ["local_item_name", "raw_sql"]
    _must_reject(bad_field)

    bad_sort = _payload()
    bad_sort.definition.sort.field = "review_reason"
    _must_reject(bad_sort)

    bad_filter = _payload()
    bad_filter.definition.filters.source_classification = "REVIEW"
    _must_reject(bad_filter)

    bad_fill = _payload()
    bad_fill.definition.fills[0].field = "expiry_date"
    _must_reject(bad_fill)

    source = Path(__file__).read_text(encoding="utf-8")
    assert "owner_user_id = CAST(:user_id AS uuid)" in source
    assert "WHERE view_id = CAST(:view_id AS uuid)" in source
    assert "A saved view with this name already exists" in source

    migration = Path(__file__).parents[1] / "alembic" / "versions" / "0023_inventory_saved_views.py"
    migration_source = migration.read_text(encoding="utf-8")
    assert '"inventory_saved_views"' in migration_source
    assert 'sa.ForeignKey("users.user_id", ondelete="CASCADE")' in migration_source
    assert "uq_inventory_saved_views_owner_name_ci" in migration_source

    print("inventory_saved_views_contract=pass typed_definition=pass owner_scope=pass no_raw_sql=pass immutable_base_provider=pass")


if __name__ == "__main__":
    main()
