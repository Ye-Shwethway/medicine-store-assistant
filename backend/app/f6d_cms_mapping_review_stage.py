from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url
from app.f6d_cms_reconciliation_plan import EXPECTED_CATALOGUE_HASH, _classify
from app.f6d_materialize_main import MAIN_SHEET, _product_id

EXPECTED_INVENTORY_HASH = "c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76"


def _unique(values: list[Any]) -> list[str]:
    result: dict[str, str] = {}
    for value in values:
        if value is None:
            continue
        value = " ".join(str(value).strip().split())
        if value:
            result.setdefault(value.casefold(), value)
    return sorted(result.values(), key=str.casefold)


def _mapping_status(category: str) -> str:
    if category == "UNMAPPED":
        return "UNMAPPED"
    if category == "CMS_DISCONTINUED_LOCAL_RETAINED":
        return "CMS_DISCONTINUED"
    if category == "REVIEW_RECYCLED_CODE":
        return "RECYCLED_CODE"
    return "REVIEW_REQUIRED"


def _load(conn) -> dict[str, Any]:
    revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
    if revision != EXPECTED_MIGRATION:
        raise RuntimeError(f"migration drift: {revision!r} != {EXPECTED_MIGRATION!r}")

    batch = conn.execute(
        text(
            """
            SELECT migration_batch_id::text AS migration_batch_id, source_hash
            FROM migration_batches
            WHERE source_kind='f6d_google_sheet_snapshot'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
    ).mappings().one()
    if batch["source_hash"] != EXPECTED_INVENTORY_HASH:
        raise RuntimeError("unexpected inventory source hash")

    version = conn.execute(
        text(
            """
            SELECT catalogue_version_id::text AS catalogue_version_id, source_hash, effective_date, row_count
            FROM cms_catalogue_versions
            ORDER BY imported_at DESC, catalogue_version_id DESC
            LIMIT 1
            """
        )
    ).mappings().one()
    if version["source_hash"] != EXPECTED_CATALOGUE_HASH:
        raise RuntimeError("unexpected catalogue source hash")

    catalogue_rows = conn.execute(
        text(
            """
            SELECT catalogue_item_id::text AS catalogue_item_id, cms_code, brand_name, description,
                   form, type, class_name, selling_price, source_row_no
            FROM cms_catalogue_items
            WHERE catalogue_version_id=CAST(:version_id AS uuid)
            ORDER BY source_row_no, cms_code
            """
        ),
        {"version_id": version["catalogue_version_id"]},
    ).mappings().all()
    catalogue = {str(row["cms_code"]): dict(row) for row in catalogue_rows}
    if len(catalogue) != int(version["row_count"]):
        raise RuntimeError("catalogue row/code cardinality drift")

    products = conn.execute(
        text("SELECT product_id::text AS product_id, local_name, default_unit FROM products ORDER BY local_name, product_id")
    ).mappings().all()
    product_by_id = {str(row["product_id"]): dict(row) for row in products}

    source_rows = conn.execute(
        text(
            """
            SELECT source_row_no, classification, review_reason, payload
            FROM migration_source_rows
            WHERE migration_batch_id=CAST(:batch_id AS uuid) AND source_sheet=:sheet
            ORDER BY source_row_no
            """
        ),
        {"batch_id": batch["migration_batch_id"], "sheet": MAIN_SHEET},
    ).mappings().all()

    by_product: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for raw in source_rows:
        row = dict(raw)
        payload = row["payload"] or {}
        product_key = str(payload.get("product_name_candidate") or "").strip().casefold()
        if not product_key:
            continue
        product_id = str(_product_id(product_key))
        if product_id in product_by_id:
            by_product[product_id].append(row)

    candidates: list[dict[str, Any]] = []
    category_counts = Counter()
    status_counts = Counter()
    for product_id, product in product_by_id.items():
        rows = by_product.get(product_id)
        if not rows:
            raise RuntimeError(f"Product missing Main Stock evidence: {product_id}")
        category, evidence = _classify(rows, catalogue)
        category_counts[category] += 1
        status = _mapping_status(category)
        status_counts[status] += 1

        source_codes = _unique(evidence.get("source_codes") or [])
        source_names = _unique(evidence.get("source_cs_names") or [])
        code = evidence.get("cms_code") or (source_codes[0] if len(source_codes) == 1 else None)
        item = catalogue.get(str(code)) if code and status == "REVIEW_REQUIRED" else None
        cms_name = item.get("brand_name") if item else (source_names[0] if len(source_names) == 1 else None)

        candidates.append(
            {
                "product_id": product_id,
                "local_name": product["local_name"],
                "catalogue_item_id": item.get("catalogue_item_id") if item else None,
                "cms_code_snapshot": str(code) if code else None,
                "cms_name_snapshot": str(cms_name) if cms_name else None,
                "mapping_status": status,
                "category": category,
                "source_rows": [int(row["source_row_no"]) for row in rows],
                "source_codes": source_codes,
                "source_names": source_names,
                "source_prices": evidence.get("source_cms_prices") or [],
                "operation_id": f"f6d-cms-review:{version['catalogue_version_id']}:{product_id}",
            }
        )

    return {
        "revision": revision,
        "batch": dict(batch),
        "version": dict(version),
        "products": product_by_id,
        "candidates": candidates,
        "category_counts": dict(sorted(category_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
    }


def _summary(plan: dict[str, Any], *, mutation: bool) -> dict[str, Any]:
    return {
        "mode": "EXECUTE" if mutation else "PLAN",
        "migration": plan["revision"],
        "inventory_source_hash": plan["batch"]["source_hash"],
        "catalogue_version_id": plan["version"]["catalogue_version_id"],
        "catalogue_source_hash": plan["version"]["source_hash"],
        "candidate_products": len(plan["candidates"]),
        "category_counts": plan["category_counts"],
        "status_counts": plan["status_counts"],
        "active_match_candidates": sum(1 for row in plan["candidates"] if row["mapping_status"] == "ACTIVE_MATCH"),
        "accepted_price_candidates": 0,
        "mutation": mutation,
        "mapping_acceptance": False,
        "price_mutation": False,
        "inventory_mutation": False,
        "database_canonical": False,
        "migration_baseline_accepted": False,
    }


def _execute(conn, plan: dict[str, Any]) -> dict[str, Any]:
    expected_inventory = os.environ.get("MSA_F6D_EXPECTED_INVENTORY_HASH", "").strip()
    expected_catalogue = os.environ.get("MSA_F6D_EXPECTED_CATALOGUE_HASH", "").strip()
    if expected_inventory != plan["batch"]["source_hash"]:
        raise RuntimeError("inventory hash guard failed")
    if expected_catalogue != plan["version"]["source_hash"]:
        raise RuntimeError("catalogue hash guard failed")
    if any(row["mapping_status"] == "ACTIVE_MATCH" for row in plan["candidates"]):
        raise RuntimeError("candidate staging must never create ACTIVE_MATCH")

    target_ops = {row["operation_id"] for row in plan["candidates"]}
    existing = conn.execute(
        text("SELECT operation_id, mapping_status, accepted_operational_price FROM product_cms_mappings")
    ).mappings().all()
    for row in existing:
        if row["operation_id"] not in target_ops:
            raise RuntimeError("refusing candidate stage: unrelated mapping rows already exist")
        if row["mapping_status"] == "ACTIVE_MATCH" or row["accepted_operational_price"] is not None:
            raise RuntimeError("refusing candidate stage: accepted mapping state already exists")

    created = 0
    for candidate in plan["candidates"]:
        reason = json.dumps(
            {
                "category": candidate["category"],
                "source_rows": candidate["source_rows"],
                "source_codes": candidate["source_codes"],
                "source_names": candidate["source_names"],
                "source_prices": candidate["source_prices"],
                "policy": "candidate only; explicit acceptance required",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        result = conn.execute(
            text(
                """
                INSERT INTO product_cms_mappings
                    (product_id, catalogue_item_id, cms_code_snapshot, cms_name_snapshot,
                     mapping_status, accepted_operational_price, operation_id, review_reason)
                VALUES
                    (CAST(:product_id AS uuid), CAST(:catalogue_item_id AS uuid), :cms_code_snapshot,
                     :cms_name_snapshot, :mapping_status, NULL, :operation_id, :review_reason)
                ON CONFLICT (operation_id) DO NOTHING
                """
            ),
            {
                "product_id": candidate["product_id"],
                "catalogue_item_id": candidate["catalogue_item_id"],
                "cms_code_snapshot": candidate["cms_code_snapshot"],
                "cms_name_snapshot": candidate["cms_name_snapshot"],
                "mapping_status": candidate["mapping_status"],
                "operation_id": candidate["operation_id"],
                "review_reason": reason,
            },
        )
        created += int(result.rowcount or 0)

    rows = conn.execute(
        text(
            """
            SELECT mapping_status, COUNT(*) AS count,
                   COUNT(*) FILTER (WHERE accepted_operational_price IS NOT NULL) AS accepted_price_count
            FROM product_cms_mappings
            GROUP BY mapping_status
            ORDER BY mapping_status
            """
        )
    ).mappings().all()
    persisted_status = {row["mapping_status"]: int(row["count"]) for row in rows}
    accepted_price_count = sum(int(row["accepted_price_count"]) for row in rows)
    active_count = persisted_status.get("ACTIVE_MATCH", 0)
    if persisted_status != plan["status_counts"]:
        raise RuntimeError(f"mapping review-state readback mismatch: {persisted_status!r} != {plan['status_counts']!r}")
    if active_count != 0 or accepted_price_count != 0:
        raise RuntimeError("candidate staging accidentally created accepted mapping/price state")

    audit_operation = f"f6d-cms-review-stage:{plan['version']['catalogue_version_id']}"
    if conn.execute(
        text("SELECT COUNT(*) FROM audit_events WHERE operation_id=:operation_id AND action='f6d_cms_mapping_review_stage'"),
        {"operation_id": audit_operation},
    ).scalar_one() == 0:
        conn.execute(
            text(
                """
                INSERT INTO audit_events (client_channel, operation_id, action, outcome, reason, details)
                VALUES ('migration', :operation_id, 'f6d_cms_mapping_review_stage', 'SUCCESS',
                        'Stage non-accepted CMS mapping review state from deterministic reconciliation evidence',
                        CAST(:details AS jsonb))
                """
            ),
            {"operation_id": audit_operation, "details": json.dumps(_summary(plan, mutation=True), sort_keys=True)},
        )

    result = _summary(plan, mutation=True)
    result.update(
        {
            "created_review_rows": created,
            "persisted_review_rows": sum(persisted_status.values()),
            "persisted_status_counts": persisted_status,
            "persisted_active_matches": active_count,
            "persisted_accepted_prices": accepted_price_count,
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
                plan = _load(conn)
                print(json.dumps(_summary(plan, mutation=False), sort_keys=True))
                print("f6d_cms_mapping_review_plan=pass mutation=false acceptance=false")
            return
        with engine.begin() as conn:
            plan = _load(conn)
            result = _execute(conn, plan)
            print(json.dumps(result, sort_keys=True))
            print("f6d_cms_mapping_review_stage=pass accepted_mapping=false price_mutation=false database_canonical=false")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
