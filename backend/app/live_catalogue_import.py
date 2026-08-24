from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import create_engine, text

from app.catalogue import CatalogueRow, import_catalogue, source_hash
from app.db import EXPECTED_MIGRATION, normalize_database_url
from app.live_sheet_snapshot import GoogleSheetReader

DEFAULT_SHEET = "CMS_Price_List_202608"
DEFAULT_RANGE = "A1:G10000"
PARSER_VERSION = "live-sheet-v1"
EXPECTED_HEADERS = (
    "Code",
    "Brand Name",
    "Description",
    "Form",
    "Type",
    "Class",
    "Selling Price (¥)",
)
DATE_RE = re.compile(r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})")


def _norm(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _price(value: Any) -> tuple[Decimal | None, bool]:
    if value in (None, ""):
        return None, True
    try:
        return Decimal(str(value).replace(",", "").replace("¥", "").strip()), True
    except (InvalidOperation, ValueError, TypeError):
        return None, False


def _effective_date(title: str | None) -> date | None:
    if not title:
        return None
    match = DATE_RE.search(title)
    if not match:
        return None
    return datetime(
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("day")),
    ).date()


def _first_title(values: list[list[Any]]) -> str | None:
    for row in values[:2]:
        if not row:
            continue
        title = _norm(row[0])
        if title:
            return title
    return None


def _read_source() -> dict[str, Any]:
    spreadsheet_id = os.environ.get("MSA_GOOGLE_SPREADSHEET_ID")
    credential_file = os.environ.get("MSA_GOOGLE_SERVICE_ACCOUNT_FILE")
    sheet_name = os.environ.get("MSA_CMS_CATALOGUE_SHEET", DEFAULT_SHEET).strip() or DEFAULT_SHEET
    if not spreadsheet_id or not credential_file:
        raise RuntimeError("MSA_GOOGLE_SPREADSHEET_ID and MSA_GOOGLE_SERVICE_ACCOUNT_FILE are required")

    reader = GoogleSheetReader(credential_file)
    values = reader._range(spreadsheet_id, f"'{sheet_name}'!{DEFAULT_RANGE}")
    if len(values) < 3:
        raise RuntimeError("CMS catalogue source has fewer than three rows")

    title = _first_title(values)
    headers = tuple(_norm(value) or "" for value in values[2][:7])
    if headers != EXPECTED_HEADERS:
        raise RuntimeError(f"CMS catalogue header drift: {headers!r}")

    rows: list[CatalogueRow] = []
    blank_code_rows: list[int] = []
    blank_price_rows: list[int] = []
    invalid_price_rows: list[int] = []
    duplicate_codes: dict[str, list[int]] = defaultdict(list)

    for source_row_no, raw in enumerate(values[3:], start=4):
        padded = list(raw) + [None] * max(0, 7 - len(raw))
        if not any(_norm(value) for value in padded[:7]):
            continue
        code = _norm(padded[0])
        if not code:
            blank_code_rows.append(source_row_no)
            continue
        price, price_ok = _price(padded[6])
        if not price_ok:
            invalid_price_rows.append(source_row_no)
            continue
        if price is None:
            blank_price_rows.append(source_row_no)
        duplicate_codes[code].append(source_row_no)
        rows.append(
            CatalogueRow(
                cms_code=code,
                brand_name=_norm(padded[1]),
                description=_norm(padded[2]),
                form=_norm(padded[3]),
                type=_norm(padded[4]),
                class_name=_norm(padded[5]),
                selling_price=price,
                source_row_no=source_row_no,
            )
        )

    duplicate_codes = {code: row_nos for code, row_nos in duplicate_codes.items() if len(row_nos) > 1}
    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "source_label": f"google-sheet:{spreadsheet_id}:{sheet_name}:{title or 'untitled'}",
        "title": title,
        "effective_date": _effective_date(title),
        "rows": rows,
        "blank_code_rows": blank_code_rows,
        "blank_price_rows": blank_price_rows,
        "invalid_price_rows": invalid_price_rows,
        "duplicate_codes": duplicate_codes,
    }


def _plan(source: dict[str, Any]) -> dict[str, Any]:
    rows: list[CatalogueRow] = source["rows"]
    price_presence = Counter("priced" if row.selling_price is not None else "blank_price" for row in rows)
    return {
        "mode": "PLAN",
        "sheet_name": source["sheet_name"],
        "title": source["title"],
        "effective_date": source["effective_date"].isoformat() if source["effective_date"] else None,
        "source_label": source["source_label"],
        "source_hash": source_hash(rows),
        "parsed_rows": len(rows),
        "unique_codes": len({row.cms_code for row in rows}),
        "duplicate_code_count": len(source["duplicate_codes"]),
        "duplicate_codes": source["duplicate_codes"],
        "blank_code_rows": source["blank_code_rows"],
        "blank_price_rows": source["blank_price_rows"],
        "invalid_price_rows": source["invalid_price_rows"],
        "price_presence": dict(sorted(price_presence.items())),
        "database_canonical": False,
        "migration_baseline_accepted": False,
        "mapping_mutation": False,
        "inventory_mutation": False,
    }


