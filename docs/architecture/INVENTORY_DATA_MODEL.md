# Inventory Data Model

Status: **canonical foundation design contract — implementation pending**

Canonical companion: `CANONICAL_INVENTORY_FOUNDATION.md`.

## Goal

Represent medicine-store inventory so the database remains correct regardless of spreadsheet row order, workbook formulas, client UI, store count, catalogue changes, or future AI workflow design.

Primary chain:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

The database must preserve source truth, lot-level history, location-level stock, catalogue history and auditability without making spreadsheet rows or derived Excel cells canonical identifiers.

## Product

Stable local operational identity.

Minimum fields:

- `product_id` — immutable internal identifier.
- `local_name` — preferred local item name.
- `type` — optional operational type/category.
- `default_unit` — established operational unit.
- `active`.
- optional `display_order` for human views.
- timestamps.

`No.` from Main Stock is not canonical identity.

Renaming does not create a new Product unless the real operational identity changes.

## Product Lot

Expiry-specific physical/operational identity belonging to one Product.

Minimum fields:

- `lot_id`.
- `product_id`.
- `expiry_date` when known.
- lifecycle/status metadata.
- optional receipt/source identity snapshot reference.
- timestamps.

Normal v1 lot boundary remains Product + Expiry Date.

A terminal expiry suffix in a spreadsheet item name is presentation metadata, not the database key.

Location does not belong in Lot identity. The same Lot may hold quantity in Main Store and multiple Sub Stores.

## Store / Location

Canonical location entity:

- `store_id`.
- unique operational `code`.
- `name`.
- `store_type = MAIN | SUB` for v1.
- `active`.
- optional display metadata.
- timestamps.

V1 has exactly one configured Main Store and unlimited Sub Stores.

Do not duplicate Product/Lot/Ledger tables per store.

## Canonical movement ledger

Quantity truth is movement-based rather than balance-cell mutation.

A canonical movement contains at least:

- `transaction_id`.
- `store_id`.
- `lot_id`.
- `transaction_type`.
- `quantity NUMERIC(18,3)` under the F2 quantity policy.
- effective date/time.
- source/provenance type and ID/line ID where available.
- operation/idempotency ID.
- actor identity/context.
- reason/note where relevant.
- reversal/correction link where required.
- created timestamp.

Required semantic types for the foundation:

- `OPENING_BALANCE` / migration opening;
- `RECEIPT`;
- `USAGE`;
- `ADJUSTMENT_POSITIVE`;
- `ADJUSTMENT_NEGATIVE`;
- `TRANSFER_OUT`;
- `TRANSFER_IN`.

The exact table shape may use one general ledger plus source-specific detail tables. Do not add movement types merely for report formatting.

## Quantity and balance semantics

Operational inventory views may expose:

- Original / Opening Qty;
- Received Qty;
- Deducted / Used Qty;
- Current Qty;
- Total Store Stock.

These are not separate mutable sources of truth.

For one Store + Lot:

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

`Received Qty` and `Deducted Qty` are aggregates for a selected period/filter.

`Current Qty` is ledger-derived. A cached/materialized balance may exist later for performance only if deterministic reconciliation against movements remains available.

For a Lot:

```text
Total Store Stock = SUM(Current Qty across all managed stores)
```

For a Product, total stock is the sum across its Lots and Stores.

Never maintain a second manually editable total-stock truth.

## External receipts

External receipt introduces stock into the managed system and is distinct from internal transfer.

### Receipt batch

Candidate fields:

- `receipt_batch_id`.
- external/source transfer/document number.
- source/effective date.
- destination `store_id`.
- external source label/reference.
- source document hash when available.
- status.
- timestamps/actor context.

Do not force external suppliers into the internal `stores` table merely because source documents use the word transfer/store.

### Receipt line

Candidate fields:

- `receipt_line_id`.
- `receipt_batch_id`.
- source line number.
- resolved `lot_id`.
- quantity.
- source unit.
- source price.
- source CMS code/description.
- source expiry.
- mapping/review status.

Idempotency must prevent one source line being committed twice.

A committed receipt line links to the corresponding `RECEIPT` ledger movement.

Historical receipt/source price remains transaction truth and is not overwritten by future catalogue updates.

## Internal transfers

Internal transfer moves quantity between two MSA-managed locations and must not change total system stock.

Preferred bounded structure:

### Transfer header

- `transfer_id`.
- source `store_id`.
- destination `store_id`.
- effective date.
- status.
- operation/idempotency identity.
- source/note.
- actor/proposal/approval context where applicable.

### Transfer line

- `transfer_line_id`.
- `transfer_id`.
- `lot_id`.
- quantity.

Commit creates linked atomic effects:

- source `TRANSFER_OUT`;
- destination `TRANSFER_IN`.

Product/Lot identity is preserved.

Both effects succeed or fail together, share transfer provenance, and remain idempotent on retry.

Do not model a real internal transfer as unrelated manual adjustments.

## Usage / deduction

Usage is a dated movement from the actual issuing Store + Lot.

