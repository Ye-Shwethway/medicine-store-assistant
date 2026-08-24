from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
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

            main_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            usage_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            for row in main_rows:
                main_by_key[_key(row["payload"])].append(row)
            for row in usage_rows:
                usage_by_key[_key(row["payload"])].append(row)

            blank_main_keys = [
                row["source_row_no"]
                for row in main_rows
                if not _key(row["payload"])[0]
            ]
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

            joined_unique = 0
            main_without_usage: list[int] = []
            usage_without_main: list[int] = []
            ambiguous_join_keys: list[str] = []
            for k, main_group in main_by_key.items():
                usage_group = usage_by_key.get(k, [])
                if len(main_group) == 1 and len(usage_group) == 1:
                    joined_unique += 1
                elif len(main_group) == 1 and len(usage_group) == 0:
                    main_without_usage.append(main_group[0]["source_row_no"])
                elif main_group and usage_group:
                    ambiguous_join_keys.append(f"{k[0]}|{k[1]}")
            for k, usage_group in usage_by_key.items():
                if k not in main_by_key:
                    usage_without_main.extend(r["source_row_no"] for r in usage_group)

            safe_rows = []
            blocked_rows = []
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
                target = safe_rows if _reason_inventory_safe(classification, reason) else blocked_rows
                target.append(row["source_row_no"])

            unique_product_names = {k[0] for k in main_by_key if k[0]}
            unique_lot_keys = {k for k in main_by_key if k[0]}

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
                "usage_duplicate_key_count": len(duplicate_usage),
                "main_duplicate_keys": duplicate_main,
                "usage_duplicate_keys": duplicate_usage,
                "blank_main_product_key_rows": blank_main_keys,
                "unique_cross_sheet_joins": joined_unique,
                "main_rows_without_usage_match": main_without_usage,
                "usage_rows_without_main_match": usage_without_main,
                "ambiguous_join_keys": ambiguous_join_keys,
                "main_classification_counts": dict(sorted(classification_counts.items())),
                "main_review_reason_counts": dict(sorted(review_reason_counts.items())),
                "main_mapping_hint_counts": dict(sorted(mapping_hints.items())),
                "inventory_safe_main_rows": len(safe_rows),
                "inventory_review_main_rows": len(blocked_rows),
                "inventory_review_source_rows": blocked_rows,
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
