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
6. `docs/architecture/F6C_WORKBOOK_PARITY_LOCK.md`
7. `docs/architecture/STORE_LOCATION_MODEL.md`
8. `docs/architecture/INVENTORY_DATA_MODEL.md`
9. `docs/architecture/CONFIGURABLE_OPERATIONAL_VIEW_ENGINE.md`
10. `docs/architecture/WORKBOOK_PARITY_MATRIX.md`
11. `docs/architecture/WORKBOOK_FUNCTION_CONTRACT.md`
12. `docs/architecture/F2_SCHEMA_DECISION_PROPOSAL.md`
13. `docs/architecture/MIGRATION_AND_SHADOW_VALIDATION.md`
14. `docs/architecture/SHEET_MIRROR_AND_COMPATIBILITY.md`
15. `docs/architecture/CMS_CATALOGUE_VERSIONING.md`
16. `docs/architecture/MONTHLY_LIFECYCLE.md`
17. `skills/medicine-store-assistant/SKILL.md`
18. task-relevant files under `skills/medicine-store-assistant/references/`
19. latest F6C/F6D checkpoints and issue #26 runtime evidence when runtime truth matters.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current project priority

The AI Workspace is accepted supporting infrastructure, not the immediate development center.

**Current bounded task: finish F6C documentation alignment around the Canonical Inventory Foundation.**

**Next bounded implementation slice: F6D Canonical Inventory Schema Parity + Fresh Shadow Import.**

Exact legacy reorder formula and monthly Excel formula/macro parity are deferred unless they change foundational inventory truth.

## Product direction — LOCKED

Canonical foundation:

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Core rules:

> **Spreadsheet layout is configurable; inventory semantics are not arbitrary.**

> **Stock belongs to a location; product and catalogue identity do not.**

> **Store quantity truth comes from movements; totals and operational quantity columns are projections of that truth.**

MSA must support:

- one Main Store plus unlimited Sub Stores;
- human staff and AI agents over one backend;
- Web, Flutter, Telegram, ChatGPT and automation clients;
- durable operation with or without ChatGPT/Google Sheets;
- preset and user-defined spreadsheet-like operational views;
- dynamic inventory intelligence/workflows on top of canonical stock history.

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

### Universal CMS Catalogue

- global/versioned external catalogue, not per store;
- local Product identity does not use CMS Code as primary key;
- Product-to-CMS mapping is auditable/version-aware;
- current catalogue price is separate from historical receipt/source price.

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

## Reorder realignment

Exact legacy Estimated Reorder Qty formula parity is **not an F6D blocker**.

Future reorder may combine usage trends/history, current/incoming stock, expiry risk, safety stock, lead time, store-specific demand, deterministic rules, AI proposal, agent review and human adjustment/approval.

The foundational requirement is good stock/history data, not one fixed formula.

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
6. ensure Universal CMS Catalogue + Product mapping works cleanly;
7. ensure actor/audit/idempotency coverage;
8. take a fresh authorized source snapshot bound to Main Store;
9. import non-canonically with provenance;
10. reconcile opening stock, receipts, usage, CMS mapping/price and current balances;
11. prove per-store balance + all-store Total Stock aggregation;
12. prove Main Stock and Daily Usage projections from DB;
13. keep mismatches explicit and PostgreSQL non-canonical.

## Immediate boundary

Do not let legacy spreadsheet formulas or report formatting drive the canonical schema. Build the minimal durable inventory foundation first, then add configurable views and dynamic AI/rule-based workflows on top.
