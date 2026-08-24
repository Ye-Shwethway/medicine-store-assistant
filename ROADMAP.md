# Medicine Store Assistant — Project Roadmap

Status: **F6C Canonical Inventory Foundation is locked. F6D shadow foundation is runtime-verified. F6E Slice A/B/C are complete and runtime-verified through the configurable read-only Inventory View Engine, generic Web renderer, CMS Mapping Review and source-vs-shadow review workspace. Current bounded target: Slice D embedded Inventory AI copilot context + deep-review handoff. PostgreSQL remains non-canonical.**

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

## F6E — ACTIVE: CONFIGURABLE INVENTORY VIEW + AI-ASSISTED REVIEW

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

PR #170:

- added `CMS Mapping Review` as the third system preset at `PRODUCT_CMS_MAPPING` grain;
- added current Product↔CMS review evidence projection;
- added provider-aware filters for `mapping_status`, `source_classification`, and `review_reason`.

PR #172 merge `9d030f357a5c3c89e20c4ebba9a702920a227220`:

- contextual Web review filters;
- unresolved REVIEW/HOLD/mapping-state highlighting;
- checkbox selection + review-context bar;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS Mapping Review catalogue/current accepted-price evidence detail;
- responsive/mobile drawer/filter behavior;
- 390x844 behavior proof covering filter request wiring, selection and drawer behavior.

Production runtime proof:

- deployment issue #26 reports `status=success` for merge `9d030f357a5c3c89e20c4ebba9a702920a227220` via run `32769124095`;
- runtime issue #171 marks Slice C COMPLETE;
- canonical flags remain false and no mutation was introduced.

Post-verification polish PR #173 merge `3d7ad88fbd7634571a317cc9b4b5b4c084d77695` humanizes structured CMS `review_reason` values in table/drawer presentation while preserving raw evidence and read-only semantics. Its CI passed backend, Web reliability, View Engine and dedicated browser regression.

### Slice D — embedded Inventory AI copilot — CURRENT

Goal: make the Inventory review workspace AI-assisted without creating a second inference/runtime stack and without giving AI acceptance authority.

Bounded direction:

1. Define an `Inventory Review Context` contract containing only current preset/view metadata, active filters, selected rows and allowed source/review evidence.
2. Add an embedded assistant entry point inside Inventory that can summarize, explain, rank and compare selected evidence.
3. Reuse the existing native AI Workspace/internal-agent runtime and existing durable conversation/review substrate.
4. Add `Deep Review` handoff from selected Inventory rows into AI Workspace/multi-agent review.
5. Preserve read-only operation by default; no mapping acceptance, price mutation or inventory mutation is implied by an AI response.
6. Keep durable Owner/authorized typed acceptance as the later mutation gate.
7. Add behavior/runtime proof that only the selected bounded evidence is transferred and canonical flags remain false.

## Subsequent path

1. Complete Slice D embedded Inventory AI copilot + deep-review handoff.
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

Do not present shadow DB as canonical. The immediate target is **Slice D bounded AI review context and handoff**, not write promotion. AI may explain/summarize/rank/propose only; it may not accept CMS mappings/prices, mutate inventory, accept the migration baseline or promote PostgreSQL.
