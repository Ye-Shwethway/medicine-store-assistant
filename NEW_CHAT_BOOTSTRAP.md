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
- F6E configurable read-only Inventory View Engine + first Web renderer are **runtime-verified**.
- Slice C feature branch `feat/f6e-slice-c-review-preset` adds a third `CMS Mapping Review` system preset plus provider-aware review-filter API (`mapping_status`, `source_classification`, `review_reason`).
- The new Slice C branch is not yet the final runtime-verified slice: source-vs-shadow detail drawer, contextual Web review filter controls, HOLD highlighting, selection/bulk context and deployment proof remain pending.
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
- Main Stock, Daily Usage, Migration Review and CMS Mapping Review are **system presets over one reusable View Engine**, not fixed screens;
- user-defined sheet-style views later bind columns to a registered semantic field/computation/typed-command contract, never arbitrary SQL/raw DB expressions;
- AI improves workflows but is not an availability dependency;
- CMS Code alone never proves local Product identity.

## Verified F6D shadow state

### Source + inventory materialization

- fresh migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- source hash `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`;
- Main Stock **823** rows;
- Daily Usage **823** rows;
- staged evidence **1,646 = 823 + 823**, not 1,646 inventory objects;
- Products **670**;
- Lots **799**;
- `OPENING_BALANCE` movements **679**;
- opening quantity **72,009**;
- zero-balance identity-only Lots **120**;
- balance mismatches **0**;
- materialization replay created **0/0/0** Product/Lot/transaction rows.

HOLDs remain unresolved instead of guessed: 14 inventory-semantic review rows, duplicate Product+Expiry rows `41,42,156,157`, and Unit-review rows `237,245,459,460,461,601`.

### CMS catalogue + review state

- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- effective date `2026-08-02`;
- source hash `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- rows / unique codes **6,891 / 6,891**;
- duplicate codes **0**;
- one blank source price preserved as `NULL`.

Deterministic reconciliation produced 526 exact-name/same-price continuity candidates, 77 exact-name/changed-price candidates, 30 multiple-source-code cases, 19 discontinued, 9 code/name mismatch, 6 unmapped, 1 missing source CMS name, 1 multiple source CMS names and 1 recycled-code case.

Durable non-accepted mapping state contains **670** rows:

- `REVIEW_REQUIRED` **644**;
- `CMS_DISCONTINUED` **19**;
- `RECYCLED_CODE` **1**;
- `UNMAPPED` **6**;
- `ACTIVE_MATCH` **0**;
- accepted operational prices **0**.

This state is review evidence, not accepted mapping authority.

## F6E Inventory View Engine — runtime verified baseline

Implemented and live on `main`:

- `backend/app/inventory_view_engine.py` typed field registry + generic View Definition model;
- semantic classes `ENTITY_FIELD`, `COMPUTED_FIELD`, `COMMAND_EDITABLE_FIELD`, `DISPLAY_HELPER`;
- `main-stock` system preset at `PRODUCT_LOT` grain / Store MAIN;
- `migration-review` system preset at `SOURCE_MAIN_ROW` grain / Store MAIN;
- authenticated `/dashboard/api/inventory-view/registry`, `/presets`, `/rows` API;
- validated caller-selected registry field subset/order; unknown fields rejected;
- generic product-facing Inventory Web renderer driven by API `columns[]` metadata;
- one renderer switches Main Stock / Migration Review;
- registry-driven visible-column selection, search and pagination;
- explicit `Shadow inventory — not canonical` banner;
- old staged-row Inventory grid removed from the product-facing runtime subtree while Shadow Inspection remains separate;
- content-derived JS/CSS asset versioning;
- Playwright 390x844 behavior proof; mobile banner overflow was caught and fixed before merge.

PR #165 merge/runtime SHA: `3da90d7e1a26eaee23fc60c4dd9467012610c1ea`; deploy status succeeded.

Runtime issue #166 proves:

- Main Stock projected rows **799**;
- Migration Review projected rows **823**;
- Main Stock current quantity sum **72,009.000**;
- Products/Lots/inventory transactions **670 / 799 / 679**;
- `ACTIVE_MATCH` **0**;
- accepted operational prices **0**;
- mutation **false**;
- canonical flags remain false.

## F6E Slice C — current feature branch

Branch: `feat/f6e-slice-c-review-preset`

Implemented on the branch:

- `CMS Mapping Review` system preset at `PRODUCT_CMS_MAPPING` grain;
- same generic `/presets` + `/rows` contract, so the existing Web preset selector/renderer can display it without a second table implementation;
- fields include local item, unit, CMS code/name, mapping status, current catalogue price, accepted store price and review reason;
- provider-aware `mapping_status`, `source_classification` and `review_reason` query filters;
- verifier updated from two to three system presets;
- browser smoke updated to switch Main Stock -> Migration Review -> CMS Mapping Review using the same generic table.

Still pending for Slice C completion:

- source-vs-shadow detail/drawer;
- explicit HOLD/review highlighting;
- contextual Web filter controls wired to the new API filters;
- selection/bulk-context substrate with no automatic acceptance;
- full CI/runtime/deployment proof after the complete Web slice is merged.

## AI / review direction

Inventory is the primary visual review/workspace. Embedded AI later receives current view, selected rows, filters and source evidence as context. Difficult/disputed cases may escalate to AI Workspace/multi-agent review. AI may explain/rank/propose but does not own acceptance authority.

Migration progression remains:

`shadow projection -> source reconciliation -> exception review -> baseline acceptance -> selected DB read promotion -> controlled write promotion -> explicit canonical promotion`

## Next sequence

1. complete contextual Web HOLD/status/reason controls over the new filter API;
2. add source-vs-shadow compare detail/drawer;
3. add selection/bulk-context substrate, still no automatic acceptance;
4. run/record full browser + runtime deployment proof and sync docs;
5. add embedded AI copilot + deep-review handoff;
6. resolve HOLD rows/mapping exceptions through reviewed typed actions;
7. persist saved user-defined view definitions and build View Builder;
8. add Daily Usage monthly-pivot preset;
9. add draft/preview/Confirm & Save editing over typed commands;
10. deterministic reorder baseline + reorder presets;
11. only then advance migration baseline/read/write/canonical promotion gates with explicit evidence.

## Immediate boundary

Do not present shadow DB as canonical. Do not create accepted CMS mappings, push catalogue prices, mutate inventory or enable production writes as part of the current review/View Engine slice.