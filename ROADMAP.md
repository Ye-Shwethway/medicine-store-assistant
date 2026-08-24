# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D schema foundation, fresh Main Store staging, source-safe Main-primary shadow materialization, live versioned CMS catalogue import, deterministic CMS reconciliation, and durable non-accepted CMS mapping review-state staging are runtime-verified. F6E configurable read-only Inventory View Engine + first Web renderer are runtime-verified. Current bounded target: source-vs-shadow review detail, HOLD/review filtering and CMS Mapping Review preset. PostgreSQL remains non-canonical.**

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

> **Main Stock, Daily Usage, Migration Review and CMS Mapping Review are presets over a reusable View Engine, not fixed database-shaped screens.**

Canonical architecture:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/MAIN_STOCK_DAILY_USAGE_MATERIALIZATION.md`
- `docs/architecture/INVENTORY_VIEW_ENGINE_V1.md`

## Canonicality / authority boundary

- Google Sheet/source documents remain the current operational source of truth.
- PostgreSQL remains deployed shadow/test only.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- The old F6B staging batch was test evidence only and was removed before the fresh F6D source stage.
- Shadow Product/Lot/opening movements, catalogue versions and mapping review-state rows do not imply production authority.
- No production inventory write, transfer execution, usage deduction, accepted CMS remap/price mutation, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

## F6C — COMPLETE ARCHITECTURE LOCK

Locked semantics include:

- stable local Product identity;
- normal v1 Lot = Product + structured Expiry Date;
- one configured Main Store + unlimited Sub Stores;
- location-scoped, movement-derived balances;
- internal transfer = linked atomic source-out + destination-in effects;
- global/versioned Universal CMS Catalogue separate from local Product identity;
- Product-CMS mapping = historical/auditable accepted lifecycle, never blind code sync;
- last accepted mapping/operational price survives newer unresolved catalogue versions;
- current catalogue price is separate from historical receipt/source price;
- human/AI operations require stable actor, operation/idempotency identity, audit and read-back;
- Main Stock and Daily Usage are operational projections/edit surfaces, not canonical worksheet-shaped tables;
- Main Stock is the primary migration source for Product/Lot/current-balance candidates;
- Daily Usage is joined usage/reconciliation evidence and never independently creates duplicate Product/Lot/opening records;
- operational Web tables are registry-driven view definitions so users can later create custom sheet-style layouts without arbitrary SQL/DB access.

Reorder remains **deterministic baseline + optional AI enhancement/review**. AI outage must not force item-by-item manual calculation.

## F6D — SHADOW FOUNDATION COMPLETE FOR CURRENT DATASET

### Schema foundation — COMPLETE

Migration `0022_inventory_foundation` provides Store-aware ledger semantics, receipt/transfer structures, Product-CMS mapping lifecycle, accepted operational price retention, `inventory_location_balances`, and `inventory_total_stock`. PostgreSQL CI proves Main/Sub balances, transfer conservation/linkage, mapping fallback, and schema migration integrity.

### Fresh Main Store staging — COMPLETE

Fresh batch:

- migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- source hash `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`;
- Main Stock source rows **823**;
- Daily Usage source rows **823**;
- staged source records **1,646 = 823 + 823**;
- exact snapshot replay idempotent.

The 1,646 count is source evidence, not 1,646 canonical inventory objects.

### Main-primary shadow materialization — COMPLETE + RUNTIME VERIFIED

- Main Stock input rows: **823**;
- persisted Products: **670**;
- persisted Lots: **799**;
- migration `OPENING_BALANCE` movements: **679**;
- opening quantity sum: **72,009**;
- zero-balance identity-only Lots: **120**;
- balance readback mismatches: **0**;
- immediate replay created Products/Lots/transactions: **0 / 0 / 0**.

Explicit HOLD evidence remains outside the write set:

- inventory-semantic review rows: 14;
- duplicate Product+Expiry source rows: 4 (`41,42,156,157`);
- Unit-review rows: 6 (`237,245,459,460,461,601`).

Unit conflicts/missing Unit values were not guessed or silently corrected.

### Live CMS catalogue version import — COMPLETE + RUNTIME VERIFIED

- source sheet: `CMS_Price_List_202608`;
- title: `August 2026 Updated Price List (Yuan) - 02.08.2026`;
- effective date: **2026-08-02**;
- exact source hash: `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- catalogue version: `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- catalogue rows / unique CMS codes: **6,891 / 6,891**;
- duplicate codes: **0**;
- blank codes: **0**;
- invalid prices: **0**;
- one source-preserved blank selling price at row **6442** stored as `NULL` rather than guessed;
- immediate replay idempotent.

### CMS reconciliation + durable review state — COMPLETE + RUNTIME VERIFIED

Deterministic screening over 670 materialized Products produced:

- exact-name + same-price continuity candidates: **526**;
- exact-name + changed-price continuity candidates: **77**;
- multiple source codes: **30**;
- CMS discontinued/local retained: **19**;
- code/name mismatch: **9**;
- unmapped: **6**;
- missing source CMS name: **1**;
- multiple source CMS names: **1**;
- recycled code: **1**.

The guarded review-state stage created **670 durable non-accepted mapping rows**:

- `REVIEW_REQUIRED`: **644**;
- `CMS_DISCONTINUED`: **19**;
- `RECYCLED_CODE`: **1**;
- `UNMAPPED`: **6**;
- `ACTIVE_MATCH`: **0**;
- accepted operational prices: **0**.

Immediate replay created **0** additional review rows. Products/Lots/inventory transaction counts remained **670 / 799 / 679**. No mapping acceptance or price mutation occurred.

## F6E — ACTIVE: CONFIGURABLE INVENTORY VIEW + REVIEW WORKSPACE

Architecture:

`Field/Computation Registry -> View Definition -> Generic Renderer -> System/User Presets -> Draft/Edit Commands later`

### Read-only substrate + Web renderer — COMPLETE + RUNTIME VERIFIED

Implemented:

- typed registry with `ENTITY_FIELD`, `COMPUTED_FIELD`, `COMMAND_EDITABLE_FIELD`, `DISPLAY_HELPER` semantics;
- generic validated registered-field projection; arbitrary SQL/raw DB expressions are rejected;
- `Main Stock` system preset at Product-Lot grain;
- `Migration Review` system preset at source Main Stock row grain;
- authenticated dashboard API;
- one generic Web table renderer driven by returned `columns[]` metadata;
- preset switching, registry-only column selection, search and pagination;
- strong `Shadow inventory — not canonical` state presentation;
- old product-facing staged-row grid replaced while Shadow Inspection remains separate;
- dedicated 390x844 Playwright behavior verification, including a real mobile overflow regression detected and fixed before merge.

Runtime issue #166 proves:

- Main Stock projected rows **799**;
- Migration Review projected rows **823**;
- Main current quantity sum **72,009.000**;
- Products/Lots/inventory transactions **670 / 799 / 679**;
- `ACTIVE_MATCH` **0**;
- accepted operational prices **0**;
- mutation **false**;
- canonical flags remain false.

### CURRENT bounded slice — source compare + review

1. source-vs-shadow compare detail/drawer for Migration Review;
2. explicit HOLD/review state highlighting and reason/status filters;
3. `CMS Mapping Review` as another system preset over the same View Engine;
4. selection/bulk-context substrate without automatic acceptance;
5. prepare current-view/selection/evidence context for embedded AI copilot;
6. no accepted CMS mapping, price mutation, inventory write or baseline/canonical promotion.

Web direction remains:

- Inventory is the primary visual operational/review workspace;
- custom saved views will later let users create their own sheet-style layouts from registered semantic fields/computations/commands;
- embedded AI will act as context-aware copilot;
- difficult cases may escalate into AI Workspace/multi-agent review;
- Owner/authorized typed acceptance remains the mutation authority boundary.

## Subsequent path

1. Source compare/HOLD filters + CMS Mapping Review preset.
2. Embedded context-aware AI assistant + deep-review handoff to AI Workspace.
3. Resolve HOLD inventory rows and mapping exceptions with typed reviewed actions.
4. Persist saved user-defined view definitions and add View Builder.
5. Add Daily Usage monthly-pivot system preset.
6. Add spreadsheet-like draft/preview/Confirm & Save editing over typed commands.
7. Add deterministic reorder baseline engine and reorder presets.
8. Dual verification of real operational events.
9. Accept migration baseline only after source/recovery/reconciliation gates pass.
10. Promote selected DB read paths.
11. Promote controlled write operation classes one at a time.
12. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
13. Sheet mirror/rebuild, exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not present shadow DB as canonical merely because normalized domain rows, review states and the new Inventory renderer exist. The immediate target is **review capability on top of the verified generic View Engine**, with no mapping acceptance or production mutation.