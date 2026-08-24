# Medicine Store Assistant — New Chat Bootstrap

Use this file for project-development continuity in a fresh chat.

## Canonical repository

`https://github.com/Ye-Shwethway/medicine-store-assistant`

## Mandatory reconciliation order

Before changing code/config/schema/runtime, read:

1. `AGENTS.md`
2. `NEW_CHAT_BOOTSTRAP.md`
3. `ROADMAP.md`
4. `IMPLEMENTATION_PLAN.md`
5. `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
6. `docs/architecture/STORE_LOCATION_MODEL.md`
7. `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
8. `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
9. `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
10. `docs/architecture/INVENTORY_DATA_MODEL.md`
11. `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
12. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
13. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
14. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
15. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
16. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
17. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
18. `skills/medicine-store-assistant/SKILL.md`
19. latest F6C/F6D checkpoints;
20. current PR/runtime evidence when deployment truth matters.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current state

- F6C Canonical Inventory Foundation is complete enough for implementation.
- F6D schema foundation migration `0022_inventory_foundation` is implemented and PostgreSQL-CI verified.
- F6D live-source snapshot staging adapter is implemented and PostgreSQL-CI verified.
- Current bounded target is **stage the actual fresh live Main Store snapshot, inspect classifications, then perform only source-safe shadow materialization/reconciliation**.
- PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.
- F6B is test-only and is not the accepted F6D migration baseline.

## Locked architecture

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Rules:

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from canonical movements;
- Total Stock is aggregate truth, not an editable master number;
- AI improves workflows but is not an availability dependency.

### Product / Lot

- `product_id` = stable local identity.
- normal v1 Lot = Product + structured Expiry Date.
- Store movement does not create new Product/Lot identity.
- Main Stock `No.` is presentation/order metadata only.

### Store / Balance

- exactly one configured Main Store + unlimited Sub Stores;
- same Lot can hold quantity in multiple stores;
- balance = per `(store_id, lot_id)`;
- current live Medicine Store Cloud contains no populated Store column and is treated as legacy Main Store context for migration.

### Transfer

Internal transfer is one typed operation with linked `TRANSFER_OUT` and `TRANSFER_IN` effects. Total system quantity must remain unchanged.

### Universal CMS Catalogue / Mapping

- CMS catalogue is global/versioned.
- CMS Code is never local Product identity.
- Product-CMS mapping is historical/auditable accepted state, not blind direct sync.
- last accepted mapping and operational price remain usable while a newer catalogue is unresolved.
- recycled/discontinued/ambiguous states remain explicit.
- AI may assist mapping review; manual mapping remains possible when AI is unavailable.
- current CMS catalogue price is separate from historical receipt/source price.

### Reorder

Future reorder has a deterministic local/backend baseline plus optional AI enhancement/review. Exact legacy Estimated Reorder Qty formula parity is not an F6D schema blocker. AI outage must still leave a useful baseline recommendation.

## F6D schema foundation — IMPLEMENTED

Migration `0022_inventory_foundation` adds:

- `stores` and deterministic `MAIN` seed;
- non-null Store on inventory movements;
- transfer movement types;
- store-bound migration batches;
- receipt batch/line provenance;
- transfer header/lines linked to paired ledger entries;
- `product_cms_mappings` lifecycle with accepted operational price retention;
- `inventory_location_balances`;
- `inventory_total_stock`.

Targeted PostgreSQL 16 CI proves:

- empty DB -> Alembic head;
- Main 100 -> transfer 25 -> Main 75 / Sub 25 / total 100;
- transfer linkage;
- unresolved new CMS candidate does not erase accepted mapping/price;
- schema downgrade/re-upgrade after cleanup of synthetic F6D-only business fixtures.

Do not make downgrade silently delete/coerce real transfer history. A real downgrade with committed F6D-only movement data requires an explicit migration decision.

## F6D snapshot staging adapter — IMPLEMENTED

The old F6B live-sheet reader was upgraded in place.

It now:

- binds staged batches explicitly to Store `MAIN` by default;
- includes Store identity in the snapshot hash;
- converts Google Sheets date serials to ISO dates;
- strips only terminal numeric expiry suffixes such as `(1/2026)` for Product matching while preserving `(Adult)`, `(China)`, strengths/sizes and other product-defining parentheses;
- preserves raw local item names;
- flags item-name expiry suffix vs structured Expiry Date mismatches;
- supports valid no-expiry consumables;
- captures CMS Price, Price display, Remark, Serial Code and CS Name;
- derives mapping hints `ACTIVE_MATCH`, `UNMAPPED`, `REVIEW_REQUIRED`, `RECYCLED_CODE`, `CMS_DISCONTINUED`;
- normalizes `Nil` CMS code to unmapped;
- preserves recycled mappings for review;
- preserves discontinued local stock as valid inventory state when stock arithmetic is valid;
- supports current Daily Usage Remaining Stock header variants;
- stages exact snapshots idempotently with sheet/row provenance.

CI on PR #135 verifies normalization plus PostgreSQL Main Store staging and replay idempotency.

This adapter stages evidence only. It has not yet staged the actual current workbook into the target runtime and has not created Product/Lot/opening movements from live rows.

## CURRENT — actual live source staging

Next bounded sequence:

1. verify target shadow runtime is on schema `0022_inventory_foundation` and contains the F6D staging adapter;
2. run one fresh authorized read-only live workbook staging pass;
3. record migration batch ID, Main Store binding, source hash and row count;
4. record SAFE/REVIEW/CONFLICT/NEW_UNMAPPED distribution;
5. record CMS mapping-hint distribution;
6. inspect representative REVIEW/CONFLICT/RECYCLED/DISCONTINUED/UNMAPPED rows;
7. replay the exact snapshot and prove no duplicate batch/source rows;
8. do not create canonical shadow movements until the real classification evidence has been reviewed.

## After staging — source-safe materialization

Only after actual source evidence is known:

1. resolve Product identity from normalized local names, never CMS Code alone;
2. resolve Lots from structured Expiry Date while allowing valid no-expiry items;
3. choose the migration opening-balance basis explicitly from source evidence;
4. create provenance-bearing shadow movements only for source-safe cases;
5. do not fabricate receipts/usage from aggregates when provenance is insufficient;
6. preserve recycled/discontinued/review-required CMS states;
7. derive Main Store balances and compare with live source;
8. prove materialization replay idempotency;
9. generate shadow Main Stock/Daily Usage projections;
10. remain non-canonical.

## Source rules

Use the live Google Sheet repeatedly whenever structure/value behavior matters. Representative `FORMULA` reads return materialized values rather than exact legacy Excel formula strings, so do not reverse-engineer formulas from cloud values.

Important known source facts:

- Product identity != expiry Lot identity != CMS catalogue identity.
- item-name expiry suffix may disagree with structured Expiry Date.
- recycled/discontinued/same-code conflicts exist and may reflect historical mapping, CMS change, or local staff error; preserve uncertainty for review.
- current workbook Audit_Log preserves previous/current price state and backup references.
- actual usage/movement wins over ideal FIFO/FEFO advice.

## Immediate boundary

No production inventory write, DB canonical promotion, live-source movement materialization, full semantic AI matcher, full reorder engine, or broad UI expansion belongs before the actual live snapshot staging evidence is inspected.
