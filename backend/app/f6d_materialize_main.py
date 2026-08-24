from __future__ import annotations

import argparse
import json
import os
import uuid
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url

MAIN_SHEET = "Main Stock"
MAPPING_ONLY_REASONS = {
    "missing accepted CMS mapping code",
    "CMS mapping marked Recycled ID",
    "CMS code present but dependent CMS name is missing",
}
SOURCE_TYPE = "F6D_MIGRATION_OPENING"
PRODUCT_NAMESPACE = uuid.UUID("4d72cfbb-b070-5e34-b654-96ba8ab6ba11")
LOT_NAMESPACE = uuid.UUID("859a3043-2f3f-5584-ac06-c39bfdb839f9")
TX_NAMESPACE = uuid.UUID("eb7388ab-2d8b-5dca-84cb-bd0a07691410")


def _key(payload: dict[str, Any]) -> tuple[str, str]:
    product = str(payload.get("product_name_candidate") or "").strip().casefold()
    expiry = str(payload.get("expiry_date") or "").strip()
    return product, expiry


def _unit(payload: dict[str, Any]) -> str:
    return str(payload.get("unit") or "").strip()


def _decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _inventory_safe(classification: str, reason: str | None) -> bool:
    if classification == "SAFE":
        return True
    if classification == "NEW_UNMAPPED":
        return True
    return classification == "REVIEW" and reason in MAPPING_ONLY_REASONS


def _product_id(product_key: str) -> uuid.UUID:
    return uuid.uuid5(PRODUCT_NAMESPACE, product_key)


def _lot_id(product_id: uuid.UUID, expiry: str) -> uuid.UUID:
    return uuid.uuid5(LOT_NAMESPACE, f"{product_id}:{expiry or 'NO_EXPIRY'}")


def _transaction_id(batch_id: str, source_row_no: int) -> uuid.UUID:
    return uuid.uuid5(TX_NAMESPACE, f"{batch_id}:Main Stock:{source_row_no}")


