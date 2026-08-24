# Canonical Inventory Foundation

Status: **LOCKED ARCHITECTURE DIRECTION — implementation pending**

## Purpose

Define the minimum durable database structure that Medicine Store Assistant must get right before advanced reorder logic, AI analysis, configurable table building, or broad client expansion.

The foundation is intentionally simple:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

The current Excel/Google workflow remains source evidence for operational meaning, but the future database must not clone spreadsheet calculations or worksheet layout as canonical truth.

Canonical companion contracts:

- `STORE_LOCATION_MODEL.md`
- `CMS_MAPPING_LIFECYCLE.md`
- `REORDER_BASELINE_AND_AI_ENHANCEMENT.md`

## Core rules

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

> **AI improves store workflows but must not become a single point of operational failure.**

## 1. Product

A Product is the stable local operational identity.

Minimum conceptual fields:

- `product_id` — immutable internal ID.
- `local_item_name` — preferred local/store-facing name.
- `type` — operational item type/category when needed.
- `default_unit` — Pcs, Bot, Set, Pair, etc.
- `active`.
- optional display metadata such as `display_order`.

`No.` from Main Stock is not canonical identity. It is view/order metadata only.

A product rename does not create a new product unless the real operational identity changes.

## 2. Lot

A Lot represents the expiry-specific physical/operational stock identity.

Normal v1 boundary remains:

`Product + Expiry Date`

Minimum conceptual fields:

- `lot_id`.
- `product_id`.
- `expiry_date` when known.
- lifecycle/status metadata.
- receipt/source identity snapshot links where needed.

The same lot identity may exist simultaneously in Main Store and multiple Sub Stores. Moving stock between stores does not create a new product or lot.

## 3. Store / Location

MSA supports exactly one configured Main Store plus unlimited Sub Stores.

Minimum conceptual fields:

- `store_id`.
- `code`.
- `name`.
- `store_type = MAIN | SUB`.
- `active`.

Do not clone product, lot, ledger, or monthly tables per store.

The current `Medicine Store Cloud` has no populated Store/Location field in Main Stock or Daily Usage, so current source rows are treated as the configured legacy Main Store context during migration.

## 4. Movement ledger

Canonical quantity change is recorded as a typed movement/event, not by directly editing a mutable balance number.

Every balance-changing movement resolves at minimum:

- `transaction_id`.
- `store_id`.
- `lot_id`.
- movement/transaction type.
- quantity using `NUMERIC(18,3)` under the locked F2 quantity policy.
- effective date/time as appropriate.
- source/provenance reference.
- operation/idempotency ID.
- actor context.
- correction/reversal linkage where required.

Required initial semantic movement classes include:

- opening/migration balance;
- external receipt;
- usage/deduction;
- positive adjustment;
- negative adjustment;
- internal transfer out;
- internal transfer in.

Exact physical table design may use one general ledger plus typed source tables. Semantics matter more than table naming.

## 5. Quantity columns and balances

Human operational views may expose familiar columns such as:

- Original / Opening Qty;
- Received Qty;
- Deducted / Used Qty;
- Current Qty;
- Total Stock.

These are not five independent mutable truths.

Conceptually, for one store + lot:

```text
Current Qty
  = Opening / Migration Qty
  + External Receipts
  + Transfer In
  + Positive Adjustments
  - Usage / Deduction
  - Transfer Out
  - Negative Adjustments
```

`Received Qty` and `Deducted Qty` are period/filter aggregates over movements.

`Current Qty` is derived/verified from the ledger. A materialized balance may be stored later for performance only if it can be reconciled against canonical movements.

### Total Store Stock

For a lot:

```text
Total Store Stock(lot)
  = SUM(Current Qty for that lot across all active managed stores)
```

For a product:

```text
Total Product Stock
  = SUM(all lot balances across all managed stores)
```

Do not maintain a separate manually editable total-stock number that can drift from location balances.

