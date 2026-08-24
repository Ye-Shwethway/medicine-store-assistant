# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D schema foundation is deployed, the legacy F6B staging batch has been cleanly removed, and a fresh live Main Store snapshot is staged. Current bounded target: Main Stock-primary canonical materialization planning and source-safe shadow Product/Lot/opening-balance construction. PostgreSQL remains non-canonical.**

The live Google workbook/source documents remain operationally authoritative. `migration_baseline_accepted=false`; `database_canonical=false`.

## Product direction — LOCKED

MSA is a canonical inventory system with configurable spreadsheet-like views and optional AI assistance, not a fixed spreadsheet clone and not an AI-only application.

Foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

> **AI enhances store operation but must not become a single point of operational failure.**

MSA targets one Main Store plus unlimited Sub Stores, PostgreSQL-backed durable inventory, shared human/AI typed operations, Web/Flutter/Telegram/ChatGPT/automation clients, deterministic fallbacks when AI is unavailable, and AI-assisted reconciliation/analysis when available.

Canonical architecture:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/MAIN_STOCK_DAILY_USAGE_MATERIALIZATION.md`

## Canonicality / authority boundary

- Google Sheet/source documents remain the current operational source of truth.
- PostgreSQL remains deployed shadow/test only.
- The old F6B staging batch was test evidence only and has been removed before the fresh F6D source stage.
- No production inventory write, internal transfer execution, Calculator deduction, Telegram/Flutter stock mutation, automatic OCR/vision commit, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.
- Provider/model selection never grants authority; participant privileges never union.

## Accepted supporting foundation

AI Workspace, Provider Registry, named agents, native inference, D4.8/D4.9 Work/Artifact/Review/Event/Attention substrate, external MCP federation, Owner Decisions and Web Production Reliability Hardening remain accepted supporting infrastructure. Do not resume extended AI-only work unless explicitly reprioritized or required for correctness.

## F6C — COMPLETE ARCHITECTURE LOCK

Locked semantics include:

- stable local Product identity;
- v1 normal Lot identity = Product + Expiry Date;
- exactly one configured Main Store plus unlimited Sub Stores;
- same Product/Lot may exist in multiple stores;
- balance is location-scoped and movement-derived;
- Total Store Stock is the sum of location balances, not a second editable truth;
- external receipt and internal transfer are distinct business events;
- internal transfer preserves Product/Lot identity and requires linked source-out + destination-in effects;
- usage/deduction belongs to the actual issuing store;
- Universal CMS Catalogue is global/versioned and separate from local Product identity;
- CMS mappings are historical/auditable lifecycle records, never blind code sync;
- last accepted CMS mapping/operational price remains usable while a newer catalogue is unresolved;
- current catalogue price is separate from historical receipt/source price;
- human and AI operations resolve stable actor identity, operation/idempotency ID, audit and read-back;
- Main Stock and Daily Usage are operational projections/edit surfaces over canonical data;
- Main Stock is the primary migration source for Product/Lot/current-balance candidates;
- Daily Usage is joined usage/reconciliation evidence only and must never independently create duplicate Product/Lot/opening-balance records.

### Reorder resilience

Exact legacy Estimated Reorder Qty formula parity is not a canonical-schema blocker. Future reorder has a deterministic local/backend baseline plus optional AI enhancement/review. AI outage must not force item-by-item manual calculation.

### CMS assisted mapping

New catalogue versions are deterministically diffed/screened. Ambiguous, recycled, discontinued or new mappings go to review. AI may help rank/explain candidates; manual review remains available when AI is unavailable. Existing accepted mapping/price state keeps ordinary inventory operational.

## F6D — ACTIVE

### Schema foundation — IMPLEMENTED + VERIFIED

Migration `0022_inventory_foundation` introduces:

- canonical `stores` with one deterministic Main Store seed;
- non-null `store_id` on inventory transactions with legacy shadow rows bound to Main Store;
- `TRANSFER_OUT` / `TRANSFER_IN` ledger semantics;
- store-bound migration provenance;
- `receipt_batches` / `receipt_lines` with destination Store and source evidence;
- `inventory_transfers` / `inventory_transfer_lines` with linked paired ledger effects;
- `product_cms_mappings` with lifecycle state and accepted operational price retention;
- `inventory_location_balances` derived view;
- `inventory_total_stock` derived view.

Targeted PostgreSQL CI proves from an empty DB:

- migration to head;
- Main/Sub independent balances;
- total-stock conservation through transfer;
- transfer-line linkage;
- unresolved new CMS candidate does not erase the accepted mapping/price;
- schema downgrade/re-upgrade after removal of synthetic F6D-only business fixtures.

Important downgrade rule: committed F6D-only transfer history must never be silently coerced into old movement semantics merely to make a downgrade succeed. A real downgrade with such data would require an explicit data-migration decision.

### Fresh-source snapshot staging adapter — IMPLEMENTED + VERIFIED

The existing F6B live-sheet reader has been upgraded rather than replaced.

The F6D staging adapter now:

- binds each snapshot batch explicitly to the configured Main Store;
- includes Store context in deterministic snapshot hashing;
- converts Google Sheets date serials to structured ISO dates;
- strips only a terminal numeric `(month/year)` expiry suffix for Product matching while preserving product-defining parentheses;
- preserves the raw local item name and flags suffix/structured-expiry disagreement;
- allows valid non-expiry consumables instead of auto-classifying all missing-expiry rows as REVIEW;
- captures CMS Price, displayed Price, Remark, Serial Code and CS Name;
- derives mapping hints `ACTIVE_MATCH`, `UNMAPPED`, `REVIEW_REQUIRED`, `RECYCLED_CODE`, `CMS_DISCONTINUED` without forcing mapping mutation;
- treats literal `Nil` CMS codes as unmapped;
- preserves recycled IDs for review and discontinued local stock as valid inventory state when stock arithmetic is otherwise sound;
- supports both observed Daily Usage Remaining Stock header spellings;
- stages source rows idempotently with sheet/row provenance.

CI proves source-shaped normalization plus PostgreSQL Main Store staging and exact snapshot replay idempotency.

### Fresh live source stage — COMPLETE

The old F6B staging batch was fingerprint-verified and deleted without changing control-plane users/agents/conversations or the Main Store seed. A fresh authorized live workbook snapshot was then staged under `MAIN`.

Current live evidence:

- fresh batch: `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- source hash: `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`;
- direct live read confirms Main Stock has **823 populated item rows** plus header;
- Daily Usage mirrors the same **823 item-name rows**;
- staged source records = **1,646 = 823 Main Stock + 823 Daily Usage**;
- 1,646 is source-evidence count, not canonical inventory count;
- snapshot replay is idempotent and returns the same batch/hash rather than creating a duplicate batch.