def _load_plan(conn) -> dict[str, Any]:
    revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
    if revision != EXPECTED_MIGRATION:
        raise RuntimeError(f"migration drift: {revision!r} != {EXPECTED_MIGRATION!r}")

    batch = conn.execute(
        text(
            """
            SELECT migration_batch_id::text AS migration_batch_id,
                   source_hash,
                   source_label,
                   store_id::text AS store_id,
                   created_at
            FROM migration_batches
            WHERE source_kind='f6d_google_sheet_snapshot'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
    ).mappings().one_or_none()
    if batch is None:
        raise RuntimeError("no F6D live snapshot batch found")
    if not batch["store_id"]:
        raise RuntimeError("F6D live snapshot is not bound to a Store")

    raw_rows = conn.execute(
        text(
            """
            SELECT source_row_no, classification, review_reason, payload
            FROM migration_source_rows
            WHERE migration_batch_id=CAST(:batch_id AS uuid)
              AND source_sheet=:source_sheet
            ORDER BY source_row_no
            """
        ),
        {"batch_id": batch["migration_batch_id"], "source_sheet": MAIN_SHEET},
    ).mappings().all()
    rows = [dict(row) for row in raw_rows]

    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_key[_key(row["payload"] or {})].append(row)
    duplicate_rows = {
        row["source_row_no"]
        for key, group in by_key.items()
        if key[0] and len(group) > 1
        for row in group
    }

    inventory_review_rows: list[int] = []
    pre_unit_rows: list[dict[str, Any]] = []
    for row in rows:
        payload = row["payload"] or {}
        product_key, _ = _key(payload)
        current = _decimal(payload.get("stock_status_today"))
        if not product_key or not _inventory_safe(str(row["classification"]), row["review_reason"]):
            inventory_review_rows.append(row["source_row_no"])
            continue
        if row["source_row_no"] in duplicate_rows:
            continue
        if current is None or current < 0:
            inventory_review_rows.append(row["source_row_no"])
            continue
        pre_unit_rows.append(row)

    missing_unit_rows = [row["source_row_no"] for row in pre_unit_rows if not _unit(row["payload"] or {})]
    units_by_product: dict[str, set[str]] = defaultdict(set)
    for row in pre_unit_rows:
        payload = row["payload"] or {}
        unit = _unit(payload)
        if unit:
            units_by_product[_key(payload)[0]].add(unit.casefold())
    conflict_products = {product for product, units in units_by_product.items() if len(units) > 1}
    unit_conflict_rows = [
        row["source_row_no"]
        for row in pre_unit_rows
        if _key(row["payload"] or {})[0] in conflict_products
    ]
    unit_hold = set(missing_unit_rows) | set(unit_conflict_rows)
    write_rows = [row for row in pre_unit_rows if row["source_row_no"] not in unit_hold]

    products: dict[str, dict[str, Any]] = {}
    lots: list[dict[str, Any]] = []
    positive_rows: list[dict[str, Any]] = []
    zero_rows: list[dict[str, Any]] = []
    for row in write_rows:
        payload = row["payload"] or {}
        product_key, expiry = _key(payload)
        pid = _product_id(product_key)
        lid = _lot_id(pid, expiry)
        current = _decimal(payload.get("stock_status_today"))
        assert current is not None and current >= 0
        product = products.setdefault(
            product_key,
            {
                "product_id": pid,
                "local_name": str(payload.get("product_name_candidate") or "").strip(),
                "default_unit": _unit(payload),
                "display_order": int(row["source_row_no"]) - 1,
            },
        )
        product["display_order"] = min(product["display_order"], int(row["source_row_no"]) - 1)
        lots.append(
            {
                "lot_id": lid,
                "product_id": pid,
                "expiry_date": expiry or None,
                "source_row_no": int(row["source_row_no"]),
                "item_name": str(payload.get("item_name") or "").strip(),
                "current_qty": current,
            }
        )
        (positive_rows if current > 0 else zero_rows).append(lots[-1])

    return {
        "revision": revision,
        "batch": dict(batch),
        "source_rows": rows,
        "duplicate_rows": sorted(duplicate_rows),
        "inventory_review_rows": sorted(set(inventory_review_rows)),
        "missing_unit_rows": sorted(missing_unit_rows),
        "unit_conflict_rows": sorted(unit_conflict_rows),
        "unit_conflict_products": sorted(conflict_products),
        "write_rows": write_rows,
        "products": products,
        "lots": lots,
        "positive_rows": positive_rows,
        "zero_rows": zero_rows,
    }


def _summary(plan: dict[str, Any], *, mutation: bool) -> dict[str, Any]:
    return {
        "mode": "EXECUTE" if mutation else "PLAN",
        "migration": plan["revision"],
        "migration_batch_id": plan["batch"]["migration_batch_id"],
        "source_hash": plan["batch"]["source_hash"],
        "store_id": plan["batch"]["store_id"],
        "main_stock_source_rows": len(plan["source_rows"]),
        "duplicate_hold_source_rows": plan["duplicate_rows"],
        "inventory_review_source_rows": plan["inventory_review_rows"],
        "missing_unit_source_rows": plan["missing_unit_rows"],
        "unit_conflict_source_rows": plan["unit_conflict_rows"],
        "unit_conflict_products": plan["unit_conflict_products"],
        "materialization_write_rows": len(plan["write_rows"]),
        "materialization_products": len(plan["products"]),
        "materialization_lots": len(plan["lots"]),
        "opening_balance_rows": len(plan["positive_rows"]),
        "zero_balance_identity_only_rows": len(plan["zero_rows"]),
        "expected_opening_quantity": str(sum((row["current_qty"] for row in plan["positive_rows"]), Decimal("0"))),
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "mutation": mutation,
    }


def _assert_bootstrap_scope(conn, plan: dict[str, Any]) -> None:
    target_product_ids = {str(item["product_id"]) for item in plan["products"].values()}
    target_lot_ids = {str(item["lot_id"]) for item in plan["lots"]}
    target_tx_ids = {
        str(_transaction_id(plan["batch"]["migration_batch_id"], item["source_row_no"]))
        for item in plan["positive_rows"]
    }

    existing_products = set(conn.execute(text("SELECT product_id::text FROM products")).scalars())
    existing_lots = set(conn.execute(text("SELECT lot_id::text FROM product_lots")).scalars())
    existing_txs = set(conn.execute(text("SELECT transaction_id::text FROM inventory_transactions")).scalars())
    if existing_products - target_product_ids:
        raise RuntimeError("refusing bootstrap: unrelated Product rows already exist")
    if existing_lots - target_lot_ids:
        raise RuntimeError("refusing bootstrap: unrelated Lot rows already exist")
    if existing_txs - target_tx_ids:
        raise RuntimeError("refusing bootstrap: unrelated inventory transactions already exist")


def _execute(conn, plan: dict[str, Any]) -> dict[str, Any]:
    expected_hash = os.environ.get("MSA_F6D_EXPECTED_SOURCE_HASH", "").strip()
    if not expected_hash:
        raise RuntimeError("MSA_F6D_EXPECTED_SOURCE_HASH is required for execution")
    if plan["batch"]["source_hash"] != expected_hash:
        raise RuntimeError(
            f"source hash changed: {plan['batch']['source_hash']!r} != expected {expected_hash!r}"
        )
    if plan["missing_unit_rows"] or plan["unit_conflict_rows"]:
        raise RuntimeError(
            "unit semantics require review before materialization: "
            f"missing={plan['missing_unit_rows']} conflict={plan['unit_conflict_rows']}"
        )

    _assert_bootstrap_scope(conn, plan)
    created_products = 0
    created_lots = 0
    created_openings = 0

    for product in sorted(plan["products"].values(), key=lambda item: item["display_order"]):
        result = conn.execute(
            text(
                """
                INSERT INTO products (product_id, local_name, default_unit, active, display_order)
                VALUES (CAST(:product_id AS uuid), :local_name, :default_unit, TRUE, :display_order)
                ON CONFLICT (product_id) DO NOTHING
                """
            ),
            {
                "product_id": str(product["product_id"]),
                "local_name": product["local_name"],
                "default_unit": product["default_unit"],
                "display_order": product["display_order"],
            },
        )
        created_products += int(result.rowcount or 0)
        persisted = conn.execute(
            text("SELECT local_name, default_unit FROM products WHERE product_id=CAST(:product_id AS uuid)"),
            {"product_id": str(product["product_id"])},
        ).mappings().one()
        if persisted["local_name"] != product["local_name"] or persisted["default_unit"] != product["default_unit"]:
            raise RuntimeError(f"Product deterministic-ID collision for {product['product_id']}")

    for lot in plan["lots"]:
        result = conn.execute(
            text(
                """
                INSERT INTO product_lots (lot_id, product_id, expiry_date, status)
                VALUES (CAST(:lot_id AS uuid), CAST(:product_id AS uuid), CAST(:expiry_date AS date), 'active')
                ON CONFLICT (lot_id) DO NOTHING
                """
            ),
            {
                "lot_id": str(lot["lot_id"]),
                "product_id": str(lot["product_id"]),
                "expiry_date": lot["expiry_date"],
            },
        )
        created_lots += int(result.rowcount or 0)
        persisted = conn.execute(
            text(
                """
                SELECT product_id::text AS product_id, expiry_date::text AS expiry_date
                FROM product_lots WHERE lot_id=CAST(:lot_id AS uuid)
                """
            ),
            {"lot_id": str(lot["lot_id"])},
        ).mappings().one()
        if persisted["product_id"] != str(lot["product_id"]) or (persisted["expiry_date"] or None) != lot["expiry_date"]:
            raise RuntimeError(f"Lot deterministic-ID collision for {lot['lot_id']}")

    effective_date: date = plan["batch"]["created_at"].date()
    for lot in plan["positive_rows"]:
        operation_id = f"f6d-opening:{plan['batch']['migration_batch_id']}:{lot['source_row_no']}"
        tx_id = _transaction_id(plan["batch"]["migration_batch_id"], lot["source_row_no"])
        metadata = json.dumps(
            {
                "migration_batch_id": plan["batch"]["migration_batch_id"],
                "source_hash": plan["batch"]["source_hash"],
                "source_sheet": MAIN_SHEET,
                "source_row_no": lot["source_row_no"],
                "source_item_name": lot["item_name"],
                "balance_source_field": "Stock Status Today",
            },
            sort_keys=True,
        )
        result = conn.execute(
            text(
                """
                INSERT INTO inventory_transactions
                    (transaction_id, store_id, lot_id, transaction_type, quantity, effective_date,
                     source_type, source_id, operation_id, reason, metadata)
                VALUES
                    (CAST(:transaction_id AS uuid), CAST(:store_id AS uuid), CAST(:lot_id AS uuid),
                     'OPENING_BALANCE', :quantity, :effective_date, :source_type, :source_id,
                     :operation_id, :reason, CAST(:metadata AS jsonb))
                ON CONFLICT (operation_id) DO NOTHING
                """
            ),
            {
                "transaction_id": str(tx_id),
                "store_id": plan["batch"]["store_id"],
                "lot_id": str(lot["lot_id"]),
                "quantity": lot["current_qty"],
                "effective_date": effective_date,
                "source_type": SOURCE_TYPE,
                "source_id": f"{plan['batch']['migration_batch_id']}:Main Stock:{lot['source_row_no']}",
                "operation_id": operation_id,
                "reason": "F6D source-safe migration opening balance from Main Stock Stock Status Today",
                "metadata": metadata,
            },
        )
        created_openings += int(result.rowcount or 0)

    balances = {
        row["lot_id"]: Decimal(str(row["current_qty"]))
        for row in conn.execute(
            text(
                """
                SELECT lot_id::text AS lot_id, current_qty
                FROM inventory_location_balances
                WHERE store_id=CAST(:store_id AS uuid)
                """
            ),
            {"store_id": plan["batch"]["store_id"]},
        ).mappings()
    }
    mismatches: list[dict[str, str]] = []
    for lot in plan["lots"]:
        actual = balances.get(str(lot["lot_id"]), Decimal("0"))
        if actual != lot["current_qty"]:
            mismatches.append(
                {
                    "source_row_no": str(lot["source_row_no"]),
                    "expected": str(lot["current_qty"]),
                    "actual": str(actual),
                }
            )
    if mismatches:
        raise RuntimeError(f"post-materialization balance mismatch: {mismatches[:10]!r}")

    audit_operation_id = f"f6d-materialize:{plan['batch']['migration_batch_id']}"
    if conn.execute(
        text("SELECT COUNT(*) FROM audit_events WHERE operation_id=:operation_id AND action='f6d_shadow_materialize_main'"),
        {"operation_id": audit_operation_id},
    ).scalar_one() == 0:
        conn.execute(
            text(
                """
                INSERT INTO audit_events
                    (client_channel, operation_id, action, outcome, reason, details)
                VALUES
                    ('migration', :operation_id, 'f6d_shadow_materialize_main', 'SUCCESS',
                     'Owner-approved F6D shadow materialization from fresh Main Stock source evidence',
                     CAST(:details AS jsonb))
                """
            ),
            {
                "operation_id": audit_operation_id,
                "details": json.dumps(_summary(plan, mutation=True), sort_keys=True),
            },
        )

    result = _summary(plan, mutation=True)
    result.update(
        {
            "created_products": created_products,
            "created_lots": created_lots,
            "created_opening_transactions": created_openings,
            "persisted_products": conn.execute(text("SELECT COUNT(*) FROM products")).scalar_one(),
            "persisted_lots": conn.execute(text("SELECT COUNT(*) FROM product_lots")).scalar_one(),
            "persisted_inventory_transactions": conn.execute(text("SELECT COUNT(*) FROM inventory_transactions")).scalar_one(),
            "balance_readback_mismatches": 0,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        if not args.execute:
            with engine.connect() as conn:
                plan = _load_plan(conn)
                print(json.dumps(_summary(plan, mutation=False), sort_keys=True))
                print("f6d_main_materialization_plan=pass mutation=false")
            return

        with engine.begin() as conn:
            plan = _load_plan(conn)
            result = _execute(conn, plan)
            print(json.dumps(result, sort_keys=True))
            print("f6d_main_materialization=pass shadow_only=true database_canonical=false")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
