from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

POSITIVE_TYPES = {"OPENING_BALANCE", "RECEIPT", "ADJUSTMENT_POSITIVE"}
NEGATIVE_TYPES = {"USAGE", "ADJUSTMENT_NEGATIVE"}
ALL_TYPES = POSITIVE_TYPES | NEGATIVE_TYPES


class LedgerError(Exception):
    pass


class DuplicateOperationError(LedgerError):
    pass


class NegativeStockError(LedgerError):
    pass


def lot_balance(connection: Connection, lot_id: str) -> Decimal:
    value = connection.execute(
        text(
            """
            SELECT COALESCE(SUM(
                CASE
                    WHEN transaction_type IN ('OPENING_BALANCE','RECEIPT','ADJUSTMENT_POSITIVE') THEN quantity
                    WHEN transaction_type IN ('USAGE','ADJUSTMENT_NEGATIVE') THEN -quantity
                    ELSE 0
                END
            ), 0)
            FROM inventory_transactions
            WHERE lot_id = :lot_id
            """
        ),
        {"lot_id": lot_id},
    ).scalar_one()
    return Decimal(value)


def record_transaction(
    connection: Connection,
    *,
    lot_id: str,
    transaction_type: str,
    quantity: Decimal,
    effective_date: date,
    operation_id: str,
    source_type: str = "synthetic",
    source_id: str | None = None,
    reversal_of_transaction_id: str | None = None,
    reason: str | None = None,
    metadata: dict[str, Any] | None = None,
    allow_negative: bool = False,
) -> str:
    if transaction_type not in ALL_TYPES:
        raise LedgerError(f"unsupported transaction type: {transaction_type}")
    if quantity <= 0:
        raise LedgerError("quantity must be positive")

    existing_operation = connection.execute(
        text("SELECT transaction_id FROM inventory_transactions WHERE operation_id = :operation_id"),
        {"operation_id": operation_id},
    ).scalar_one_or_none()
    if existing_operation is not None:
        raise DuplicateOperationError(operation_id)

    if transaction_type in NEGATIVE_TYPES and not allow_negative:
        current = lot_balance(connection, lot_id)
        if current - quantity < 0:
            raise NegativeStockError(
                f"operation would create negative stock: balance={current}, quantity={quantity}"
            )

    try:
        transaction_id = connection.execute(
            text(
                """
                INSERT INTO inventory_transactions (
                    lot_id,
                    transaction_type,
                    quantity,
                    effective_date,
                    source_type,
                    source_id,
                    operation_id,
                    reversal_of_transaction_id,
                    reason,
                    metadata
                ) VALUES (
                    :lot_id,
                    :transaction_type,
                    :quantity,
                    :effective_date,
                    :source_type,
                    :source_id,
                    :operation_id,
                    :reversal_of_transaction_id,
                    :reason,
                    CAST(:metadata AS jsonb)
                )
                RETURNING transaction_id
                """
            ),
            {
                "lot_id": lot_id,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "effective_date": effective_date,
                "source_type": source_type,
                "source_id": source_id,
                "operation_id": operation_id,
                "reversal_of_transaction_id": reversal_of_transaction_id,
                "reason": reason,
                "metadata": __import__("json").dumps(metadata or {}),
            },
        ).scalar_one()
    except IntegrityError as exc:
        if "operation_id" in str(exc.orig):
            raise DuplicateOperationError(operation_id) from exc
        raise

    return str(transaction_id)
