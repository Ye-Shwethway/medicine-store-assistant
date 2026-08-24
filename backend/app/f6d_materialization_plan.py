from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url

MAIN_SHEET = "Main Stock"
USAGE_SHEET = "Daily Usage"

MAPPING_ONLY_REASONS = {
    "missing accepted CMS mapping code",
    "CMS mapping marked Recycled ID",
    "CMS code present but dependent CMS name is missing",
}


def _key(payload: dict[str, Any]) -> tuple[str, str]:
    product = str(payload.get("product_name_candidate") or "").strip().casefold()
    expiry = str(payload.get("expiry_date") or "").strip().casefold()
    return product, expiry


def _reason_inventory_safe(classification: str, reason: str | None) -> bool:
    if classification == "SAFE":
        return True
    if classification == "NEW_UNMAPPED":
        return True
    if classification == "REVIEW" and reason in MAPPING_ONLY_REASONS:
        return True
    return False


def _decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
            if revision != EXPECTED_MIGRATION:
                raise RuntimeError(f"migration drift: {revision!r} != {EXPECTED_MIGRATION!r}")

            batch = conn.execute(
                text(
                    """
                    SELECT migration_batch_id, source_hash, source_label, row_count, store_id
                    FROM migration_batches
                    WHERE source_kind='f6d_google_sheet_snapshot'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                )
            ).mappings().one_or_none()
            if batch is None:
                raise RuntimeError("no F6D live snapshot batch found")

            rows = conn.execute(
                text(
                    """
                    SELECT source_sheet, source_row_no, classification, review_reason, payload
                    FROM migration_source_rows
                    WHERE migration_batch_id=:batch_id
                    ORDER BY source_sheet, source_row_no
                    """
                ),
                {"batch_id": batch["migration_batch_id"]},
            ).mappings().all()

            main_rows = [dict(r) for r in rows if r["source_sheet"] == MAIN_SHEET]
            usage_rows = [dict(r) for r in rows if r["source_sheet"] == USAGE_SHEET]
            if len(rows) != len(main_rows) + len(usage_rows):
                raise RuntimeError("unexpected source sheet present in F6D snapshot")

            main_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            usage_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            for row in main_rows:
                main_by_key[_key(row["payload"])].append(row)
            for row in usage_rows:
                usage_by_key[_key(row["payload"])].append(row)

            blank_main_keys = [row["source_row_no"] for row in main_rows if not _key(row["payload"])[0]]
            duplicate_main = {
                f"{k[0]}|{k[1]}": [r["source_row_no"] for r in v]
                for k, v in main_by_key.items()
                if k[0] and len(v) > 1
            }
            duplicate_usage = {
                f"{k[0]}|{k[1]}": [r["source_row_no"] for r in v]
                for k, v in usage_by_key.items()
                if k[0] and len(v) > 1
            }
            duplicate_main_rows = {row_no for row_nos in duplicate_main.values() for row_no in row_nos}

            joined_unique = 0
            main_without_usage: list[int] = []
            usage_without_main: list[int] = []
            ambiguous_join_keys: list[str] = []
            for key, main_group in main_by_key.items():
                usage_group = usage_by_key.get(key, [])
                if len(main_group) == 1 and len(usage_group) == 1:
                    joined_unique += 1
                elif len(main_group) == 1 and len(usage_group) == 0:
                    main_without_usage.append(main_group[0]["source_row_no"])
                elif main_group and usage_group:
                    ambiguous_join_keys.append(f"{key[0]}|{key[1]}")
            for key, usage_group in usage_by_key.items():
                if key not in main_by_key:
                    usage_without_main.extend(r["source_row_no"] for r in usage_group)

            inventory_safe_rows: list[dict[str, Any]] = []
            inventory_review_rows: list[dict[str, Any]] = []
            mapping_hints = Counter()
            classification_counts = Counter()
            review_reason_counts = Counter()
            for row in main_rows:
                classification = str(row["classification"])
                reason = row["review_reason"]
                payload = row["payload"] or {}
                classification_counts[classification] += 1
                if reason:
                    review_reason_counts[str(reason)] += 1
                hint = payload.get("mapping_hint")
                if hint:
                    mapping_hints[str(hint)] += 1
                target = inventory_safe_rows if _reason_inventory_safe(classification, reason) else inventory_review_rows
                target.append(row)

            unambiguous_inventory_safe = [
                row for row in inventory_safe_rows if row["source_row_no"] not in duplicate_main_rows
            ]
            positive_rows: list[int] = []
            zero_rows: list[int] = []
            negative_rows: list[int] = []
            missing_current_rows: list[int] = []
            for row in unambiguous_inventory_safe:
                current = _decimal((row["payload"] or {}).get("stock_status_today"))
                if current is None:
                    missing_current_rows.append(row["source_row_no"])
                elif current > 0:
                    positive_rows.append(row["source_row_no"])
                elif current == 0:
                    zero_rows.append(row["source_row_no"])
                else:
                    negative_rows.append(row["source_row_no"])

            write_ready_rows = [
                row["source_row_no"]
                for row in unambiguous_inventory_safe
                if row["source_row_no"] not in set(negative_rows) | set(missing_current_rows)
            ]

            unique_product_names = {key[0] for key in main_by_key if key[0]}
            unique_lot_keys = {key for key in main_by_key if key[0]}

            result = {
                "mode": "READ_ONLY_MATERIALIZATION_PLAN",
                "migration": revision,
                "migration_batch_id": str(batch["migration_batch_id"]),
                "source_hash": batch["source_hash"],
                "source_label": batch["source_label"],
                "store_id": str(batch["store_id"]),
                "staged_source_records": len(rows),
                "main_stock_source_rows": len(main_rows),
                "daily_usage_source_rows": len(usage_rows),
                "canonical_lot_candidates_before_reconciliation": len(main_rows),
                "unique_product_name_candidates": len(unique_product_names),
                "unique_product_expiry_keys": len(unique_lot_keys),
                "main_duplicate_key_count": len(duplicate_main),
                "main_duplicate_source_row_count": len(duplicate_main_rows),
                "main_duplicate_keys": duplicate_main,
                "usage_duplicate_key_count": len(duplicate_usage),
                "usage_duplicate_keys": duplicate_usage,
                "blank_main_product_key_rows": blank_main_keys,
                "unique_cross_sheet_joins": joined_unique,
                "main_rows_without_usage_match": main_without_usage,
                "usage_rows_without_main_match": usage_without_main,
                "ambiguous_join_keys": ambiguous_join_keys,
                "main_classification_counts": dict(sorted(classification_counts.items())),
                "main_review_reason_counts": dict(sorted(review_reason_counts.items())),
                "main_mapping_hint_counts": dict(sorted(mapping_hints.items())),
                "inventory_safe_main_rows_before_duplicate_hold": len(inventory_safe_rows),
                "inventory_review_main_rows": len(inventory_review_rows),
                "inventory_review_source_rows": [row["source_row_no"] for row in inventory_review_rows],
                "unambiguous_inventory_safe_rows": len(unambiguous_inventory_safe),
                "current_balance_positive_rows": len(positive_rows),
                "current_balance_zero_rows": len(zero_rows),
                "current_balance_negative_rows": len(negative_rows),
                "current_balance_negative_source_rows": negative_rows,
                "current_balance_missing_source_rows": missing_current_rows,
                "materialization_write_ready_rows": len(write_ready_rows),
                "materialization_write_ready_source_rows": write_ready_rows,
                "opening_balance_rows": len(positive_rows),
                "zero_balance_identity_only_rows": len(zero_rows),
                "duplicate_hold_source_rows": sorted(duplicate_main_rows),
                "database_canonical": False,
                "migration_baseline_accepted": False,
                "mutation": False,
            }
            print(json.dumps(result, sort_keys=True))
            print("f6d_materialization_plan=pass mutation=false main_primary=true daily_usage_join_only=true")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
