# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D shadow foundation is runtime-verified. F6E Slice A/B/C/D are complete and runtime-verified through the configurable read-only Inventory View Engine, review workspace, bounded AI handoff and Deep Review integration. Inventory Spreadsheet Focus Mode v1 is also production-runtime verified. Current bounded target: Spreadsheet Workbench v2 read/review ergonomics. PostgreSQL remains non-canonical.**

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
- Shadow Product/Lot/opening movements, catalogue versions and mapping review-state rows do not imply production authority.
- No production inventory write, transfer execution, usage deduction, accepted CMS remap/price mutation, arbitrary agent SQL/DB mutation, or DB canonical promotion is authorized.

## F6C — COMPLETE ARCHITECTURE LOCK

Locked semantics include stable local Product identity; Product+Expiry Lot identity; one Main Store + unlimited Sub Stores; movement-derived balances; linked transfer effects; versioned Universal CMS Catalogue; auditable Product-CMS mapping lifecycle; retained last accepted mapping/price while newer catalogue evidence remains unresolved; actor/idempotency/audit/read-back requirements; operational projections instead of worksheet-shaped canonical tables; and registry-driven configurable Web views.

Reorder remains **deterministic baseline + optional AI enhancement/review**. AI outage must not force item-by-item manual calculation.

## F6D — SHADOW FOUNDATION COMPLETE FOR CURRENT DATASET

### Source + inventory materialization

- migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- Main Stock **823** rows;
- Daily Usage **823** rows;
- staged evidence **1,646** rows;
- Products **670**;
- Lots **799**;
- `OPENING_BALANCE` movements **679**;
- opening quantity **72,009**;
- zero-balance identity-only Lots **120**;
- balance mismatches **0**;
- replay created **0 / 0 / 0** Product/Lot/transaction rows.

Explicit HOLD evidence remains unresolved instead of guessed: 14 inventory-semantic review rows, duplicate Product+Expiry rows `41,42,156,157`, and Unit-review rows `237,245,459,460,461,601`.

### CMS catalogue + durable review state

- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- effective date `2026-08-02`;
- catalogue rows / unique codes **6,891 / 6,891**;
- duplicate codes **0**;
- one blank source price preserved as `NULL`;
- durable mapping review rows **670**: `REVIEW_REQUIRED 644`, `CMS_DISCONTINUED 19`, `RECYCLED_CODE 1`, `UNMAPPED 6`, `ACTIVE_MATCH 0`;
- accepted operational prices **0**;
- replay created **0** additional rows.

## F6E — ACTIVE: CONFIGURABLE INVENTORY WORKBENCH

Architecture:

`Field/Computation Registry -> View Definition -> Generic Renderer -> System/User Presets -> Draft/Edit Commands later`

### Slice A/B — generic read substrate + Web renderer — COMPLETE + RUNTIME VERIFIED

Implemented and verified:

- typed field registry and generic view-definition model;
- Main Stock and Migration Review system presets;
- authenticated rows/presets/registry API;
- registered-field projection and unknown-field rejection;
- one generic Web table renderer driven by returned `columns[]` metadata;
- preset switching, visible-column selection, search and pagination;
- explicit `Shadow inventory — not canonical` state;
- content-derived JS/CSS asset identity and no-store delivery;
- dedicated 390x844 behavior proof;
- runtime issue #166: Main Stock **799**, Migration Review **823**, quantity **72,009.000**, Products/Lots/transactions **670/799/679**, accepted mappings/prices **0/0**, mutation false, canonical flags false.

### Slice C — source compare + review — COMPLETE + RUNTIME VERIFIED

- `CMS Mapping Review` third system preset at `PRODUCT_CMS_MAPPING` grain;
- provider-aware review filters for `mapping_status`, `source_classification`, and `review_reason`;
- contextual Web review filters and REVIEW/HOLD/mapping-state highlighting;
- checkbox selection + review-context bar;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS Mapping Review current catalogue/accepted-price evidence detail;
- human-friendly presentation of structured CMS review reasons while preserving raw evidence;
- mobile behavior verified at 390x844.

Primary runtime evidence: PR #172 merge `9d030f357a5c3c89e20c4ebba9a702920a227220`, issue #171, and production deployment issue #26. Slice C introduced no accepted mapping, price mutation, inventory mutation, migration-baseline acceptance or DB canonical promotion.

