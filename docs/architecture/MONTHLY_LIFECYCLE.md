# Monthly Inventory Lifecycle

Status: **reporting/compatibility design contract — foundation schema does not wait on exact Excel month formulas**

## Purpose

Describe how monthly operational views and historical reporting can be produced from the canonical movement ledger without making monthly spreadsheet resets or formulas the source of inventory truth.

Canonical companion: `CANONICAL_INVENTORY_FOUNDATION.md`.

## Foundation relationship

The canonical database is lifetime movement/history based.

Monthly views are selected-period projections over that history.

Therefore:

- do not create a new stock movement merely because a calendar month changed;
- do not delete/reset canonical receipt/usage history to imitate Excel;
- migration/opening balance provenance remains explicit under the F2 decision;
- month snapshots may be added for reporting/performance/history convenience, but they do not replace the movement ledger.

## Calendar month entity

A shared month/period entity may contain:

- month ID;
- year/month;
- open/closed/reporting status where needed;
- opened/closed timestamps and actor context.

Whether a formal operational close is mandatory for every future workflow can be decided after the canonical stock foundation is proven.

## Store-scoped monthly projections

Any monthly stock values are scoped by Store + Lot.

A monthly view may expose:

- opening/selected-period starting quantity;
- receipt total;
- transfer in/out totals;
- usage/deduction total;
- adjustments;
- closing/current quantity;
- daily usage pivot;
- CMS/display context;
- planning/reorder outputs when relevant.

System-wide reporting aggregates store-scoped values when requested; it never merges store balances into one mutable canonical total.

## Main Stock

For a selected Store and period, Main Stock is a generated operational inventory projection over Product/Lot/CMS data and movement aggregates.

## Daily Usage

Day 1-31 is a monthly pivot of normalized dated usage movements.

The future backend does not need 31 canonical database quantity columns.

## This Month Received

Generated view of selected-period receipt movements. No separate canonical receipt ledger is required for this worksheet.

## Reorder / Final Reorder

Legacy workflow used a fixed Estimated Reorder Qty calculation followed by manual reasoning and adjustment in Final Reorder.

Future planning is intentionally dynamic and may use history/trends, current/incoming stock, expiry risk, store demand, deterministic calculations, AI proposal/review and human approval.

Exact legacy reorder formula parity is not required before F6D.

A final approved reorder may later be stored as a durable reviewed business artifact/snapshot associated with a month/period when useful.

## Optional closed-period snapshot

When historical snapshot support is implemented, a Store+Lot snapshot may preserve:

- Product/Lot display context;
- selected-period opening quantity;
- receipt/transfer/usage/adjustment totals;
- closing quantity;
- relevant CMS/catalogue display context;
- final approved planning/reorder artifact references if produced.

Snapshots are append-only under normal operation and remain reconcilable to canonical movements.

## Next-period behavior

The user-facing view for a new month can present the prior period closing/current balance as the next period opening reference without fabricating a new physical stock event.

Month-scoped display totals such as received/usage/day cells reset because the selected period changed, not because canonical history was erased.

## Excel Master compatibility

The familiar monthly workbook package remains an export/report compatibility target:

- Main Stock;
- Daily Usage;
- This Month Received;
- Final Reorder when applicable.

High-fidelity formatting/macros can be implemented after the canonical database foundation is stable.

Exact legacy reset/archive formulas are not foundation blockers unless source evidence proves that a specific macro carries independent inventory truth that cannot be reconstructed from canonical movements/provenance.

## Back-dated evidence

Always distinguish:

- event effective date;
- recorded/imported timestamp;
- source provenance;
- later reconciliation/correction time.

Never force historical source evidence into the current month merely because it was entered later.

## Historical queries

The canonical database should support queries such as:

- Store/Lot balance at a date or period boundary;
- usage for a Product/Lot/Store/date;
- receipts by source transfer/document;
- internal transfers between locations;
- month-over-month usage trends;
- historical catalogue context;
- planning/reorder proposals and final approvals when those workflows are implemented.

These queries must not depend on locating an old workbook copy.

## Boundary

Do not let exact Excel monthly formula/macro parity delay the F6D canonical inventory schema unless a genuinely independent quantity/provenance rule is discovered.
