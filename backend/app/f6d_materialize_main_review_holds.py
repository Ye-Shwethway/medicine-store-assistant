from __future__ import annotations

import json
import os

from sqlalchemy import create_engine, text

from app.db import normalize_database_url
from app.f6d_materialize_main import _execute, _load_plan, _summary


UNIT_HOLD_KEYS = ("missing_unit_rows", "unit_conflict_rows")


def _held_row_ids(plan: dict) -> set[int]:
    return {
        int(row_no)
        for key in UNIT_HOLD_KEYS
        for row_no in plan.get(key, [])
    }


def _assert_holds_are_excluded(plan: dict) -> None:
    held = _held_row_ids(plan)
    write_rows = {int(row["source_row_no"]) for row in plan["write_rows"]}
    leaked = sorted(held & write_rows)
    if leaked:
        raise RuntimeError(f"unit-review HOLD rows leaked into write set: {leaked}")


def _execute_with_review_holds(conn, plan: dict) -> dict:
    _assert_holds_are_excluded(plan)

    # The core planner has already removed missing/conflicting Unit rows from
    # Products/Lots/opening movements. Preserve those rows as explicit review
    # evidence while allowing the remaining source-safe subset to materialize.
    original_missing = list(plan["missing_unit_rows"])
    original_conflicts = list(plan["unit_conflict_rows"])
    execution_plan = dict(plan)
    execution_plan["missing_unit_rows"] = []
    execution_plan["unit_conflict_rows"] = []

    result = _execute(conn, execution_plan)

    # Restore the HOLD evidence in both the returned proof and the durable
    # audit event. No held row is written by the underlying execution plan.
    result["missing_unit_source_rows"] = original_missing
    result["unit_conflict_source_rows"] = original_conflicts
    result["unit_conflict_products"] = plan["unit_conflict_products"]
    result["unit_review_hold_rows"] = sorted(set(original_missing + original_conflicts))
    result["materialization_policy"] = "source-safe subset; unit ambiguity held for review"

    audit_operation_id = f"f6d-materialize:{plan['batch']['migration_batch_id']}"
    corrected_summary = _summary(plan, mutation=True)
    corrected_summary.update(
        {
            "unit_review_hold_rows": result["unit_review_hold_rows"],
            "materialization_policy": result["materialization_policy"],
            "created_products": result["created_products"],
            "created_lots": result["created_lots"],
            "created_opening_transactions": result["created_opening_transactions"],
            "persisted_products": result["persisted_products"],
            "persisted_lots": result["persisted_lots"],
            "persisted_inventory_transactions": result["persisted_inventory_transactions"],
            "balance_readback_mismatches": result["balance_readback_mismatches"],
        }
    )
    conn.execute(
        text(
            """
            UPDATE audit_events
            SET details=CAST(:details AS jsonb)
            WHERE operation_id=:operation_id
              AND action='f6d_shadow_materialize_main'
            """
        ),
        {
            "operation_id": audit_operation_id,
            "details": json.dumps(corrected_summary, sort_keys=True),
        },
    )
    return result


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            plan = _load_plan(conn)
            result = _execute_with_review_holds(conn, plan)
            print(json.dumps(result, sort_keys=True))
            print(
                "f6d_main_materialization=pass shadow_only=true "
                "unit_review_holds=true database_canonical=false"
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
