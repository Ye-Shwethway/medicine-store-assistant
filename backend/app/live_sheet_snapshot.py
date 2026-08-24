from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import requests
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from sqlalchemy import Connection, text

from app.shadow_migration import row_hash

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
MAIN_SHEET = "Main Stock"
USAGE_SHEET = "Daily Usage"
DEFAULT_STORE_CODE = "MAIN"
GOOGLE_DATE_EPOCH = datetime(1899, 12, 30)
EXPIRY_SUFFIX_RE = re.compile(r"\s*\((?P<month>0?[1-9]|1[0-2])/(?P<year>\d{2}|\d{4})\)\s*$")


def _decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _norm(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _header_map(header: list[Any]) -> dict[str, int]:
    return {str(value).strip(): index for index, value in enumerate(header) if value not in (None, "")}


def _get(row: list[Any], columns: dict[str, int], name: str) -> Any:
    index = columns.get(name)
    if index is None or index >= len(row):
        return None
    return row[index]


def _get_any(row: list[Any], columns: dict[str, int], *names: str) -> Any:
    for name in names:
        if name in columns:
            return _get(row, columns, name)
    return None


def _sheet_date(value: Any) -> str | None:
    if value in (None, ""):
        return None

    numeric = _decimal(value)
    if numeric is not None and Decimal("20000") <= numeric <= Decimal("100000"):
        return (GOOGLE_DATE_EPOCH + timedelta(days=float(numeric))).date().isoformat()

    raw = _norm(value)
    if raw is None:
        return None

    for fmt in ("%Y-%m-%d", "%b-%Y", "%B-%Y", "%m/%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(raw, fmt)
            if fmt in {"%b-%Y", "%B-%Y", "%m/%Y"}:
                parsed = parsed.replace(day=1)
            return parsed.date().isoformat()
        except ValueError:
            continue
    return raw


def _normalize_cms_code(value: Any) -> str | None:
    normalized = _norm(value)
    if normalized is None:
        return None
    if normalized.casefold() in {"nil", "none", "n/a", "na", "-"}:
        return None
    return normalized


def _product_name_candidate(item_name: str) -> tuple[str, str | None]:
    match = EXPIRY_SUFFIX_RE.search(item_name)
    if match is None:
        return item_name.strip(), None
    month = int(match.group("month"))
    year_text = match.group("year")
    year = int(year_text)
    if len(year_text) == 2:
        year += 2000
    product_name = item_name[: match.start()].strip()
    return product_name, f"{year:04d}-{month:02d}"


def _expiry_suffix_mismatch(expiry_date: str | None, suffix_month: str | None) -> bool:
    if not expiry_date or not suffix_month:
        return False
    if len(expiry_date) < 7:
        return False
    return expiry_date[:7] != suffix_month


def _mapping_hint(serial_code: str | None, cs_name: str | None, remark: str | None) -> str:
    folded_remark = (remark or "").casefold()
    if "recycled id" in folded_remark:
        return "RECYCLED_CODE"
    if "cms discontinued" in folded_remark:
        return "CMS_DISCONTINUED"
    if not serial_code:
        return "UNMAPPED"
    if not cs_name:
        return "REVIEW_REQUIRED"
    return "ACTIVE_MATCH"


def _canonical_key(product_name: str | None, expiry_date: str | None) -> tuple[str, str]:
    return ((product_name or "").strip().casefold(), (expiry_date or "").strip().casefold())


@dataclass(frozen=True)
class SnapshotRead:
    spreadsheet_id: str
    main_values: list[list[Any]]
    usage_values: list[list[Any]]


class GoogleSheetReader:
    def __init__(self, credentials_file: str) -> None:
        path = Path(credentials_file)
        if not path.is_file():
            raise RuntimeError(f"Google service-account file not found: {path}")
        credentials = service_account.Credentials.from_service_account_file(str(path), scopes=SCOPES)
        self.session = AuthorizedSession(credentials)

    def _range(self, spreadsheet_id: str, a1_range: str) -> list[list[Any]]:
        url = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/"
            f"{requests.utils.quote(a1_range, safe='')}"
        )
        response = self.session.get(
            url,
            params={"majorDimension": "ROWS", "valueRenderOption": "UNFORMATTED_VALUE"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("values", [])

    def read_inventory_snapshot(self, spreadsheet_id: str) -> SnapshotRead:
        return SnapshotRead(
            spreadsheet_id=spreadsheet_id,
            main_values=self._range(spreadsheet_id, f"'{MAIN_SHEET}'!A1:U1005"),
            usage_values=self._range(spreadsheet_id, f"'{USAGE_SHEET}'!A1:AM1005"),
        )


def _main_payloads(values: list[list[Any]]) -> list[dict[str, Any]]:
    if not values:
        return []
    columns = _header_map(values[0])
    payloads: list[dict[str, Any]] = []
    for row_no, row in enumerate(values[1:], start=2):
        item_name = _norm(_get(row, columns, "Items"))
        if not item_name:
            continue
        product_name, suffix_month = _product_name_candidate(item_name)
        expiry_date = _sheet_date(_get_any(row, columns, "Expiry Date", "Expiry Date "))
        serial_code = _normalize_cms_code(_get(row, columns, "Serial Code"))
        cs_name = _norm(_get(row, columns, "CS Name"))
        remark = _norm(_get(row, columns, "Remark"))
        payloads.append(
            {
                "source_row_no": row_no,
                "item_name": item_name,
                "product_name_candidate": product_name,
                "item_name_expiry_suffix": suffix_month,
                "expiry_date": expiry_date,
                "expiry_suffix_mismatch": _expiry_suffix_mismatch(expiry_date, suffix_month),
                "unit": _norm(_get(row, columns, "Unit")),
                "remaining_stock": str(_decimal(_get(row, columns, "Remaining Stock"))) if _decimal(_get(row, columns, "Remaining Stock")) is not None else None,
                "received_stock": str(_decimal(_get(row, columns, "Received Stock"))) if _decimal(_get(row, columns, "Received Stock")) is not None else None,
                "stock_status_today": str(_decimal(_get(row, columns, "Stock Status Today"))) if _decimal(_get(row, columns, "Stock Status Today")) is not None else None,
                "this_month_usage": str(_decimal(_get(row, columns, "This Month Usage"))) if _decimal(_get(row, columns, "This Month Usage")) is not None else None,
                "cms_price": str(_decimal(_get(row, columns, "CMS Price"))) if _decimal(_get(row, columns, "CMS Price")) is not None else None,
                "price_display": _norm(_get(row, columns, "Price")),
                "remark": remark,
                "serial_code": serial_code,
                "cs_name": cs_name,
                "mapping_hint": _mapping_hint(serial_code, cs_name, remark),
            }
        )
    return payloads


def _usage_payloads(values: list[list[Any]]) -> list[dict[str, Any]]:
    if not values:
        return []
    columns = _header_map(values[0])
    payloads: list[dict[str, Any]] = []
    for row_no, row in enumerate(values[1:], start=2):
        item_name = _norm(_get(row, columns, "Items"))
        if not item_name:
            continue
        product_name, suffix_month = _product_name_candidate(item_name)
        expiry_date = _sheet_date(_get_any(row, columns, "Expiry Date", "Expiry Date "))
        daily = {
            str(day): str(_decimal(_get(row, columns, str(day)))) if _decimal(_get(row, columns, str(day))) is not None else None
            for day in range(1, 32)
        }
        remaining_value = _get_any(row, columns, "Remaining Stock", "Remaining  Stock")
        payloads.append(
            {
                "source_row_no": row_no,
                "item_name": item_name,
                "product_name_candidate": product_name,
                "item_name_expiry_suffix": suffix_month,
                "expiry_date": expiry_date,
                "expiry_suffix_mismatch": _expiry_suffix_mismatch(expiry_date, suffix_month),
                "remaining_stock": str(_decimal(remaining_value)) if _decimal(remaining_value) is not None else None,
                "received_stock": str(_decimal(_get(row, columns, "Received Stock"))) if _decimal(_get(row, columns, "Received Stock")) is not None else None,
                "daily_usage": daily,
                "this_month_usage": str(_decimal(_get(row, columns, "This Month Usage"))) if _decimal(_get(row, columns, "This Month Usage")) is not None else None,
                "this_month_remaining": str(_decimal(_get(row, columns, "This Month Remaining"))) if _decimal(_get(row, columns, "This Month Remaining")) is not None else None,
                "remark": _norm(_get(row, columns, "Remark")),
            }
        )
    return payloads


def _d(value: Any) -> Decimal | None:
    return _decimal(value)


def classify_main(payload: dict[str, Any]) -> tuple[str, str | None]:
    remaining = _d(payload.get("remaining_stock"))
    received = _d(payload.get("received_stock")) or Decimal("0")
    usage = _d(payload.get("this_month_usage")) or Decimal("0")
    status_today = _d(payload.get("stock_status_today"))
    if remaining is None or status_today is None:
        return "REVIEW", "missing numeric stock value"
    if payload.get("expiry_suffix_mismatch"):
        return "REVIEW", "item-name expiry suffix disagrees with structured Expiry Date"
    if remaining + received - usage != status_today:
        return "CONFLICT", "Main Stock source arithmetic mismatch"
    mapping_hint = payload.get("mapping_hint")
    if mapping_hint == "UNMAPPED":
        return "NEW_UNMAPPED", "missing accepted CMS mapping code"
    if mapping_hint == "RECYCLED_CODE":
        return "REVIEW", "CMS mapping marked Recycled ID"
    if mapping_hint == "REVIEW_REQUIRED":
        return "REVIEW", "CMS code present but dependent CMS name is missing"
    return "SAFE", None


def classify_usage(payload: dict[str, Any]) -> tuple[str, str | None]:
    remaining = _d(payload.get("remaining_stock"))
    received = _d(payload.get("received_stock")) or Decimal("0")
    month_usage = _d(payload.get("this_month_usage")) or Decimal("0")
    month_remaining = _d(payload.get("this_month_remaining"))
    if remaining is None or month_remaining is None:
        return "REVIEW", "missing numeric usage summary value"
    if payload.get("expiry_suffix_mismatch"):
        return "REVIEW", "item-name expiry suffix disagrees with structured Expiry Date"
    daily_sum = sum((_d(value) or Decimal("0") for value in payload.get("daily_usage", {}).values()), Decimal("0"))
    if daily_sum != month_usage:
        return "CONFLICT", "Daily Usage day-column sum does not equal This Month Usage"
    if remaining + received - month_usage != month_remaining:
        return "CONFLICT", "Daily Usage source arithmetic mismatch"
    return "SAFE", None


def cross_sheet_conflicts(main_rows: list[dict[str, Any]], usage_rows: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    main = {_canonical_key(row.get("product_name_candidate"), row.get("expiry_date")): row for row in main_rows}
    usage = {_canonical_key(row.get("product_name_candidate"), row.get("expiry_date")): row for row in usage_rows}
    conflicts: dict[tuple[str, str], str] = {}
    for key in sorted(set(main) & set(usage)):
        m, u = main[key], usage[key]
        if _d(m.get("this_month_usage")) != _d(u.get("this_month_usage")):
            conflicts[key] = "Main Stock and Daily Usage monthly usage mismatch"
        elif _d(m.get("stock_status_today")) != _d(u.get("this_month_remaining")):
            conflicts[key] = "Main Stock current balance and Daily Usage remaining mismatch"
    return conflicts


def _snapshot_hash(store_id: Any, all_rows: list[tuple[str, dict[str, Any]]]) -> str:
    canonical = {
        "store_id": str(store_id),
        "rows": [{"source_sheet": sheet, "payload": payload} for sheet, payload in all_rows],
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _resolve_store_id(connection: Connection, store_code: str) -> Any:
    store_id = connection.execute(
        text("SELECT store_id FROM stores WHERE code = :code AND active"),
        {"code": store_code},
    ).scalar_one_or_none()
    if store_id is None:
        raise RuntimeError(f"Active store not found for code={store_code!r}")
    return store_id


def stage_live_snapshot(
    connection: Connection,
    *,
    spreadsheet_id: str,
    main_values: list[list[Any]],
    usage_values: list[list[Any]],
    store_code: str = DEFAULT_STORE_CODE,
) -> dict[str, Any]:
    store_id = _resolve_store_id(connection, store_code)
    main_rows = _main_payloads(main_values)
    usage_rows = _usage_payloads(usage_values)
    all_rows = [(MAIN_SHEET, row) for row in main_rows] + [(USAGE_SHEET, row) for row in usage_rows]
    digest = _snapshot_hash(store_id, all_rows)
    existing = connection.execute(
        text("SELECT migration_batch_id FROM migration_batches WHERE source_hash = :h"),
        {"h": digest},
    ).scalar_one_or_none()
    if existing is not None:
        return {
            "migration_batch_id": str(existing),
            "created": False,
            "source_hash": digest,
            "store_id": str(store_id),
            "store_code": store_code,
        }

    cross_conflict = cross_sheet_conflicts(main_rows, usage_rows)
    batch_id = connection.execute(
        text("""
            INSERT INTO migration_batches
                (source_kind, source_label, source_hash, status, row_count, store_id)
            VALUES
                ('f6d_google_sheet_snapshot', :label, :hash, 'classified', :count, :store_id)
            RETURNING migration_batch_id
        """),
        {
            "label": f"google-sheet:{spreadsheet_id}:store:{store_code}",
            "hash": digest,
            "count": len(all_rows),
            "store_id": store_id,
        },
    ).scalar_one()

    counts = {"SAFE": 0, "REVIEW": 0, "CONFLICT": 0, "NEW_UNMAPPED": 0}
    mapping_hints: dict[str, int] = {}
    for sheet, payload in all_rows:
        classification, reason = classify_main(payload) if sheet == MAIN_SHEET else classify_usage(payload)
        key = _canonical_key(payload.get("product_name_candidate"), payload.get("expiry_date"))
        if key in cross_conflict:
            classification, reason = "CONFLICT", cross_conflict[key]
        counts[classification] = counts.get(classification, 0) + 1
        if sheet == MAIN_SHEET:
            hint = str(payload.get("mapping_hint") or "UNKNOWN")
            mapping_hints[hint] = mapping_hints.get(hint, 0) + 1
        connection.execute(
            text("""
                INSERT INTO migration_source_rows
                    (migration_batch_id, source_sheet, source_row_no, source_row_hash, classification, review_reason, payload)
                VALUES (:batch, :sheet, :row_no, :row_hash, :class, :reason, CAST(:payload AS jsonb))
            """),
            {
                "batch": batch_id,
                "sheet": sheet,
                "row_no": payload["source_row_no"],
                "row_hash": row_hash(sheet, payload),
                "class": classification,
                "reason": reason,
                "payload": json.dumps(payload, sort_keys=True, separators=(",", ":")),
            },
        )

    return {
        "migration_batch_id": str(batch_id),
        "created": True,
        "source_hash": digest,
        "store_id": str(store_id),
        "store_code": store_code,
        "row_count": len(all_rows),
        "classification_counts": counts,
        "mapping_hint_counts": mapping_hints,
    }


def configured_snapshot_read() -> SnapshotRead:
    spreadsheet_id = os.environ.get("MSA_GOOGLE_SPREADSHEET_ID")
    credential_file = os.environ.get("MSA_GOOGLE_SERVICE_ACCOUNT_FILE")
    if not spreadsheet_id or not credential_file:
        raise RuntimeError("MSA_GOOGLE_SPREADSHEET_ID and MSA_GOOGLE_SERVICE_ACCOUNT_FILE are required")
    return GoogleSheetReader(credential_file).read_inventory_snapshot(spreadsheet_id)