### Slice D — bounded Inventory AI copilot + Deep Review — COMPLETE + RUNTIME VERIFIED

Implemented without creating a second inference stack:

- server-owned `Inventory Review Context` rehydrates the selected review page from preset/filter/pagination coordinates; browser-selected row facts are not trusted as canonical context;
- `Ask AI` hands selected evidence to the existing native AI Workspace Chat path;
- Ask AI creates a **fresh conversation** only after explicit agent choice, prefills the bounded review prompt, and never auto-sends it;
- focused Ask AI modal exposes selected-row context, reliable agent loading/retry, Cancel and explicit Start new chat;
- `Deep Review` opens the existing Owner Multi-Agent REVIEW workspace, prefills title/task and exposes quick REVIEW-preset / role / explicit-run controls;
- Deep Review never auto-selects or auto-runs a review;
- selected review reasons remain human-friendly in the handoff while server-rehydrated evidence remains the source;
- all paths remain read-only with no mapping acceptance, price mutation or inventory mutation authority.

Evidence chain includes PRs #175, #177, #179, #180, #181, #183 and #184; runtime checkpoints #176/#178; deployment issue #26 has confirmed the deployed descendants. Canonical flags remained false throughout.

### Spreadsheet Focus Mode v1 — COMPLETE + RUNTIME VERIFIED

PR #185 merge `af461f2f4ddd329c81fd983955c26e905970e0af` adds the first spreadsheet-workbench interaction layer:

- near-fullscreen Focus mode with explicit Exit and `Escape` exit;
- View/Search/Filters/Columns remain available in focused mode;
- Comfortable/Compact density toggle;
- header Select visible rows checkbox with checked/indeterminate synchronization;
- explicit `Clear selection` action;
- frozen selection column and first visible data column during horizontal scrolling;
- existing Ask AI / Deep Review behavior preserved;
- 390x844 Playwright proof covers focus viewport, selection, density and frozen columns.

Production evidence: issue #186 and deployment issue #26 `status=success` for `af461f2f4ddd329c81fd983955c26e905970e0af` via run `32811537864`.

### Spreadsheet Workbench v2 — CURRENT BOUNDED TARGET

Keep this slice read/review-only. Prioritize high-value spreadsheet ergonomics without turning the browser into a raw DB editor:

1. server-side validated sorting with visible sort indicators;
2. active filter chips and fast per-filter clearing;
3. column resize/reorder, auto-fit and reset-layout controls;
4. copy selected rows as TSV and export current projection as CSV;
5. keyboard navigation/copy shortcuts after the core interaction model is stable;
6. desktop split-pane review detail after table ergonomics are proven.

User-owned persistence of layouts belongs to Slice E rather than being hard-coded into v2.

### Slice E — saved custom views

- persist user-defined view definitions;
- View Builder for row grain, Store scope, fields/order, labels, widths, filters/sorts/groups/formatting;
- duplicate a system preset into a user-owned view without mutating the system preset;
- never permit arbitrary SQL/raw DB expressions.

### Slice F — Daily Usage + typed editing

- Daily Usage monthly-pivot system preset over normalized dated usage events;
- spreadsheet-like `draft -> validation -> preview -> Confirm & Save -> typed command -> audit -> read-back` editing;
- direct current-balance overwrite remains blocked/translated to explicit adjustment workflow.

## Subsequent path

1. Complete Spreadsheet Workbench v2 read/review ergonomics.
2. Persist saved user-defined view definitions / View Builder.
3. Resolve HOLD inventory rows and reviewed CMS mapping exceptions through typed reviewed actions when that mutation slice is explicitly authorized.
4. Add Daily Usage monthly-pivot preset + typed editing flow.
5. Add deterministic reorder baseline engine and reorder presets.
6. Dual verification of real operational events.
7. Accept migration baseline only after source/recovery/reconciliation gates pass.
8. Promote selected DB read paths.
9. Promote controlled write operation classes one at a time.
10. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
11. Sheet mirror/rebuild, exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not present shadow DB as canonical. The immediate target is **Spreadsheet Workbench v2 read/review ergonomics**, not write promotion. Sorting, filtering, layout controls, copy/export and keyboard navigation may improve the review workspace but must not accept CMS mappings/prices, mutate inventory, accept the migration baseline or promote PostgreSQL.