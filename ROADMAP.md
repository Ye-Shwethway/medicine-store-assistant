# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D schema foundation, fresh Main Store staging, source-safe Main-primary shadow materialization, live versioned CMS catalogue import, deterministic CMS reconciliation, and durable non-accepted CMS mapping review-state staging are runtime-verified. F6E configurable read-only Inventory View Engine + first Web renderer are runtime-verified. Slice C implementation is complete on PR #172 and is awaiting CI/merge/production runtime verification. PostgreSQL remains non-canonical.**

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

## F6E — ACTIVE: CONFIGURABLE INVENTORY VIEW + REVIEW WORKSPACE

Architecture:

`Field/Computation Registry -> View Definition -> Generic Renderer -> System/User Presets -> Draft/Edit Commands later`

### Read-only substrate + Web renderer — COMPLETE + RUNTIME VERIFIED

Implemented and verified:

- typed field registry;
- Main Stock and Migration Review system presets;
- authenticated generic rows/presets/registry API;
- registered-field projection and unknown-field rejection;
- one generic Web table renderer driven by returned `columns[]` metadata;
- preset switching, visible-column selection, search and pagination;
- explicit `Shadow inventory — not canonical` state;
- mobile 390x844 browser behavior proof;
- runtime issue #166: Main Stock **799**, Migration Review **823**, quantity **72,009.000**, Products/Lots/transactions **670/799/679**, accepted mappings/prices **0/0**, mutation false, canonical flags false.

### Slice C — source compare + review — IMPLEMENTED, VERIFICATION PENDING

PR #170 merged the first Slice C substrate:

- `CMS Mapping Review` as a third system preset over the same View Engine;
- current Product↔CMS review evidence projection;
- provider-aware filters for `mapping_status`, `source_classification`, and `review_reason`;
- shared-renderer/browser proof for all three presets.

PR #172 implements the remaining Web review workspace:

- contextual mapping-status/source-class/review-reason filter controls;
- unresolved REVIEW/HOLD/mapping-state row highlighting;
- checkbox selection + selection-context bar with no mutation semantics;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS Mapping Review catalogue/current accepted-price evidence detail;
- responsive/mobile drawer/filter behavior;
- behavior-level 390x844 verification covering request wiring, selection and drawer behavior.

Still required before Slice C is COMPLETE:

1. PR #172 CI green and merge;
2. production asset-delivery verification through the content-derived Inventory JS/CSS asset identity;
3. live/runtime proof that review behavior is delivered without changing canonical flags or introducing mutation;
4. sync final checkpoint and advance next authorized work only after that proof.

No accepted CMS mapping, price mutation, inventory write, baseline acceptance or canonical promotion is part of Slice C.

## Subsequent path

1. Embedded context-aware AI assistant + deep-review handoff to AI Workspace.
2. Resolve HOLD inventory rows and mapping exceptions with typed reviewed actions.
3. Persist saved user-defined view definitions and add View Builder.
4. Add Daily Usage monthly-pivot system preset.
5. Add spreadsheet-like draft/preview/Confirm & Save editing over typed commands.
6. Add deterministic reorder baseline engine and reorder presets.
7. Dual verification of real operational events.
8. Accept migration baseline only after source/recovery/reconciliation gates pass.
9. Promote selected DB read paths.
10. Promote controlled write operation classes one at a time.
11. Explicit DB canonicality promotion only after migration/recovery/reconciliation/write gates pass.
12. Sheet mirror/rebuild, exports, Flutter/Telegram expansion and further automation.

## Immediate boundary

Do not present shadow DB as canonical. The immediate target is **Slice C verification**, not AI copilot or write promotion. No mapping acceptance or production mutation is authorized.
