# Main Stock / Daily Usage Materialization Contract

Status: **LOCKED — F6D source-safe materialization contract**

## Purpose

Prevent worksheet mirror rows from becoming duplicate canonical inventory objects during migration from `Medicine Store Cloud`.

## Core rule

> **Main Stock and Daily Usage are user-facing source projections of the same inventory domain. They are not two canonical inventory tables and their source-row counts must never be summed as canonical inventory count.**

The fresh F6D staging batch contains both worksheets as source evidence. Therefore a staging count such as 1,646 means source records, not 1,646 inventory items/lots.

## Migration ownership

### Main Stock

Main Stock is the primary migration source for:

- local Product candidate identity;
- structured Expiry Date / Lot candidate identity;
- Unit;
- current Main Store stock/balance evidence;
- current-month received/usage aggregates used only as consistency evidence;
- local CMS code/name/price/remark evidence and mapping hints.

Each populated Main Stock item row produces at most one canonical Product/Lot migration candidate before duplicate-key reconciliation.

### Daily Usage

Daily Usage is joined evidence for the same Product/Lot candidates. It is the primary source for:

- day 1-31 usage values;
- monthly usage consistency;
- monthly remaining consistency;
- future reconstruction of dated usage events only where source semantics are accepted.

A Daily Usage row must not independently create a second Product, Lot, opening balance, or store balance when the matching Main Stock row already represents that inventory line.

## Canonical DB shape

Do not create `main_stock` and `daily_usage` canonical tables that clone worksheet shape.

Canonical data remains normalized around:

`Product -> Lot -> Store -> Movement -> Balance`

with separate versioned CMS Catalogue and Product-CMS mapping lifecycle.

Main Stock and Daily Usage are regenerated as operational views/projections from canonical data.

Daily Usage day columns are a pivot over dated usage events, not 31 physical database columns.

Main Stock columns such as Remaining Stock, Received Stock, This Month Usage and Stock Status Today are projections/aggregates over canonical movement truth rather than four independent mutable balances.

## Candidate count semantics

Report these separately:

- `main_stock_source_rows`;
- `daily_usage_source_rows`;
- `staged_source_records` = both source sets combined;
- `canonical_lot_candidates_before_reconciliation` = Main Stock-derived candidates only;
- `unique_products` after local Product normalization;
- `unique_lots` after Product + structured Expiry reconciliation.

Never label `staged_source_records` as inventory rows/items/lots.

The current live row count is snapshot evidence, not a hard-coded system constant. It will change as lots are added, depleted, closed, or otherwise represented differently in the operational view.

## Join / reconciliation rule

Match Daily Usage to Main Stock using canonical candidate semantics, not row number alone.

Primary v1 reconciliation key:

`normalized local Product candidate + structured Expiry Date`

Preserve raw item names and source row numbers for provenance and diagnostics.

If the key is ambiguous, duplicated, missing, or cross-sheet values conflict, flag review rather than silently merging unrelated records.

CMS Code must never be used as the sole join or Product identity key.

## Opening balance migration

The initial source-safe materializer may create one migration `OPENING_BALANCE` per accepted Main Store Lot candidate using the accepted current-balance source field.

It must not create a second opening balance from Daily Usage.

Current-month Received/Usage worksheet aggregates must not be converted into fabricated historical movement events unless stronger source provenance supports that reconstruction.

## CMS boundary

CMS Catalogue is a separate global/versioned dataset.

Local Product/Lot materialization must remain possible when CMS mapping is unmapped, recycled, discontinued, stale, or under review, provided local inventory identity and quantity evidence are otherwise safe.

Mapping uncertainty is not automatically inventory-identity failure.

## Required F6D proof

Before canonical promotion, prove:

1. fresh source record counts are reported per worksheet;
2. canonical candidates are derived from Main Stock only;
3. Daily Usage rows join to those candidates without creating duplicate Products/Lots/opening balances;
4. ambiguous duplicate keys are surfaced explicitly;
5. Main Store balances reconstructed from canonical movements match accepted Main Stock current-state evidence;
6. Daily Usage projection can be regenerated from canonical usage data/history when that history is materialized;
7. PostgreSQL remains non-canonical until explicit promotion.