Conceptual operation:

`record_usage(store_id, lot_id, effective_date, quantity, source, operation_id, actor)`

Daily Usage Day 1-31 is a monthly pivot/edit representation of these records.

Multiple same-day events may remain separate canonical events while a view displays their sum.

Actual historical movement is preserved even when FIFO/FEFO advice would have preferred another Lot.

## Adjustments and corrections

Physical count corrections and exceptional changes use explicit adjustment movements with reason, actor, timestamp and source/approval evidence where applicable.

Do not silently rewrite prior receipt/usage history.

Committed historical mistakes should use reversal/corrective patterns under the locked F2 correction policy.

## Universal CMS Catalogue

The CMS catalogue is a separate global/versioned external reference domain.

### Catalogue version

Candidate fields:

- `catalogue_version_id`.
- effective date/period.
- source label/hash.
- import timestamp.

### Catalogue item

Candidate fields include:

- `catalogue_item_id`.
- `catalogue_version_id`.
- `cms_code`.
- CMS/brand name.
- description.
- form/type/class.
- selling price.

### Product-CMS mapping

Use an auditable/version-aware mapping entity between local Product and CMS catalogue identity.

CMS code alone never becomes stable local identity because codes can change, disappear, retire or be reused.

Store location does not duplicate the mapping. All stores use the same accepted local Product -> CMS mapping.

### Price separation

Keep distinct:

- current catalogue selling price;
- historical receipt/source price;
- any compatibility/display-derived price.

Updating a catalogue must not rewrite genuine historical transaction price.

## Main Stock / operational inventory view

The future default inventory view can expose a compact set such as:

`Local Item Name | CMS Name | Type | Unit | CMS Code | Expiry Date | Original/Opening Qty | Received Qty | Deducted Qty | Current Qty | CMS Price`

with Store/Location provided by view context or an explicit column.

These columns map to canonical Product/Lot/CMS fields or movement aggregates. They are not a requirement to store a same-shaped `main_stock` table.

## This Month Received

Derived view over current-period receipt movements plus Product/Lot/Store information.

Do not create a second receipt truth table merely to reproduce the worksheet.

## Reorder / planning domain

Exact legacy Estimated Reorder Qty formula is not part of the canonical inventory schema requirement.

Future reorder/planning is a dynamic workflow layer over the canonical foundation and may use:

- current location and total stock;
- historical usage/trends;
- expiry risk;
- incoming stock/transfers;
- safety stock and lead time;
- seasonality or unusual demand;
- deterministic calculation modules;
- AI proposal;
- single/multi-agent review;
- human adjustment/approval.

The database foundation must preserve the data needed for these approaches without locking the project to one Excel formula.

A final approved reorder may be stored as a durable business artifact/snapshot with proposal/review/approval provenance.

## Monthly reporting / snapshots

Monthly snapshots are useful for reporting and archive reconstruction but do not replace the lifetime movement ledger.

Snapshot rows, when implemented, should be Store + Lot scoped and may include opening, receipt total, usage summary, closing balance and report-context metadata.

Exact legacy Excel reset/archive formula parity is deferred unless a specific behavior changes canonical quantity/provenance truth.

Migration opening balances remain explicit provenance-bearing movements under the F2 decision.

## Actors and audit

Every protected inventory operation is attributable to stable human and/or authorized non-human actor context.

Use existing canonical concepts:

- users / user IDs;
- service principals / AI agent identities as appropriate;
- client/channel;
- operation/idempotency ID;
- timestamps;
- reason/source/evidence;
- proposal/review/approval relationships when applicable;
- audit event outcome/read-back.

Human UI and AI workflows use the same typed backend operation layer. AI reasoning does not imply mutation authority.

## Product lifecycle and view order

A spreadsheet row insertion may mean a new Product, new Lot, or only a view/order change. The backend must classify the semantic change.

A row disappearing from a current view does not delete historical Product/Lot/transactions.

Display order is presentation metadata only.

## Fixed assets

Fixed Assets remain a separate domain and must not be forced into medicine/consumable stock transactions simply because the same source documents contain them.

## F6D schema gap from current shadow migrations

Current shadow schema already contains Products, Product Lots, CMS version/items, identities/audit and a lot-only transaction ledger, but it does not yet satisfy this foundation because:

- there is no canonical Store/Location entity;
- inventory transactions are not location-aware;
- transfer semantics are absent;
- receipt provenance/destination structures are incomplete for the target model;
- Product-CMS mapping must be sufficient for current/versioned accepted mapping;
- total-stock/location-balance projection proof has not been performed against a fresh real source snapshot.

## Constraints to preserve

- preserve local operational identity and names unless authorized change occurs;
- preserve distinct expiry Lots;
- never use CMS code alone as identity;
- preserve actual historical movement;
- keep source provenance and idempotency;
- keep quantities fixed-point under the F2 policy;
- prevent silent negative stock under the locked F2 policy;
- keep derived values derivable from canonical inputs;
- treat worksheet/report layouts as projections unless they contain genuinely independent business data.
