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
- F6E configurable read-only Inventory View Engine + first Web renderer are runtime-verified.
- PR #170 is merged: `CMS Mapping Review` is the third system preset and provider-aware review filters (`mapping_status`, `source_classification`, `review_reason`) exist in the generic API.
- PR #172 implements the remaining Slice C Web review workspace: review filter controls, HOLD/review highlighting, checkbox selection context, row-click detail drawer, Migration Review source-vs-shadow quantity comparison, CMS mapping/price detail, and mobile behavior proof.
- PR #172 is not yet considered complete until CI, merge, production asset delivery and runtime verification are all green.
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

## F6E baseline — runtime verified

- typed field registry and generic View Definition model;
- `main-stock` preset at `PRODUCT_LOT` grain / MAIN;
- `migration-review` preset at `SOURCE_MAIN_ROW` grain / MAIN;
- authenticated `/dashboard/api/inventory-view/registry`, `/presets`, `/rows`;
- caller-selected registered field order/subset; unknown fields rejected;
- one generic Web renderer, preset switching, visible-column selection, search and pagination;
- explicit `Shadow inventory — not canonical` banner;
- content-derived Inventory JS/CSS asset identity with no-store/no-cache delivery;
- 390x844 behavior proof.

Runtime issue #166 proves Main Stock **799**, Migration Review **823**, quantity **72,009.000**, Products/Lots/transactions **670/799/679**, `ACTIVE_MATCH 0`, accepted prices **0**, mutation false, canonical flags false.

## F6E Slice C — verification gate

Merged PR #170 provides:

- `CMS Mapping Review` system preset at `PRODUCT_CMS_MAPPING` grain;
- local Product/CMS code/name/mapping status/current catalogue price/accepted store price/review reason projection;
- generic API filters for mapping status, source classification and review reason.

PR #172 provides:

- contextual Web filter controls wired to those API parameters;
- unresolved review/HOLD/mapping-state highlighting;
- checkbox selection and selection-context bar with no automatic acceptance;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS Mapping Review mapping/price evidence detail;
- responsive mobile drawer/filter behavior;
- expanded Playwright proof at 390x844.

Slice C becomes COMPLETE only after PR #172 CI is green, the PR is merged, issue #26 confirms deployment of the merge SHA, and live/runtime proof confirms the delivered UI while canonical flags and mutation boundary remain unchanged.

## Next sequence

1. finish Slice C verification and final continuity sync;
2. embedded context-aware AI assistant + deep-review handoff to AI Workspace;
3. resolve HOLD rows/mapping exceptions through reviewed typed actions;
4. persist saved user-defined view definitions and build View Builder;
5. add Daily Usage monthly-pivot preset;
6. add draft/preview/Confirm & Save editing over typed commands;
7. deterministic reorder baseline + reorder presets;
8. only then advance migration baseline/read/write/canonical promotion gates with explicit evidence.

## Immediate boundary

Do not present shadow DB as canonical. Do not create accepted CMS mappings, push catalogue prices, mutate inventory or enable production writes as part of Slice C. Do not advance to AI copilot work before Slice C verification is complete.