## 6. Internal transfer

An internal transfer moves stock between two MSA-managed locations without changing total system quantity.

Minimum business structure:

### Transfer header

- `transfer_id`.
- source `store_id`.
- destination `store_id`.
- effective/transfer date.
- status.
- operation/idempotency ID.
- requested/proposed/approved/executed actor context as applicable.
- source/reference/note.

### Transfer line

- `transfer_line_id`.
- `transfer_id`.
- `lot_id`.
- quantity.

On commit, one transfer line creates linked atomic ledger effects:

```text
source store      TRANSFER_OUT   quantity
Destination store TRANSFER_IN    quantity
```

Both effects must succeed or fail together. Retry must not duplicate either side.

## 7. External receipts

External receipt is distinct from internal transfer.

Receipt source evidence may include transfer/document number, source code/name, quantity, unit, source price and expiry.

A committed receipt resolves:

- destination `store_id`;
- Product/Lot identity;
- source receipt/batch/line provenance;
- quantity;
- receipt-time source price/catalogue context where available.

The current legacy workbook source can default to Main Store only where migration/source evidence establishes that context.

## 8. Usage / deduction

Usage belongs to the store from which stock was actually issued.

Canonical meaning:

`record_usage(store_id, lot_id, effective_date, quantity, source, operation_id, actor)`

The current Daily Usage Day 1-31 sheet is a monthly pivot/edit view over these dated usage events, not the canonical storage shape.

Actual historical movement is preserved even when it does not follow ideal FIFO/FEFO advice.

## 9. Universal CMS Catalogue and mapping lifecycle

The CMS catalogue is a separate global/versioned external reference domain.

It is not duplicated per store and is not the local Product primary key.

Conceptual structure:

- `cms_catalogue_versions` — each issued catalogue/version/effective period.
- `cms_catalogue_items` — code, CMS name/brand, description, form/type/class, selling price, etc.
- `product_cms_mappings` — auditable/version-aware mapping lifecycle from local Product to external catalogue identity/context.

CMS code alone never becomes stable local identity because codes may change, disappear, retire, be reused, or be incorrectly/stale-mapped in local data.

The live workbook contains real evidence of recycled/discontinued/ambiguous states, so mapping must be treated as assisted reconciliation rather than direct synchronization.

Core mapping rule:

> **CMS mapping is never blindly auto-synced. Last accepted mapping and price state remain usable until a newer mapping is reviewed and accepted.**

A new catalogue version may be deterministically diffed and screened, but ambiguous identity changes go to review. AI can rank/explain candidates when available; human manual mapping remains possible when AI is unavailable.

Accepted mapping history is never destructively replaced merely because a new catalogue was issued.

See `CMS_MAPPING_LIFECYCLE.md` for the full state/fallback contract.

### Price semantics

Separate:

- newest/current catalogue price from the imported CMS dataset;
- last accepted operational mapping/price used by the store;
- historical receipt/source price;
- local display/derived price where required by compatibility rules.

Updating the Universal CMS Catalogue must not rewrite genuine historical receipt-price truth.

If a new catalogue mapping is unresolved, the store may continue using its last accepted operational mapping/price while clearly surfacing stale/unreviewed status. Do not silently adopt a new price from code equality alone.

Operational Store/Main Stock views may display current accepted `CMS Code`, `CMS Name`, `CMS Price`, mapping status and catalogue-review warning by resolving mapping lifecycle state.

## 10. Actors and audit

Every protected operation must be attributable.

Human operations use stable `user_id`.

AI/integration operations use stable agent/service-principal identity.

Important operation context includes:

- human `user_id` and/or authorized agent/service-principal identity according to the operation model;
- client/channel such as Web, Flutter, Telegram, ChatGPT or automation;
- operation/idempotency ID;
- timestamps;
- source/evidence/reason;
- proposal/review/approval relationships when AI workflow participates;
- final execution outcome and read-back evidence.

