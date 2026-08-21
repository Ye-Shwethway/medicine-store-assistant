from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable

from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError


@dataclass(frozen=True)
class CatalogueRow:
    cms_code: str
    brand_name: str | None = None
    description: str | None = None
    form: str | None = None
    type: str | None = None
    class_name: str | None = None
    selling_price: Decimal | None = None
    source_row_no: int | None = None


def canonical_payload(rows: Iterable[CatalogueRow]) -> bytes:
    payload = [
        {
            "cms_code": row.cms_code,
            "brand_name": row.brand_name,
            "description": row.description,
            "form": row.form,
            "type": row.type,
            "class_name": row.class_name,
            "selling_price": str(row.selling_price) if row.selling_price is not None else None,
            "source_row_no": row.source_row_no,
        }
        for row in rows
    ]
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def source_hash(rows: Iterable[CatalogueRow]) -> str:
    return hashlib.sha256(canonical_payload(rows)).hexdigest()


def import_catalogue(
    connection: Connection,
    *,
    rows: list[CatalogueRow],
    effective_date: date | None,
    source_label: str,
    parser_version: str = "f5-synthetic-v1",
) -> tuple[str, bool]:
    digest = source_hash(rows)
    existing = connection.execute(
        text("SELECT catalogue_version_id FROM cms_catalogue_versions WHERE source_hash = :source_hash"),
        {"source_hash": digest},
    ).scalar_one_or_none()
    if existing is not None:
        return str(existing), False

    try:
        version_id = connection.execute(
            text(
                """
                INSERT INTO cms_catalogue_versions
                    (effective_date, source_hash, source_label, row_count, import_status, parser_version)
                VALUES
                    (:effective_date, :source_hash, :source_label, :row_count, 'complete', :parser_version)
                RETURNING catalogue_version_id
                """
            ),
            {
                "effective_date": effective_date,
                "source_hash": digest,
                "source_label": source_label,
                "row_count": len(rows),
                "parser_version": parser_version,
            },
        ).scalar_one()
        for row in rows:
            connection.execute(
                text(
                    """
                    INSERT INTO cms_catalogue_items
                        (catalogue_version_id, cms_code, brand_name, description, form, type, class_name,
                         selling_price, source_row_no)
                    VALUES
                        (:version_id, :cms_code, :brand_name, :description, :form, :type, :class_name,
                         :selling_price, :source_row_no)
                    """
                ),
                {
                    "version_id": version_id,
                    "cms_code": row.cms_code,
                    "brand_name": row.brand_name,
                    "description": row.description,
                    "form": row.form,
                    "type": row.type,
                    "class_name": row.class_name,
                    "selling_price": row.selling_price,
                    "source_row_no": row.source_row_no,
                },
            )
    except IntegrityError:
        raise
    return str(version_id), True


def version_rows(connection: Connection, version_id: str) -> dict[str, dict[str, object]]:
    records = connection.execute(
        text(
            """
            SELECT cms_code, brand_name, description, form, type, class_name, selling_price
            FROM cms_catalogue_items
            WHERE catalogue_version_id = :version_id
            ORDER BY cms_code
            """
        ),
        {"version_id": version_id},
    ).mappings()
    return {row["cms_code"]: dict(row) for row in records}


def diff_versions(connection: Connection, old_version_id: str, new_version_id: str) -> dict[str, object]:
    old = version_rows(connection, old_version_id)
    new = version_rows(connection, new_version_id)
    old_codes, new_codes = set(old), set(new)
    changed: list[dict[str, object]] = []
    identity_fields = ("brand_name", "description", "form", "type", "class_name")
    for code in sorted(old_codes & new_codes):
        fields = [field for field in (*identity_fields, "selling_price") if old[code][field] != new[code][field]]
        if fields:
            changed.append({
                "cms_code": code,
                "fields": fields,
                "identity_shift_candidate": any(field in fields for field in identity_fields),
            })
    return {
        "new_codes": sorted(new_codes - old_codes),
        "removed_codes": sorted(old_codes - new_codes),
        "changed": changed,
    }
