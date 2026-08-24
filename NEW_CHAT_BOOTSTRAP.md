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
9. `docs/architecture/REORDER_BASELINE_AND_AI_ENHANCEMENT.md`
10. `docs/architecture/MAIN_STOCK_DAILY_USAGE_MATERIALIZATION.md`
11. `docs/architecture/INVENTORY_DATA_MODEL.md`
12. latest F6C/F6D checkpoints;
13. current runtime evidence issues/PRs when deployment truth matters.

Treat newer verified repository/runtime/source evidence as authoritative over remembered chat context.

## Current state

- F6C Canonical Inventory Foundation is locked.
- F6D migration `0022_inventory_foundation` is implemented and PostgreSQL-CI verified.
- Fresh live Main Store source staging is complete and idempotent.
- Source-safe Main-primary shadow Product/Lot/opening-balance materialization is complete and runtime-verified.
- The first live CMS catalogue version is imported into shadow PostgreSQL as reference data and replay-idempotent.
- Current bounded target: **CMS assisted-reconciliation read-only planner**.
- PostgreSQL remains non-canonical: `database_canonical=false`, `migration_baseline_accepted=false`.

## Locked architecture

`Product -> Lot -> Store -> Movement -> Balance -> Transfer -> CMS Mapping -> Actor/Audit`

Rules:

- spreadsheet layout is configurable; inventory semantics are not arbitrary;
- stock belongs to a location; Product/CMS identity does not;
- quantity truth comes from canonical movements;
- Total Stock is aggregate truth, not an editable master number;
- Main Stock/Daily Usage are projections, not canonical worksheet-shaped tables;
- AI improves workflows but is not an availability dependency;
- CMS Code alone never proves local Product identity.

### Product / Lot / Store

- `product_id` = stable local operational identity.
- normal v1 Lot = Product + structured Expiry Date.
- Store movement does not create a new Product/Lot identity.
- exactly one configured Main Store + unlimited Sub Stores.
- balance = per `(store_id, lot_id)` and movement-derived.

### Universal CMS Catalogue / Mapping

- CMS catalogue is global/versioned external reference data.
- Product-CMS mapping is historical/auditable accepted state, not blind direct sync.
- catalogue import does not create a mapping.
- last accepted mapping and operational price remain usable while a newer catalogue is unresolved.
- recycled/discontinued/ambiguous/local-error possibilities remain explicit review states.
- AI may assist mapping review; deterministic/manual workflow must remain available without AI.
- current catalogue price is separate from historical receipt/source price and local accepted operational price.

### Reorder

Future reorder has a deterministic backend baseline plus optional AI enhancement/review. AI outage must still leave a useful recommendation.

## F6D runtime evidence

### Fresh Main Store stage

- migration batch `7ecf9a2b-0521-400d-8990-caaea20d3a57`;
- source hash `c212d7da6192e7e20f340e7b302436f588dfb0fa191459fd572dfdb46f23ba76`;
- Main Stock **823** rows;
- Daily Usage **823** rows;
- staged records **1,646 = 823 + 823**;
- replay idempotency PASS.

Main Stock owns migration Product/Lot/current-balance evidence. Daily Usage is joined usage evidence only.

### Main-primary materialization

Runtime shadow state:

- Products **670**;
- Lots **799**;
- `OPENING_BALANCE` movements **679**;
- opening quantity **72,009**;
- zero-balance identity-only Lots **120**;
- balance readback mismatches **0**;
- immediate replay created **0 Products / 0 Lots / 0 transactions**.

HOLDs were preserved instead of guessed:

- 14 inventory-semantic review rows;
- duplicate Product+Expiry rows `41,42,156,157`;
- Unit-review rows `237,245,459,460,461,601`.

### Live CMS catalogue version

- sheet `CMS_Price_List_202608`;
- title `August 2026 Updated Price List (Yuan) - 02.08.2026`;
- effective date `2026-08-02`;
- source hash `6f221152024c9a06b73f7f7115097abfb688a37a6ba6bf0be78345f3b70dd116`;
- catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
- rows/codes **6,891 / 6,891**;
- duplicate codes **0**;
- blank codes **0**;
- invalid prices **0**;
- one blank source selling price at row `6442`, code `S10105035`, preserved as `NULL`;
- replay `created=false` for the same version.

Catalogue import protected the local domain. Before/after counts stayed:

- Products **670**;
- Lots **799**;
- inventory transactions **679**;
- Product-CMS mappings **0**.

## CURRENT — CMS assisted-reconciliation planner

Next bounded sequence:

1. join each materialized local Product to its fresh Main Stock source evidence using deterministic normalized local identity;
2. inspect source `serial_code`, `cs_name`, local name, remark, mapping hint and price evidence;
3. compare against catalogue version `34947c29-6427-4b7c-9fb8-ba8ffe3278b0`;
4. produce deterministic read-only categories for continuity, unmapped, discontinued, recycled/review, code absent from current catalogue, code/name conflict and ambiguous local evidence;
5. never treat code equality alone as identity proof;
6. preserve uncertainty where evidence could be historical catalogue change or local staff error;
7. keep `product_cms_mappings=0` during this planner;
8. produce counts and representative review cases before any mapping persistence;
9. AI candidate reasoning may be added later as optional assistance, not authority.

## Source rules

Use the live Google Sheet repeatedly whenever structure/value behavior matters. Do not reverse-engineer exact legacy formulas from cloud materialized values.

Important known facts:

- Product identity != expiry Lot identity != CMS catalogue identity.
- item-name expiry suffix may disagree with structured Expiry Date.
- recycled/discontinued/same-code conflicts may reflect historical mapping, CMS change, or local staff error; preserve uncertainty.
- actual historical movement wins over ideal FIFO/FEFO advice.

## Immediate boundary

No production inventory write, DB canonical promotion, accepted Product-CMS mapping, automatic catalogue-price propagation, full AI matcher, or broad UI expansion belongs in the next slice. The immediate task is deterministic **read-only CMS reconciliation planning**.