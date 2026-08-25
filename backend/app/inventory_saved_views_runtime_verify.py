from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import Response
from sqlalchemy import create_engine, text

from app.dashboard_auth import ensure_bootstrap_owner
from app.db import normalize_database_url
from app.inventory_saved_views import (
    SavedViewUpsert,
    _database_url,
    create_saved_view,
    delete_saved_view,
    list_saved_views,
    update_saved_view,
)


def _payload(name: str, *, density: str = "compact") -> SavedViewUpsert:
    return SavedViewUpsert.model_validate(
        {
            "name": name,
            "base_preset": "main-stock",
            "definition": {
                "fields": ["local_item_name", "current_qty", "cms_code"],
                "column_widths": {"local_item_name": 260, "current_qty": 120},
                "density": density,
                "filters": {
                    "q": "runtime-saved-view-proof",
                    "mapping_status": "",
                    "source_classification": "",
                    "review_reason": "",
                },
                "sort": {"field": "local_item_name", "direction": "asc"},
                "fills": [
                    {"row_key": "runtime-proof-row", "field": "current_qty", "fill": "green"}
                ],
            },
        }
    )


def main() -> None:
    owner = ensure_bootstrap_owner()
    principal = {
        "user_id": owner["user_id"],
        "username": owner["username"],
        "role": owner.get("role", "owner"),
    }
    name = f"runtime-saved-view-{uuid4()}"
    renamed = f"{name}-updated"
    created_id: str | None = None

    engine = create_engine(normalize_database_url(_database_url()), pool_pre_ping=True)
    try:
        created = create_saved_view(_payload(name), Response(), principal)
        created_id = str(created["view_id"])
        UUID(created_id)
        assert created["name"] == name
        assert created["base_preset"] == "main-stock"
        assert created["definition"]["density"] == "compact"
        assert created["definition"]["fills"][0]["fill"] == "green"

        listed = list_saved_views(Response(), principal)
        assert listed["database_canonical"] is False
        assert listed["migration_baseline_accepted"] is False
        match = next(item for item in listed["items"] if item["view_id"] == created_id)
        assert match["name"] == name
        assert match["definition"]["filters"]["q"] == "runtime-saved-view-proof"

        updated = update_saved_view(UUID(created_id), _payload(renamed, density="comfortable"), Response(), principal)
        assert updated["name"] == renamed
        assert updated["definition"]["density"] == "comfortable"

        delete_saved_view(UUID(created_id), principal)
        created_id = None
        listed_after = list_saved_views(Response(), principal)
        assert all(item["name"] not in {name, renamed} for item in listed_after["items"])

        with engine.connect() as connection:
            count = connection.execute(
                text("SELECT count(*) FROM inventory_saved_views WHERE owner_user_id = CAST(:user_id AS uuid) AND name IN (:name, :renamed)"),
                {"user_id": principal["user_id"], "name": name, "renamed": renamed},
            ).scalar_one()
        assert count == 0

        print(
            "inventory_saved_views_runtime=pass create=pass list_readback=pass update=pass delete=pass "
            "database_canonical=false migration_baseline_accepted=false inventory_mutation=false"
        )
    finally:
        if created_id:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "DELETE FROM inventory_saved_views "
                        "WHERE view_id = CAST(:view_id AS uuid) AND owner_user_id = CAST(:user_id AS uuid)"
                    ),
                    {"view_id": created_id, "user_id": principal["user_id"]},
                )
        engine.dispose()


if __name__ == "__main__":
    main()
