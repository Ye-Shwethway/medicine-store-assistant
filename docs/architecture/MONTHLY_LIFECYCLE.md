# Monthly Inventory Lifecycle

Status: **design contract — implementation pending**

## Purpose

Preserve the useful behavior of the existing Excel Master workflow while moving monthly history and month-transition logic into deterministic backend operations.

The current four core operational concepts remain first-class:

1. Main Stock
2. Daily Usage
3. This Month Received
4. Final Reorder

The database must be able to produce a historical month package equivalent to those four views without depending on an old workbook copy as the only archive.

## Month entity

Represent each operating month explicitly.

Candidate fields:

- `month_id`
- `year`
- `month_number`
- `status` — `OPEN`, `CLOSING`, `CLOSED`
- `opened_at`
- `closed_at`
- `closed_by_actor`
- optional close-operation identifier

Only one normal active store month should be `OPEN` unless a future workflow explicitly requires overlap.

## Open month behavior

At month open:

- prior closed-month lot closing balances become the new month's opening/brought-forward balances according to the approved carry-forward rule,
- current active products/lots become available to operational views,
- monthly usage starts at zero,
- monthly received totals start at zero,
- reorder calculations begin from current configuration and the new month's activity,
- historical prior-month transactions and snapshots remain unchanged.

Do not simulate this by deleting old transactions or overwriting their dates.

## During-month activity

### Receipts

Every committed intake records receipt batch/line history and canonical stock movement.

`This Month Received` is a projection of receipt activity whose effective date belongs to the open month, subject to explicit authorized handling of legitimate back-dated source transfers.

### Usage

Daily usage records remain date-based canonical events.

The month view projects them into Day 1–31 columns and monthly totals.

### Adjustments

Approved adjustments are explicit events with reason and actor. They must not silently masquerade as usage or receipts.

### New product/lot

A new product or expiry lot can become active during an open month.

Its month snapshot must reflect its real opening semantics:

- a newly introduced receipt lot normally begins with zero brought-forward stock and gains stock from its receipt transaction,
- a migrated pre-existing lot may have an opening balance established by the migration evidence.

## Derived monthly views

For the open month, the backend should be able to generate:

### Main Stock

Lot-level current state including current balance, current-month usage, expiry and configured reorder fields.

### Daily Usage

For each lot:

- opening/base stock as required by the compatibility contract,
- current-month received total,
- Day 1–31 aggregated usage,
- this-month usage total,
- this-month remaining/current balance,
- expiry projection.

### This Month Received

Receipt-line or receipt-summary view for the month, retaining transfer/batch traceability.

### Final Reorder

Deterministic reorder result derived from the approved reorder algorithm and the month's state/configuration.

The exact reorder formula must be documented from the existing Excel behavior before backend implementation. Do not invent a replacement formula during architecture work.

## Month close preflight

Month close is a controlled operation, not a simple date flip.

Before close, the backend should require deterministic checks such as:

- all committed usage/receipt operations are internally consistent,
- no half-committed import exists,
- stock ledger balances reconcile to materialized/current state,
- unresolved conflicts that are defined as close-blocking are surfaced,
- required reorder computation has completed under the approved rule,
- the intended month is still `OPEN`,
- the close operation has not already been completed.

Whether specific REVIEW items block close or are allowed with explicit carry-forward warning should be decided during implementation policy review.

## Closed-month snapshot

Closing creates an immutable historical snapshot package.

At minimum, preserve enough data to reproduce the four core views for that month:

- product/lot identity snapshot,
- opening stock,
- receipt totals and batch references,
- daily/monthly usage,
- closing stock,
- expiry data,
- reorder configuration used,
- final reorder result,
- relevant current CMS price/mapping snapshot if the historical report requires it.

Closed snapshots are append-only/immutable under normal operation.

If a genuine historical correction is later required, use a documented correction/amendment mechanism rather than silently rewriting the original closed snapshot.

## Next-month preparation

After successful close:

1. freeze the closed-month snapshot,
2. set the prior month to `CLOSED`,
3. create the next `OPEN` month,
4. carry forward eligible lot closing balances,
5. preserve product/lot identities even if display order changes,
6. reset only month-scoped projections, not canonical lifetime history,
7. regenerate/synchronize the Google Sheet operational mirror for the new month.

This replaces the fragile parts of macro-driven archive/reset behavior with a deterministic backend transaction or controlled sequence.

## Excel Master compatibility

The future system should support export of any closed month into an `.xlsx` workbook containing the familiar four views:

- Main Stock
- Daily Usage
- This Month Received
- Final Reorder

Historical Excel export becomes a portable representation generated from the database, not the only canonical archive.

If exact existing workbook formatting/macros must be preserved, treat that as a compatibility/export project after the canonical data model is stable.

## Back-dated source evidence

A source document may legitimately arrive or be reconciled after its effective date.

The system must distinguish:

- event effective date,
- event recorded/imported timestamp,
- month in which the event belongs operationally,
- date of later reconciliation/correction.

Never force a historical transfer into the current month merely because it was entered later.

## Historical queries

The database should allow queries such as:

- stock state at a closed month,
- usage for a product/lot on a particular date,
- receipts for a transfer or month,
- month-over-month usage changes,
- historical reorder outputs,
- price/catalouge context at a prior month.

These queries should not depend on locating an archived worksheet copy.
