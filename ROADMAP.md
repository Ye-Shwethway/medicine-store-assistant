# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D schema foundation, fresh Main Store staging, source-safe Main-primary shadow materialization, and the first live versioned CMS catalogue shadow import are implemented and runtime-verified. Current bounded target: read-only CMS assisted-reconciliation planning over the materialized local Products and imported catalogue. PostgreSQL remains non-canonical.**

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

Canonical architecture:

- `docs/architecture/CANONICAL_INVENTORY_FOUNDATION.md`
- `docs/architecture/STORE_LOCATION_MODEL.md`
- `docs/architecture/CMS_MAPPING_LIFECYCLE.md`
- `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
- `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
- `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
- `docs/architecture/MAIN_STOCK_DAILY_USAGE_MATERIALIZATION.md`

## Canonicality / authority boundary

- Google Sheet/source documents remain the current operational source of truth.
- PostgreSQL remains deployed shadow/test only.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- The old F6B staging batch was test evidence only and was removed before the fresh F6D source stage.
- Shadow Product/Lot/opening movements and CMS catalogue versions do not imply production authority.
- No production inventory write, transfer execution, usage deduction, local CMS remap/price mutation, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

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
- Daily Usage is joined usage/reconciliation evidence and never independently creates duplicate Product/Lot/opening records.

Reorder remains **deterministic baseline + optional AI enhancement/review**. AI outage must not force item-by-item manual calculation.

## F6D — ACTIVE

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

Runtime evidence proves the bounded source-safe subset was materialized without guessing ambiguous source facts:

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

Unit conflicts/missing Unit values were not guessed or silently corrected. CMS uncertainty did not block otherwise-safe local inventory identity, but no Product-CMS mapping was created in this slice.

### Live CMS catalogue version import — COMPLETE + RUNTIME VERIFIED

The first real CMS catalogue was imported into the shadow database as **reference/versioned catalogue data only**:

- source sheet: `CMS_Price_List_202608`;
- source title: `August 2026 Updated Price List (Yuan) - 02.08.2026`;
- effective date: **2026-08-02**;
- exact source hash: `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- catalogue version: `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- catalogue rows: **6,891**;
- unique CMS codes: **6,891**;
- duplicate codes: **0**;
- blank codes: **0**;
- invalid prices: **0**;
- one source-preserved blank selling price at row **6442** (`S10105035`) stored as `NULL` rather than guessed;
- immediate replay returned the same catalogue version with `created=false`.

Protected local-domain counts were unchanged by catalogue import:

- Products **670**;
- Lots **799**;
- inventory transactions **679**;
- Product-CMS mappings **0**.

Therefore catalogue ingestion did **not** remap local Products, update operational prices, or mutate inventory.

## CURRENT — CMS assisted-reconciliation planner

The next bounded slice is read-only reconciliation planning between the 670 materialized local Products/source mapping evidence and the 6,891-row imported CMS catalogue.

Required behavior:

1. use local Product identity independently of CMS Code;
2. join the fresh Main Stock source evidence to materialized Products deterministically;
3. compare source `serial_code`, `cs_name`, mapping hints, local names and current catalogue evidence;
4. classify deterministic continuity separately from `UNMAPPED`, `CMS_DISCONTINUED`, `RECYCLED_CODE`, identity/name conflict and review-required cases;
5. never interpret code equality alone as proof of identity;
6. preserve uncertainty where source evidence may reflect historical catalogue change or local staff error;
7. produce review candidates and counts before any `product_cms_mappings` write;
8. keep AI optional: deterministic screening first, AI candidate reasoning later;
9. keep Product-CMS mapping count at zero until a separately reviewed mapping-acceptance slice is authorized.

## Subsequent path

1. CMS assisted-reconciliation read-only planner.
2. Reviewed mapping-candidate workflow with human acceptance; no blind code sync.
3. Historical bootstrap from strongest available evidence without inventing movements.
4. Shadow Main Stock/Daily Usage projection parity and transfer tests.
5. Field/computation registry + saved views.
6. DB-backed Main Stock and Daily Usage presets.
7. Spreadsheet-like draft/confirm/save editing over typed commands.
8. Deterministic reorder baseline engine.
9. AI-enhanced CMS/reorder/trend proposal-review workflows.
10. Dual verification of real operational events.
11. Selected DB read-path promotion.
12. Controlled write promotion one operation class at a time.
13. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
14. Sheet mirror/rebuild, exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not promote PostgreSQL or create accepted Product-CMS mappings merely because the live catalogue is now present. The immediate next action is a **read-only assisted-reconciliation planner** over the imported catalogue and existing local source/mapping evidence.