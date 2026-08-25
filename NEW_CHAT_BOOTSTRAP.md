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
13. `docs/architecture/REUSABLE_EXCEL_EXPORT.md`
14. latest F6D/F6E checkpoints and current runtime evidence issues/PRs.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current state

- F6C Canonical Inventory Foundation is locked.
- F6D shadow foundation for the current dataset is runtime-verified.
- F6E Slice A/B/C/D are **complete and runtime-verified**.
- Inventory Spreadsheet Focus Mode v1 is **complete and production-runtime verified**.
- Spreadsheet Workbench v2 filter chips, session layout tools, Copy TSV, validated server-side sorting, CSV compatibility export and formatted Excel export are **complete and production-runtime verified**.
- Inventory now exposes **Export Excel** rather than CSV as the user-facing export action.
- The `.xlsx` renderer is a **globally reusable tabular export module**, not an Inventory-only serializer; later user-created View Builder tables and other MSA areas should reuse it.
- Current system-preset exports use the preset name and current visible registered field order/filter/sort structure.
- PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.
- Google Sheet/source documents remain operational authority.

Key recent evidence:

- PR #199 merge `4d407e5d01343deb3da9a8a0f82f6122e989035f`: Inventory quantity/date display format polish; runtime run `32821445117`; deploy run `32821445217`.
- Slice C runtime issue #171.
- Slice D runtime checkpoints #176 and #178.
- PR #183: focused Ask AI modal with reliable agent loading and fresh-chat flow.
- PR #184: Ask AI modal control polish.
- PR #185 merge `af461f2f4ddd329c81fd983955c26e905970e0af`: Spreadsheet Focus Mode v1.
- Runtime checkpoint #186: Focus Mode v1 production evidence.
- PR #188 merge `2012c2656032a274a185ba1e9ce63378aa95c182`: Workbench v2 filter chips, session column reorder/width/Auto-fit/Reset and Copy TSV.
- Runtime checkpoint #189: PR #188 production evidence.
- PR #190 merge `1ecbe7457166c6b1b29faf1a1a05a2d69e3e4756`: validated server-side sorting and sort-aware AI review context.
- PR #192 merge `27d41d7ffbdcdf60252f591b7978bea02819527e`: F6E runtime-verifier sorting-signature compatibility.
- Runtime checkpoint #191: server-side sorting delivery/runtime complete.
- PR #194 merge `db22884e2d5ad7c27ada1ae80ea14913fb90a148`: validated server-side CSV compatibility export.
- PR #195 merge `5451e5e698a379f4fbfcf3a9944903746ae5a075`: CSV export runtime proof.
- PR #197 merge `8a73fb856a05d347f32c5158034fb7435a9cf82f`: globally reusable formatted Excel export + Inventory `Export Excel` UI.
- Runtime issue #166 / run `32818308165` at `8a73fb856a05d347f32c5158034fb7435a9cf82f`: Excel export success with `Main Stock`, **799** rows, columns `Items / Current Qty / CMS Code`, freeze pane `A2`, sort `local_item_name:asc`, mutation false and canonical flags false.

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
- reusable Excel export accepts already-authorized typed tabular projections and owns workbook presentation only; it does not query data or decide authorization/domain semantics;
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

Latest read-only runtime baseline at main SHA `8a73fb856a05d347f32c5158034fb7435a9cf82f`:

- Main Stock projected rows **799**;
- Migration Review projected rows **823**;
- Main Stock current quantity sum **72,009.000**;
- Products/Lots/transactions **670/799/679**;
- `ACTIVE_MATCH 0`;
- accepted operational prices **0**;
- formatted Excel export rows **799**;
- Excel export sheet `Main Stock`;
- Excel export columns `Items / Current Qty / CMS Code`;
- Excel freeze pane `A2`;
- CSV compatibility rows **799**;
- `mutation=false`;
- `database_canonical=false`;
- `migration_baseline_accepted=false`.

## Slice D AI copilot — COMPLETE

Current AI review behavior:

1. Browser sends preset/filter/pagination/sort coordinates and selected row indices to `/review-context`; server rehydrates the bounded review context.
2. `Ask AI` explicitly opens AI Workspace Chat.
3. A focused modal shows selected Inventory context and lets the user choose an agent.
4. Agent list waits for the canonical AI Workspace list and can use the existing agents API as a fallback; failures expose Retry.
5. Only explicit `Start new chat` creates a fresh conversation; selected Inventory context never lands in the previous chat.
6. The bounded prompt is prefilled in the fresh chat, but the user must explicitly press Send.
7. `Deep Review` opens the existing Owner Multi-Agent REVIEW workspace, prefills title/task and exposes quick REVIEW-preset / role / explicit-run controls.
8. Deep Review never silently selects a preset or runs a review.
9. No AI path can accept a mapping/price/inventory change.

