# Store / Location Model

Status: **F6C architecture decision — source-backed core, bounded open items remain**

## Purpose

Define the minimum location model required for Medicine Store Assistant to support one Main Store plus unlimited Sub Stores without cloning inventory tables or turning spreadsheet layouts into canonical data structures.

This document is intentionally small. It locks the semantics required for F6D schema parity and leaves unsupported workflow detail explicit.

## Evidence used

Source-backed evidence currently available:

- Owner-confirmed product direction: one Main Store plus unlimited Sub Stores.
- Current live `Medicine Store Cloud` is a single-store operational workbook and has no `Store`, `Location`, or `Sub Store` field in the populated `Main Stock` contract.
- Current live `Main Stock` therefore represents one operational store context implicitly rather than proving a multi-store schema.
- Existing inventory data-model notes already treat `This Month Received` as a projection that may include a `Sub Store Qty` display field.
- Existing receipt-batch design already anticipated `from_store` / `to_store` concepts.
- Current PostgreSQL migrations do not yet have a store/location table or location foreign key on inventory transactions.

The current Google Sheet must not be stretched into a multi-store source contract it does not contain.

## Locked core rule

> **Stock belongs to a location; product and catalogue identity do not.**

A `Product` is the stable local operational identity shared across the store system.

A `Product Lot` is the stable product/expiry operational lot identity.

A `Store/Location` identifies where quantity is physically/accountably held.

The same product/lot may therefore have balances in more than one location without creating duplicate product identities or duplicate lot identities merely because stock moved.

## Store entity

Minimum future entity:

- `store_id` — immutable internal identifier.
- `code` — unique short operational code.
- `name` — user-facing store name.
- `store_type` — `MAIN` or `SUB` for v1.
- `active` — whether the location accepts current operations.
- `display_order` — optional presentation order; never identity.
- `created_at`, `updated_at`.

V1 has exactly one active `MAIN` store and zero or more `SUB` stores.

Do not build separate product, lot, transaction, monthly, or view-definition tables per store.

## Location-scoped stock ledger

Canonical balance is derived per `(store_id, lot_id)`.

Conceptually:

```text
location_balance(store, lot)
  = opening at location
  + receipts into location
  + transfer-ins
  + positive adjustments
  - usage at location
  - transfer-outs
  - negative adjustments
```

Therefore every canonical stock movement that changes a location balance must resolve a `store_id`.

Current migration gap: `inventory_transactions` is lot-only and must be made location-aware before canonical multi-store inventory use.

## Product and lot identity across stores

Do not create a new product merely because a Sub Store receives stock.

Do not create a new lot merely because quantity from an existing product/expiry lot moves from Main Store to a Sub Store.

Normal v1 lot identity remains:

`product + expiry date`

with stronger source evidence allowed to split a lot when genuinely necessary.

Location balance is separate from lot identity.

This preserves one shared product/lot catalogue while allowing independent store balances.

## External receipt versus internal transfer

These are different business events.

### External receipt

Stock enters the managed store system from an external/source supply event.

Canonical target location is normally explicit, and for the current legacy workflow may default to the Main Store when source evidence and configured workflow prove that convention.

A receipt must retain its original batch/transfer/source evidence and source price.

### Internal transfer

Stock moves between two MSA-managed locations.

Required semantics:

- source store and destination store are both explicit;
- product/lot identity is preserved;
- total system quantity does not change from the transfer itself;
- source location decreases and destination location increases as one atomic business operation;
- the two ledger effects share one transfer/operation identity;
- retry/idempotency must not duplicate either side;
- audit/read-back verifies both source and destination results.

The exact future schema may use a transfer header + lines with paired ledger effects. Do not represent a real transfer as unrelated manual adjustments once transfer support is implemented.

## Movement types — F6D schema implication

The current F2 transaction set contains:

- `OPENING_BALANCE`
- `RECEIPT`
- `USAGE`
- `ADJUSTMENT_POSITIVE`
- `ADJUSTMENT_NEGATIVE`

That set is insufficient to represent an internal Main Store <-> Sub Store transfer with correct business meaning.

F6D must add an explicit transfer representation. Preferred bounded design:

- `inventory_transfers` — transfer header/workflow identity;
- `inventory_transfer_lines` — lot + quantity per line;
- committed transfer line produces paired location ledger entries, semantically `TRANSFER_OUT` and `TRANSFER_IN`, linked to the same transfer line/operation.

The precise table names remain an implementation detail, but paired atomic transfer semantics are locked.

