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
8. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
9. `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
10. `docs/architecture/INVENTORY_VIEW_ENGINE_V1.md`
11. `docs/architecture/MAIN_STOCK_DAILY_USAGE_MATERIALIZATION.md`
12. `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
13. latest F6D/F6E checkpoints and current runtime evidence issues/PRs.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current state

- F6C Canonical Inventory Foundation is locked.
- F6D shadow foundation for the current dataset is runtime-verified through source staging, Product/Lot/opening-balance materialization, live CMS catalogue import, deterministic CMS reconciliation and durable non-accepted mapping review-state staging.
- F6E Slice A/B/C are **complete and runtime-verified**.
- Slice C runtime issue: #171.
- PR #170 merged the `CMS Mapping Review` preset + provider-aware review filter API.
- PR #172 merged the remaining review workspace at `9d030f357a5c3c89e20c4ebba9a702920a227220`: contextual filters, HOLD/review highlighting, checkbox selection context, row-click detail drawer, Migration Review source-vs-shadow quantity comparison, CMS mapping/price detail and mobile behavior.
- Deployment issue #26 confirmed `status=success` for PR #172 merge via run `32769124095`.
- PR #173 merge `3d7ad88fbd7634571a317cc9b4b5b4c084d77695` is a presentation-only polish that converts structured CMS `review_reason` JSON into human-friendly table/drawer output while preserving raw evidence; its CI is green.
- Current bounded target is **F6E Slice D — embedded Inventory AI copilot context + deep-review handoff**.
- PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.
- Google Sheet/source documents remain operational authority.

## Locked architecture

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Rules:

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from movements;
- Total Stock is aggregate truth, not an editable master number;
- Main Stock/Daily Usage are projections, not canonical worksheet-shaped tables;
- Main Stock, Daily Usage, Migration Review and CMS Mapping Review are system presets over one reusable View Engine;
- user-defined sheet-style views later bind columns to registered semantic fields/computations/typed commands, never arbitrary SQL/raw DB expressions;
- AI improves workflows but is not an availability dependency;
- CMS Code alone never proves local Product identity.

## Verified F6D shadow state

- migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- Main Stock **823**, Daily Usage **823**, staged evidence **1,646**;
- Products **670**, Lots **799**, opening movements **679**, opening quantity **72,009**;
- zero-balance identity-only Lots **120**, balance mismatches **0**, replay created **0/0/0**;
- unresolved HOLD evidence remains: 14 inventory-semantic review rows, duplicate Product+Expiry rows `41,42,156,157`, Unit-review rows `237,245,459,460,461,601`.

CMS state:

- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`, effective `2026-08-02`;
- rows / unique codes **6,891 / 6,891**, duplicates **0**, one blank price preserved as `NULL`;
- durable non-accepted mapping rows **670**: `REVIEW_REQUIRED 644`, `CMS_DISCONTINUED 19`, `RECYCLED_CODE 1`, `UNMAPPED 6`, `ACTIVE_MATCH 0`;
- accepted operational prices **0**.

## F6E Slice A/B/C — runtime verified baseline

Implemented:

- typed field registry and generic View Definition model;
- `main-stock` preset at `PRODUCT_LOT` grain / MAIN;
- `migration-review` preset at `SOURCE_MAIN_ROW` grain / MAIN;
- `cms-mapping-review` preset at `PRODUCT_CMS_MAPPING` grain / ALL;
- authenticated `/dashboard/api/inventory-view/registry`, `/presets`, `/rows`;
- caller-selected registered field order/subset; unknown fields rejected;
- provider-aware review filters: `mapping_status`, `source_classification`, `review_reason`;
- one generic Web renderer, preset switching, visible-column selection, search and pagination;
- contextual review filters and unresolved review/HOLD/mapping-state highlighting;
- checkbox selection + read-only review-context bar;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS mapping/current catalogue/accepted-price evidence detail;
- explicit `Shadow inventory — not canonical` banner;
- content-derived Inventory JS/CSS asset identity with no-store/no-cache delivery;
- 390x844 behavior proof.

Runtime evidence:

- issue #166: Main Stock **799**, Migration Review **823**, quantity **72,009.000**, Products/Lots/transactions **670/799/679**, `ACTIVE_MATCH 0`, accepted prices **0**, mutation false, canonical flags false;
- issue #171: Slice C production-delivery gate complete;
- deployment issue #26: `status=success` for Slice C merge `9d030f357a5c3c89e20c4ebba9a702920a227220`.

## F6E Slice D — CURRENT

Goal: make Inventory review AI-assisted without creating a second inference stack and without giving AI acceptance authority.

Next bounded work:

1. Define an `Inventory Review Context` payload containing only current preset/view metadata, active filters, selected rows and allowed source/review evidence.
2. Add an embedded assistant entry point inside Inventory that can summarize, explain, compare and rank selected evidence.
3. Reuse the existing native AI Workspace/internal-agent runtime instead of adding a parallel inference implementation.
4. Add `Deep Review` handoff from selected Inventory rows into AI Workspace/multi-agent review using the existing durable conversation/review substrate.
5. Keep the Inventory AI path read-only by default; AI may propose but cannot accept a mapping/price/inventory change.
6. Keep durable Owner/authorized typed acceptance as a later mutation gate.
7. Add browser/runtime proof that only the bounded selected context is handed off and canonical flags remain false.

## Next sequence

1. complete Slice D embedded Inventory AI copilot + deep-review handoff;
2. resolve HOLD rows/mapping exceptions through reviewed typed actions;
3. persist saved user-defined view definitions and build View Builder;
4. add Daily Usage monthly-pivot preset;
5. add draft/preview/Confirm & Save editing over typed commands;
6. deterministic reorder baseline + reorder presets;
7. only then advance migration baseline/read/write/canonical promotion gates with explicit evidence.

## Immediate boundary

Do not present shadow DB as canonical. Slice D is an AI **review/context** feature, not a write feature. Do not create accepted CMS mappings, push catalogue prices, mutate inventory, accept the migration baseline, or promote PostgreSQL while implementing the embedded assistant/handoff.