AI Workspace general UX work is not the current slice; the current product focus remains the Inventory section.

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

PR #185 merge: `af461f2f4ddd329c81fd983955c26e905970e0af`.

## Spreadsheet Workbench v2 — ACTIVE

Already production-runtime verified:

1. active Search/Mapping/Source-class/Review-reason chips with per-chip clearing;
2. session-only column reorder and width controls over registered fields;
3. Auto-fit and Reset preset/layout;
4. Copy selected visible rows as TSV;
5. Product+Lot row selection keyed by Lot ID before Product ID;
6. provider-owned validated server-side sorting with stable tie-breakers;
7. sortable headers with `↕ / ▲ / ▼`, `aria-sort` and an active Sort chip;
8. selection/drawer reset on order changes;
9. Ask AI / Deep Review preserve exact sort field/direction for server rehydration;
10. validated server-side CSV compatibility export with registered field/filter/sort state and a 5,000-row no-truncation cap;
11. user-facing `Export Excel` over the same validated projection/filter/sort contract;
12. globally reusable `.xlsx` renderer with blue/white wrapped header, typed cells, bounded auto sizing, thin borders/grid appearance, freeze pane `A2`, visible gridlines and Excel Table filters;
13. formula-significant source strings remain literal text in the workbook.

The reusable renderer lives in `backend/app/tabular_excel_export.py` and is intentionally domain-agnostic. Current Inventory presets are the first consumer. Later user-owned View Builder tables and other MSA tabular areas must reuse this renderer rather than creating parallel Excel-export implementations.

Next bounded Inventory work: consider one-click Clear all, then keyboard navigation/copy shortcuts, then optional desktop split-pane review detail. Saved layout persistence and user-created tables belong to Slice E.

Mutation-capable Excel-like editing belongs to the later typed editing substrate: `draft -> validation -> preview -> Confirm & Save -> typed command -> audit -> read-back`.

## Next sequence

1. complete remaining Spreadsheet Workbench v2 read/review ergonomics: optional clear-all / keyboard / split-pane;
2. persist saved user-defined view definitions and build View Builder, reusing global Excel export;
3. resolve HOLD rows/mapping exceptions through reviewed typed actions when explicitly authorized;
4. add Daily Usage monthly-pivot preset;
5. add typed draft/preview/Confirm & Save editing;
6. deterministic reorder baseline + reorder presets;
7. only then advance migration baseline/read/write/canonical promotion gates with explicit evidence.

### Inventory display/export format polish — COMPLETE + RUNTIME VERIFIED

PR #199 merge `4d407e5d01343deb3da9a8a0f82f6122e989035f` refined presentation without changing inventory semantics:

- Excel quantity fields use whole-number display format `0`;
- Excel price fields use decimal display format `0.00`;
- Excel Expiry Date uses `mmm-yy` (for example `Mar-26`);
- the global `ExcelColumn` contract accepts caller-owned `number_format`, keeping the reusable renderer area-agnostic;
- Inventory Web date display defaults to `DD-MM-YYYY`;
- the Web toolbar provides `DD-MM-YYYY`, `MM-DD-YYYY`, `YYYY-MM-DD`, and `DD-MMM-YYYY` display choices;
- the selected Web date format is display-only and persists locally across reopen; underlying ISO dates/query semantics are unchanged.

Runtime issue #166, run `32821445117`, verified Main Stock **799** rows with Excel formats `expiry=mmm-yy`, `qty=0`, `price=0.00`, `mutation=false`, `database_canonical=false`, `migration_baseline_accepted=false`. Deployment issue #26, run `32821445217`, verified production deployment success at the same SHA.

## Immediate boundary

Do not present shadow DB as canonical. The current workbench may sort/filter/rearrange/copy/export validated projections, including globally reusable formatted Excel output, but must not create accepted CMS mappings, push catalogue prices, mutate inventory, accept the migration baseline, or promote PostgreSQL.

## Current bounded target — Inventory Sheet Interaction Foundation v1

Formatted Excel export is complete and production-runtime verified. The active Inventory work is now `docs/design/INVENTORY_SHEET_INTERACTION_V1.md`: cell-first selection, rectangular ranges, keyboard navigation, whole-row selector gutter, explicit Details, and selection-aware copy. Do not restore row-wide click-to-open behavior. Whole-row selection remains the only source for Ask AI / Deep Review row context. Fill colors/persistent formatting follow after this v1; Saved Custom Views / View Builder follows the sheet interaction/formatting foundation. All current work remains read-only and PostgreSQL remains non-canonical.
