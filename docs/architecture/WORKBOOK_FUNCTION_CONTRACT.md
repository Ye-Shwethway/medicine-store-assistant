# Workbook Function Contract

Status: **F6C working artifact — core Main Stock / Daily Usage / CMS / intake behavior source-backed; exact rollover and legacy reorder formula still open**

Purpose: capture the operational behavior that the future backend must reproduce while allowing the human spreadsheet layout to become configurable.

Core rule:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

## Evidence hierarchy for this contract

1. exact source document / physical movement evidence;
2. verified live operational workbook state;
3. verified current CMS catalogue;
4. established MSA skill workflow and confirmed mappings;
5. Owner-confirmed legacy process;
6. model inference only as an explicitly labeled proposal.

Representative `FORMULA` reads of the live Google Sheet returned materialized values, not formula strings, for both Main Stock and Daily Usage. Therefore exact Excel formula/macro logic must not be reconstructed from those materialized values alone.

## Main Stock

### Role

Main Stock is the primary human operational stock/lot view and structural source for the Daily Usage projection. It is not a canonical database table design.

### Identity

A Main Stock row may represent one expiry lot of a local product. Multiple sibling rows can share a CMS code while having different expiry dates. Therefore:

- local product identity is stable across expiry rows;
- lot identity is separate and normally distinguishes expiry in v1;
- CMS catalogue identity is external/versioned;
- row number/order is presentation metadata only.

A terminal `(month/year)` item-name suffix is lot presentation metadata, not part of product identity. Product-defining parentheses remain identity-significant.

### Current field behavior

Source-backed classifications are maintained in `WORKBOOK_PARITY_MATRIX.md`.

Important write/derive boundaries:

- source/authorized fields include local item metadata, structured expiry, unit, opening/base stock evidence, received activity, reorder configuration, CMS mapping/current-price metadata and supported remarks;
- current balance, monthly usage, expiry status, reorder status, estimated request quantity, shortage date, pricing output and helper/filter fields are derived or projection outputs;
- `Price` is not routine-write data; the MSA skill explicitly preserves it as Excel-derived pricing output;
- `Serial Code` is a mapping field, never canonical identity by itself.

### New expiry-lot behavior

When verified source evidence establishes a new expiry lot of an existing item:

1. preserve the existing product identity;
2. create a distinct lot;
3. keep the human row adjacent to sibling lots in compatibility views;
4. opening/base stock for the new lot begins at 0 under the established current intake workflow;
5. source receipt quantity is represented as receipt activity;
6. do not copy neighboring derived/helper outputs as source truth;
7. preserve mapping/current catalogue evidence separately from historical receipt evidence.

In the future DB, this becomes a lot creation + receipt command, not a raw row insert/update.

## Daily Usage

### Role

Daily Usage is the operational consumption-entry view. Its 1–31 day grid is a monthly presentation of normalized usage events.

Established flow:

`Main Stock structure/base state -> Daily Usage forward projection -> actual day usage -> deterministic monthly calculations -> Main Stock current-state projection`.

### Forward projection

Current verified mapping:

- Main Stock `No.` -> Daily Usage `No.`
- Main Stock `Items` -> Daily Usage `Items`
- Main Stock `Remaining Stock` -> Daily Usage `Remaining Stock`
- Main Stock `Received Stock` -> Daily Usage `Received Stock`
- Main Stock structured `Expiry Date` -> Daily Usage far-right `Expiry Date`

Daily structural parity is checked by item/lot identity rather than blindly trusting row numbers.

### Usage entry

Day columns 1–31 are the routine operational usage input surface.

Canonical future command meaning:

`record_usage(store, lot, date, quantity, source, operation_id, actor)`.

The grid cell is only a client representation of that command/event.

Rules:

- record the actual lot/date/quantity supplied by evidence;
- do not redirect history to satisfy FIFO/FEFO;
- preserve blank versus numeric zero in the view/input semantics;
- if an existing day cell already has a value, determine whether new evidence means correction/replacement or an additional event rather than blindly adding/overwriting;
- multiple same-day usage events may remain separate canonically even when the view displays their sum.

### Deterministic monthly calculations

Current established contract:

`This Month Usage = SUM(Day 1..31)`

`This Month Remaining = Remaining Stock + Received Stock - This Month Usage`

Current monthly result projects back to Main Stock:

- Daily `This Month Usage` -> Main Stock `This Month Usage`;
- Daily `This Month Remaining` -> Main Stock `Stock Status Today`.

