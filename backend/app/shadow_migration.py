from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Iterable

from sqlalchemy import Connection, text


@dataclass(frozen=True)
class MainStockFixtureRow:
    row_no: int
    item_name: str | None
    expiry_date: str | None
    opening_balance: Decimal | None


@dataclass(frozen=True)
class DailyUsageFixtureRow:
    row_no: int
    item_name: str | None
    usage_date: str
    quantity: Decimal | None


def _json_default(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(type(value).__name__)


def row_payload(row: object) -> dict[str, object]:
    return asdict(row)


def row_hash(source_sheet: str, payload: dict[str, object]) -> str:
    raw = json.dumps(
        {"source_sheet": source_sheet, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def batch_hash(rows: Iterable[tuple[str, dict[str, object]]]) -> str:
    canonical = [
        {"source_sheet": sheet, "payload": payload}
        for sheet, payload in rows
    ]
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=_json_default).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def classify_main_stock(row: MainStockFixtureRow) -> tuple[str, str | None]:
    if not row.item_name:
        return "REVIEW", "missing item name"
    if row.opening_balance is None:
        return "REVIEW", "missing opening balance"
    if row.opening_balance < 0:
        return "REVIEW", "negative source opening balance requires reconciliation"
    return "LOT_OPENING_CANDIDATE", None


def classify_daily_usage(row: DailyUsageFixtureRow) -> tuple[str, str | None]:
    if not row.item_name:
        return "REVIEW", "missing item name"
    if row.quantity is None or row.quantity <= 0:
        return "REVIEW", "usage quantity must be positive"
    return "USAGE_CANDIDATE", None


def stage_fixture_batch(
    connection: Connection,
    *,
    source_label: str,
    main_rows: list[MainStockFixtureRow],
    usage_rows: list[DailyUsageFixtureRow],
) -> tuple[str, bool]:
    all_rows: list[tuple[str, object]] = [
        *(('Main Stock', row) for row in main_rows),
        *(('Daily Usage', row) for row in usage_rows),
    ]
    hashed_rows = [(sheet, row_payload(row)) for sheet, row in all_rows]
    digest = batch_hash(hashed_rows)

    existing = connection.execute(
        text("SELECT migration_batch_id FROM migration_batches WHERE source_hash = :source_hash"),
        {"source_hash": digest},
    ).scalar_one_or_none()
    if existing is not None:
        return str(existing), False

    batch_id = connection.execute(
        text(
            """
            INSERT INTO migration_batches (source_kind, source_label, source_hash, status, row_count)
            VALUES ('synthetic_fixture', :source_label, :source_hash, 'classified', :row_count)
            RETURNING migration_batch_id
            """
        ),
        {"source_label": source_label, "source_hash": digest, "row_count": len(all_rows)},
    ).scalar_one()

    for sheet, row in all_rows:
        payload = row_payload(row)
        if sheet == "Main Stock":
            classification, reason = classify_main_stock(row)
        else:
            classification, reason = classify_daily_usage(row)
        connection.execute(
            text(
                """
                INSERT INTO migration_source_rows
                    (migration_batch_id, source_sheet, source_row_no, source_row_hash,
                     classification, review_reason, payload)
                VALUES
                    (:batch_id, :sheet, :row_no, :row_hash, :classification, :reason, CAST(:payload AS jsonb))
                """
            ),
            {
                "batch_id": batch_id,
                "sheet": sheet,
                "row_no": row.row_no,
                "row_hash": row_hash(sheet, payload),
                "classification": classification,
                "reason": reason,
                "payload": json.dumps(payload, default=_json_default),
            },
        )

    return str(batch_id), True
