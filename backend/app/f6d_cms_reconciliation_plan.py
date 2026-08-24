from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import create_engine, text

from app.db import EXPECTED_MIGRATION, normalize_database_url
from app.f6d_materialize_main import MAIN_SHEET, _product_id

EXPECTED_CATALOGUE_HASH = "6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116"
MAX_EXAMPLES = 20


def _norm(value: Any) -> str | None:
    if value is None:
        return None
    text_value = " ".join(str(value).strip().split())
    return text_value or None


def _fold(value: Any) -> str | None:
    normalized = _norm(value)
    return normalized.casefold() if normalized else None


def _decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _unique(values: list[Any]) -> list[str]:
    result: dict[str, str] = {}
    for value in values:
        normalized = _norm(value)
        if normalized is None:
            continue
        result.setdefault(normalized.casefold(), normalized)
    return sorted(result.values(), key=str.casefold)


def _classify(source_rows: list[dict[str, Any]], catalogue: dict[str, dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    payloads = [row["payload"] or {} for row in source_rows]
    hints = set(_unique([payload.get("mapping_hint") for payload in payloads]))
    codes = _unique([payload.get("serial_code") for payload in payloads])
    cs_names = _unique([payload.get("cs_name") for payload in payloads])
    remarks = _unique([payload.get("remark") for payload in payloads])
    source_prices = sorted(
        {str(value) for value in (_decimal(payload.get("cms_price")) for payload in payloads) if value is not None},
        key=Decimal,
    )

    evidence: dict[str, Any] = {
        "source_rows": [int(row["source_row_no"]) for row in source_rows],
        "mapping_hints": sorted(hints),
        "source_codes": codes,
        "source_cs_names": cs_names,
        "source_cms_prices": source_prices,
        "remarks": remarks,
    }

    if "RECYCLED_CODE" in hints:
        return "REVIEW_RECYCLED_CODE", evidence
    if "CMS_DISCONTINUED" in hints:
        return "CMS_DISCONTINUED_LOCAL_RETAINED", evidence
    if not codes:
        return "UNMAPPED", evidence
    if len(codes) > 1:
        return "REVIEW_MULTIPLE_SOURCE_CODES", evidence

    code = codes[0]
    cat = catalogue.get(code)
    if cat is None:
        evidence["cms_code"] = code
        return "REVIEW_CODE_ABSENT_CURRENT_CATALOGUE", evidence

    evidence["cms_code"] = code
    evidence["catalogue_brand_name"] = cat.get("brand_name")
    evidence["catalogue_description"] = cat.get("description")
    evidence["catalogue_form"] = cat.get("form")
    evidence["catalogue_type"] = cat.get("type")
    evidence["catalogue_class"] = cat.get("class_name")
    evidence["catalogue_selling_price"] = str(cat["selling_price"]) if cat.get("selling_price") is not None else None

    if not cs_names:
        return "REVIEW_MISSING_SOURCE_CMS_NAME", evidence
    if len(cs_names) > 1:
        return "REVIEW_MULTIPLE_SOURCE_CMS_NAMES", evidence

    source_name = _fold(cs_names[0])
    catalogue_name = _fold(cat.get("brand_name"))
    if source_name != catalogue_name:
        return "REVIEW_CODE_NAME_MISMATCH", evidence

    catalogue_price = cat.get("selling_price")
    if catalogue_price is None:
        return "CONTINUITY_EXACT_NAME_CATALOGUE_PRICE_MISSING", evidence
    if not source_prices:
        return "CONTINUITY_EXACT_NAME_SOURCE_PRICE_MISSING", evidence
    if any(Decimal(price) == catalogue_price for price in source_prices):
        if all(Decimal(price) == catalogue_price for price in source_prices):
            return "CONTINUITY_EXACT_NAME_PRICE_SAME", evidence
        return "CONTINUITY_EXACT_NAME_MIXED_HISTORICAL_PRICE", evidence
    return "CONTINUITY_EXACT_NAME_PRICE_CHANGED", evidence


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
                    SELECT migration_batch_id::text AS migration_batch_id, source_hash
                    FROM migration_batches
                    WHERE source_kind='f6d_google_sheet_snapshot'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                )
            ).mappings().one()

            version = conn.execute(
                text(
                    """
                    SELECT catalogue_version_id::text AS catalogue_version_id,
                           source_hash, effective_date, row_count
                    FROM cms_catalogue_versions
                    ORDER BY imported_at DESC, catalogue_version_id DESC
                    LIMIT 1
                    """
                )
            ).mappings().one_or_none()
            if version is None:
                raise RuntimeError("no CMS catalogue version available")
            if version["source_hash"] != EXPECTED_CATALOGUE_HASH:
                raise RuntimeError(
                    f"unexpected current catalogue hash: {version['source_hash']!r} != {EXPECTED_CATALOGUE_HASH!r}"
                )

            catalogue_rows = conn.execute(
                text(
                    """
                    SELECT cms_code, brand_name, description, form, type, class_name, selling_price, source_row_no
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

            product_rows = conn.execute(
                text("SELECT product_id::text AS product_id, local_name, default_unit FROM products ORDER BY local_name, product_id")
            ).mappings().all()
            product_ids = {str(row["product_id"]): dict(row) for row in product_rows}

            source_rows = conn.execute(
                text(
                    """
                    SELECT source_row_no, classification, review_reason, payload
                    FROM migration_source_rows
                    WHERE migration_batch_id=CAST(:batch_id AS uuid)
                      AND source_sheet=:sheet
                    ORDER BY source_row_no
                    """
                ),
                {"batch_id": batch["migration_batch_id"], "sheet": MAIN_SHEET},
            ).mappings().all()

            by_product_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
            unmaterialized_source_rows: list[int] = []
            for raw in source_rows:
                row = dict(raw)
                payload = row["payload"] or {}
                product_key = str(payload.get("product_name_candidate") or "").strip().casefold()
                if not product_key:
                    unmaterialized_source_rows.append(int(row["source_row_no"]))
                    continue
                product_id = str(_product_id(product_key))
                if product_id not in product_ids:
                    unmaterialized_source_rows.append(int(row["source_row_no"]))
                    continue
                by_product_id[product_id].append(row)

            missing_source_products = sorted(set(product_ids) - set(by_product_id))
            if missing_source_products:
                raise RuntimeError(f"materialized Products missing Main Stock evidence: {missing_source_products[:20]}")

            category_counts = Counter()
            examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
            continuity_products = 0
            review_products = 0
            for product_id in sorted(product_ids, key=lambda pid: str(product_ids[pid]["local_name"]).casefold()):
                category, evidence = _classify(by_product_id[product_id], catalogue)
                category_counts[category] += 1
                if category.startswith("CONTINUITY_"):
                    continuity_products += 1
                else:
                    review_products += 1
                if len(examples[category]) < MAX_EXAMPLES:
                    examples[category].append(
                        {
                            "product_id": product_id,
                            "local_name": product_ids[product_id]["local_name"],
                            "default_unit": product_ids[product_id]["default_unit"],
                            **evidence,
                        }
                    )

            mapping_count = int(conn.execute(text("SELECT COUNT(*) FROM product_cms_mappings")).scalar_one())
            if mapping_count != 0:
                raise RuntimeError(f"read-only reconciliation planner expected product_cms_mappings=0, found {mapping_count}")

            result = {
                "mode": "READ_ONLY_CMS_RECONCILIATION_PLAN",
                "migration": revision,
                "migration_batch_id": batch["migration_batch_id"],
                "inventory_source_hash": batch["source_hash"],
                "catalogue_version_id": version["catalogue_version_id"],
                "catalogue_source_hash": version["source_hash"],
                "catalogue_effective_date": version["effective_date"].isoformat() if version["effective_date"] else None,
                "catalogue_rows": len(catalogue_rows),
                "materialized_products": len(product_rows),
                "products_with_source_evidence": len(by_product_id),
                "continuity_candidate_products": continuity_products,
                "review_or_unmapped_products": review_products,
                "category_counts": dict(sorted(category_counts.items())),
                "category_examples": dict(sorted(examples.items())),
                "unmaterialized_main_source_rows": unmaterialized_source_rows,
                "product_cms_mappings": mapping_count,
                "mutation": False,
                "mapping_mutation": False,
                "inventory_mutation": False,
                "database_canonical": False,
                "migration_baseline_accepted": False,
                "policy": "deterministic screening only; code equality is evidence, not identity proof",
            }
            print(json.dumps(result, sort_keys=True))
            print(
                "f6d_cms_reconciliation_plan=pass mutation=false mapping_mutation=false "
                "ai_required=false database_canonical=false"
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