AI reasoning does not grant inventory authority. Human UI and AI workflows converge on the same typed backend command layer.

## 11. Reorder resilience and intelligence

The legacy Excel `Estimated Reorder Qty` is a useful historical/manual baseline, not a required canonical database formula.

The future system must still provide reorder capability when all AI services are unavailable.

Core rule:

> **A deterministic baseline reorder engine is always available. AI enhances/reviews the baseline; AI is not the only way to calculate a proposal.**

Deterministic fallback may use structured local data such as current balance, usage history, configured reorder level/safety settings, lead time, incoming stock and store scope. The exact strategy may evolve and be versioned/configurable without changing canonical inventory identity.

When AI is available, reorder may additionally use:

- recent and long-term usage trends;
- store-specific demand;
- current and incoming stock;
- expiry risk;
- safety stock;
- lead time;
- seasonality;
- unusual consumption;
- cross-store context;
- AI proposal;
- single/multi-agent review;
- authorized human adjustment/approval.

Keep deterministic baseline, AI-enhanced proposal, reviews and final authorized quantity distinguishable for audit.

Therefore F6D must preserve the underlying stock/history/configuration data needed for later reorder strategies, but **exact legacy reorder formula parity is not a blocker for the canonical inventory schema**.

See `REORDER_BASELINE_AND_AI_ENHANCEMENT.md`.

## 12. Monthly Excel formulas and archives

Legacy month formulas, reset macros, Reorder Form, Final Reorder Form, This Month Received and Master archive remain compatibility/workflow evidence.

They should not delay foundation schema implementation unless a specific behavior changes canonical identity, quantity, source provenance, transfer meaning or historical audit truth.

Initial migration still needs explicit opening/migration balance provenance. Monthly reporting/snapshots can be built over the canonical ledger after the foundation is proven.

## 13. Minimum canonical tables / domains for F6D

Exact names may change during implementation, but F6D must provide the equivalent of:

- `stores`;
- `products`;
- `product_lots`;
- location-aware `inventory_transactions` / stock movements;
- external `receipt_batches` / `receipt_lines` or equivalent provenance structures;
- `inventory_transfers` / `inventory_transfer_lines` or equivalent typed transfer structures;
- `cms_catalogue_versions`;
- `cms_catalogue_items`;
- historical/auditable `product_cms_mappings` with lifecycle state;
- existing human identity / service-principal / agent identity structures;
- `audit_events`.

Usage and adjustments may remain typed ledger transactions with source-detail tables only where real workflow requires them.

Avoid speculative tables that are not needed to prove this foundation.

## 14. F6D proof requirements

Before any canonical promotion, the shadow database must prove that it can:

1. import current authorized source inventory into the configured Main Store with provenance;
2. preserve stable Product and expiry-lot identity;
3. derive Main Store quantity correctly from opening + receipts - usage +/- adjustments;
4. represent the same lot in multiple stores with independent balances;
5. perform/replay an internal transfer atomically without changing total system stock;
6. aggregate Total Store Stock across locations without a second mutable truth;
7. preserve last accepted CMS mapping/price state while allowing a newer catalogue to remain unresolved;
8. represent recycled/discontinued/review-required CMS mapping lifecycle without corrupting local Product identity;
9. keep current catalogue price separate from historical receipt price;
10. attribute mutations/proposals/reviews/execution to stable human/agent identities;
11. reproduce useful Main Stock and Daily Usage projections from DB data;
12. reconcile all mismatches explicitly while PostgreSQL remains non-canonical.

The full deterministic reorder engine is a later slice, but the foundation must retain the structured history/configuration needed to run it without AI.

## Boundary

This architecture does not authorize production stock mutation or PostgreSQL canonical promotion.

The current Google workbook/source documents remain operationally authoritative until migration, reconciliation, backup/recovery, controlled write promotion and explicit canonicality acceptance are completed.