The source stage still creates no canonical Product/Lot/opening-balance rows by itself.

### CURRENT — Main-primary materialization planning + safe shadow materialization

Main Stock and Daily Usage are now explicitly separated by migration responsibility:

- Main Stock owns Product candidate, structured Expiry/Lot candidate and current Main Store balance evidence;
- Daily Usage joins to that same candidate as usage/monthly consistency evidence;
- Daily Usage must never independently create a second Product, Lot, opening balance or store balance;
- Main Stock/Daily Usage remain future operational views over canonical data, not canonical worksheet-shaped tables;
- CMS mapping uncertainty does not automatically block otherwise-safe local inventory identity/quantity materialization.

Next bounded work:

1. run the read-only Main-primary planner against the fresh staged batch;
2. report Main/Daily counts separately and calculate unique Product/Product+Expiry candidates;
3. surface exact duplicate/ambiguous Product+Expiry keys rather than silently merging them;
4. inspect inventory-identity/quantity review cases separately from CMS-only mapping review cases;
5. materialize only source-safe Main-derived Products/Lots;
6. create at most one migration opening-balance effect per accepted Main Store Lot candidate, with no duplicate effect from Daily Usage;
7. do not fabricate historical receipt/usage movements from monthly aggregates alone;
8. derive Main Store balances and compare them to accepted Main Stock current-state evidence;
9. prove materialization replay idempotency;
10. keep PostgreSQL non-canonical until explicit later acceptance.

## Subsequent path

1. Safe F6D Main-primary shadow materialization/reconciliation.
2. Historical bootstrap from strongest available evidence without inventing movements.
3. Shadow balance/projection parity and transfer tests.
4. Minimal field/computation registry + saved view definitions.
5. DB-backed Main Stock and Daily Usage presets.
6. Spreadsheet-like draft/confirm/save editing over typed commands.
7. Deterministic reorder baseline engine + versioned strategy attribution.
8. CMS assisted reconciliation workflow + optional AI candidate reasoning.
9. AI-enhanced reorder/trend proposal-review workflows.
10. Dual verification of real operational events.
11. Selected DB read-path promotion.
12. Controlled write promotion one operation class at a time.
13. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
14. Sheet mirror/rebuild, monthly exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not let legacy spreadsheet formulas or report formatting dictate the canonical schema. Continue re-reading the live workbook whenever source behavior matters. The immediate next action is read-only Main-primary materialization planning over the fresh 823+823 source evidence, followed by source-safe shadow materialization only after duplicate/ambiguity evidence is understood.