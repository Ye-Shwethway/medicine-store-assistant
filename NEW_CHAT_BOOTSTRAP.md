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
8. `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
9. `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
10. `docs/architecture/INVENTORY_DATA_MODEL.md`
11. `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
12. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
13. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
14. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
15. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
16. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
17. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
18. `docs/architecture/MONTHLY_LIFECYCLE.md`
19. `skills/medicine-store-assistant/SKILL.md`
20. task-relevant files under `skills/medicine-store-assistant/references/`
21. latest F6C/F6D checkpoints and issue #26 runtime evidence when runtime truth matters.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current project priority

The AI Workspace is accepted supporting infrastructure, not the immediate development center.

**F6C Canonical Inventory Foundation documentation is aligned enough to move into F6D.**

**Current bounded implementation slice: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

Exact legacy reorder formula and monthly Excel formula/macro parity are deferred unless they change foundational inventory truth.

## Product direction — LOCKED

Canonical foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

> **AI enhances store workflows but must not become a single point of operational failure.**

MSA must support:

- one Main Store plus unlimited Sub Stores;
- human staff and AI agents over one backend;
- Web, Flutter, Telegram, ChatGPT and automation clients;
- durable operation with or without ChatGPT/Google Sheets;
- preset and user-defined spreadsheet-like operational views;
- deterministic essential fallbacks when AI is unavailable;
- optional AI-assisted reconciliation and intelligence.

## Canonical inventory semantics

### Product / Lot

- `product_id` = stable local identity.
- v1 normal `lot_id` = Product + Expiry Date operational identity.
- changing store/location does not create a new Product/Lot.
- `No.` is display/order metadata only.

### Store / balance

- exactly one configured Main Store plus unlimited Sub Stores.
- canonical balance is per `(store_id, lot_id)`.
- current live Medicine Store Cloud contains no populated Store/Location field and is treated as the configured legacy Main Store context for migration.

### Quantity fields

Operational views may show:

`Original/Opening Qty | Received Qty | Deducted/Used Qty | Current Qty | Total Stock`

These are not separate mutable truths.

```text
Current Qty
  = Opening
  + Receipts
  + Transfer In
  + Positive Adjustments
  - Usage
  - Transfer Out
  - Negative Adjustments
```

Total system stock is the sum of location balances, not a separately editable master number.

### Transfer

Internal transfer preserves Product/Lot identity and atomically produces source `TRANSFER_OUT` + destination `TRANSFER_IN` effects under one transfer/operation identity.

### Universal CMS Catalogue / mapping lifecycle

- global/versioned external catalogue, not per store;
- local Product identity does not use CMS Code as primary key;
- mapping is historical/auditable accepted state, not blind direct sync;
- current catalogue price is separate from historical receipt/source price;
- last accepted mapping and operational price remain usable while a newer catalogue is unresolved;
- recycled/discontinued/ambiguous mappings are structured review states;
- AI can assist candidate reasoning but cannot silently remap;
- when AI is unavailable, manual mapping remains possible and ordinary inventory continues with accepted state.

Core rule:

> **CMS mapping is never blindly auto-synced. Last accepted mapping and price state remain usable until a newer mapping is reviewed and accepted.**

The live workbook contains `Recycled ID`, `CMS Discontinued (Local Stock Retained)` and same-code/identity-conflict evidence. Do not treat every conflict as a CMS error or a local error; preserve uncertainty for review.

### Actor / audit

All protected operations resolve stable human or agent/service-principal identity, client/channel, operation/idempotency ID, source/reason/evidence, outcome and read-back.

AI proposal/review never implicitly grants mutation authority.

## Workbook role

Use the live Google Sheet repeatedly whenever current structure/value behavior matters.

- Main Stock = operational stock/lot projection.
- Daily Usage = monthly Day 1-31 pivot/edit view over normalized usage events.
- This Month Received = derived receipt view.
- Reorder Form = working view.
- Final Reorder = reviewed/manual-adjustable output.
- Master archive = legacy reporting/archive compatibility.

Representative Google Sheet `FORMULA` reads return materialized values, not exact Excel formula strings. Do not reverse-engineer Excel formulas from them.

## Reorder resilience

Exact legacy Estimated Reorder Qty formula parity is **not an F6D blocker**, but reorder must work without AI.

Two-layer model:

1. deterministic baseline calculation from structured local/backend data and configuration;
2. optional AI/advanced enhancement/review.

AI unavailable:

`stock/history -> deterministic baseline -> human review/adjustment -> final reorder`

AI available:

`stock/history -> deterministic baseline -> AI enhancement/review -> human/authorized workflow -> final reorder`

The user must not be forced to manually calculate every item merely because AI providers are unavailable.

## Current canonicality boundary

- Google Sheet/source documents remain operationally authoritative.
- PostgreSQL remains **non-canonical shadow/test**.
- F6B is not an accepted migration baseline.
- `database_canonical=false`; `migration_baseline_accepted=false`.
- no production inventory mutation or canonical promotion is authorized.

## F6D immediate sequence

1. add canonical Store/Location identity;
2. make stock movements location-aware;
3. add receipt destination/provenance;
4. add explicit atomic internal transfer representation;
5. preserve Product/Lot identity independently of location;
6. retain Universal CMS Catalogue versioning;
7. implement historical/auditable Product-CMS mapping lifecycle and last-accepted-state persistence;
8. ensure actor/audit/idempotency coverage;
9. take a fresh authorized source snapshot bound to Main Store;
10. import non-canonically with provenance;
11. reconcile opening stock, receipts, usage, CMS mapping/price and current balances;
12. preserve recycled/discontinued/review-required mapping states rather than forcing matches;
13. prove per-store balance + all-store Total Stock aggregation;
14. prove Main Stock and Daily Usage projections from DB;
15. keep mismatches explicit and PostgreSQL non-canonical.

F6D does not need the final AI semantic matcher or full deterministic reorder engine. It must persist the state needed to add them later without redesign.

## Immediate boundary

Do not let legacy spreadsheet formulas or report formatting drive the canonical schema. Build the minimal durable inventory foundation first, then add configurable views, deterministic fallback engines and optional AI-assisted workflows on top.