## Usage

Usage always belongs to the location where the stock was actually issued/consumed from.

Future command meaning:

`record_usage(store_id, lot_id, date, quantity, source, operation_id, actor)`

A Main Store Daily Usage view and a Sub Store Daily Usage view can use the same preset/view definition with a different store context.

Actual movement remains authoritative even when FIFO/FEFO advice says another lot would have been preferable.

## Receipts

A receipt line ultimately affects one destination location.

Future receipt data must therefore resolve `to_store_id` or equivalent canonical destination location before commitment.

Source documents may contain an external origin label that is not an MSA store. Do not force every external supplier/source into the internal `stores` table.

## Monthly state

The current `inventory_months` schema is global by calendar month. Calendar month identity may remain global, but operational month snapshots/balances must be location-aware.

Required future semantics:

- month identity can remain one shared calendar period;
- opening/received/usage/closing/reorder snapshot values are scoped to store + lot;
- month close does not merge balances from different stores;
- system-wide reporting may aggregate store-scoped snapshots when requested.

Do not create one separate calendar month record per store unless implementation proves it materially simpler and preserves one coordinated close period. The preferred v1 model is global month period + store-scoped snapshot rows.

## Reorder

Reorder configuration needs an explicit scope.

Locked default direction:

- stock balance and usage are store-specific;
- reorder recommendation must declare which store's demand/state it represents;
- the Main Store may have its own reorder configuration and recommendation;
- Sub Store reorder/replenishment may later use either independent thresholds or a request-to-Main-Store workflow.

Still Owner/workflow review:

- whether current `Reorder Level` and `Reorder Surplus Factor` should be global product defaults, Main-Store-only settings, or per-store overrides;
- whether Sub Stores create external CMS reorder demand directly or normally request replenishment from Main Store.

F6D should preserve a schema path for per-store configuration without inventing the final Sub Store business policy.

## Configurable operational views

Every inventory view runs in an explicit location context unless it is intentionally cross-location.

Examples:

- `Main Stock` preset + `store_id = Main Store`.
- `Daily Usage` preset + selected store.
- `Near Expiry` custom view + one store or all stores.
- `Sub Store Balances` cross-location report + grouped by store.

A saved view definition may have:

- no fixed store — user chooses at runtime;
- a fixed store — useful for a named operational preset;
- an all-stores/report scope when permission allows it.

Store context is a filter/domain input, not a reason to duplicate table definitions.

## Authorization

Backend authorization must resolve both operation permission and location scope.

V1 roles remain OWNER / ADMIN / STAFF / READ_ONLY, but a future user-store assignment or allowed-location scope may restrict which stores a non-Owner can read/write.

F6D only needs the canonical location identity and a clean path for scoped authorization. Do not build an arbitrary enterprise permission editor.

## Current Google Sheet compatibility

The current `Medicine Store Cloud` has no populated store/location column in Main Stock or Daily Usage. Treat it as the legacy Main Store context unless Owner/source evidence later establishes otherwise.

Compatibility import/export can therefore bind the current workbook to the configured Main Store without adding a new production column to the existing sheet.

Future Google Sheet mirrors for Sub Stores can use separate configured views/files or explicit generated location-aware exports rather than changing canonical identity rules.

## F6D required schema parity changes

At minimum, F6D must account for:

1. canonical `stores` (or equivalently named locations) entity;
2. one configured Main Store seed/identity for migration;
3. `store_id` on canonical balance-changing movements;
4. location-aware indexes/queries for lot balance;
5. receipt destination location;
6. explicit internal transfer representation with paired atomic effects;
7. store-scoped monthly snapshot rows;
8. a path for store-scoped reorder configuration;
9. migration provenance binding the current live workbook snapshot to the Main Store context.

No production inventory write or canonical promotion is authorized by this document.

## Open items that do not block the core model

- Sub Store naming/code conventions.
- Exact UI for switching stores.
- Whether all staff see all locations.
- Whether Sub Store reorder means request-to-Main-Store or external CMS reorder.
- Exact per-store/global fallback policy for reorder settings.
- Future cross-store dashboards and analytics layout.

These can be resolved after the location-aware canonical schema exists.

## Acceptance rule

The Store/Location model is sufficient for F6D when the backend can represent the same product/lot simultaneously in Main Store and any number of Sub Stores, record location-specific receipt/usage/adjustment, transfer quantity atomically between locations, derive each location's balance independently, and reproduce store-scoped operational views without cloning schemas.