Do not reverse-sync current calculated balance into the opening/base `Remaining Stock` field.

In the DB-backed design, the ledger becomes authoritative and both Main Stock and Daily Usage current-balance cells become projections of the same state.

## CMS catalogue and mapping

### Catalogue role

The current CMS price list is a versioned external catalogue with fields such as:

`Code | Brand Name | Description | Form | Type | Class | Selling Price`.

It is not the local product master.

### Mapping rule

Do not use `CMS code match -> identity` or `CMS code match -> price propagation` alone.

Evaluate code with compatible descriptive evidence such as local name, brand/description, strength, formulation, size/type, unit and mapping history.

A code can be retired, changed or reused. Mapping history must survive catalogue changes.

### Price rule

Current CMS catalogue price is current external catalogue truth. It must not overwrite genuine receipt-time/historical transaction price merely because the catalogue changes.

Future storage therefore separates:

- versioned catalogue price;
- local product/lot mapping;
- receipt-line source price;
- derived/current display price where business rules require it.

## Batch / receipt intake

### Source semantics

Observed current staging structure includes code, description, quantity received, unit, sale price, expiry and transfer number.

### Intake command flow

Future semantic flow must preserve the already-proven MSA process:

`source evidence -> classify fixed asset vs consumable -> resolve product/catalogue identity -> resolve existing lot/new lot/new product -> idempotency check -> stage/review if ambiguous -> commit receipt -> audit/read-back`.

Important rules:

- same product + new expiry normally creates a distinct lot;
- repeated historical source evidence must not double-intake quantity;
- if receipt is already represented, use the source for reconciliation rather than applying the quantity again;
- fixed assets remain a separate domain;
- current catalogue mapping corrections do not fabricate stock movement.

## Reorder

### Confirmed structure

Main Stock contains reorder inputs/configuration and calculated outputs including at least:

- Reorder Level;
- Reorder Surplus Factor;
- current stock/monthly usage inputs;
- Estimated Request Qty;
- reorder status/helper outputs.

Owner-confirmed workflow:

`Main Stock calculated Estimated Request Qty -> filtered Reorder Form -> copy to Final Reorder Form -> optional manual adjustment -> submit/archive final result`.

### Canonical treatment

- reorder configuration is canonical configuration;
- calculated recommendation is deterministic computed output;
- Reorder Form is a projection;
- Final Reorder becomes a durable business snapshot only when approved/submitted;
- manual final adjustment must remain distinguishable from the deterministic recommendation.

### Still open

The exact legacy formula/threshold/rounding logic behind the calculated recommendation remains source-unverified and must not be invented from current materialized values.

## This Month Received

Owner-confirmed role: a filtered/derived view of Main Stock rows with current-month received quantity.

It contains no known independent canonical inventory truth. Future implementation should generate it from receipt/lot state as a view/export.

## Audit

The live workbook already maintains significant-operation history with previous value, updated value and backup snapshot reference.

Future backend audit must add stable actor/client/operation/idempotency context while preserving the key principle:

**a successful operational mutation is not complete until its intended resulting state can be read back and attributed.**

Routine AI and human operations converge on the same typed domain command and audit layer.

## Store / location scope

Product direction is one Main Store plus unlimited Sub Stores.

The canonical model should therefore make `store/location` explicit and avoid cloning inventory tables per store.

Still to lock during F6C:

- whether each store holds independent lot balances under the same product/lot catalogue identity;
- transfer semantics between Main Store and Sub Stores;
- which reorder/usage/config values are global vs store-specific;
- default view presets and authority boundaries by location.

## Month rollover / close — still open

Exact original Excel behavior remains to be source-verified for:

- closing/current balance -> next-month opening/base balance;
- received/month-usage/day-column reset behavior;
- archive snapshot timing;
- macro effects required for historical reproduction;
- whether any operational remarks/configuration roll forward automatically.

The existing schema decision remains valid: opening balance is not fabricated as a monthly stock movement each month; monthly opening can be a frozen/derived carry-forward state, while migration uses explicit opening-balance transactions as required.

## Completion rule

F6C can advance to F6D when the canonical meaning of Product, Lot, Store, Catalogue Mapping, Receipt, Usage, Adjustment/Ledger, Reorder configuration and Audit is locked strongly enough to reproduce Main Stock and Daily Usage from DB state.

Exact cosmetic/report-only workbook behavior does not block F6D. Unresolved behavior that changes inventory meaning, identity, balance, store allocation, reorder calculation or month carry-forward does block or remains explicitly gated.