def _assert_source_safe(source: dict[str, Any]) -> None:
    if source["blank_code_rows"]:
        raise RuntimeError(f"blank CMS code rows require review: {source['blank_code_rows'][:20]}")
    if source["invalid_price_rows"]:
        raise RuntimeError(f"invalid CMS price rows require review: {source['invalid_price_rows'][:20]}")
    if source["duplicate_codes"]:
        sample = dict(list(source["duplicate_codes"].items())[:20])
        raise RuntimeError(f"duplicate CMS codes require review before version import: {sample!r}")


def _counts(conn) -> dict[str, int]:
    return {
        "products": int(conn.execute(text("SELECT COUNT(*) FROM products")).scalar_one()),
        "product_lots": int(conn.execute(text("SELECT COUNT(*) FROM product_lots")).scalar_one()),
        "inventory_transactions": int(conn.execute(text("SELECT COUNT(*) FROM inventory_transactions")).scalar_one()),
        "product_cms_mappings": int(conn.execute(text("SELECT COUNT(*) FROM product_cms_mappings")).scalar_one()),
        "cms_catalogue_versions": int(conn.execute(text("SELECT COUNT(*) FROM cms_catalogue_versions")).scalar_one()),
        "cms_catalogue_items": int(conn.execute(text("SELECT COUNT(*) FROM cms_catalogue_items")).scalar_one()),
    }


def _execute(conn, source: dict[str, Any]) -> dict[str, Any]:
    revision = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one()
    if revision != EXPECTED_MIGRATION:
        raise RuntimeError(f"migration drift: {revision!r} != {EXPECTED_MIGRATION!r}")
    _assert_source_safe(source)

    before = _counts(conn)
    rows: list[CatalogueRow] = source["rows"]
    digest = source_hash(rows)
    expected_hash = os.environ.get("MSA_EXPECTED_CMS_SOURCE_HASH", "").strip()
    if expected_hash and digest != expected_hash:
        raise RuntimeError(f"CMS source hash changed: {digest!r} != expected {expected_hash!r}")

    version_id, created = import_catalogue(
        conn,
        rows=rows,
        effective_date=source["effective_date"],
        source_label=source["source_label"],
        parser_version=PARSER_VERSION,
    )

    persisted = conn.execute(
        text(
            """
            SELECT source_hash, row_count, import_status, parser_version
            FROM cms_catalogue_versions
            WHERE catalogue_version_id=CAST(:version_id AS uuid)
            """
        ),
        {"version_id": version_id},
    ).mappings().one()
    item_count = int(
        conn.execute(
            text("SELECT COUNT(*) FROM cms_catalogue_items WHERE catalogue_version_id=CAST(:version_id AS uuid)"),
            {"version_id": version_id},
        ).scalar_one()
    )
    if persisted["source_hash"] != digest or int(persisted["row_count"]) != len(rows) or item_count != len(rows):
        raise RuntimeError("catalogue version readback mismatch")
    if persisted["import_status"] != "complete" or persisted["parser_version"] != PARSER_VERSION:
        raise RuntimeError("catalogue version metadata mismatch")

    after = _counts(conn)
    for protected in ("products", "product_lots", "inventory_transactions", "product_cms_mappings"):
        if before[protected] != after[protected]:
            raise RuntimeError(f"catalogue import changed protected domain count: {protected}")

    operation_id = f"cms-catalogue-import:{digest}"
    if conn.execute(
        text("SELECT COUNT(*) FROM audit_events WHERE operation_id=:operation_id AND action='cms_catalogue_live_import'"),
        {"operation_id": operation_id},
    ).scalar_one() == 0:
        conn.execute(
            text(
                """
                INSERT INTO audit_events
                    (client_channel, operation_id, action, outcome, reason, details)
                VALUES
                    ('migration', :operation_id, 'cms_catalogue_live_import', 'SUCCESS',
                     'Shadow import of versioned live CMS catalogue reference data; no local mapping mutation',
                     CAST(:details AS jsonb))
                """
            ),
            {
                "operation_id": operation_id,
                "details": json.dumps(
                    {
                        "catalogue_version_id": version_id,
                        "source_hash": digest,
                        "row_count": len(rows),
                        "effective_date": source["effective_date"].isoformat() if source["effective_date"] else None,
                        "mapping_mutation": False,
                        "inventory_mutation": False,
                    },
                    sort_keys=True,
                ),
            },
        )

    return {
        **_plan(source),
        "mode": "EXECUTE",
        "catalogue_version_id": version_id,
        "created": created,
        "persisted_version_rows": item_count,
        "protected_counts_before": {key: before[key] for key in ("products", "product_lots", "inventory_transactions", "product_cms_mappings")},
        "protected_counts_after": {key: after[key] for key in ("products", "product_lots", "inventory_transactions", "product_cms_mappings")},
        "catalogue_counts_after": {
            "cms_catalogue_versions": after["cms_catalogue_versions"],
            "cms_catalogue_items": after["cms_catalogue_items"],
        },
        "mutation": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    source = _read_source()
    plan = _plan(source)
    if not args.execute:
        print(json.dumps(plan, sort_keys=True))
        print("live_cms_catalogue_plan=pass mutation=false mapping_mutation=false")
        return

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            result = _execute(conn, source)
        print(json.dumps(result, sort_keys=True))
        print("live_cms_catalogue_import=pass shadow_only=true mapping_mutation=false database_canonical=false")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
