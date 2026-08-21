from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, text

from app.db import normalize_database_url
from app.ledger import DuplicateOperationError, NegativeStockError, lot_balance, record_transaction

DATABASE_URL = os.getenv("DATABASE_URL")


def main() -> None:
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL is required")

    engine = create_engine(normalize_database_url(DATABASE_URL), pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        product_id = connection.execute(
            text(
                """
                INSERT INTO products (local_name, default_unit, active)
                VALUES ('F4 Synthetic Product', 'Piece', true)
                RETURNING product_id
                """
            )
        ).scalar_one()
        lot_id = connection.execute(
            text(
                """
                INSERT INTO product_lots (product_id, expiry_date, status)
                VALUES (:product_id, DATE '2099-12-31', 'active')
                RETURNING lot_id
                """
            ),
            {"product_id": product_id},
        ).scalar_one()

        opening_id = record_transaction(
            connection,
            lot_id=str(lot_id),
            transaction_type="OPENING_BALANCE",
            quantity=Decimal("10"),
            effective_date=date(2026, 8, 22),
            operation_id="f4-verify-opening",
        )
        record_transaction(
            connection,
            lot_id=str(lot_id),
            transaction_type="RECEIPT",
            quantity=Decimal("5"),
            effective_date=date(2026, 8, 22),
            operation_id="f4-verify-receipt",
        )
        record_transaction(
            connection,
            lot_id=str(lot_id),
            transaction_type="USAGE",
            quantity=Decimal("4"),
            effective_date=date(2026, 8, 22),
            operation_id="f4-verify-usage",
        )
        if lot_balance(connection, str(lot_id)) != Decimal("11.000"):
            raise AssertionError("unexpected balance after opening + receipt - usage")

        try:
            record_transaction(
                connection,
                lot_id=str(lot_id),
                transaction_type="USAGE",
                quantity=Decimal("20"),
                effective_date=date(2026, 8, 22),
                operation_id="f4-verify-negative",
            )
            raise AssertionError("negative stock guard did not block")
        except NegativeStockError:
            pass

        try:
            record_transaction(
                connection,
                lot_id=str(lot_id),
                transaction_type="RECEIPT",
                quantity=Decimal("1"),
                effective_date=date(2026, 8, 22),
                operation_id="f4-verify-receipt",
            )
            raise AssertionError("duplicate operation was not blocked")
        except DuplicateOperationError:
            pass

        record_transaction(
            connection,
            lot_id=str(lot_id),
            transaction_type="ADJUSTMENT_NEGATIVE",
            quantity=Decimal("10"),
            effective_date=date(2026, 8, 22),
            operation_id="f4-verify-opening-reversal",
            reversal_of_transaction_id=opening_id,
            reason="synthetic reversal verification",
        )
        if lot_balance(connection, str(lot_id)) != Decimal("1.000"):
            raise AssertionError("unexpected balance after linked reversal adjustment")

        print("F4 synthetic ledger verification PASS")
        print("balance_math=pass idempotency=pass negative_guard=pass reversal_link=pass")
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


if __name__ == "__main__":
    main()
