# F6C — Canonical Inventory Foundation / Workbook Semantics Lock

Status: **CURRENT BOUNDED SLICE — foundation direction locked; documentation reconciliation in progress**

## Purpose

Extract the durable inventory meaning from the existing Medicine Store Cloud / Excel workflow before changing the PostgreSQL schema.

The goal is no longer exact workbook/formula parity. F6C exists to distinguish canonical inventory truth from spreadsheet presentation, manual calculations, and future AI workflow logic.

The existing Google Sheet/source documents remain operationally authoritative while PostgreSQL remains shadow/test only.

Canonical companion docs:

- `CANONICAL_INVENTORY_FOUNDATION.md`
- `STORE_LOCATION_MODEL.md`
- `CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `WORKBOOK_PARITY_MATRIX.md`
- `WORKBOOK_FUNCTION_CONTRACT.md`

## Locked architectural direction

Canonical foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Guiding rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

## F6C priority

### Priority A — canonical inventory foundation

Lock and source-check:

- stable local Product identity;
- expiry-specific Lot identity;
- one Main Store plus unlimited Sub Stores;
- location-scoped stock movements and balances;
- external receipts vs internal transfers;
- usage/deduction and adjustments;
- Total Store Stock as an aggregate across location balances, not a second mutable truth;
- Universal CMS Catalogue versioning and Product-to-CMS mapping;
- current catalogue price vs historical receipt/source price;
- stable human/agent actor attribution, operation IDs and audit/read-back;
- migration/opening-balance provenance.

### Priority B — operational inventory fields/views

The familiar inventory view may expose fields such as:

- Local Item Name;
- CMS Name;
- Type;
- Unit;
- CMS Code;
- Expiry Date;
- Original/Opening Qty;
- Received Qty;
- Deducted/Used Qty;
- Current Qty;
- CMS Price;
- location/store context;
- optional helper/status fields.

`No.` is display/order metadata only and is not required as canonical DB identity.

Quantity columns are not independent mutable truths:

```text
Current Qty
  = Opening
  + Receipts
  + Transfer In
  + Positive Adjustments
  - Usage
  - Transfer Out
  - Negative Adjustments
```

`Received`, `Deducted`, `Current`, and total-stock values can be generated for a selected period/location from canonical movements.

### Priority C — workbook compatibility

Main Stock and Daily Usage remain important source evidence and future preset views.

- Main Stock = stock/lot operational projection.
- Daily Usage = monthly Day 1-31 pivot/edit surface over dated usage events.
- This Month Received = filtered/derived receipt view.
- Reorder Form = working/derived view.
- Final Reorder = manually reviewable/final business output.
- Master archive = legacy reporting/archive workflow.

These surfaces must not dictate canonical table structure.

## Reorder / calculation policy

Exact legacy `Estimated Reorder Qty` formula parity is **deprioritized and non-blocking for F6D**.

The old formula exists because the workflow was manual. Future reorder logic is intentionally dynamic and may use deterministic calculations, usage trends, expiry risk, lead time, stock position, store-specific demand, AI proposal, multi-agent review, and authorized human adjustment.

F6D must preserve the underlying data needed for such reasoning. It does not need to reproduce one fixed Excel formula before the canonical inventory foundation can be implemented.

Any final approved reorder may later be stored as a durable reviewed business artifact/snapshot.

## Monthly formulas / macro policy

Exact Excel reset/archive/formula behavior is also non-blocking unless it changes canonical identity, quantity, source provenance, transfer meaning, or historical audit truth.

Initial migration still requires explicit opening-balance provenance. Monthly snapshots/reporting can be built after the ledger foundation is proven.

## Current live source evidence

The live `Medicine Store Cloud` continues to be re-read whenever current structure/value behavior matters.

Verified important surfaces include:

- Main Stock;
- Daily Usage;
- Fixed Assets;
- versioned CMS price list;
- Audit_Log;
- preserved CMS batch tabs.

The current live Main Stock/Daily Usage contract contains no populated Store/Location field and is treated as the configured legacy Main Store context during migration.

Representative Google Sheet `FORMULA` reads returned materialized values rather than exact Excel formula strings. Do not reverse-engineer legacy formulas from those values.

## F6C deliverables

1. `CANONICAL_INVENTORY_FOUNDATION.md` — primary domain contract.
2. `STORE_LOCATION_MODEL.md` — location/transfer semantics.
3. `WORKBOOK_PARITY_MATRIX.md` — source field -> canonical/view meaning.
4. `WORKBOOK_FUNCTION_CONTRACT.md` — source-backed operational compatibility rules.
5. explicit current-schema gap list.
6. fresh non-canonical shadow-import plan.

## Acceptance

F6C is sufficiently complete for F6D when:

- Product, Lot, Store, Movement, Balance, Transfer, CMS Mapping and Actor/Audit semantics are explicit;
- operational inventory columns can be explained as canonical fields or derived movement aggregates;
- Main Stock and Daily Usage can be reproduced as projections over canonical data;
- current schema gaps are explicit;
- formula/reorder/report behavior that is not foundational is clearly deferred instead of blocking implementation;
- unresolved inventory-meaning gaps are explicit rather than guessed;
- no production store mutation or canonical DB promotion occurred.

## Next slice

**F6D — Canonical Inventory Schema Parity + Fresh Shadow Import**

Implement the minimum schema changes needed by `CANONICAL_INVENTORY_FOUNDATION.md`, then perform a fresh authorized non-canonical import bound to the Main Store context and reconcile source vs DB state.

Do not reuse F6B as an accepted migration baseline merely because it already contains data.

The full configurable table-builder UI, advanced AI reorder logic, and exact Excel compatibility are later layers after the canonical inventory foundation is proven.
