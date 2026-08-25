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
- F6D shadow foundation for the current dataset is runtime-verified.
- F6E Slice A/B/C/D are **complete and runtime-verified**.
- Inventory Spreadsheet Focus Mode v1 is **complete and production-runtime verified**.
- Current bounded target is **Spreadsheet Workbench v2 read/review ergonomics**.
- PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.
- Google Sheet/source documents remain operational authority.

Key recent evidence:

- Slice C runtime issue #171.
- Slice D runtime checkpoints #176 and #178.
- PR #183: focused Ask AI modal with reliable agent loading and fresh-chat flow.
- PR #184: Ask AI modal control polish.
- PR #185 merge `af461f2f4ddd329c81fd983955c26e905970e0af`: Spreadsheet Focus Mode v1.
- Runtime checkpoint #186: Focus Mode v1 production evidence.
- Deployment issue #26 confirms `status=success` for `af461f2f4ddd329c81fd983955c26e905970e0af` via run `32811537864`.

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

## F6E verified Inventory baseline

The reusable View Engine currently provides:

- typed field registry and generic View Definition model;
- `main-stock` preset at `PRODUCT_LOT` grain / MAIN;
- `migration-review` preset at `SOURCE_MAIN_ROW` grain / MAIN;
- `cms-mapping-review` preset at `PRODUCT_CMS_MAPPING` grain / ALL;
- authenticated `/dashboard/api/inventory-view/registry`, `/presets`, `/rows`, `/review-context`;
- caller-selected registered field order/subset; unknown fields rejected;
- provider-aware review filters: `mapping_status`, `source_classification`, `review_reason`;
- one generic Web renderer, preset switching, visible-column selection, search and pagination;
- contextual review filters and unresolved review/HOLD/mapping-state highlighting;
- checkbox selection + read-only review-context bar;
- row-click review detail drawer;
- Migration Review source-vs-shadow quantity comparison;
- CMS mapping/current catalogue/accepted-price evidence detail;
- human-friendly structured review-reason presentation;
- explicit `Shadow inventory — not canonical` banner;
- content-derived Inventory JS/CSS asset identity with no-store/no-cache delivery.

Runtime baseline evidence:

- issue #166: Main Stock **799**, Migration Review **823**, quantity **72,009.000**, Products/Lots/transactions **670/799/679**, `ACTIVE_MATCH 0`, accepted prices **0**, mutation false, canonical flags false;
- issue #171: Slice C production-delivery gate complete;
- issues #176/#178: bounded Ask AI / Deep Review runtime checkpoints;
- issue #186: Spreadsheet Focus Mode v1 runtime checkpoint.

## Slice D AI copilot — COMPLETE

Current AI review behavior:

1. Browser sends preset/filter/pagination coordinates and selected row indices to `/review-context`; server rehydrates the bounded review context.
2. `Ask AI` explicitly opens AI Workspace Chat.
3. A focused modal shows selected Inventory context and lets the user choose an agent.
4. Agent list waits for the canonical AI Workspace list and can use the existing agents API as a fallback; failures expose Retry.
5. Only explicit `Start new chat` creates a fresh conversation; selected Inventory context never lands in the previous chat.
6. The bounded prompt is prefilled in the fresh chat, but the user must explicitly press Send.
7. `Deep Review` opens the existing Owner Multi-Agent REVIEW workspace, prefills title/task and exposes quick REVIEW-preset / role / explicit-run controls.
8. Deep Review never silently selects a preset or runs a review.
9. No AI path can accept a mapping/price/inventory change.

## Inventory Spreadsheet Focus Mode v1 — COMPLETE

Production behavior:

- near-fullscreen Inventory Focus mode;
- explicit Exit focus and `Escape` exit;
- View/Search/Filters/Columns retained in the focused workspace;
- Comfortable/Compact density toggle;
- Select visible rows header checkbox with indeterminate state;
- explicit `Clear selection` action;
- frozen selection + first visible data column;
- existing review drawer / Ask AI / Deep Review remain compatible;
- 390x844 Playwright behavior proof is green.

PR #185 merge: `af461f2f4ddd329c81fd983955c26e905970e0af`. Deployment issue #26: `status=success`, run `32811537864`.

## CURRENT — Spreadsheet Workbench v2

Keep the next slice read/review-only. Recommended bounded order:

1. server-side validated sorting + visible sort indicators;
2. active filter chips with per-chip clearing;
3. column resize/reorder + Auto-fit / Reset layout;
4. Copy selected as TSV + CSV export of the current validated projection;
5. keyboard navigation/copy shortcuts after the core interaction model stabilizes;
6. optional desktop split-pane review detail after table ergonomics are proven.

Do **not** add direct spreadsheet mutation yet. Saved layout persistence belongs to Slice E. Mutation-capable Excel-like editing belongs to the later typed editing substrate: `draft -> validation -> preview -> Confirm & Save -> typed command -> audit -> read-back`.

## Next sequence

1. complete Spreadsheet Workbench v2 read/review ergonomics;
2. persist saved user-defined view definitions and build View Builder;
3. resolve HOLD rows/mapping exceptions through reviewed typed actions when explicitly authorized;
4. add Daily Usage monthly-pivot preset;
5. add typed draft/preview/Confirm & Save editing;
6. deterministic reorder baseline + reorder presets;
7. only then advance migration baseline/read/write/canonical promotion gates with explicit evidence.

## Immediate boundary

Do not present shadow DB as canonical. The current workbench slice may sort/filter/rearrange/copy/export validated projections but must not create accepted CMS mappings, push catalogue prices, mutate inventory, accept the migration baseline, or promote PostgreSQL.